"""
LangGraph API 測試腳本
測試 AI 調酒大師的 LangGraph 功能

包含：
- 基本 API 測試（健康檢查、調酒查詢）
- LangGraph 特有功能測試（7 個工具、多輪對話、語義搜尋）
- RAG 功能測試（口味搜尋、場景搜尋）
"""
import requests
import json
from datetime import datetime
import time

BASE_URL = 'http://localhost:5000'

# ANSI 顏色碼
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_section(title):
    """打印分節標題"""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{title:^70}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}")

def print_success(message):
    """打印成功訊息"""
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    """打印錯誤訊息"""
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    """打印資訊訊息"""
    print(f"{YELLOW}ℹ {message}{RESET}")

def print_tool(tool_name):
    """打印工具使用訊息"""
    print(f"{CYAN}🔧 工具: {tool_name}{RESET}")


# ========== 基本測試 ==========

def test_health_check():
    """測試健康檢查"""
    print_section("1. 健康檢查")
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API 運行正常")
            print(f"  狀態: {data.get('status')}")
            print(f"  MongoDB: {data.get('mongodb')}")
            print(f"  Groq: {data.get('groq')}")
            print(f"  RAG: {data.get('rag')}")
            print(f"  LangSmith: {data.get('langsmith', 'N/A')}")
            
            # 檢查 RAG 是否啟用
            if data.get('rag') == 'enabled':
                print_success("RAG 功能已啟用 ✨")
                return True
            else:
                print_error("RAG 功能未啟用")
                return False
        else:
            print_error(f"健康檢查失敗: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"錯誤: {str(e)}")
        return False


def get_auth_token():
    """取得認證 token"""
    print_section("2. 用戶認證")
    
    # 嘗試登入
    login_data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/login', json=login_data, timeout=5)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print_success("使用現有帳號登入成功")
            return token
    except:
        pass
    
    # 如果登入失敗，嘗試註冊
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    register_data = {
        'username': f'test_user_{timestamp}',
        'email': f'test_{timestamp}@example.com',
        'password': 'password123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/register', json=register_data, timeout=5)
        if response.status_code == 201:
            token = response.json().get('access_token')
            print_success(f"註冊新帳號成功: {register_data['email']}")
            return token
        else:
            print_error(f"註冊失敗: {response.json().get('message')}")
            return None
    except Exception as e:
        print_error(f"認證錯誤: {str(e)}")
        return None


# ========== LangGraph 工具測試 ==========

def test_tool_search_by_name(token):
    """測試工具 1: search_by_name"""
    print_section("3. 測試工具: search_by_name")
    
    test_cases = [
        "Mojito 怎麼做？",
        "告訴我 Margarita 的配方",
        "我想知道 Old Fashioned"
    ]
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for message in test_cases:
        print(f"\n💬 測試: {message}")
        try:
            response = requests.post(
                f'{BASE_URL}/api/chat/message',
                json={'message': message},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('tool_used'):
                    print_success("工具已調用")
                    print(f"  回應長度: {len(result.get('message', ''))} 字元")
                    return True
                else:
                    print_info("未使用工具（可能 LLM 直接回答）")
            else:
                print_error(f"請求失敗: {response.status_code}")
        except Exception as e:
            print_error(f"錯誤: {str(e)}")
        
        time.sleep(1)
    
    return False


def test_tool_search_by_ingredients(token):
    """測試工具 2: search_by_ingredients"""
    print_section("4. 測試工具: search_by_ingredients")
    
    message = "有什麼調酒用到伏特加和檸檬汁？"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"💬 測試: {message}")
    try:
        response = requests.post(
            f'{BASE_URL}/api/chat/message',
            json={'message': message},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('tool_used'):
                print_success("材料搜尋工具已調用")
                print(f"  回應: {result.get('message', '')[:200]}...")
                return True
            else:
                print_info("未使用材料搜尋工具")
                return False
        else:
            print_error(f"請求失敗: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"錯誤: {str(e)}")
        return False


def test_tool_semantic_taste(token):
    """測試工具 4: search_by_taste_semantic (RAG)"""
    print_section("5. 測試 RAG: 語義口味搜尋")
    
    test_cases = [
        "推薦清爽酸甜的調酒",
        "我想要濃烈一點的",
        "有沒有甜甜的適合女生喝的？"
    ]
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for message in test_cases:
        print(f"\n💬 測試: {message}")
        try:
            response = requests.post(
                f'{BASE_URL}/api/chat/message',
                json={'message': message},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('tool_used'):
                    print_success("語義搜尋工具已調用 ✨")
                    print(f"  回應: {result.get('message', '')[:200]}...")
                    return True
                else:
                    print_info("未使用語義搜尋")
            else:
                print_error(f"請求失敗: {response.status_code}")
        except Exception as e:
            print_error(f"錯誤: {str(e)}")
        
        time.sleep(1)
    
    return False


def test_tool_semantic_scenario(token):
    """測試工具 5: search_by_scenario_semantic (RAG)"""
    print_section("6. 測試 RAG: 語義場景搜尋")
    
    test_cases = [
        "適合慶祝的調酒",
        "約會時喝什麼好？",
        "適合夏天海邊的"
    ]
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for message in test_cases:
        print(f"\n💬 測試: {message}")
        try:
            response = requests.post(
                f'{BASE_URL}/api/chat/message',
                json={'message': message},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('tool_used'):
                    print_success("場景搜尋工具已調用 ✨")
                    print(f"  回應: {result.get('message', '')[:200]}...")
                    return True
                else:
                    print_info("未使用場景搜尋")
            else:
                print_error(f"請求失敗: {response.status_code}")
        except Exception as e:
            print_error(f"錯誤: {str(e)}")
        
        time.sleep(1)
    
    return False


def test_multi_turn_conversation(token):
    """測試多輪對話記憶"""
    print_section("7. 測試多輪對話記憶")
    
    conversation = [
        "推薦一款適合夏天的調酒",
        "它怎麼做？",  # 應該記得前一個推薦
        "有沒有更簡單的？"  # 應該記得前面的上下文
    ]
    
    headers = {'Authorization': f'Bearer {token}'}
    conversation_id = None
    
    for i, message in enumerate(conversation, 1):
        print(f"\n💬 第 {i} 輪: {message}")
        
        data = {'message': message}
        if conversation_id:
            data['conversation_id'] = conversation_id
        
        try:
            response = requests.post(
                f'{BASE_URL}/api/chat/message',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                conversation_id = result.get('conversation_id')
                
                print_success(f"回應: {result.get('message', '')[:150]}...")
                print(f"  對話 ID: {conversation_id}")
                print(f"  使用工具: {'是' if result.get('tool_used') else '否'}")
                
                if i == len(conversation):
                    return True
            else:
                print_error(f"請求失敗: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"錯誤: {str(e)}")
            return False
        
        time.sleep(2)  # 給 LLM 一點時間
    
    return True


def test_random_and_filter(token):
    """測試隨機推薦和屬性篩選"""
    print_section("8. 測試工具組合")
    
    test_cases = [
        "隨便推薦一款調酒",  # tool 7: get_random_cocktail
        "給我一款簡單的調酒",  # tool 3: filter_by_attributes (difficulty)
        "推薦高評分的 Gin 調酒"  # tool 3 + 6: filter + category
    ]
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for message in test_cases:
        print(f"\n💬 測試: {message}")
        try:
            response = requests.post(
                f'{BASE_URL}/api/chat/message',
                json={'message': message},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"工具使用: {'是' if result.get('tool_used') else '否'}")
                print(f"  回應: {result.get('message', '')[:200]}...")
            else:
                print_error(f"請求失敗: {response.status_code}")
        except Exception as e:
            print_error(f"錯誤: {str(e)}")
        
        time.sleep(1)
    
    return True


def test_casual_chat(token):
    """測試閒聊（不應使用工具）"""
    print_section("9. 測試閒聊模式")
    
    test_cases = [
        "你好",
        "今天天氣不錯",
        "謝謝你的推薦"
    ]
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for message in test_cases:
        print(f"\n💬 測試: {message}")
        try:
            response = requests.post(
                f'{BASE_URL}/api/chat/message',
                json={'message': message},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get('tool_used'):
                    print_success("正確：未使用工具（直接對話）")
                else:
                    print_info("使用了工具（可能誤判為查詢）")
                print(f"  回應: {result.get('message', '')[:100]}...")
            else:
                print_error(f"請求失敗: {response.status_code}")
        except Exception as e:
            print_error(f"錯誤: {str(e)}")
        
        time.sleep(1)
    
    return True


# ========== 主程式 ==========

def run_all_tests():
    """執行所有測試"""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{'🍸 AI 調酒大師 LangGraph 功能測試':^70}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}")
    print(f"測試開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    try:
        # 1. 健康檢查
        health_ok = test_health_check()
        results.append(('健康檢查', health_ok))
        
        if not health_ok:
            print_error("\n⚠️  RAG 功能未啟用，部分測試將失敗")
            print_info("請確認:")
            print("  1. 已執行 setup_rag_qdrant_only.py")
            print("  2. Qdrant 正在運行")
            print("  3. .env 中 GROQ_ENABLED=true")
        
        # 2. 取得認證
        token = get_auth_token()
        if not token:
            print_error("\n無法取得認證 token，無法繼續測試")
            return
        
        # 3-9. LangGraph 功能測試
        print_info("\n開始測試 LangGraph 功能...\n")
        
        results.append(('工具: 名稱搜尋', test_tool_search_by_name(token)))
        results.append(('工具: 材料搜尋', test_tool_search_by_ingredients(token)))
        results.append(('RAG: 口味語義搜尋', test_tool_semantic_taste(token)))
        results.append(('RAG: 場景語義搜尋', test_tool_semantic_scenario(token)))
        results.append(('多輪對話記憶', test_multi_turn_conversation(token)))
        results.append(('工具組合使用', test_random_and_filter(token)))
        results.append(('閒聊模式', test_casual_chat(token)))
        
        # 總結
        print_section("測試總結")
        print(f"測試結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        for name, result in results:
            status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
            print(f"{status} {name}")
        
        print(f"\n{BLUE}{'=' * 70}{RESET}")
        if percentage >= 80:
            print(f"{GREEN}總體評估: 優秀 ({passed}/{total} 通過, {percentage:.1f}%){RESET}")
            print(f"{GREEN}✓ LangGraph 功能運行正常！{RESET}")
        elif percentage >= 60:
            print(f"{YELLOW}總體評估: 良好 ({passed}/{total} 通過, {percentage:.1f}%){RESET}")
            print(f"{YELLOW}⚠ 部分功能可能需要檢查{RESET}")
        else:
            print(f"{RED}總體評估: 需要改進 ({passed}/{total} 通過, {percentage:.1f}%){RESET}")
            print(f"{RED}✗ 請檢查配置和服務狀態{RESET}")
        print(f"{BLUE}{'=' * 70}{RESET}")
        
    except requests.exceptions.ConnectionError:
        print_section("連接錯誤")
        print_error("無法連接到伺服器")
        print_info("請確認:")
        print("  1. Flask 應用正在運行: python run.py")
        print("  2. 伺服器位址正確: http://localhost:5000")
    except Exception as e:
        print_section("未預期的錯誤")
        print_error(f"測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()