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
    CORS(app, origins=app.config['CORS_ORIGINS'])
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

    # 註冊藍圖（路由）
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.cocktails import cocktails_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(cocktails_bp)

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
                'cocktails': '/api/cocktails'
            }
        }, 200

    return app
