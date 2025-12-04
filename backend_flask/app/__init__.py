"""
Flask 應用初始化
支援多 LLM 和 LangGraph
"""

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from app.config import Config


def create_app(config_class=Config):
    """Flask 應用程式工廠函數"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ========== 初始化擴充套件 ==========
    CORS(app, origins=app.config['CORS_ORIGINS'])
    JWTManager(app)

    # ========== 連接 MongoDB ==========
    try:
        client = MongoClient(app.config['MONGODB_URI'])
        db = client[app.config['MONGODB_DB']]
        app.config['DB'] = db
        app.logger.info(f"✓ 成功連接到 MongoDB: {app.config['MONGODB_DB']}")
    except Exception as e:
        app.logger.error(f"❌ MongoDB 連接失敗: {str(e)}")
        raise

    # ========== 檢查 LLM API Keys ==========
    llm_provider = app.config.get('LLM_PROVIDER', 'gemini')
    llm_enabled = False
    
    # 檢查 Gemini
    if app.config.get('GEMINI_API_KEY'):
        llm_enabled = True
        if llm_provider == 'gemini':
            app.logger.info("✓ Gemini API Key 已設定（當前使用）")
        else:
            app.logger.info("✓ Gemini API Key 已設定")
    
    # 檢查 Groq
    if app.config.get('GROQ_API_KEY'):
        llm_enabled = True
        if llm_provider == 'groq':
            app.logger.info("✓ Groq API Key 已設定（當前使用）")
        else:
            app.logger.info("✓ Groq API Key 已設定")
    
    # 檢查 OpenAI
    if app.config.get('OPENAI_API_KEY'):
        llm_enabled = True
        if llm_provider == 'openai':
            app.logger.info("✓ OpenAI API Key 已設定（當前使用）")
        else:
            app.logger.info("✓ OpenAI API Key 已設定")
    
    # 設定 LLM 狀態
    if llm_enabled:
        app.config['LLM_ENABLED'] = True
        app.logger.info(f"✓ LLM 提供商: {llm_provider.upper()}")
    else:
        app.config['LLM_ENABLED'] = False
        app.logger.warning("⚠ 未設定任何 LLM API Key，AI 對話功能將無法使用")
    
    # 保留舊的 GROQ_ENABLED 以維持向後相容
    app.config['GROQ_ENABLED'] = app.config.get('GROQ_API_KEY', '') != ''

    # ========== 初始化 RAG/LangGraph ==========
    if app.config.get('LLM_ENABLED'):
        try:
            # 設定 LangSmith 環境變數（如果啟用）
            if app.config.get('LANGCHAIN_TRACING_V2') == 'true':
                import os
                os.environ['LANGCHAIN_TRACING_V2'] = 'true'
                os.environ['LANGCHAIN_API_KEY'] = app.config.get('LANGCHAIN_API_KEY', '')
                os.environ['LANGCHAIN_PROJECT'] = app.config.get('LANGCHAIN_PROJECT', 'cocktail-ai-bartender')
                os.environ['LANGCHAIN_ENDPOINT'] = app.config.get('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
                app.logger.info("✓ LangSmith 追蹤已啟用")
            
            # 初始化 RAG 服務（可選，如果沒有 Qdrant 會靜默失敗）
            try:
                from app.services.rag_service import rag_service
                rag_service.initialize(
                    qdrant_host=app.config['QDRANT_HOST'],
                    qdrant_port=app.config['QDRANT_PORT'],
                    embedding_model=app.config['EMBEDDING_MODEL']
                )
                app.config['RAG_ENABLED'] = True
                app.logger.info("✓ RAG 服務已初始化")
            except Exception as e:
                app.config['RAG_ENABLED'] = False
                app.logger.info(f"ℹ RAG 服務未啟用（可選功能）: {str(e)}")
            
            # 初始化 LangGraph（必須）
            from app.services.langgraph_agent import initialize_graph
            with app.app_context():
                initialize_graph()
            
        except Exception as e:
            app.logger.warning(f"⚠ LangGraph 初始化失敗: {str(e)}")
            app.logger.warning("⚠ AI 對話功能將受限")
            app.config['RAG_ENABLED'] = False

    # ========== 註冊藍圖（路由）==========
    from app.routes.auth import auth_bp
    from app.routes.cocktails import cocktails_bp
    from app.routes.chat import chat_bp
    from app.routes.drinking_records import records_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(cocktails_bp)
    app.register_blueprint(records_bp)

    app.logger.info("✓ 所有路由已註冊")

    # ========== 健康檢查路由 ==========
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'mongodb': 'connected',
            'llm': {
                'enabled': app.config.get('LLM_ENABLED', False),
                'provider': app.config.get('LLM_PROVIDER', 'none'),
                'gemini': 'configured' if app.config.get('GEMINI_API_KEY') else 'not configured',
                'groq': 'configured' if app.config.get('GROQ_API_KEY') else 'not configured',
                'openai': 'configured' if app.config.get('OPENAI_API_KEY') else 'not configured'
            },
            'rag': 'enabled' if app.config.get('RAG_ENABLED') else 'disabled',
            'langsmith': 'enabled' if app.config.get('LANGCHAIN_TRACING_V2') == 'true' else 'disabled'
        }, 200

    # ========== 根路由 ==========
    @app.route('/')
    def index():
        return {
            'message': '🍸 歡迎使用 AI 調酒大師 API',
            'version': '2.0 (LangGraph Multi-LLM)',
            'features': {
                'auth': '✓ 用戶認證',
                'cocktails': '✓ 6,659 款調酒資料庫',
                'chat': f"✓ AI 酒保對話 ({app.config.get('LLM_PROVIDER', 'N/A').upper()})" if app.config.get('LLM_ENABLED') else '✗ AI 對話未啟用',
                'multi_llm': f"✓ 多 LLM 支援 (Gemini/Groq/OpenAI)",
                'rag': '✓ 語義搜尋' if app.config.get('RAG_ENABLED') else 'ℹ 語義搜尋（可選）',
                'multi_turn': '✓ 多輪對話',
                'langsmith': '✓ 追蹤除錯' if app.config.get('LANGCHAIN_TRACING_V2') == 'true' else 'ℹ 追蹤除錯（可選）'
            },
            'endpoints': {
                'auth': '/api/auth',
                'chat': '/api/chat',
                'cocktails': '/api/cocktails',
                'records': '/api/records',
                'health': '/health'
            }
        }, 200

    return app