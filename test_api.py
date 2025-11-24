"""
API 測試腳本
用於快速測試 AI 調酒大師 API 端點是否正常運作
"""
import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

# ANSI 顏色碼
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    """打印分節標題"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")

def print_success(message):
    """打印成功訊息"""
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    """打印錯誤訊息"""
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    """打印資訊訊息"""
    print(f"{YELLOW}ℹ {message}{RESET}")

def test_health_check():
    """測試健康檢查"""
    print_section("測試健康檢查")
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        if response.status_code == 200:
            print_success(f"狀態碼: {response.status_code}")
            data = response.json()
            print(f"  回應: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return True
        else:
            print_error(f"狀態碼: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"錯誤: {str(e)}")
        return False

def test_register():
    """測試註冊"""
    print_section("測試用戶註冊")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    data = {
        'username': f'測試用戶_{timestamp}',
        'email': f'test_{timestamp}@example.com',
        'password': 'password123'
    }
    try:
        response = requests.post(f'{BASE_URL}/api/auth/register', json=data, timeout=5)
        print(f"狀態碼: {response.status_code}")
        result = response.json()
        if response.status_code == 201:
            print_success("註冊成功")
            print(f"  用戶名: {data['username']}")
            print(f"  Email: {data['email']}")
            return result.get('access_token')
        else:
            print_error(f"註冊失敗: {result.get('message', '未知錯誤')}")
            return None
    except Exception as e:
        print_error(f"錯誤: {str(e)}")
        return None

def test_login():
    """測試登入"""
    print_section("測試用戶登入")
    # 使用固定的測試帳號
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    try:
        response = requests.post(f'{BASE_URL}/api/auth/login', json=data, timeout=5)
        print(f"狀態碼: {response.status_code}")
        result = response.json()
        if response.status_code == 200:
            print_success("登入成功")
            return result.get('access_token')
        else:
            print_info(f"登入失敗（測試帳號可能不存在）: {result.get('message')}")
            return None
    except Exception as e:
        print_error(f"錯誤: {str(e)}")
        return None

def test_get_cocktails():
    """測試取得調酒列表"""
    print_section("測試取得調酒列表")
    try:
        response = requests.get(f'{BASE_URL}/api/cocktails/?limit=5', timeout=5)
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            cocktails = data.get('cocktails', [])
            print_success(f"成功取得 {len(cocktails)} 個調酒")
            print(f"  總數: {data.get('count', 0)}")
            print(f"  當前頁: {data.get('page', 1)}")
            if cocktails:
                print(f"\n  前 5 個調酒:")
                for i, c in enumerate(cocktails[:5], 1):
                    rating = c.get('ratings', {}).get('professional', 'N/A')
                    print(f"    {i}. {c['name']} - 評分: {rating}")
            return True
        else:
            print_error(f"失敗: {response.json().get('message')}")
            return False
    except Exception as e:
        print_error(f"錯誤: {str(e)}")
        return False

def test_search_cocktails():
    """測試搜尋調酒"""
    print_section("測試搜尋調酒")
    search_terms = ['Mojito', 'Margarita', 'Martini']

    for term in search_terms:
        try:
            response = requests.get(f'{BASE_URL}/api/cocktails/search?q={term}', timeout=5)
            print(f"\n搜尋關鍵字: '{term}'")
            print(f"狀態碼: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                if count > 0:
                    print_success(f"找到 {count} 個結果")
                    cocktails = data.get('cocktails', [])[:3]
                    for c in cocktails:
                        print(f"  - {c['name']} ({c.get('category', 'N/A')})")
                else:
                    print_info(f"沒有找到結果")
            else:
                print_error(f"失敗: {response.json().get('message')}")
        except Exception as e:
            print_error(f"錯誤: {str(e)}")

def test_filter_cocktails():
    """測試進階篩選"""
    print_section("測試進階篩選")

    # 測試：高評分調酒
    print("\n篩選條件: 評分 >= 4.5")
    try:
        response = requests.get(
            f'{BASE_URL}/api/cocktails/filter?min_rating=4.5&limit=5',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print_success(f"找到 {count} 個高評分調酒")
            cocktails = data.get('cocktails', [])[:5]
            for c in cocktails:
                rating = c.get('ratings', {}).get('professional', 'N/A')
                print(f"  - {c['name']} - 評分: {rating}")
        else:
            print_error(f"失敗")
    except Exception as e:
        print_error(f"錯誤: {str(e)}")

    # 測試：簡單調酒
    print("\n篩選條件: 難度 = easy")
    try:
        response = requests.get(
            f'{BASE_URL}/api/cocktails/filter?difficulty=easy&limit=5',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print_success(f"找到 {count} 個簡單調酒")
            cocktails = data.get('cocktails', [])[:5]
            for c in cocktails:
                print(f"  - {c['name']} (難度: {c.get('difficulty', 'N/A')})")
        else:
            print_error(f"失敗")
    except Exception as e:
        print_error(f"錯誤: {str(e)}")

def test_categories():
    """測試取得分類"""
    print_section("測試取得調酒分類")
    try:
        response = requests.get(f'{BASE_URL}/api/cocktails/categories', timeout=5)
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            categories = data.get('categories', [])
            print_success(f"找到 {len(categories)} 個分類")
            print(f"  分類列表: {', '.join(categories[:10])}")
            if len(categories) > 10:
                print(f"  ... 還有 {len(categories) - 10} 個分類")
            return True
        else:
            print_error(f"失敗: {response.json().get('message')}")
            return False
    except Exception as e:
        print_error(f"錯誤: {str(e)}")
        return False

def test_random_cocktail():
    """測試隨機調酒"""
    print_section("測試隨機調酒")
    try:
        response = requests.get(f'{BASE_URL}/api/cocktails/random', timeout=5)
        print(f"狀態碼: {response.status_code}")
        if response.status_code == 200:
            cocktail = response.json().get('cocktail', {})
            print_success("成功取得隨機調酒")
            print(f"  名稱: {cocktail.get('name')}")
            print(f"  分類: {cocktail.get('category')}")
            rating = cocktail.get('ratings', {}).get('professional')
            if rating:
                print(f"  評分: {rating}")
            return True
        else:
            print_error(f"失敗: {response.json().get('message')}")
            return False
    except Exception as e:
        print_error(f"錯誤: {str(e)}")
        return False

def test_chat(token):
    """測試對話功能"""
    print_section("測試 AI 酒保對話")
    if not token:
        print_info("需要認證 token，跳過測試")
        return

    headers = {'Authorization': f'Bearer {token}'}
    messages = [
        '推薦我一款適合夏天的調酒',
        'Mojito 怎麼做？'
    ]

    for message in messages:
        print(f"\n用戶: {message}")
        try:
            data = {'message': message}
            response = requests.post(
                f'{BASE_URL}/api/chat/message',
                json=data,
                headers=headers,
                timeout=30
            )
            print(f"狀態碼: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                ai_message = result.get('message', '')
                print_success("AI 回應:")
                print(f"  {ai_message[:200]}{'...' if len(ai_message) > 200 else ''}")
                sentiment = result.get('sentiment', 0)
                print(f"  情感分數: {sentiment:.2f}")
            else:
                error_msg = response.json().get('message', '未知錯誤')
                print_error(f"失敗: {error_msg}")
        except Exception as e:
            print_error(f"錯誤: {str(e)}")

def test_cocktail_detail():
    """測試調酒詳情"""
    print_section("測試調酒詳情")

    # 先搜尋一個調酒取得 ID
    try:
        response = requests.get(f'{BASE_URL}/api/cocktails/search?q=Mojito', timeout=5)
        if response.status_code == 200:
            data = response.json()
            cocktails = data.get('cocktails', [])
            if cocktails:
                cocktail_id = cocktails[0].get('_id')
                print(f"測試調酒: {cocktails[0]['name']}")

                # 取得詳情
                detail_response = requests.get(
                    f'{BASE_URL}/api/cocktails/{cocktail_id}',
                    timeout=5
                )
                if detail_response.status_code == 200:
                    detail = detail_response.json().get('cocktail', {})
                    print_success("成功取得調酒詳情")
                    print(f"  名稱: {detail.get('name')}")
                    print(f"  分類: {detail.get('category')}")
                    print(f"  難度: {detail.get('difficulty')}")
                    print(f"  材料數: {len(detail.get('ingredients', []))}")
                    if detail.get('image_url'):
                        print(f"  圖片: {detail.get('image_url')[:50]}...")
                    return True
                else:
                    print_error("無法取得調酒詳情")
                    return False
            else:
                print_info("沒有找到調酒")
                return False
        else:
            print_error("搜尋失敗")
            return False
    except Exception as e:
        print_error(f"錯誤: {str(e)}")
        return False

def run_all_tests():
    """執行所有測試"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{'AI 調酒大師 API 測試':^60}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"測試開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        '基本測試': [],
        '調酒測試': [],
        '認證測試': []
    }

    try:
        # 基本測試
        print_section("第一部分：基本測試")
        results['基本測試'].append(('健康檢查', test_health_check()))

        # 調酒測試
        print_section("第二部分：調酒功能測試")
        results['調酒測試'].append(('取得調酒列表', test_get_cocktails()))
        test_search_cocktails()  # 不計入成功率
        test_filter_cocktails()  # 不計入成功率
        results['調酒測試'].append(('取得分類', test_categories()))
        results['調酒測試'].append(('隨機調酒', test_random_cocktail()))
        results['調酒測試'].append(('調酒詳情', test_cocktail_detail()))

        # 認證測試
        print_section("第三部分：用戶認證測試")
        token = None
        try:
            token = test_register()
            if token:
                results['認證測試'].append(('註冊', True))
            else:
                results['認證測試'].append(('註冊', False))
        except:
            results['認證測試'].append(('註冊', False))

        # 如果註冊失敗，嘗試登入
        if not token:
            token = test_login()
            if token:
                results['認證測試'].append(('登入', True))

        # AI 對話測試
        if token:
            test_chat(token)
            results['認證測試'].append(('AI 對話', True))
        else:
            print_info("無法取得認證 token，跳過 AI 對話測試")
            results['認證測試'].append(('AI 對話', False))

        # 總結
        print_section("測試總結")
        print(f"測試結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        for category, tests in results.items():
            if tests:
                passed = sum(1 for _, result in tests if result)
                total = len(tests)
                percentage = (passed / total * 100) if total > 0 else 0

                if percentage == 100:
                    color = GREEN
                elif percentage >= 50:
                    color = YELLOW
                else:
                    color = RED

                print(f"{color}{category}: {passed}/{total} 通過 ({percentage:.1f}%){RESET}")
                for name, result in tests:
                    status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
                    print(f"  {status} {name}")

        # 總體評估
        all_tests = [result for tests in results.values() for _, result in tests]
        overall_passed = sum(all_tests)
        overall_total = len(all_tests)
        overall_percentage = (overall_passed / overall_total * 100) if overall_total > 0 else 0

        print(f"\n{BLUE}{'=' * 60}{RESET}")
        if overall_percentage >= 80:
            print(f"{GREEN}總體評估: 優秀 ({overall_percentage:.1f}%){RESET}")
            print(f"{GREEN}✓ API 運行正常，可以開始使用！{RESET}")
        elif overall_percentage >= 50:
            print(f"{YELLOW}總體評估: 良好 ({overall_percentage:.1f}%){RESET}")
            print(f"{YELLOW}⚠ 部分功能可能需要檢查{RESET}")
        else:
            print(f"{RED}總體評估: 需要改進 ({overall_percentage:.1f}%){RESET}")
            print(f"{RED}✗ 請檢查配置和服務狀態{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}")

    except requests.exceptions.ConnectionError:
        print_section("連接錯誤")
        print_error("無法連接到伺服器")
        print_info("請確認 Flask 應用正在運行:")
        print("  1. 開啟新終端")
        print("  2. 執行: python run.py")
        print("  3. 等待伺服器啟動後，重新執行本測試")
    except Exception as e:
        print_section("未預期的錯誤")
        print_error(f"測試過程中發生錯誤: {str(e)}")

if __name__ == '__main__':
    run_all_tests()
