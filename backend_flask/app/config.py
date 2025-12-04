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

    # API 設定
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')

    # CORS 設定
    CORS_ORIGINS = [
        'http://localhost:5173',
        'http://localhost:5174'  # 備用端口
    ]

    # LangGraph 設定 
    USE_LANGGRAPH = os.getenv('USE_LANGGRAPH', 'true').lower() == 'true'
    
    # RAG 設定 
    QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
    QDRANT_PORT = int(os.getenv('QDRANT_PORT', '6333'))
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-mpnet-base-v2')
    
    # Tavily API 設定（可選）
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
    
    # LangSmith 設定（追蹤與除錯）
    LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'false')
    LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY', '')
    LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT', 'cocktail-ai-bartender')
    LANGCHAIN_ENDPOINT = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')