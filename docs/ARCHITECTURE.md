# 系統架構文檔

本文檔說明 Cocktail AI 系統的整體架構設計，包括端口配置、服務連接、資料庫架構、認證機制和部署結構。

---

## 1. 系統總覽

Cocktail AI 是一個智慧調酒推薦平台，採用前後端分離架構，結合：
- **React 19 前端**：提供互動式使用者介面
- **Flask 3.1 後端**：處理業務邏輯和 API 服務
- **MongoDB 資料庫**：儲存調酒資料和用戶記錄
- **Qdrant 向量資料庫**：支援 RAG 語義搜尋（需 Docker）
- **LLM 服務**：整合 Gemini/Groq/OpenAI API

---

## 2. 系統架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    用戶端 (Browser)                          │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP
┌─────────────────────────────────────────────────────────────┐
│                    前端 (Frontend)                           │
│                React 19 + TypeScript + Vite                  │
│                   Port: 5173 (開發)                          │
│                   Port: 80/443 (生產)                        │
└─────────────────────────────────────────────────────────────┘
                              ↕ REST API
┌─────────────────────────────────────────────────────────────┐
│                    後端 (Backend)                            │
│                      Flask + Python                          │
│                   Port: 5000 (預設)                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              API 路由層 (Routes)                    │    │
│  │  /api/auth/*      - 認證與授權                     │    │
│  │  /api/chat/*      - AI 對話                        │    │
│  │  /api/cocktails/* - 調酒查詢                       │    │
│  │  /api/records/*   - 飲用記錄                       │    │
│  │  /api/recommend/* - 推薦系統                       │    │
│  │  /api/favorites/* - 收藏管理                       │    │
│  └────────────────────────────────────────────────────┘    │
│                              ↕                               │
│  ┌────────────────────────────────────────────────────┐    │
│  │            核心服務層 (Services)                    │    │
│  │  • ai_bartender.py   - LangGraph Agent             │    │
│  │  • rag_service.py    - RAG 語義搜尋                │    │
│  │  • recommendation.py - 推薦演算法                  │    │
│  │  • analytics.py      - 偏好分析                    │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    資料層 (Data Layer)                       │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │   MongoDB     │   │   Qdrant      │   │  LangSmith    │   │
│  │ Port: 27017  │   │ Port: 6333    │   │  (Cloud API)  │   │
│  │              │   │ (Docker)      │   │               │   │
│  │ • cocktails  │   │ • taste       │   │ • Traces      │   │
│  │ • users      │   │ • scenario    │   │ • Metrics     │   │
│  │ • records    │   │               │   │               │   │
│  │ • favorites  │   │               │   │               │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              外部 LLM API 服務                        │  │
│  │  • Gemini API (Google)                               │  │
│  │  • Groq API                                          │  │
│  │  • OpenAI API                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 端口配置

### 3.1 開發環境端口

| 服務 | 端口 | 協議 | 說明 |
|------|------|------|------|
| **前端 (Vite Dev Server)** | 5173 | HTTP | React 開發伺服器 |
| **後端 (Flask)** | 5000 | HTTP | Flask API 伺服器 |
| **MongoDB** | 27017 | TCP | 資料庫連接 |
| **Qdrant** | 6333 | HTTP | 向量資料庫 REST API |
| **Qdrant gRPC** | 6334 | gRPC | 向量資料庫 gRPC API（選用）|

### 3.2 生產環境端口

| 服務 | 端口 | 協議 | 說明 |
|------|------|------|------|
| **Nginx** | 80, 443 | HTTP/HTTPS | 反向代理與靜態檔案伺服器 |
| **Flask (Gunicorn)** | 5000 | HTTP | 內部 API 伺服器（不對外）|
| **MongoDB** | 27017 | TCP | 內部網路，不對外開放 |
| **Qdrant** | 6333 | HTTP | 內部網路，不對外開放 |

### 3.3 端口安全配置

**防火牆規則建議**：
- ✅ 開放：80 (HTTP)、443 (HTTPS)
- ❌ 關閉：5000 (Flask)、27017 (MongoDB)、6333 (Qdrant)
- 內部服務僅允許 localhost 或內網存取

---

## 4. 服務連接與通訊

### 4.1 前端 ↔ 後端

**開發環境**：
```
前端 (localhost:5173) → 後端 (localhost:5000)
```

**連接方式**：
- 協議：HTTP REST API
- 跨域處理：Flask-CORS 允許前端來源
- 認證：JWT Token 放在 Authorization Header

**前端配置** (`frontend/.env`):
```env
VITE_API_BASE_URL=http://localhost:5000
```

**請求範例**：
```typescript
// frontend/src/api/auth.ts
import axios from 'axios';

const response = await axios.post(
  `${import.meta.env.VITE_API_BASE_URL}/api/auth/login`,
  { email, password }
);
```

### 4.2 後端 ↔ MongoDB

**連接字串**：
```python
# backend_flask/app/config.py
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/cocktail_ai')
```

**連接方式**：
- 使用 PyMongo 驅動
- 連接池管理（預設 100 連線）
- 自動重連機制

**初始化**：
```python
# backend_flask/app/__init__.py
from pymongo import MongoClient

client = MongoClient(Config.MONGO_URI)
db = client.get_database()
```

### 4.3 後端 ↔ Qdrant (Docker)

**Qdrant 需使用 Docker 運行**：

**啟動 Qdrant 容器**：
```powershell
docker run -d `
  --name qdrant `
  -p 6333:6333 `
  -p 6334:6334 `
  -v "${PWD}/qdrant_storage:/qdrant/storage" `
  qdrant/qdrant:latest
```

**連接配置**：
```python
# backend_flask/app/config.py
QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
```

**連接方式**：
```python
# backend_flask/app/services/rag_service.py
from qdrant_client import QdrantClient

qdrant_client = QdrantClient(
    host=Config.QDRANT_HOST,
    port=Config.QDRANT_PORT
)
```

**資料持久化**：
- 向量資料存儲在 `qdrant_storage/` 資料夾
- 支援容器重啟後資料保留

### 4.4 後端 ↔ LLM API

**連接方式**：
- 透過 HTTPS API 呼叫
- 使用 API Key 認證
- LangChain 統一介面

**配置**：
```python
# backend_flask/app/config.py
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

**LangSmith 追蹤**：
```python
# 環境變數
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=cocktail-ai
```

---

## 5. 認證與授權機制

### 5.1 JWT 認證流程

```
┌─────────┐                                    ┌─────────┐
│  前端   │                                    │  後端   │
└────┬────┘                                    └────┬────┘
     │                                              │
     │  POST /api/auth/login                       │
     │  { email, password }                        │
     ├─────────────────────────────────────────────>│
     │                                              │
     │                      驗證 email 存在         │
     │                      bcrypt 驗證密碼         │
     │                      生成 JWT Token          │
     │                                              │
     │  { access_token, user }                     │
     │<─────────────────────────────────────────────┤
     │                                              │
儲存 Token 到 localStorage                          │
     │                                              │
     │  GET /api/cocktails                         │
     │  Authorization: Bearer <token>              │
     ├─────────────────────────────────────────────>│
     │                                              │
     │                      驗證 Token 有效性       │
     │                      解析 user_id            │
     │                      執行查詢                 │
     │                                              │
     │  { cocktails: [...] }                       │
     │<─────────────────────────────────────────────┤
     │                                              │
```

### 5.2 JWT Token 結構

**生成 Token**：
```python
# backend_flask/app/routes/auth.py
from flask_jwt_extended import create_access_token

access_token = create_access_token(
    identity=str(user['_id']),
    expires_delta=timedelta(days=1)
)
```

**Token Payload**：
```json
{
  "sub": "user_id",
  "iat": 1702567890,
  "exp": 1702654290,
  "type": "access"
}
```

**驗證 Token**：
```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/api/cocktails')
@jwt_required()
def get_cocktails():
    user_id = get_jwt_identity()
    # 執行業務邏輯
```

### 5.3 密碼安全

**密碼加密**：
```python
from werkzeug.security import generate_password_hash, check_password_hash

# 註冊時加密
password_hash = generate_password_hash(password, method='bcrypt')

# 登入時驗證
is_valid = check_password_hash(user['password_hash'], password)
```

**安全配置**：
- bcrypt 加密演算法（cost factor = 12）
- 密碼最小長度 8 字元
- JWT Secret Key 使用環境變數

### 5.4 CORS 配置

```python
# backend_flask/app/__init__.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, 
     origins=['http://localhost:5173'],  # 開發環境
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'])
```

---

## 6. 資料庫架構

### 6.1 MongoDB 架構

**資料庫名稱**：`cocktail_ai`

**Collections 列表**：

| Collection | 文檔數量 | 說明 |
|-----------|---------|------|
| `cocktails` | ~8,000+ | 調酒資料（英文）|
| `cocktails_zh` | ~8,000+ | 調酒資料（中文）|
| `users` | 動態 | 用戶帳號 |
| `conversations` | 動態 | AI 對話記錄 |
| `drinking_records` | 動態 | 飲用記錄 |
| `favorites` | 動態 | 收藏清單 |
| `personalities` | ~10 | 酒保性格 |
| `translations` | ~500 | 材料翻譯表 |
| `tag_translations` | ~200 | 標籤翻譯表 |

**索引配置**：
```javascript
// cocktails collection
db.cocktails.createIndex({ "name": "text" });
db.cocktails.createIndex({ "tags_categorized.base_spirits": 1 });
db.cocktails.createIndex({ "tags_categorized.flavors": 1 });
db.cocktails.createIndex({ "ratings.professional": -1 });

// drinking_records collection
db.drinking_records.createIndex({ "user_id": 1, "drunk_at": -1 });
db.drinking_records.createIndex({ "cocktail_id": 1 });

// conversations collection
db.conversations.createIndex({ "user_id": 1, "updated_at": -1 });

// favorites collection
db.favorites.createIndex({ "user_id": 1, "created_at": -1 });
```

### 6.2 Qdrant 向量資料庫架構

**需要 Docker 運行**：
```powershell
# 啟動 Qdrant (PowerShell)
docker run -d `
  --name qdrant `
  -p 6333:6333 `
  -p 6334:6334 `
  -v "${PWD}/qdrant_storage:/qdrant/storage" `
  qdrant/qdrant:latest
```

**Collections 結構**：

#### cocktails_taste（口味向量）
```python
{
  "collection_name": "cocktails_taste",
  "vectors_config": {
    "size": 384,
    "distance": "Cosine"
  },
  "payload": {
    "cocktail_id": "string",
    "name": "string",
    "name_zh": "string",
    "description": "string",
    "tags": ["array"]
  }
}
```

#### cocktails_scenario（情境向量）
```python
{
  "collection_name": "cocktails_scenario",
  "vectors_config": {
    "size": 384,
    "distance": "Cosine"
  },
  "payload": {
    "cocktail_id": "string",
    "name": "string",
    "scenario_tags": ["array"],
    "mood_tags": ["array"]
  }
}
```

**建立向量資料庫**：
```powershell
cd backend_flask\scripts
python setup_rag.py
```

---

## 7. Flask 應用架構

### 7.1 應用初始化

```python
# backend_flask/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object('app.config.Config')

# CORS 配置
CORS(app, origins=['http://localhost:5173'])

# JWT 配置
jwt = JWTManager(app)

# MongoDB 連接
mongo_client = MongoClient(app.config['MONGO_URI'])
db = mongo_client.get_database()

# 註冊路由
from app.routes import auth, chat, cocktails, records, recommendations, favorites
app.register_blueprint(auth.bp)
app.register_blueprint(chat.bp)
app.register_blueprint(cocktails.bp)
app.register_blueprint(records.bp)
app.register_blueprint(recommendations.bp)
app.register_blueprint(favorites.bp)
```

### 7.2 配置管理

```python
# backend_flask/app/config.py
import os

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/cocktail_ai')
    
    # Qdrant (需 Docker)
    QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
    QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # LLM API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # LangSmith
    LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'false')
    LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
    LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT', 'cocktail-ai')
```

### 7.3 路由架構

```python
# backend_flask/app/routes/auth.py
from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    # 註冊邏輯
    pass

@bp.route('/login', methods=['POST'])
def login():
    # 登入邏輯
    pass

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    # 取得當前用戶
    pass
```

---

## 8. 部署架構

### 8.1 開發環境部署

```
本地機器
├── Frontend (npm run dev)           → localhost:5173
├── Backend (python run.py)          → localhost:5000
├── MongoDB (mongod)                 → localhost:27017
└── Qdrant (docker run)              → localhost:6333
```

**啟動步驟**：
```powershell
# 1. 啟動 MongoDB
mongod --dbpath C:\data\db

# 2. 啟動 Qdrant (Docker)
docker run -d --name qdrant `
  -p 6333:6333 `
  -v "${PWD}/qdrant_storage:/qdrant/storage" `
  qdrant/qdrant:latest

# 3. 啟動後端
cd backend_flask
.\venv\Scripts\Activate.ps1
python run.py

# 4. 啟動前端
cd frontend
npm run dev
```

### 8.2 生產環境部署（建議）

```
┌─────────────────────────────────────────────┐
│           Nginx (反向代理)                   │
│         Port: 80, 443 (HTTPS)               │
│                                             │
│  ├─ / → 前端靜態檔案                        │
│  └─ /api → 後端 API (proxy_pass)           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│        Flask + Gunicorn (WSGI)              │
│            Port: 5000 (內部)                │
│         Workers: 4 (多進程)                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│              資料層                          │
│  ├─ MongoDB (Replica Set)                  │
│  │    - Primary: 27017                     │
│  │    - Secondary: 27018, 27019            │
│  │                                         │
│  └─ Qdrant (Docker Compose)                │
│       - Port: 6333 (內部)                   │
│       - Volume: 持久化存儲                  │
└─────────────────────────────────────────────┘
```

**Nginx 配置範例**：
```nginx
# /etc/nginx/sites-available/cocktail-ai
server {
    listen 80;
    server_name yourdomain.com;
    
    # 前端靜態檔案
    location / {
        root /var/www/cocktail-ai/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 後端 API 反向代理
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Gunicorn 啟動**：
```bash
cd backend_flask
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

**Docker Compose 配置**（Qdrant + MongoDB）：
```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: cocktail_ai

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  mongodb_data:
  qdrant_data:
```

---

## 9. 環境變數配置

### 9.1 後端環境變數

建立 `backend_flask/.env` 檔案：
```env
# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# MongoDB
MONGO_URI=mongodb://localhost:27017/cocktail_ai

# Qdrant (需 Docker)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# LLM API Keys
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key

# LangSmith (選用)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=cocktail-ai
```

### 9.2 前端環境變數

建立 `frontend/.env` 檔案：
```env
# API Base URL
VITE_API_BASE_URL=http://localhost:5000

# 其他配置
VITE_APP_TITLE=Cocktail AI
```

---

## 10. 資料流向與互動

### 10.1 用戶登入流程

```
前端輸入 → POST /api/auth/login → Flask 路由
                                     ↓
                            驗證 email (MongoDB)
                                     ↓
                            bcrypt 驗證密碼
                                     ↓
                            生成 JWT Token
                                     ↓
                            返回 Token + 用戶資料
                                     ↓
前端儲存 Token (localStorage) ← 回應
```

### 10.2 AI 對話流程

```
前端訊息 → POST /api/chat/message (JWT Auth)
                    ↓
          Flask 路由驗證 Token
                    ↓
          LangGraph Agent 處理
                    ↓
          ┌─────────┴──────────┐
          ↓                    ↓
    Qdrant 語義搜尋      MongoDB 資料查詢
    (Docker 容器)
          ↓                    ↓
          └─────────┬──────────┘
                    ↓
          整合結果 → LLM 生成回應
                    ↓
          提取調酒卡片資訊
                    ↓
          儲存對話記錄 (MongoDB)
                    ↓
          返回回應 + 卡片資料 → 前端顯示
```

### 10.3 推薦系統流程

```
請求推薦 → GET /api/recommend (JWT Auth)
                    ↓
          取得用戶偏好 (MongoDB)
                    ↓
          分析飲用記錄
                    ↓
          計算相似度分數
                    ↓
          從 MongoDB 查詢候選調酒
                    ↓
          按比例抽取 (平衡/冒險模式)
                    ↓
          多樣性處理與排序
                    ↓
          返回推薦清單 → 前端顯示
```

---

## 11. 監控與維護

### 11.1 服務健康檢查

```python
# backend_flask/app/routes/health.py
@app.route('/health')
def health_check():
    return {
        'status': 'ok',
        'mongodb': check_mongodb(),
        'qdrant': check_qdrant(),
        'timestamp': datetime.now().isoformat()
    }
```

### 11.2 日誌記錄

```python
# backend_flask/app/__init__.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 11.3 效能監控

- **MongoDB**：使用 `mongostat`、`mongotop` 監控
- **Qdrant**：透過 Web UI (http://localhost:6333/dashboard) 監控
- **Flask**：記錄 API 回應時間
- **LangSmith**：追蹤 LLM 調用次數和成本

---

## 12. 安全性最佳實踐

### 12.1 網路安全

- ✅ 使用 HTTPS (生產環境)
- ✅ 設定 CORS 白名單
- ✅ 內部服務不對外開放（MongoDB、Qdrant）
- ✅ 使用防火牆限制端口存取
- ✅ API Rate Limiting

### 12.2 資料安全

- ✅ 密碼 bcrypt 加密
- ✅ JWT Token 有效期限制
- ✅ 敏感資料使用環境變數
- ✅ MongoDB 啟用認證
- ✅ 定期備份資料庫

### 12.3 應用安全

- ✅ 輸入驗證與清理
- ✅ SQL/NoSQL 注入防護
- ✅ XSS 防護
- ✅ CSRF Token（必要時）
- ✅ 依賴套件定期更新

---

## 13. 故障排除

### 13.1 常見問題

**問題：前端無法連接後端**
- 檢查後端是否啟動：`curl http://localhost:5000/health`
- 檢查 CORS 配置
- 檢查防火牆設定

**問題：Qdrant 連接失敗**
- 確認 Docker 容器運行：`docker ps | grep qdrant`
- 檢查端口是否被佔用：`netstat -an | grep 6333`
- 重啟容器：`docker restart qdrant`

**問題：MongoDB 連接失敗**
- 確認 MongoDB 服務運行：`systemctl status mongod`
- 檢查連接字串：`MONGO_URI` 環境變數
- 檢查防火牆規則

**問題：JWT Token 無效**
- 檢查 Token 是否過期
- 檢查 `JWT_SECRET_KEY` 是否一致
- 清除前端 localStorage 重新登入

---

## 14. 擴展性考量

### 14.1 水平擴展

- **後端**：部署多個 Flask Instance + 負載均衡器
- **MongoDB**：使用 Replica Set 或 Sharding
- **Qdrant**：使用 Qdrant Cluster

### 14.2 快取策略

- **Redis**：API 回應快取、Session 快取
- **CDN**：前端靜態資源快取
- **MongoDB**：查詢結果快取

### 14.3 未來架構

- 微服務架構：AI 服務、推薦服務獨立部署
- 訊息佇列：RabbitMQ/Kafka 處理非同步任務
- Kubernetes：容器編排與自動擴展
