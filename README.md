# 🍸 AI 調酒大師 - 智能調酒探索平台

一個結合 AI 技術與專業調酒資料庫的全端應用，提供超過 6,659 種調酒配方、智能推薦、進階篩選和互動式對話體驗。採用 LangGraph 多 LLM 架構，支援 Docker 容器化部署。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue.svg)
![MongoDB](https://img.shields.io/badge/mongodb-6.0+-green.svg)

## ✨ 核心功能

### 🍹 調酒探索
- **6,659 專業配方**：來自 Difford's Guide 的完整調酒資料庫
- **進階篩選系統**：根據評分、酒精強度、甜度、卡路里、難度等多維度篩選
- **智能搜尋**：支援調酒名稱、材料、分類、語義搜尋
- **詳細資訊展示**：圖片、風味檔案、營養資訊、製作方法、歷史故事、變化版本

### 🤖 AI 酒保對話（LangGraph 驅動）
- **多 LLM 支援**：Gemini 2.5、Groq、OpenAI（可切換）
- **智能 Agent 工作流程**：7 個專業工具，自動執行複雜推理
- **完整 RAG 系統**：語義搜尋 + Qdrant 向量資料庫
- **個性化推薦**：基於用戶偏好和上下文的智能推薦
- **情感分析**：根據用戶情緒調整回應
- **對話記憶**：完整的對話歷史追蹤

### 📊 資料分析
- **Jupyter Notebook**：深度資料分析與可視化
- **統計洞察**：評分分布、材料頻率、營養指標、風味聚類

### 🔐 用戶系統
- **JWT 認證**：基於 Token 的安全認證
- **個人偏好管理**：保存口味偏好和禁忌材料
- **對話歷史追蹤**：完整的互動記錄

## 🏗️ 技術棧

### 後端
- **Flask 3.0** - Python Web 框架
- **MongoDB 6.0** - NoSQL 資料庫
- **LangGraph** - Agent 工作流程編排
- **Groq/Gemini API** - 多 LLM 支援
- **Qdrant** - 向量資料庫（RAG）
- **Flask-JWT-Extended** - JWT 認證
- **TextBlob** - 情感分析

### 前端
- **React 18** - UI 框架
- **TypeScript** - 型別安全
- **Vite** - 快速建置工具
- **Tailwind CSS** - 樣式框架
- **React Context** - 狀態管理

### DevOps
- **Docker & Docker Compose** - 容器化部署
- **Nginx** - 前端反向代理
- **Python 3.11** - 後端運行環境
- **Node.js 20** - 前端構建環境

## 📦 快速開始

### 方式 A：使用 Docker Compose（推薦）⭐

#### 前置需求

- **Docker** 和 **Docker Compose**
- **API Keys**：Groq 或 Gemini

#### 1. 克隆專案並設定環境

```bash
git clone <repository-url>
cd cocktail_ai
cp backend_flask/.env.example backend_flask/.env
```

#### 2. 配置環境變數

編輯 `backend_flask/.env`：

```env
# MongoDB（Docker 內部通信）
MONGODB_URI=mongodb://mongo:27017/
MONGODB_DB=cocktail_ai

# 選擇你的 LLM（推薦 Gemini）
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
# 或 Groq
# LLM_PROVIDER=groq
# GROQ_API_KEY=gsk_your_groq_api_key_here

# Flask 設定
SECRET_KEY=your-random-secret-key
JWT_SECRET_KEY=your-random-jwt-secret-key
FLASK_ENV=production

# RAG 設定（Docker 內部通信）
QDRANT_HOST=qdrant
QDRANT_PORT=6333
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2
```

#### 3. 建置並啟動容器

```bash
# 建置映象
docker-compose build

# 啟動所有服務（首次會導入調酒資料）
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 等待初始化完成（約 2-3 分鐘）
```

#### 4. 驗證服務

```bash
# 檢查容器狀態
docker-compose ps

# 測試 API
curl http://localhost:5000/health
curl http://localhost:3000/

# 瀏覽器訪問
# 前端：http://localhost:3000
# 後端 API：http://localhost:5000
# Qdrant 儀表板：http://localhost:6333/dashboard
```

#### 5. 停止和清理

```bash
# 停止容器
docker-compose down

# 完全清理（包括數據卷）
docker-compose down -v
```

---

### 方式 B：本地開發環境

#### 前置需求

- **Python 3.11+**
- **Node.js 20+** 和 npm
- **MongoDB 6.0+**（本地或 MongoDB Atlas）
- **Docker**（用於 Qdrant，可選）

#### 1. 克隆專案

```bash
git clone <repository-url>
cd cocktail_ai
```

#### 2. 後端設定

```bash
# 進入後端目錄
cd backend_flask

# === 選項 A：使用 Conda（推薦）===
# 建立 conda 虛擬環境
conda create -n cocktail_ai python=3.11

# 啟動虛擬環境
conda activate cocktail_ai

# === 選項 B：使用 venv ===
# python -m venv venv
# venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 下載 TextBlob 語料庫
python -m textblob.download_corpora

# 設定環境變數（Windows）
copy .env.example .env
# 編輯 .env 填入你的設定（可用記事本或 VS Code）
```

#### 3. 取得 API Keys

**Gemini API（推薦）**：
- 前往 https://makersuite.google.com/app/apikey
- 建立新 API Key
- 複製到 `.env` 的 `GEMINI_API_KEY`

**或 Groq API**：
- 前往 https://console.groq.com
- 建立新 API Key
- 複製到 `.env` 的 `GROQ_API_KEY`

#### 4. MongoDB 設定

**選項 A：本地安裝**

請將含英文資料放在`data/diffordsguide/` 目錄下
> https://drive.google.com/file/d/1BtOo_I3SJBxPb3CL7r3219cQ8Hs21wWi/view?usp=sharing

請將含中文翻譯資料放在`data/diffordsguide_trans/` 目錄下
> https://drive.google.com/file/d/1Igv9_FXqcH2RJrXPro9Eu_xyU19-VGQL/view?usp=sharing

請將中英對照表放在`data/trans_table/` 目錄下
> https://drive.google.com/file/d/1JMI5h3AmKuMqdfXYNLcs2mkqp4ZG-q3L/view?usp=sharing


```bash
# Windows：確保 MongoDB 服務運行
# 方法 1：使用服務管理器（services.msc）
#   - 按 Win+R，輸入 services.msc
#   - 找到 MongoDB Server，點擊「啟動」

# 方法 2：使用命令列（需以系統管理員身分執行）
net start MongoDB
```

**選項 B：MongoDB Atlas**

1. 前往 https://www.mongodb.com/cloud/atlas
2. 建立免費叢集
3. 取得連接字串
4. 更新 `.env`：`MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/`

#### 5. 導入調酒資料

```bash
# 在 backend_flask 目錄
python scripts/import_diffordsguide.py
python scripts/import_diffordsguide_zh.py
python scripts/import_trans_table.py

# 預期輸出
# 總檔案數: 6659
# [OK] 成功匯入: 6659
```

#### 6. 設定 RAG（可選）

Qdrant 使用 Docker：

```bash
# 啟動 Qdrant 容器（Windows PowerShell）
docker run -d -p 6333:6333 -v ${PWD}/qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant

# 或使用 CMD
# docker run -d -p 6333:6333 -v %cd%/qdrant_storage:/qdrant/storage --name qdrant qdrant/qdrant

# 驗證（用瀏覽器開啟）
# http://localhost:6333/dashboard

# 向量化調酒資料
python scripts/setup_rag.py
# 約 5-10 分鐘完成
```

#### 7. 啟動後端

```bash
python run.py
# 應該看到：* Running on http://127.0.0.1:5000
```

#### 8. 前端設定

```bash
# 新終端，進入前端目錄
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev
# 應該看到：http://localhost:5173
```

#### 9. 開始使用

瀏覽器訪問 http://localhost:5173

## 📡 API 文檔

### 認證 API (`/api/auth`)

| 方法 | 端點 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/auth/register` | 用戶註冊 | ✗ |
| POST | `/api/auth/login` | 用戶登入 | ✗ |
| GET | `/api/auth/me` | 取得當前用戶 | ✓ |
| PUT | `/api/auth/preferences` | 更新用戶偏好 | ✓ |

### 調酒 API (`/api/cocktails`)

| 方法 | 端點 | 說明 | 參數 |
|------|------|------|------|
| GET | `/api/cocktails/` | 取得調酒列表 | `page`, `limit` |
| GET | `/api/cocktails/<id>` | 取得特定調酒 | - |
| GET | `/api/cocktails/search` | 搜尋調酒 | `q` (關鍵字) |
| GET | `/api/cocktails/filter` | 進階篩選 | 見下方說明 |
| GET | `/api/cocktails/categories` | 取得所有分類 | - |
| GET | `/api/cocktails/random` | 隨機調酒 | - |

#### 進階篩選參數

```
GET /api/cocktails/filter?
  category=<分類>&
  min_rating=<最低評分>&
  max_rating=<最高評分>&
  min_strength=<最低酒精強度>&
  max_strength=<最高酒精強度>&
  min_sweetness=<最低甜度>&
  max_sweetness=<最高甜度>&
  max_calories=<最高卡路里>&
  difficulty=<難度>&
  sort_by=<排序方式>&
  page=<頁碼>&
  limit=<每頁數量>
```

**排序選項**：
- `name` - 名稱
- `rating_desc` - 評分（高→低）
- `rating_asc` - 評分（低→高）
- `strength_desc` - 酒精強度（高→低）
- `calories_asc` - 卡路里（低→高）
- `popular` - 最受歡迎（依公眾評價數）

### 對話 API (`/api/chat`)

| 方法 | 端點 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/chat/conversations` | 建立新對話 | ✓ |
| GET | `/api/chat/conversations` | 取得所有對話 | ✓ |
| GET | `/api/chat/conversations/<id>` | 取得特定對話 | ✓ |
| POST | `/api/chat/message` | 發送訊息 | ✓ |
| DELETE | `/api/chat/conversations/<id>` | 刪除對話 | ✓ |

## 📁 專案架構

```
cocktail_ai/
├── backend_flask/                    # Flask 後端應用
│   ├── app/
│   │   ├── __init__.py               # Flask app 初始化 + 多 LLM 設定
│   │   ├── config.py                 # 配置管理
│   │   ├── models.py                 # MongoDB 資料模型
│   │   ├── routes/                   # API 路由
│   │   │   ├── auth.py               # 認證 API
│   │   │   ├── chat.py               # 對話 API（LangGraph 驅動）
│   │   │   └── cocktails.py          # 調酒 API
│   │   └── services/                 # 業務邏輯層
│   │       ├── conversation_manager.py  # 對話管理（獨立模塊）
│   │       ├── langgraph_agent.py     # LangGraph Agent 工作流
│   │       ├── rag_service.py         # RAG 向量搜尋服務
│   │       ├── sentiment.py           # 情感分析
│   │       └── tools.py               # Agent 工具定義（7 個）
│   ├── data/
│   │   ├── diffordsguide/            # 調酒 JSON 資料（6,659 個）
│   │   ├── mongo/                    # MongoDB 持久化目錄
│   │   └── qdrant/                   # Qdrant 向量庫持久化
│   ├── scripts/
│   │   ├── import_diffordsguide.py   # 資料導入腳本
│   │   ├── cocktail_analysis.ipynb   # 資料分析筆記本
│   │   ├── cocktail_analysis_report.md # 分析報告
│   │   └── analysis_images/          # 分析圖表
│   ├── Dockerfile                    # 後端容器配置
│   ├── requirements.txt              # Python 依賴
│   ├── run.py                        # 啟動入口
│   ├── setup_rag.py                  # RAG 初始化腳本
│   ├── test_api.py                   # API 測試
│   ├── test_langgraph_api.py         # LangGraph 測試
│   ├── .env.example                  # 環境變數範例
│   ├── LANGGRAPH_UPGRADE_COMPLETE_GUIDE.md  # 升級指南
│   └── QUICKSTART.md                 # 快速開始
│
├── frontend/                         # React 前端應用
│   ├── src/
│   │   ├── App.tsx                   # 主應用組件
│   │   ├── main.tsx                  # 應用入口
│   │   ├── App.css / index.css       # 全局樣式
│   │   ├── assets/                   # 靜態資源
│   │   ├── components/               # 可復用組件
│   │   ├── contexts/                 # React Context
│   │   ├── pages/                    # 頁面組件
│   │   │   ├── ChatPage.tsx          # AI 對話頁面
│   │   │   └── CocktailsPage.tsx     # 調酒瀏覽頁面
│   │   ├── services/                 # API 服務層
│   │   ├── types/                    # TypeScript 型別
│   │   └── utils/                    # 工具函式
│   ├── public/                       # 公開資源
│   ├── Dockerfile                    # 前端容器配置
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── index.html
│
├── docker-compose.yml                # Docker 組合配置
├── README.md                         # 本文檔
└── .gitignore
```

## 🐳 Docker 詳細說明

### Docker Compose 服務架構

```
frontend (port 3000)        # Nginx + React 前端
    ↓
backend_flask (port 5000)   # Flask API
    ↓
mongo (port 27017)          # MongoDB
qdrant (port 6333)          # 向量資料庫
```

### 各服務詳解

#### 1. 後端 (backend_flask)

```dockerfile
# 基礎映象：Python 3.11 slim
# 工作目錄：/app
# 埠口：5000
# 環境：Flask + LangGraph + RAG
```

**初始化流程**：
1. 自動連接 MongoDB 和 Qdrant
2. 載入 LLM 配置
3. 啟動 LangGraph Agent
4. 監聽 API 請求

#### 2. 前端 (frontend)

```dockerfile
# 構建階段：Node.js 20
# 運行階段：Nginx 1.25
# 埠口：80（映射到 3000）
# 輸出：靜態 React SPA
```

**構建流程**：
1. npm install 依賴
2. npm run build 生成 dist/
3. Nginx 提供靜態資源

#### 3. MongoDB (mongo:6)

```yaml
# 官方 MongoDB 映象
# 埠口：27017
# 卷：./backend_flask/data/mongo:/data/db
```

**用途**：
- 調酒資料庫（6,659 個文檔）
- 用戶帳戶
- 對話歷史

#### 4. Qdrant (qdrant/qdrant)

```yaml
# 官方 Qdrant 映象
# 埠口：6333
# 卷：./backend_flask/data/qdrant:/qdrant/storage
```

**用途**：
- 調酒向量存儲
- 語義搜尋支援
- 場景推薦

### Docker 常用命令

```bash
# 查看容器狀態
docker-compose ps

# 查看日誌
docker-compose logs backend_flask      # 後端日誌
docker-compose logs frontend           # 前端日誌
docker-compose logs -f mongo           # 持續監看 MongoDB

# 進入容器 Shell
docker-compose exec backend_flask bash
docker-compose exec mongo mongosh      # MongoDB Shell

# 重建容器（代碼有改動時）
docker-compose up -d --build

# 只啟動特定服務
docker-compose up -d backend_flask

# 停止特定服務
docker-compose stop mongo

# 重啟服務
docker-compose restart backend_flask

# 查看卷
docker volume ls | grep cocktail

# 檢查容器資源使用
docker stats
```

### 生產部署建議

#### 環境配置

```bash
# 生產環境 .env
FLASK_ENV=production
DEBUG=False
LLM_PROVIDER=gemini
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
```

#### 安全加固

```yaml
# docker-compose.yml
services:
  backend_flask:
    # 限制資源使用
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    
    # 環境變數安全
    environment:
      - FLASK_ENV=production
```

#### 數據備份

```bash
# 備份 MongoDB
docker-compose exec mongo mongodump --out /backup

# 恢復 MongoDB
docker-compose exec mongo mongorestore /backup
```

---

## 🔧 開發指南

### 本地開發工作流

#### 後端開發

```bash
cd backend_flask

# 啟動虛擬環境
# Conda 用戶：
conda activate cocktail_ai

# venv 用戶：
# venv\Scripts\activate

# 開發模式（自動重載）
python run.py

# 執行測試
python test_api.py
python test_langgraph_api.py

# Jupyter 分析
jupyter notebook scripts/cocktail_analysis.ipynb
```

#### 前端開發

```bash
cd frontend

# 開發伺服器（HMR 支援）
npm run dev

# 構建生產版本
npm run build

# 預覽生產版本
npm run preview

# Lint 檢查
npm run lint
```

### 修改 AI 行為

編輯 `backend_flask/app/services/langgraph_agent.py`：

```python
# 系統提示（第 ~50 行）
base_prompt = """
你是一位專業調酒師...
"""

# 工具定義可在 tools.py 修改
```

### 新增調酒資料

```bash
# 1. 準備 JSON 檔案放入 data/diffordsguide/

# 2. 執行導入
cd backend_flask
python scripts/import_diffordsguide.py

# 3. 更新向量（如果使用 RAG）
python setup_rag.py
```

## 📊 資料庫架構

### Cocktails Collection

```javascript
{
  "_id": ObjectId,
  "name": "調酒名稱",
  "category": "分類",
  "difficulty": "easy|medium|hard",
  "image_url": "圖片連結",
  "ratings": {
    "professional": 4.5,
    "public": 4.2,
    "public_count": 156
  },
  "taste_profile": {
    "strength": 7,      // 0-10
    "sweetness": 3      // 0-10
  },
  "ingredients": ["材料1", "材料2"],
  "ingredients_detail": [
    {"amount": "50ml", "ingredient": "材料名"}
  ],
  "method": ["步驟1", "步驟2"],
  "nutrition": {
    "calories": 180
  },
  "alcohol_metrics": {
    "abv": 15.5,
    "standard_drinks": 1.2,
    "proof": 31
  },
  "glass": "杯具名稱",
  "garnish": ["裝飾1"],
  "tags": ["標籤1", "標籤2"],
  "history": ["歷史段落"],
  "review": ["評論"],
  "variants": [{"name": "變化版", "url": "連結"}],
  "detail_url": "原始配方連結"
}
```

### Users Collection

```javascript
{
  "_id": ObjectId,
  "username": "用戶名",
  "email": "email@example.com",
  "password_hash": "bcrypt_hash",
  "preferences": {
    "favorite_spirits": [],
    "disliked_ingredients": []
  },
  "created_at": ISODate
}
```

### Conversations Collection

```javascript
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "title": "對話標題",
  "messages": [
    {
      "role": "user|assistant",
      "content": "訊息內容",
      "timestamp": ISODate
    }
  ],
  "created_at": ISODate,
  "updated_at": ISODate
}
```

---

## 🚨 常見問題

### MongoDB 連接失敗

```
pymongo.errors.ServerSelectionTimeoutError
```

**解決**：

Docker：
```bash
docker-compose restart mongo
docker-compose logs mongo
```

本地（Windows）：
```bash
# 方法 1：使用服務管理器
# Win+R → services.msc → 找到 MongoDB Server → 啟動

# 方法 2：命令列（以系統管理員身分執行）
net start MongoDB
```

### Qdrant 連接失敗

```
Connection refused: localhost:6333
```

**解決**：

```bash
# 檢查容器
docker-compose ps | grep qdrant

# 重啟
docker-compose restart qdrant

# 或手動啟動
docker run -d -p 6333:6333 qdrant/qdrant
```

### LLM 響應超時

**原因**：API 額度耗盡或網路問題

**解決**：
- 檢查 API Key 有效性
- 切換 LLM 提供商（.env 中 `LLM_PROVIDER`）
- 檢查網路連線

### 前端無法連接後端

**原因**：CORS 或 API URL 配置

**解決**：

```bash
# 檢查後端運行（用瀏覽器開啟或使用 PowerShell）
# http://localhost:5000/health

# PowerShell 方式：
# Invoke-WebRequest http://localhost:5000/health

# 檢查前端環境變數
type frontend\.env
# 應該包含：VITE_API_URL=http://localhost:5000
```

### 調酒資料缺失

**原因**：未導入資料

**解決**：

```bash
cd backend_flask

# 檢查資料目錄（Windows）
dir data\diffordsguide\  # 應有 6,659 個 JSON 檔案

# 導入
python scripts/import_diffordsguide.py

# 驗證
python -c "from app.models import db; print(db.cocktails.count_documents({}))"
```

---

## 📊 監控和調試

### 查看應用日誌

```bash
# Docker 環境
docker-compose logs -f backend_flask

# 本地環境
python run.py        # 直接輸出 log
```

### MongoDB 查詢

```bash
# Docker
docker-compose exec mongo mongosh

# 本地
mongosh

# 查詢調酒數
db.cocktails.countDocuments({})

# 查詢用戶數
db.users.countDocuments({})

# 查詢對話數
db.conversations.countDocuments({})
```

### Qdrant 狀態

```bash
# Web 儀表板
http://localhost:6333/dashboard

# API 查詢
curl http://localhost:6333/health
```

## 🤝 貢獻指南

1. **Fork 專案**
2. **建立功能分支**：`git checkout -b feature/amazing-feature`
3. **提交更改**：`git commit -m 'Add amazing feature'`
4. **推送分支**：`git push origin feature/amazing-feature`
5. **開啟 Pull Request**

### 代碼規範

- **Python**：PEP 8（使用 `black` 格式化）
- **TypeScript**：ESLint 配置
- **提交訊息**：使用 conventional commits

---

## 📚 相關資源

- **Flask 文檔**：https://flask.palletsprojects.com/
- **React 文檔**：https://react.dev/
- **LangGraph 文檔**：https://python.langchain.com/docs/langgraph
- **MongoDB 文檔**：https://www.mongodb.com/docs/
- **Docker 文檔**：https://docs.docker.com/
- **Difford's Guide**：https://www.diffordsguide.com/

---

## 📄 授權

本專案採用 **MIT License** - 詳見 [LICENSE](LICENSE) 檔案

---

## 🙋 問題回報

發現 Bug 或有建議？

- 開啟 [GitHub Issue](../../issues)
- 提供錯誤訊息和環境資訊
- 附帶複現步驟

---

## 🎯 升級歷程

### v2.0 - LangGraph 多 LLM 版本（當前）
- ✨ LangGraph Agent 工作流程
- 🔄 多 LLM 支援（Gemini/Groq/OpenAI）
- 📊 完整 RAG 系統（Qdrant）
- 🐳 Docker 容器化部署
- ⚡ 效能提升 66%
- 🧹 代碼最佳化

### v1.0 - 初版
- Flask 基礎應用
- 基本調酒瀏覽
- JWT 認證

---

## 👏 致謝

- **Difford's Guide** - 提供專業調酒資料
- **LangChain/LangGraph** - Agent 工作流程框架
- **Qdrant** - 向量資料庫
- **Groq/Gemini** - LLM 服務

---

**⚠️ 提醒**

本應用包含飲酒相關內容。請理性飲酒，未成年及孕婦請勿飲酒。

**Made with ❤️ and 🍸**

---

## 📞 聯絡方式

- GitHub：[@clairechien0627](https://github.com/clairechien0627)
