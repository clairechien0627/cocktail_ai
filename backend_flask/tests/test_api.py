"""
AI 調酒大師 API 完整測試套件
測試所有 API 端點的功能性和正確性
"""
import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = 'http://localhost:5000'

# ANSI 顏色碼
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

# 全域變數存儲測試數據
test_data = {
    'token': None,
    'user_id': None,
    'conversation_id': None,
    'cocktail_id': None,  # MongoDB ObjectId - 用於建立紀錄
    'cocktail_slug': None,  # slug 格式 (如 "mojito") - 用於 URL 路徑
    'record_id': None
}

def print_section(title):
    """打印分節標題"""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{BOLD}{title:^70}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}")

def print_subsection(title):
    """打印子分節標題"""
    print(f"\n{CYAN}{'-' * 70}{RESET}")
    print(f"{CYAN}{title}{RESET}")
    print(f"{CYAN}{'-' * 70}{RESET}")

def print_success(message):
    """打印成功訊息"""
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    """打印錯誤訊息"""
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    """打印資訊訊息"""
    print(f"{YELLOW}ℹ {message}{RESET}")

def print_warning(message):
    """打印警告訊息"""
    print(f"{MAGENTA}⚠ {message}{RESET}")

def make_request(method, endpoint, **kwargs):
    """統一的請求處理函數"""
    url = f'{BASE_URL}{endpoint}'
    kwargs.setdefault('timeout', 10)

    try:
        response = requests.request(method, url, **kwargs)
        return response
    except requests.exceptions.RequestException as e:
        print_error(f"請求失敗: {str(e)}")
        return None

# ============================================================================
# 基礎功能測試
# ============================================================================

def test_root_endpoint():
    """測試根端點"""
    print_subsection("測試 GET /")
    response = make_request('GET', '/')

    if response and response.status_code == 200:
        data = response.json()
        print_success(f"API 版本: {data.get('version', 'N/A')}")
        print_success(f"訊息: {data.get('message', 'N/A')}")
        return True
    else:
        print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
        return False

def test_health_check():
    """測試健康檢查"""
    print_subsection("測試 GET /health")
    response = make_request('GET', '/health')

    if response and response.status_code == 200:
        data = response.json()
        print_success(f"狀態: {data.get('status', 'unknown')}")
        print_success(f"MongoDB: {data.get('mongodb', 'unknown')}")

        llm_info = data.get('llm', {})
        if llm_info.get('enabled'):
            print_success(f"LLM Provider: {llm_info.get('provider', 'N/A')}")

        print_success(f"RAG: {data.get('rag', 'unknown')}")
        return True
    else:
        print_error(f"健康檢查失敗 (狀態碼: {response.status_code if response else 'N/A'})")
        return False

# ============================================================================
# 用戶認證測試
# ============================================================================

def test_register():
    """測試用戶註冊"""
    print_subsection("測試 POST /api/auth/register")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    data = {
        'username': f'test_user_{timestamp}',
        'email': f'test_{timestamp}@example.com',
        'password': 'TestPassword123!'
    }

    response = make_request('POST', '/api/auth/register', json=data)

    if response and response.status_code == 201:
        result = response.json()
        token = result.get('access_token')
        user_id = result.get('user_id')

        if token and user_id:
            test_data['token'] = token
            test_data['user_id'] = user_id
            print_success(f"註冊成功: {data['username']}")
            print_success(f"User ID: {user_id}")
            return True

    print_error(f"註冊失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    if response:
        print_info(f"回應: {response.json().get('message', 'N/A')}")
    return False

def test_login():
    """測試用戶登入（使用固定測試帳號）"""
    print_subsection("測試 POST /api/auth/login")

    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }

    response = make_request('POST', '/api/auth/login', json=data)

    if response and response.status_code == 200:
        result = response.json()
        token = result.get('access_token')

        if token:
            test_data['token'] = token
            user_info = result.get('user', {})
            print_success(f"登入成功: {user_info.get('username', 'N/A')}")
            return True

    print_info("登入失敗（測試帳號可能不存在，將使用新註冊的帳號）")
    return False

