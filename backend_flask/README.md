# 🍸 AI 調酒大師 API (Flask 後端)

基於 LangGraph 的智能調酒推薦系統

## ✨ 功能特色

- ✅ **6,659 款專業調酒**（來自 Difford's Guide）
- ✅ **多 LLM 支援**（Gemini / Groq / OpenAI）
- ✅ **LangGraph Agent**（智能工具調用）
- ✅ **RAG 語義搜尋**（Qdrant 向量資料庫）
- ✅ **多輪對話記憶**
- ✅ **JWT 認證系統**
- ✅ **情感分析**
- ✅ **7 種搜尋工具**

---

## 📋 系統需求

- Python 3.10+
- MongoDB 4.4+
- Docker（用於 Qdrant）
- 至少一個 LLM API Key（Gemini / Groq / OpenAI）

---

## 🚀 快速開始

### Step 1：克隆專案（如果需要）

```bash
git clone <your-repo>
cd backend_flask
```

---

### Step 2：安裝 Python 依賴

```bash
# 建立虛擬環境（推薦）
python -m venv .venv

# 啟動虛擬環境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

---

### Step 3：啟動 MongoDB

#### 選項 A：本地安裝（推薦開發環境）

```bash
# macOS (Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
# 從「服務」啟動 MongoDB
```

#### 選項 B：使用 Docker

```bash
docker run -d \
  --name cocktail-mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  mongo:7.0

# 環境變數改為
MONGODB_URI=mongodb://admin:password123@localhost:27017/
```

---

### Step 4：啟動 Qdrant（Docker）⭐

**這是 RAG 語義搜尋的必要步驟！**

```bash
# 啟動 Qdrant
docker run -d \
  --name cocktail-qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Windows PowerShell 使用
docker run -d --name cocktail-qdrant -p 6333:6333 -p 6334:6334 -v ${PWD}/qdrant_storage:/qdrant/storage qdrant/qdrant:latest

# 驗證 Qdrant 運行
curl http://localhost:6333/health

# 應該返回
{"title":"qdrant - vector search engine","version":"..."}
```

**查看 Qdrant 狀態**：

```bash
# 查看容器
docker ps | grep qdrant

# 查看日誌
docker logs cocktail-qdrant

# 停止
docker stop cocktail-qdrant

# 啟動（如果已存在）
docker start cocktail-qdrant
```

---

### Step 5：設定環境變數

```bash
# 複製範本
cp .env.example .env

# 編輯 .env
nano .env
```

**必須設定的變數**：

```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=cocktail_ai

# LLM（至少選一個）
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your_key_here

# Qdrant（Docker 預設）
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Flask
SECRET_KEY=your_random_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

**如何取得 API Keys**：

- **Gemini**：https://makersuite.google.com/app/apikey
- **Groq**：https://console.groq.com/keys
- **OpenAI**：https://platform.openai.com/api-keys

---

### Step 6：初始化資料

#### 6.1 匯入調酒資料到 MongoDB

```bash
python scripts/optimize_mongodb.py
```

**預期輸出**：

```
開始匯入 Diffordsguide 調酒資料
============================================================
找到 6659 個 JSON 檔案

匯入報告
============================================================
總檔案: 6659
成功: 6659
略過: 0
失敗: 0
============================================================
```

#### 6.2 向量化資料到 Qdrant（RAG 功能）

**⚠️ 重要：確保 Qdrant Docker 容器正在運行！**

```bash
python scripts/setup_rag.py
```

**預期輸出**：

```
============================================================
AI 調酒大師 - RAG 向量化設定
============================================================

[1/4] 連接 MongoDB...
✓ 找到 6659 筆調酒資料

[2/4] 載入 Embedding 模型: paraphrase-multilingual-mpnet-base-v2
✓ 模型載入完成（維度: 768）

[3/4] 連接 Qdrant 向量資料庫...
✓ Qdrant 連接成功 (localhost:6333)

[4/4] 建立向量集合...
 ✓ 建立集合: cocktails_taste
 ✓ 建立集合: cocktails_scenario

開始向量化...
============================================================

[1/3] 準備文本...
100%|████████████████████| 6659/6659

[2/3] 生成向量...
Batches: 100%|████████████| 209/209

[3/3] 存入向量資料庫...
上傳口味向量: 100%|████████████| 67/67
上傳場景向量: 100%|████████████| 67/67

✓ 向量化完成！

驗證設定
============================================================

Qdrant:
 - cocktails_taste: 6659 筆
 - cocktails_scenario: 6659 筆

測試查詢: '清爽酸甜的調酒'

查詢結果:
1. Mojito - score=0.8765
2. Margarita - score=0.8432
3. Daiquiri - score=0.8201

✓ 驗證完成！

============================================================
RAG 設定完成！
============================================================
```

**如果遇到錯誤**：

