import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """應用程式設定"""

    # Flask 基本設定
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # JWT 設定
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 小時

    # MongoDB 設定
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB = os.getenv('MONGODB_DB', 'cocktail_ai')

    # Groq API 設定
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

    # CORS 設定
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://localhost:5174'  # 備用端口
    ]
