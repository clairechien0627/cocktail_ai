"""
LangSmith 整合測試腳本
測試 LangSmith 追蹤功能是否正常運作
"""
import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def test_langsmith_config():
    """測試 LangSmith 配置"""
    print("=" * 60)
    print("LangSmith 配置測試")
    print("=" * 60)

    # 檢查環境變數
    tracing = os.getenv('LANGSMITH_TRACING', 'false')
    api_key = os.getenv('LANGSMITH_API_KEY', '')
    endpoint = os.getenv('LANGSMITH_ENDPOINT', '')
    project = os.getenv('LANGSMITH_PROJECT', '')

    print(f"✓ LANGSMITH_TRACING: {tracing}")
    print(f"✓ LANGSMITH_API_KEY: {'已設定 (' + api_key[:20] + '...)' if api_key else '未設定'}")
    print(f"✓ LANGSMITH_ENDPOINT: {endpoint}")
    print(f"✓ LANGSMITH_PROJECT: {project}")
    print()

    if tracing.lower() != 'true':
        print("⚠ 警告：LANGSMITH_TRACING 未啟用")
        return False

    if not api_key:
        print("❌ 錯誤：LANGSMITH_API_KEY 未設定")
        return False

    print("✓ LangSmith 配置完整")
    return True

def test_langsmith_import():
    """測試 LangSmith 導入"""
    print("=" * 60)
    print("LangSmith 導入測試")
    print("=" * 60)

    try:
        from langsmith import traceable
        print("✓ langsmith 模組導入成功")

        # 測試簡單的追蹤函數
        @traceable(name="test_function")
        def simple_test(x, y):
            return x + y

        result = simple_test(1, 2)
        print(f"✓ @traceable 裝飾器測試成功，結果: {result}")
        return True

    except ImportError as e:
        print(f"❌ langsmith 模組導入失敗: {e}")
        return False
    except Exception as e:
        print(f"❌ @traceable 測試失敗: {e}")
        return False

def test_app_initialization():
    """測試應用初始化"""
    print("=" * 60)
    print("Flask 應用初始化測試")
    print("=" * 60)

    try:
        from app import create_app
        app = create_app()

        print(f"✓ Flask 應用創建成功")
        print(f"✓ GROQ_ENABLED: {app.config.get('GROQ_ENABLED', False)}")
        print(f"✓ LANGSMITH_ENABLED: {app.config.get('LANGSMITH_ENABLED', False)}")

        # 檢查環境變數是否正確設置
        if os.getenv('LANGCHAIN_TRACING_V2') == 'true':
            print("✓ LANGCHAIN_TRACING_V2 環境變數已設置")
        else:
            print("⚠ LANGCHAIN_TRACING_V2 環境變數未設置")

        return True

    except Exception as e:
        print(f"❌ 應用初始化失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_service():
    """測試 LLM 服務追蹤"""
    print("=" * 60)
    print("LLM 服務追蹤測試")
    print("=" * 60)

    try:
        from app.services.llm_service import llm_service

        # 檢查 LLM 服務是否已初始化
        if llm_service.client is None:
            print("⚠ LLM 服務未初始化，嘗試初始化...")
            groq_api_key = os.getenv('GROQ_API_KEY', '')
            if groq_api_key:
                llm_service.initialize(groq_api_key)
                print("✓ LLM 服務初始化成功")
            else:
                print("❌ GROQ_API_KEY 未設定")
                return False
        else:
            print("✓ LLM 服務已初始化")

        # 檢查 traceable 裝飾器是否存在
        if hasattr(llm_service.get_bartender_response, '__wrapped__'):
            print("✓ get_bartender_response 已添加 @traceable 裝飾器")
        else:
            print("⚠ get_bartender_response 可能未添加 @traceable 裝飾器")

        return True

    except Exception as e:
        print(f"❌ LLM 服務測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("\n" + "=" * 60)
    print("LangSmith 整合測試")
    print("=" * 60 + "\n")

    results = []

    # 執行測試
    results.append(("配置測試", test_langsmith_config()))
    print()

    results.append(("導入測試", test_langsmith_import()))
    print()

    results.append(("應用初始化測試", test_app_initialization()))
    print()

    results.append(("LLM 服務測試", test_llm_service()))
    print()

    # 總結
    print("=" * 60)
    print("測試總結")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ 通過" if result else "❌ 失敗"
        print(f"{status}: {name}")

    print()
    print(f"總計: {passed}/{total} 測試通過")

    if passed == total:
        print("\n🎉 所有測試通過！LangSmith 整合成功！")
        print("\n下一步：")
        print("1. 啟動 Flask 應用: python run.py")
        print("2. 測試對話功能")
        print("3. 前往 LangSmith Dashboard 查看追蹤資料: https://smith.langchain.com")
    else:
        print("\n⚠ 部分測試失敗，請檢查上述錯誤訊息")

    return passed == total

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