```bash
# 錯誤：連接失敗
# 解決：檢查 Qdrant 是否運行
docker ps | grep qdrant

# 如果沒有運行，啟動它
docker start cocktail-qdrant

# 重新執行向量化
python scripts/setup_rag.py
```

---

### Step 7：啟動 Flask 應用

```bash
python run.py
```

**預期輸出**：

```
✓ 成功連接到 MongoDB: cocktail_ai
✓ Gemini API Key 已設定（當前使用）
✓ LLM 提供商: GEMINI
✓ RAG 服務已初始化
✓ LangGraph Agent 已初始化 (使用 GEMINI)
✓ 所有路由已註冊
 * Running on http://0.0.0.0:5000
```

---

### Step 8：驗證服務

```bash
# 健康檢查
curl http://localhost:5000/health

# 應該返回
{
  "status": "healthy",
  "mongodb": "connected",
  "llm": {
    "enabled": true,
    "provider": "gemini",
    "gemini": "configured"
  },
  "rag": "enabled",
  "langsmith": "disabled"
}
```

---

## 🎯 API 端點

### 認證 API

```bash
# 註冊
POST /api/auth/register
Content-Type: application/json

{
  "username": "test_user",
  "email": "test@example.com",
  "password": "password123"
}

# 登入
POST /api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}

# 當前使用者
GET /api/auth/me
Authorization: Bearer <token>
```

---

### 聊天 API

```bash
# 發送訊息
POST /api/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "推薦一款適合夏天的調酒",
  "conversation_id": "optional_conversation_id"
}

# 回應範例
{
  "conversation_id": "67890...",
  "message": "我推薦 Mojito！這是一款...",
  "sentiment": 0.5,
  "warning_issued": false,
  "tool_used": true,
  "mode": "langgraph"
}

# 對話列表
GET /api/chat/conversations
Authorization: Bearer <token>

# 對話詳情
GET /api/chat/conversations/<conversation_id>
Authorization: Bearer <token>
```

---

### 調酒 API

```bash
# 列表（分頁）
GET /api/cocktails?page=1&limit=20

# 詳情
GET /api/cocktails/<cocktail_id>

# 搜尋
GET /api/cocktails/search?q=mojito

# 分類
GET /api/cocktails/category/Gin%20Cocktails

# 隨機
GET /api/cocktails/random

# 進階篩選
GET /api/cocktails/filter?min_rating=4.0&difficulty=easy&max_calories=200

# 統計
GET /api/cocktails/stats

# 所有分類
GET /api/cocktails/categories
```

---

## 🛠️ LangGraph Agent 工具

Agent 可以使用以下 7 個工具：

1. **search_by_name** - 根據名稱搜尋
2. **search_by_ingredients** - 根據材料搜尋
3. **filter_by_attributes** - 多維度篩選
4. **search_by_taste_semantic** - 口味語義搜尋（RAG）
5. **search_by_scenario_semantic** - 場景語義搜尋（RAG）
6. **search_by_category** - 根據分類搜尋
7. **get_random_cocktail** - 隨機推薦

---

## 🔧 開發指南

### 開發模式（自動重載）

```bash
# 設定環境變數
export FLASK_ENV=development  # macOS/Linux
set FLASK_ENV=development     # Windows CMD
$env:FLASK_ENV="development"  # Windows PowerShell

# 啟動
python run.py
```

---

### 查看日誌

```bash
# Flask 日誌（終端輸出）
python run.py

# Qdrant 日誌
docker logs -f cocktail-qdrant

# MongoDB 日誌
# macOS
tail -f /usr/local/var/log/mongodb/mongo.log

# Linux
sudo tail -f /var/log/mongodb/mongod.log
```

---

### 測試 API

使用 `curl` 或 Postman：

```bash
# 註冊
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"123456"}'

# 登入
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123456"}'

# 聊天（需要替換 token）
curl -X POST http://localhost:5000/api/chat/message \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"message":"推薦清爽的調酒"}'
```

---

## 🐳 Docker 管理（Qdrant）

### 常用命令

```bash
# 啟動
docker start cocktail-qdrant

# 停止
docker stop cocktail-qdrant

# 重啟
docker restart cocktail-qdrant

# 刪除（會保留資料）
docker stop cocktail-qdrant
docker rm cocktail-qdrant

# 完全重建
docker stop cocktail-qdrant
docker rm cocktail-qdrant
rm -rf qdrant_storage/
docker run -d --name cocktail-qdrant -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant:latest
python scripts/setup_rag.py
```

---

### Qdrant Web UI

訪問：http://localhost:6333/dashboard

可以：
- 查看 collections
- 瀏覽向量
- 測試查詢

---

## 🗂️ 專案架構

