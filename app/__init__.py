import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from app.config import Config
from app.services.llm_service import llm_service


def create_app(config_class=Config):
    """Flask 應用程式工廠函數"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化擴充套件
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"],
    )

    JWTManager(app)

    # 連接 MongoDB
    try:
        client = MongoClient(app.config['MONGODB_URI'])
        db = client[app.config['MONGODB_DB']]
        app.config['DB'] = db
        app.logger.info(f"成功連接到 MongoDB: {app.config['MONGODB_DB']}")
    except Exception as e:
        app.logger.error(f"MongoDB 連接失敗: {str(e)}")
        raise

    # 初始化 Groq LLM 服務
    groq_api_key = app.config.get('GROQ_API_KEY', '')
    if groq_api_key:
        try:
            llm_service.initialize(groq_api_key)
            app.logger.info("✓ Groq LLM 服務初始化成功")
            app.config['GROQ_ENABLED'] = True
        except Exception as e:
            app.logger.warning(f"⚠ Groq LLM 服務初始化失敗: {str(e)}")
            app.logger.warning("⚠ AI 對話功能將無法使用，但其他功能正常")
            app.config['GROQ_ENABLED'] = False
    else:
        app.logger.warning("⚠ 未設定 Groq API Key，AI 對話功能將無法使用")
        app.config['GROQ_ENABLED'] = False

    # 初始化 LangSmith 追蹤
    if app.config.get('LANGSMITH_TRACING', False):
        try:
            os.environ['LANGCHAIN_TRACING_V2'] = 'true'
            os.environ['LANGCHAIN_API_KEY'] = app.config.get('LANGSMITH_API_KEY', '')
            os.environ['LANGCHAIN_ENDPOINT'] = app.config.get('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com')
            os.environ['LANGCHAIN_PROJECT'] = app.config.get('LANGSMITH_PROJECT', 'cocktail_ai')
            app.config['LANGSMITH_ENABLED'] = True
            app.logger.info("✓ LangSmith 追蹤已啟用")
        except Exception as e:
            app.logger.warning(f"⚠ LangSmith 初始化失敗: {str(e)}")
            app.config['LANGSMITH_ENABLED'] = False
    else:
        app.config['LANGSMITH_ENABLED'] = False
        app.logger.info("ℹ LangSmith 追蹤未啟用")

    # 註冊藍圖（路由）
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.cocktails import cocktails_bp
    from app.routes.drinking_records import records_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(cocktails_bp)
    app.register_blueprint(records_bp)

    

    # 健康檢查路由
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'AI 酒保服務運行中'}, 200

    # 根路由
    @app.route('/')
    def index():
        return {
            'message': '歡迎使用 AI 酒保 API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'chat': '/api/chat',
                'cocktails': '/api/cocktails',
                'records': '/api/records'
            }
        }, 200

    return app