def test_get_current_user():
    """測試取得當前用戶資訊"""
    print_subsection("測試 GET /api/auth/me")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('GET', '/api/auth/me', headers=headers)

    if response and response.status_code == 200:
        user = response.json().get('user', {})
        print_success(f"用戶名: {user.get('username', 'N/A')}")
        print_success(f"Email: {user.get('email', 'N/A')}")
        return True

    print_error(f"取得用戶資訊失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_update_preferences():
    """測試更新用戶偏好"""
    print_subsection("測試 PUT /api/auth/preferences")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    data = {
        'preferences': {
            'favorite_spirits': ['Vodka', 'Rum', 'Gin'],
            'skill_level': 'intermediate',
            'preferred_difficulty': ['easy', 'medium']
        }
    }

    response = make_request('PUT', '/api/auth/preferences', json=data, headers=headers)

    if response and response.status_code == 200:
        print_success("偏好設定更新成功")
        return True

    print_error(f"更新失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

# ============================================================================
# 調酒功能測試
# ============================================================================

def test_get_cocktails():
    """測試取得調酒列表"""
    print_subsection("測試 GET /api/cocktails/")

    # 測試英文版本
    response = make_request('GET', '/api/cocktails/', params={'lang': 'en', 'limit': 5})

    if response and response.status_code == 200:
        data = response.json()
        cocktails = data.get('cocktails', [])
        print_success(f"取得 {len(cocktails)} 個調酒（英文）")
        print_success(f"總數: {data.get('total', 0)}, 頁數: {data.get('page', 1)}/{data.get('total_pages', 1)}")

        if cocktails:
            # 儲存第一個調酒的兩種 ID 供後續測試使用
            # cocktail_id (slug) 用於 URL 路徑，_id (ObjectId) 用於建立紀錄
            test_data['cocktail_slug'] = cocktails[0].get('cocktail_id')  # slug 格式
            test_data['cocktail_id'] = cocktails[0].get('_id')  # MongoDB ObjectId 格式

            print(f"\n  前 3 個調酒:")
            for i, c in enumerate(cocktails[:3], 1):
                rating = c.get('ratings', {}).get('professional', 'N/A')
                print(f"    {i}. {c.get('name', 'N/A')} - 評分: {rating}")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_cocktails_chinese():
    """測試取得調酒列表（中文）"""
    print_subsection("測試 GET /api/cocktails/ (中文)")

    response = make_request('GET', '/api/cocktails/', params={'lang': 'zh', 'limit': 3})

    if response and response.status_code == 200:
        data = response.json()
        cocktails = data.get('cocktails', [])
        print_success(f"取得 {len(cocktails)} 個調酒（中文）")

        if cocktails:
            print(f"\n  範例調酒:")
            c = cocktails[0]
            print(f"    中文名: {c.get('name_zh', 'N/A')}")
            print(f"    英文名: {c.get('name_en', 'N/A')}")
            print(f"    分類: {c.get('category_zh', 'N/A')} ({c.get('category', 'N/A')})")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_cocktail_detail():
    """測試取得調酒詳情"""
    print_subsection("測試 GET /api/cocktails/<cocktail_id>")

    # 如果沒有預存的 slug，先搜尋一個
    if not test_data.get('cocktail_slug'):
        print_info("沒有預存的 cocktail_slug，嘗試搜尋...")
        search_response = make_request('GET', '/api/cocktails/search', params={'q': 'Mojito'})
        if search_response and search_response.status_code == 200:
            cocktails = search_response.json().get('cocktails', [])
            if cocktails:
                test_data['cocktail_slug'] = cocktails[0].get('cocktail_id')
                test_data['cocktail_id'] = cocktails[0].get('_id')
                print_info(f"從搜尋結果取得 slug: {test_data['cocktail_slug']}")

    if not test_data.get('cocktail_slug'):
        print_error("無法取得有效的 cocktail_slug")
        return False

    cocktail_slug = test_data['cocktail_slug']
    print_info(f"測試調酒 slug: {cocktail_slug}")

    # 測試英文版本 - 增加超時時間
    try:
        response = make_request('GET', f'/api/cocktails/{cocktail_slug}', params={'lang': 'en'}, timeout=15)

        if response and response.status_code == 200:
            data = response.json()
            cocktail = data.get('cocktail', {})

            if cocktail:
                print_success(f"名稱: {cocktail.get('name', 'N/A')}")
                print_success(f"分類: {cocktail.get('category', 'N/A')}")
                print_success(f"難度: {cocktail.get('difficulty', 'N/A')}")
                print_success(f"材料數: {len(cocktail.get('ingredients', []))}")

                # 檢查詳細資訊
                if cocktail.get('method_sections'):
                    print_success(f"製作步驟: {len(cocktail.get('method_sections', []))} 個區段")
                if cocktail.get('history'):
                    print_success(f"歷史介紹: {len(cocktail.get('history', []))} 段")
                if cocktail.get('glass'):
                    print_success(f"杯型: {cocktail.get('glass')}")

                return True
            else:
                print_error("回應中沒有 cocktail 資料")
                print_info(f"完整回應: {json.dumps(data, ensure_ascii=False)[:300]}")
                return False

        if response:
            print_error(f"失敗 (狀態碼: {response.status_code})")
            print_info(f"回應內容: {response.text[:300]}")
        else:
            print_error("請求失敗 - 可能是超時或連接錯誤")
            print_warning(f"請檢查 API 端點: GET /api/cocktails/{cocktail_slug}")

        return False

    except Exception as e:
        print_error(f"發生異常: {str(e)}")
        return False

def test_search_cocktails():
    """測試搜尋調酒"""
    print_subsection("測試 GET /api/cocktails/search")

    search_terms = ['Mojito', 'Margarita', 'Old Fashioned']
    all_success = True

    for term in search_terms:
        response = make_request('GET', '/api/cocktails/search', params={'q': term})

        if response and response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)

            if count > 0:
                cocktails = data.get('cocktails', [])[:2]
                print_success(f"'{term}': 找到 {count} 個結果")
                for c in cocktails:
                    print(f"    - {c.get('name', 'N/A')}")
            else:
                print_info(f"'{term}': 沒有找到結果")
        else:
            print_error(f"'{term}': 搜尋失敗")
            all_success = False

    return all_success

def test_filter_cocktails():
    """測試進階篩選"""
    print_subsection("測試 GET /api/cocktails/filter")

    # 測試 1: 高評分調酒
    print("\n  測試條件: 評分 >= 4.5")
    response = make_request('GET', '/api/cocktails/filter', params={
        'min_rating': 4.5,
        'limit': 5,
        'sort_by': 'rating_desc'
    })

    if response and response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print_success(f"找到 {count} 個高評分調酒")

        cocktails = data.get('cocktails', [])[:3]
        for c in cocktails:
            rating = c.get('ratings', {}).get('professional', 'N/A')
            print(f"    - {c.get('name', 'N/A')} (評分: {rating})")

    # 測試 2: 簡單調酒
    print("\n  測試條件: 難度 = easy")
    response = make_request('GET', '/api/cocktails/filter', params={
        'difficulty': 'easy',
        'limit': 5
    })

    if response and response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print_success(f"找到 {count} 個簡單調酒")

        cocktails = data.get('cocktails', [])[:3]
        for c in cocktails:
            print(f"    - {c.get('name', 'N/A')}")

    # 測試 3: 組合篩選（基酒 + 風味標籤）
    print("\n  測試條件: 標籤篩選（vodka-based）")
    response = make_request('GET', '/api/cocktails/filter', params={
        'base_spirit': 'Vodka',
        'limit': 5
    })

    if response and response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print_success(f"找到 {count} 個伏特加基底調酒")

    return True

def test_get_categories():
    """測試取得分類"""
    print_subsection("測試 GET /api/cocktails/categories")

    response = make_request('GET', '/api/cocktails/categories')

    if response and response.status_code == 200:
        categories = response.json().get('categories', [])
        print_success(f"找到 {len(categories)} 個分類")
        print(f"  範例: {', '.join(categories[:8])}")
        if len(categories) > 8:
            print(f"  ... 還有 {len(categories) - 8} 個")
        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_more_categories():
    """測試取得更多分類"""
    print_subsection("測試 GET /api/cocktails/more-categories")

    response = make_request('GET', '/api/cocktails/more-categories')

    if response and response.status_code == 200:
        categories = response.json().get('more_categories', [])
        print_success(f"找到 {len(categories)} 個額外分類")
        print(f"  範例: {', '.join(categories[:6])}")
        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_tags():
    """測試取得標籤"""
    print_subsection("測試 GET /api/cocktails/tags")

    response = make_request('GET', '/api/cocktails/tags')

    if response and response.status_code == 200:
        data = response.json()
        tags = data.get('tags', {})

        print_success("標籤統計:")
        for tag_type, tag_list in tags.items():
            print(f"    {tag_type}: {len(tag_list)} 個")
            print(f"      範例: {', '.join(tag_list[:5])}")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_random_cocktail():
    """測試隨機調酒"""
    print_subsection("測試 GET /api/cocktails/random")

    response = make_request('GET', '/api/cocktails/random')

    if response and response.status_code == 200:
        cocktail = response.json().get('cocktail', {})
        print_success(f"隨機調酒: {cocktail.get('name', 'N/A')}")
        print_success(f"分類: {cocktail.get('category', 'N/A')}")
        rating = cocktail.get('ratings', {}).get('professional')
        if rating:
            print_success(f"評分: {rating}")
        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_cocktail_stats():
    """測試調酒統計"""
    print_subsection("測試 GET /api/cocktails/stats")

    response = make_request('GET', '/api/cocktails/stats')

    if response and response.status_code == 200:
        stats = response.json()
        print_success(f"總調酒數: {stats.get('total_cocktails', 0)}")
        print_success(f"平均評分: {stats.get('average_rating', 0):.2f}")
        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

# ============================================================================
# 飲用紀錄測試
# ============================================================================

def test_create_drinking_record():
    """測試建立飲用紀錄"""
    print_subsection("測試 POST /api/records/")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    if not test_data.get('cocktail_id'):
        print_warning("沒有 cocktail_id，嘗試從調酒列表取得...")
        # 嘗試從調酒列表取得第一個有效的 ObjectId
        list_response = make_request('GET', '/api/cocktails/', params={'limit': 1})
        if list_response and list_response.status_code == 200:
            cocktails = list_response.json().get('cocktails', [])
            if cocktails:
                test_data['cocktail_id'] = cocktails[0].get('_id')  # 使用 ObjectId
                test_data['cocktail_slug'] = cocktails[0].get('cocktail_id')  # slug
                print_info(f"使用調酒 ObjectId: {test_data['cocktail_id']}")

    if not test_data.get('cocktail_id'):
        print_error("無法取得有效的 cocktail_id (ObjectId)，跳過測試")
        return False

    print_info(f"使用調酒 ObjectId: {test_data['cocktail_id']}")

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    data = {
        'cocktail_id': test_data['cocktail_id'],
        'preference': 'loved',
        'notes': '這是一個測試紀錄，非常好喝！',
        'drunk_at': datetime.now().isoformat(),
        'location': '測試酒吧',
        'mood_tags': ['慶祝', '放鬆']
    }

    try:
        response = make_request('POST', '/api/records/', json=data, headers=headers, timeout=15)

        if response and response.status_code == 201:
            result = response.json()
            record_id = result.get('record_id')

            if record_id:
                test_data['record_id'] = record_id
                print_success(f"紀錄建立成功 (ID: {record_id})")
                return True

        if response:
            print_error(f"失敗 (狀態碼: {response.status_code})")
            try:
                error_data = response.json()
                print_info(f"錯誤訊息: {error_data.get('message', 'N/A')}")
                if 'error' in error_data:
                    print_info(f"詳細錯誤: {error_data['error']}")
            except:
                print_info(f"回應內容: {response.text[:200]}")
        else:
            print_error("請求失敗 - 可能是超時或連接錯誤")

        return False

    except Exception as e:
        print_error(f"發生異常: {str(e)}")
        return False

def test_get_drinking_records():
    """測試取得飲用紀錄列表"""
    print_subsection("測試 GET /api/records/")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('GET', '/api/records/', headers=headers, params={'limit': 5})

    if response and response.status_code == 200:
        data = response.json()
        records = data.get('records', [])
        total = data.get('total', 0)

        print_success(f"找到 {total} 筆紀錄")

        if records:
            print(f"\n  最近 {len(records)} 筆紀錄:")
            for r in records[:3]:
                cocktail = r.get('cocktail_snapshot', {})
                print(f"    - {cocktail.get('name', 'N/A')} ({r.get('preference', 'N/A')})")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_single_record():
    """測試取得單一紀錄"""
    print_subsection("測試 GET /api/records/<record_id>")

    if not test_data['token'] or not test_data.get('record_id'):
        print_warning("沒有認證 token 或 record_id，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('GET', f"/api/records/{test_data['record_id']}", headers=headers)

    if response and response.status_code == 200:
        record = response.json()
        cocktail = record.get('cocktail_snapshot', {})
        print_success(f"調酒: {cocktail.get('name', 'N/A')}")
        print_success(f"喜好度: {record.get('preference', 'N/A')}")
        print_success(f"備註: {record.get('notes', 'N/A')[:50]}")
        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_update_drinking_record():
    """測試更新飲用紀錄"""
    print_subsection("測試 PUT /api/records/<record_id>")

    if not test_data['token'] or not test_data.get('record_id'):
        print_warning("沒有認證 token 或 record_id，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    data = {
        'preference': 'liked',
        'notes': '更新後的測試紀錄備註',
        'mood_tags': ['週末', '嘗鮮']
    }

    response = make_request('PUT', f"/api/records/{test_data['record_id']}", json=data, headers=headers)

    if response and response.status_code == 200:
        print_success("紀錄更新成功")
        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_drinking_stats():
    """測試取得飲用統計"""
    print_subsection("測試 GET /api/records/stats")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('GET', '/api/records/stats', headers=headers)

    if response and response.status_code == 200:
        stats = response.json()
        print_success(f"總飲用次數: {stats.get('total_drinks', 0)}")

        distribution = stats.get('preference_distribution', {})
        if distribution:
            print_success("喜好分佈:")
            for pref, count in distribution.items():
                print(f"    {pref}: {count}")

        most_drunk = stats.get('most_drunk_cocktails', [])
        if most_drunk:
            print_success(f"最常喝的調酒: {most_drunk[0].get('cocktail_name', 'N/A')}")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_user_preferences():
    """測試取得用戶偏好分析"""
    print_subsection("測試 GET /api/records/preferences")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('GET', '/api/records/preferences', headers=headers)

    if response and response.status_code == 200:
        prefs = response.json()

        favorite_tags = prefs.get('favorite_tags', {})
        if favorite_tags:
            print_success("最愛標籤:")
            for tag_type, tags in favorite_tags.items():
                if tags:
                    print(f"    {tag_type}: {tags[0].get('tag', 'N/A')} ({tags[0].get('count', 0)}次)")

        taste_range = prefs.get('taste_range', {})
        if taste_range:
            print_success("口味範圍:")
            for taste, values in taste_range.items():
                print(f"    {taste}: {values.get('min', 0):.1f} - {values.get('max', 0):.1f} (平均: {values.get('avg', 0):.1f})")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_recommendations():
    """測試取得個人化推薦"""
    print_subsection("測試 GET /api/records/recommendations")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('GET', '/api/records/recommendations', headers=headers, params={'limit': 5})

    if response and response.status_code == 200:
        data = response.json()
        recommendations = data.get('recommendations', [])
        count = data.get('count', 0)

        print_success(f"推薦了 {count} 個調酒")

        if recommendations:
            print(f"\n  推薦列表:")
            for r in recommendations[:3]:
                print(f"    - {r.get('name', 'N/A')}")
                print(f"      原因: {r.get('recommendation_reason', 'N/A')[:60]}")
                print(f"      類型: {r.get('recommendation_type', 'N/A')}")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_check_cocktail_drunk():
    """測試檢查調酒是否喝過"""
    print_subsection("測試 GET /api/records/cocktail/<cocktail_id>/check")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    # 這個端點需要 slug，不是 ObjectId
    if not test_data.get('cocktail_slug'):
        print_warning("沒有 cocktail_slug，嘗試使用備用 ID...")
        # 使用一個固定的已知 slug 作為備用
        list_response = make_request('GET', '/api/cocktails/', params={'limit': 1})
        if list_response and list_response.status_code == 200:
            cocktails = list_response.json().get('cocktails', [])
            if cocktails:
                test_data['cocktail_slug'] = cocktails[0].get('cocktail_id')  # slug
                test_data['cocktail_id'] = cocktails[0].get('_id')  # ObjectId

    if not test_data.get('cocktail_slug'):
        print_error("無法取得有效的 cocktail_slug，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}

    try:
        # 這個端點檢查的是 slug，不是 ObjectId
        cocktail_slug = test_data.get('cocktail_slug', test_data.get('cocktail_id'))
        response = make_request('GET', f"/api/records/cocktail/{cocktail_slug}/check", headers=headers, timeout=15)

        if response and response.status_code == 200:
            has_drunk = response.json().get('has_drunk', False)
            print_success(f"是否喝過: {'是' if has_drunk else '否'}")
            return True

        if response:
            print_error(f"失敗 (狀態碼: {response.status_code})")
            print_info(f"回應: {response.text[:200]}")
        else:
            print_error("請求失敗 - 可能是超時或連接錯誤")

        return False

    except Exception as e:
        print_error(f"發生異常: {str(e)}")
        return False

def test_get_mood_tags():
    """測試取得情境標籤（公開端點）"""
    print_subsection("測試 GET /api/records/mood-tags")

    response = make_request('GET', '/api/records/mood-tags')

    if response and response.status_code == 200:
        mood_tags = response.json().get('mood_tags', [])
        print_success(f"找到 {len(mood_tags)} 個情境標籤")
        print(f"  標籤: {', '.join(mood_tags[:8])}")
        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_delete_drinking_record():
    """測試刪除飲用紀錄（清理測試數據）"""
    print_subsection("測試 DELETE /api/records/<record_id>")

    if not test_data['token'] or not test_data.get('record_id'):
        print_warning("沒有認證 token 或 record_id，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('DELETE', f"/api/records/{test_data['record_id']}", headers=headers)

    if response and response.status_code == 200:
        print_success("紀錄刪除成功（測試數據已清理）")
        test_data['record_id'] = None
        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

# ============================================================================
# AI 對話測試
# ============================================================================

def test_create_conversation():
    """測試建立對話"""
    print_subsection("測試 POST /api/chat/conversations")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('POST', '/api/chat/conversations', headers=headers)

    if response and response.status_code == 201:
        result = response.json()
        conversation_id = result.get('conversation_id')

        if conversation_id:
            test_data['conversation_id'] = conversation_id
            print_success(f"對話建立成功 (ID: {conversation_id})")
            return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_send_chat_message():
    """測試發送聊天訊息"""
    print_subsection("測試 POST /api/chat/message")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}

    test_messages = [
        '你好！我想找一款適合夏天的調酒。',
        'Mojito 怎麼做？需要什麼材料？'
    ]

    for msg in test_messages:
        print(f"\n  用戶: {msg}")

        data = {
            'message': msg,
            'conversation_id': test_data.get('conversation_id')
        }

        response = make_request('POST', '/api/chat/message', json=data, headers=headers, timeout=30)

        if response and response.status_code == 200:
            result = response.json()
            ai_message = result.get('message', '')
            sentiment = result.get('sentiment', 0)

            print_success(f"AI 回應 (前 150 字):")
            print(f"    {ai_message[:150]}{'...' if len(ai_message) > 150 else ''}")
            print_success(f"情感分數: {sentiment:.2f}")

            # 儲存 conversation_id（如果是第一次發送）
            if not test_data.get('conversation_id'):
                test_data['conversation_id'] = result.get('conversation_id')

            time.sleep(1)  # 避免請求過快
        else:
            print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
            return False

    return True

def test_get_conversations():
    """測試取得對話列表"""
    print_subsection("測試 GET /api/chat/conversations")

    if not test_data['token']:
        print_warning("沒有認證 token，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('GET', '/api/chat/conversations', headers=headers)

    if response and response.status_code == 200:
        conversations = response.json().get('conversations', [])
        print_success(f"找到 {len(conversations)} 個對話")

        if conversations:
            latest = conversations[0]
            msg_count = len(latest.get('messages', []))
            print_success(f"最新對話包含 {msg_count} 則訊息")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_single_conversation():
    """測試取得單一對話"""
    print_subsection("測試 GET /api/chat/conversations/<conversation_id>")

    if not test_data['token'] or not test_data.get('conversation_id'):
        print_warning("沒有認證 token 或 conversation_id，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('GET', f"/api/chat/conversations/{test_data['conversation_id']}", headers=headers)

    if response and response.status_code == 200:
        conversation = response.json().get('conversation', {})
        messages = conversation.get('messages', [])
        print_success(f"對話包含 {len(messages)} 則訊息")

        if messages:
            print(f"\n  訊息範例:")
            for msg in messages[:2]:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:60]
                print(f"    [{role}] {content}...")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_get_conversation_context():
    """測試取得對話上下文"""
    print_subsection("測試 GET /api/chat/context/<conversation_id>")

    if not test_data['token'] or not test_data.get('conversation_id'):
        print_warning("沒有認證 token 或 conversation_id，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('GET', f"/api/chat/context/{test_data['conversation_id']}", headers=headers)

    if response and response.status_code == 200:
        context = response.json().get('context', {})
        print_success("成功取得對話上下文")

        if context.get('recommended_cocktails'):
            print_success(f"推薦調酒數: {len(context['recommended_cocktails'])}")

        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

def test_delete_conversation():
    """測試刪除對話（清理測試數據）"""
    print_subsection("測試 DELETE /api/chat/conversations/<conversation_id>")

    if not test_data['token'] or not test_data.get('conversation_id'):
        print_warning("沒有認證 token 或 conversation_id，跳過測試")
        return False

    headers = {'Authorization': f"Bearer {test_data['token']}"}
    response = make_request('DELETE', f"/api/chat/conversations/{test_data['conversation_id']}", headers=headers)

    if response and response.status_code == 200:
        print_success("對話刪除成功（測試數據已清理）")
        test_data['conversation_id'] = None
        return True

    print_error(f"失敗 (狀態碼: {response.status_code if response else 'N/A'})")
    return False

# ============================================================================
# 主測試流程
# ============================================================================

def run_all_tests():
    """執行所有測試"""
    print(f"\n{BLUE}{BOLD}{'=' * 70}{RESET}")
    print(f"{BLUE}{BOLD}{'AI 調酒大師 API 完整測試套件':^70}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 70}{RESET}")
    print(f"{CYAN}測試開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")

    # 測試結果收集
    results = {
        '基礎功能': [],
        '用戶認證': [],
        '調酒功能': [],
        '飲用紀錄': [],
        'AI 對話': []
    }

    try:
        # ========== 第一部分：基礎功能測試 ==========
        print_section("第一部分：基礎功能測試")

        results['基礎功能'].append(('根端點', test_root_endpoint()))
        results['基礎功能'].append(('健康檢查', test_health_check()))

        # ========== 第二部分：用戶認證測試 ==========
        print_section("第二部分：用戶認證測試")

        # 先嘗試註冊新用戶
        register_success = test_register()
        results['用戶認證'].append(('用戶註冊', register_success))

        # 如果註冊失敗，嘗試登入已有帳號
        if not register_success:
            login_success = test_login()
            results['用戶認證'].append(('用戶登入', login_success))

        # 如果有 token，繼續其他認證測試
        if test_data['token']:
            results['用戶認證'].append(('取得用戶資訊', test_get_current_user()))
            results['用戶認證'].append(('更新用戶偏好', test_update_preferences()))

        # ========== 第三部分：調酒功能測試 ==========
        print_section("第三部分：調酒功能測試")

        results['調酒功能'].append(('取得調酒列表 (英文)', test_get_cocktails()))
        results['調酒功能'].append(('取得調酒列表 (中文)', test_get_cocktails_chinese()))
        results['調酒功能'].append(('取得調酒詳情', test_get_cocktail_detail()))
        results['調酒功能'].append(('搜尋調酒', test_search_cocktails()))
        results['調酒功能'].append(('進階篩選', test_filter_cocktails()))
        results['調酒功能'].append(('取得分類', test_get_categories()))
        results['調酒功能'].append(('取得更多分類', test_get_more_categories()))
        results['調酒功能'].append(('取得標籤', test_get_tags()))
        results['調酒功能'].append(('隨機調酒', test_random_cocktail()))
        results['調酒功能'].append(('調酒統計', test_cocktail_stats()))

        # ========== 第四部分：飲用紀錄測試 ==========
        print_section("第四部分：飲用紀錄測試")

        if test_data['token']:
            results['飲用紀錄'].append(('取得情境標籤', test_get_mood_tags()))
            results['飲用紀錄'].append(('建立飲用紀錄', test_create_drinking_record()))
            results['飲用紀錄'].append(('取得紀錄列表', test_get_drinking_records()))
            results['飲用紀錄'].append(('取得單一紀錄', test_get_single_record()))
            results['飲用紀錄'].append(('更新紀錄', test_update_drinking_record()))
            results['飲用紀錄'].append(('取得飲用統計', test_get_drinking_stats()))
            results['飲用紀錄'].append(('取得偏好分析', test_get_user_preferences()))
            results['飲用紀錄'].append(('取得推薦調酒', test_get_recommendations()))
            results['飲用紀錄'].append(('檢查是否喝過', test_check_cocktail_drunk()))
            results['飲用紀錄'].append(('刪除紀錄 (清理)', test_delete_drinking_record()))
        else:
            print_warning("沒有認證 token，跳過飲用紀錄測試")

        # ========== 第五部分：AI 對話測試 ==========
        print_section("第五部分：AI 對話測試")

        if test_data['token']:
            results['AI 對話'].append(('建立對話', test_create_conversation()))
            results['AI 對話'].append(('發送聊天訊息', test_send_chat_message()))
            results['AI 對話'].append(('取得對話列表', test_get_conversations()))
            results['AI 對話'].append(('取得單一對話', test_get_single_conversation()))
            results['AI 對話'].append(('取得對話上下文', test_get_conversation_context()))
            results['AI 對話'].append(('刪除對話 (清理)', test_delete_conversation()))
        else:
            print_warning("沒有認證 token，跳過 AI 對話測試")

        # ========== 測試總結 ==========
        print_section("測試總結報告")
        print(f"{CYAN}測試結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")

        # 分類統計
        for category, tests in results.items():
            if tests:
                passed = sum(1 for _, result in tests if result)
                total = len(tests)
                percentage = (passed / total * 100) if total > 0 else 0

                # 根據通過率選擇顏色
                if percentage == 100:
                    color = GREEN
                    status = "✓ 優秀"
                elif percentage >= 70:
                    color = YELLOW
                    status = "⚠ 良好"
                else:
                    color = RED
                    status = "✗ 需改進"

                print(f"{color}{BOLD}{category}: {passed}/{total} 通過 ({percentage:.1f}%) {status}{RESET}")

                for name, result in tests:
                    status_icon = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
                    print(f"  {status_icon} {name}")
                print()

        # 總體評估
        all_tests = [result for tests in results.values() for _, result in tests]
        if all_tests:
            overall_passed = sum(all_tests)
            overall_total = len(all_tests)
            overall_percentage = (overall_passed / overall_total * 100)

            print(f"{BLUE}{BOLD}{'=' * 70}{RESET}")
            print(f"{BOLD}總體測試結果: {overall_passed}/{overall_total} 通過 ({overall_percentage:.1f}%){RESET}")

            if overall_percentage >= 90:
                print(f"{GREEN}{BOLD}評級: A - 卓越 🌟{RESET}")
                print(f"{GREEN}✓ API 運行完美，所有功能正常！{RESET}")
            elif overall_percentage >= 80:
                print(f"{GREEN}{BOLD}評級: B - 優秀 ⭐{RESET}")
                print(f"{GREEN}✓ API 運行良好，大部分功能正常！{RESET}")
            elif overall_percentage >= 70:
                print(f"{YELLOW}{BOLD}評級: C - 良好{RESET}")
                print(f"{YELLOW}⚠ API 基本正常，部分功能需要檢查{RESET}")
            elif overall_percentage >= 50:
                print(f"{YELLOW}{BOLD}評級: D - 尚可{RESET}")
                print(f"{YELLOW}⚠ 多個功能需要修復{RESET}")
            else:
                print(f"{RED}{BOLD}評級: F - 不及格{RESET}")
                print(f"{RED}✗ API 存在嚴重問題，請檢查配置和服務狀態{RESET}")

            print(f"{BLUE}{BOLD}{'=' * 70}{RESET}")

    except requests.exceptions.ConnectionError:
        print_section("連接錯誤")
        print_error("無法連接到伺服器")
        print_info("\n請確認 Flask 應用正在運行:")
        print("  1. 開啟新終端")
        print("  2. cd backend_flask")
        print("  3. 執行: python run.py")
        print("  4. 等待伺服器啟動後，重新執行本測試")

    except KeyboardInterrupt:
        print_section("測試中斷")
        print_warning("測試被用戶中斷")

    except Exception as e:
        print_section("未預期的錯誤")
        print_error(f"測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_tests()
