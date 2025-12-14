# 🍸 AI 調酒大師 - 智能調酒探索平台

一個結合 AI 技術與專業調酒資料庫的全端應用，提供超過 6,659 種調酒配方、智能推薦、進階篩選和互動式對話體驗。採用 **LangGraph** 多 LLM 架構，打造專業的 AI 調酒師 Agent。

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-19-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![MongoDB](https://img.shields.io/badge/mongodb-6.0+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-orange.svg)

## ✨ 核心功能

### 🍹 調酒探索
- **6,659 專業配方**：來自 Difford's Guide 的完整調酒資料庫
- **進階篩選系統**：根據評分、酒精強度、甜度、卡路里、難度等多維度篩選
- **智能搜尋**：支援調酒名稱、材料、分類、語義搜尋
- **詳細資訊展示**：圖片、風味檔案、營養資訊、製作方法、歷史故事、變化版本

### 🤖 AI 酒保對話（LangGraph 驅動）
- **多 LLM 支援**：Gemini 2.5、Groq (Llama 3)、OpenAI (GPT-4o) 可自由切換
- **智能 Agent 工作流程**：使用 LangGraph 編排，具備 7 個專業工具（搜尋、篩選、RAG 等）
- **完整 RAG 系統**：Qdrant 向量資料庫支援語義搜尋（如「酸酸甜甜的調酒」）
- **個性化推薦**：基於用戶偏好（口味、禁忌材料）與上下文的智能推薦
- **情感分析**：根據用戶情緒調整回應風格
- **對話記憶**：完整的對話歷史追蹤與上下文理解

### 📊 資料分析
- **Jupyter Notebook**：深度資料分析與可視化 (`scripts/cocktail_analysis.ipynb`)
- **統計洞察**：評分分布、材料頻率、營養指標、風味聚類

### 🔐 用戶系統
- **JWT 認證**：基於 Token 的安全認證
- **個人偏好管理**：保存口味偏好、性格設定和禁忌材料
- **收藏與紀錄**：調酒收藏、飲酒紀錄追蹤

## 🏗️ 技術棧

### 後端 (`backend_flask/`)
- **框架**: Flask 3.1
- **Agent**: LangGraph, LangChain
- **LLM**: Gemini Pro, Groq, OpenAI
- **資料庫**: MongoDB (主要資料), Qdrant (向量搜尋)
- **認證**: Flask-JWT-Extended
- **工具**: TextBlob (情感分析), Pandas (資料處理)

### 前端 (`frontend/`)
- **框架**: React 19
- **構建**: Vite
- **語言**: TypeScript
- **樣式**: Tailwind CSS, Lucide React
- **路由**: React Router v7
- **HTTP**: Axios

## 📂 專案架構

```
cocktail_ai/
├── backend_flask/               # Flask 後端
│   ├── app/
│   │   ├── routes/              # API 路由 (Chat, Auth, Cocktails...)
│   │   ├── services/            # 業務邏輯 (LangGraph Agent, RAG...)
│   │   ├── models.py            # MongoDB 模型
│   │   └── ...
│   ├── scripts/                 # 後端專用腳本 (setup_rag.py)
│   ├── qdrant_storage/          # 向量資料庫儲存位置
│   ├── run.py                   # 啟動入口
│   └── requirements.txt         # Python 依賴
├── frontend/                    # React 前端
│   ├── src/                     # 原始碼
│   ├── public/                  # 靜態資源
│   └── ...
├── data/                        # 資料檔案 (Difford's Guide JSON)
│   ├── diffordsguide/           # 原始英文資料
│   ├── diffordsguide_trans/     # 中文翻譯資料
│   └── ...
├── scripts/                     # 專案通用腳本 (資料匯入、分析)
│   ├── import_diffordsguide.py  # 主要資料匯入腳本
│   └── ...
└── README.md
```

## 📦 快速開始 (Local Development)

### 1. 環境準備

確保已安裝：
- Python 3.11+
- Node.js 20+
- MongoDB 6.0+ (本地服務或 Atlas)

### 2. 資料庫初始化與資料下載 (重要 ⭐)

在執行專案前，**必須先下載調酒資料集**並放入對應目錄：

1. **英文資料 (Difford's Guide)**
   - 下載連結：[Google Drive](https://drive.google.com/file/d/1BtOo_I3SJBxPb3CL7r3219cQ8Hs21wWi/view?usp=sharing)
   - 存放位置：請將 JSON 檔案解壓/放入 `data/diffordsguide/` 目錄下

2. **中文翻譯資料**
   - 下載連結：[Google Drive](https://drive.google.com/file/d/1Igv9_FXqcH2RJrXPro9Eu_xyU19-VGQL/view?usp=sharing)
   - 存放位置：請將檔案放入 `data/diffordsguide_trans/` 目錄下

3. **中英對照表**
   - 下載連結：[Google Drive](https://drive.google.com/file/d/1JMI5h3AmKuMqdfXYNLcs2mkqp4ZG-q3L/view?usp=sharing)
   - 存放位置：請將檔案放入 `data/trans_table/` 目錄下 (注意目錄名稱可能為 `trans_tables`，請依實際目錄為準)

**啟動 MongoDB 服務**：
- **Windows (透過服務管理器)**:
    1.  按下 `Win + R` 鍵，輸入 `services.msc` 並按下 Enter。
    2.  在服務列表中找到 `MongoDB Server`。
    3.  右鍵點擊 `MongoDB Server`，選擇「啟動」。
- **Windows (透過命令列)**:
    1.  以「管理員身份」開啟命令提示字元 (CMD) 或 PowerShell。
    2.  輸入 `net start MongoDB` 並按下 Enter。

### 3. 後端與環境變數設定

```bash
# 進入後端目錄
cd backend_flask

# 建立虛擬環境 (選擇一種方式)
# === 選項 A：使用 Conda (推薦) ===
# 建立 conda 虛擬環境
conda create -n cocktail_ai python=3.11
# 啟動虛擬環境
conda activate cocktail_ai

# === 選項 B：使用 venv ===
# python -m venv venv
# # Windows:
# venv\Scripts\activate
# # Mac/Linux:
# # source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 下載 TextBlob 語料庫 (情感分析用)
python -m textblob.download_corpora

# 設定環境變數 (backend_flask/.env)
cp .env.example .env
# 編輯 .env 填入 API Keys (Gemini/Groq) 和 MongoDB URI

# 重要：複製一份 .env 到專案根目錄，供資料匯入腳本使用
cd ..
cp backend_flask/.env .env
```

### 4. 匯入資料與 RAG 初始化

確保 MongoDB 服務已啟動，且資料已放入步驟 2 指定的目錄中。

```bash
# 回到專案根目錄
# 1. 匯入調酒資料
python scripts/import_diffordsguide.py
python scripts/import_diffordsguide_zh.py
python scripts/import_trans_table.py

# 2. 初始化 RAG 向量資料庫 (需先設定好 Qdrant)
# 若使用本地 Qdrant Docker: docker run -d -p 6333:6333 qdrant/qdrant
python backend_flask/scripts/setup_rag.py
```

### 5. 啟動後端

```bash
cd backend_flask
python run.py
# 伺服器將在 http://localhost:5000 啟動
```

### 6. 前端設定

開啟新的終端機視窗：

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev
# 應用將在 http://localhost:5173 啟動
```

## 📡 API 文檔摘要

### 認證 (`/api/auth`)
- `POST /register`: 用戶註冊
- `POST /login`: 用戶登入

### 調酒 (`/api/cocktails`)
- `GET /`: 列表與篩選
- `GET /search`: 關鍵字搜尋
- `GET /<id>`: 詳細資訊

### AI 對話 (`/api/chat`)
- `POST /message`: 發送訊息 (LangGraph Agent)
  - 支援自動工具調用 (RAG, 篩選, 隨機推薦)
  - 回傳包含 `message`, `cocktails` (推薦卡片), `sentiment`

## 🐳 Docker 部署

專案包含 `Dockerfile`，可自行構建映像檔：

- **Backend**: `backend_flask/Dockerfile`
- **Frontend**: `frontend/Dockerfile`

若需使用 Docker Compose，請確保根目錄有 `docker-compose.yml` 配置文件。

## 🤝 貢獻

歡迎提交 Pull Request 或回報 Issue。

## 📄 授權

MIT License