```
backend_flask/
├── app/
│   ├── __init__.py              # Flask 應用初始化
│   ├── config.py                # 配置管理
│   ├── models.py                # 資料模型
│   │
│   ├── routes/                  # API 路由
│   │   ├── auth.py              # 認證 API
│   │   ├── chat.py              # 聊天 API
│   │   └── cocktails.py         # 調酒 API
│   │
│   └── services/                # 業務邏輯
│       ├── langgraph_agent.py   # LangGraph Agent
│       ├── tools.py             # 7 個工具
│       ├── rag_service.py       # RAG 服務
│       ├── conversation_manager.py  # 對話管理
│       └── sentiment.py         # 情感分析
│
├── scripts/                     # 初始化腳本
│   ├── optimize_mongodb.py     # MongoDB 資料匯入
│   └── setup_rag.py            # Qdrant 向量化
│
├── data/                        # 資料目錄
│   └── diffordsguide/          # 6659 個 JSON 檔案
│
├── qdrant_storage/             # Qdrant 資料（Docker volume）
│
├── run.py                       # 應用入口
├── requirements.txt             # Python 依賴
├── .env                         # 環境變數（不提交）
├── .env.example                 # 環境變數範本
├── .gitignore                   # Git 忽略
└── README.md                    # 本文檔
```

---

## ⚙️ 環境變數說明

| 變數 | 說明 | 預設值 | 必須 |
|------|------|--------|------|
| `SECRET_KEY` | Flask 密鑰 | - | ✅ |
| `JWT_SECRET_KEY` | JWT 密鑰 | - | ✅ |
| `MONGODB_URI` | MongoDB 連接 | `mongodb://localhost:27017/` | ✅ |
| `MONGODB_DB` | 資料庫名稱 | `cocktail_ai` | ✅ |
| `LLM_PROVIDER` | LLM 提供商 | `gemini` | ✅ |
| `GEMINI_API_KEY` | Gemini Key | - | ⭐ |
| `GROQ_API_KEY` | Groq Key | - | - |
| `OPENAI_API_KEY` | OpenAI Key | - | - |
| `QDRANT_HOST` | Qdrant 主機 | `localhost` | ✅ |
| `QDRANT_PORT` | Qdrant 端口 | `6333` | ✅ |
| `EMBEDDING_MODEL` | 向量模型 | `paraphrase-multilingual-mpnet-base-v2` | - |
| `LANGCHAIN_TRACING_V2` | LangSmith 追蹤 | `false` | - |

---

## 🐛 常見問題

### 1. Qdrant 連接失敗

**錯誤**：
```
❌ Qdrant 連接失敗: Cannot connect to host localhost:6333
```

**解決**：
```bash
# 檢查 Qdrant 是否運行
docker ps | grep qdrant

# 如果沒有，啟動它
docker start cocktail-qdrant

# 如果容器不存在，重新建立
docker run -d --name cocktail-qdrant -p 6333:6333 qdrant/qdrant:latest
```

---

### 2. MongoDB 連接失敗

**錯誤**：
```
❌ MongoDB 連接失敗: connection refused
```

**解決**：
```bash
# 檢查 MongoDB 是否運行
# macOS
brew services list | grep mongodb

# Linux
sudo systemctl status mongod

# 啟動 MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod           # Linux
```

---

### 3. RAG 服務未初始化

**錯誤**：
```
ℹ RAG 服務未啟用（可選功能）
```

**解決**：
```bash
# 1. 確保 Qdrant 運行
docker ps | grep qdrant

# 2. 執行向量化
python scripts/setup_rag.py

# 3. 重啟 Flask
python run.py
```

---

### 4. LLM API Key 無效

**錯誤**：
```
⚠ 未設定任何 LLM API Key
```

**解決**：
```bash
# 編輯 .env
nano .env

# 確保設定了正確的 Key
GEMINI_API_KEY=AIzaSy...

# 重啟應用
python run.py
```

---

### 5. 缺少調酒資料

**錯誤**：
```
找到 0 筆調酒資料
```

**解決**：
```bash
# 確保資料檔案存在
ls data/diffordsguide/*.json | wc -l

# 應該輸出 6659

# 執行資料匯入
python scripts/optimize_mongodb.py
```

---

## 📚 相關資源

- **LangChain 文檔**：https://python.langchain.com/docs/
- **LangGraph 文檔**：https://langchain-ai.github.io/langgraph/
- **Qdrant 文檔**：https://qdrant.tech/documentation/
- **Flask 文檔**：https://flask.palletsprojects.com/
- **MongoDB 文檔**：https://www.mongodb.com/docs/

---

## 🤝 開發團隊

如有問題，請聯繫開發團隊或提交 Issue。

---

## 📝 更新日誌

### v2.0 (Current)
- ✅ LangGraph Agent
- ✅ 多 LLM 支援（Gemini / Groq / OpenAI）
- ✅ RAG 語義搜尋
- ✅ 7 個智能工具
- ✅ 多輪對話記憶

### v1.0
- 基礎 API
- JWT 認證
- MongoDB 資料庫

---

**🎉 現在你可以開始開發了！**

如有任何問題，請參考上方的「常見問題」或查看日誌。