# 🍸 AI 調酒大師 - 智能調酒探索平台

一個結合 AI 技術與專業調酒資料庫的全端應用，提供超過 4,600 種調酒配方、智能推薦、進階篩選和互動式對話體驗。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)
![MongoDB](https://img.shields.io/badge/mongodb-6.0+-green.svg)

## ✨ 功能特色

### 🍹 調酒探索
- **6,000+ 專業配方**：來自 Difford's Guide 的完整調酒資料庫
- **進階篩選系統**：根據評分、酒精強度、甜度、卡路里、難度等多維度篩選
- **智能搜尋**：支援調酒名稱、材料、分類搜尋
- **詳細資訊展示**：包含圖片、風味檔案、營養資訊、製作方法、歷史故事等

### 🤖 AI 酒保對話
- **智能推薦**：基於 Groq LLM (llama-3.3-70b) 的個性化推薦
- **互動教學**：詳細的製作步驟和技巧分享
- **情感識別**：根據用戶情緒調整回應
- **對話記憶**：保存完整的對話歷史

### 📊 資料分析
- **視覺化儀表板**：使用 Jupyter Notebook 進行深度資料分析
- **風味地圖**：互動式氣泡圖展示調酒分布
- **統計洞察**：評分趨勢、材料使用頻率、營養分析等

### 🔐 用戶系統
- **JWT 認證**：安全的用戶認證機制
- **個人偏好**：保存用戶的口味偏好
- **對話歷史**：追蹤所有對話記錄

## 🏗️ 技術棧

### 後端
- **Flask 3.0** - Python Web 框架
- **MongoDB** - NoSQL 資料庫 (6,000+ 調酒文檔)
- **Groq API** - LLM 服務 (llama-3.3-70b-versatile)
- **Flask-JWT-Extended** - JWT 認證
- **TextBlob** - 情感分析

### 前端
- **React 18** - UI 框架
- **TypeScript** - 類型安全
- **Vite** - 快速建置工具
- **Tailwind CSS** - 樣式框架
- **Lucide React** - 圖標庫

### 資料分析
- **Jupyter Notebook** - 互動式分析環境
- **Pandas** - 資料處理
- **Plotly** - 互動式視覺化
- **Matplotlib & Seaborn** - 靜態圖表

### 資料來源
- **Difford's Guide** - 6,000+ 專業調酒配方
  - 專業評分 (0-5 星)
  - 公眾評價
  - 風味檔案 (酒精強度 0-10, 甜度 0-10)
  - 難度分級 (easy/medium/hard)
  - 營養資訊 (卡路里)
  - 酒精指標 (ABV, 標準飲酒量, proof)
  - 完整圖片與歷史故事

## 📦 快速開始

### 前置需求

- **Python 3.8+**
- **Node.js 18+** 和 npm
- **MongoDB 6.0+** (本地或 MongoDB Atlas)
- **Groq API Key** (免費註冊：https://console.groq.com)

### 1. 克隆專案

```bash
git clone <repository-url>
cd cocktail_ai
```

### 2. 後端設定

```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 下載 TextBlob 語料庫
python -m textblob.download_corpora

# 設定環境變數
cp .env.example .env
# 編輯 .env 填入您的設定
```

`.env` 範例：
```env
# MongoDB 設定
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=cocktail_ai

# Groq API 設定
GROQ_API_KEY=gsk_your_groq_api_key_here

# Flask 設定
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

FLASK_ENV=development
FLASK_DEBUG=True
```

### 3. 導入調酒資料

確保你有 Difford's Guide 調酒資料（應該在 `data/diffordsguide/` 目錄下）

> 若無，請先從 Google Drive 下載壓縮檔，並解壓縮後放置於指定目錄下：
> https://drive.google.com/file/d/1BtOo_I3SJBxPb3CL7r3219cQ8Hs21wWi/view?usp=sharing

請將含中文翻譯資料放在`data/diffordsguide_trans/` 目錄下
> https://drive.google.com/file/d/18yI-BZJb8UubBKvj7bBCKpI8TkhpS-Bt/view?usp=sharing

請將中英對照表放在`data/trans_table/` 目錄下
> https://drive.google.com/file/d/1_kiZJ5dOQ5eT0YAi9C38kHA8xnYUTEK6/view?usp=sharing


```bash
# 檢查資料目錄
ls data/diffordsguide/  # Mac/Linux
dir data\diffordsguide\  # Windows

# 導入調酒資料到 MongoDB
python scripts/import_diffordsguide.py
python scripts/import_diffordsguide_zh.py
python scripts/import_trans_table.py
```

你應該會看到：

```
總檔案數: 6659
[OK] 成功匯入: 6659
[SKIP] 略過（重複）: 0
[FAIL] 失敗: 0

資料庫調酒總數: 6659
```

### 4. 啟動後端服務

```bash
python run.py
```

服務將在 `http://localhost:5000` 啟動。

### 5. 前端設定與啟動

```bash
# 進入前端目錄
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev
```

前端將在 `http://localhost:5173` 啟動。

### 6. 測試 API

```bash
python test_api.py
```

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

## 🗂️ 專案結構

```
.
├── app/                          # 後端應用
│   ├── __init__.py               # Flask 應用初始化
│   ├── config.py                 # 設定檔
│   ├── models.py                 # MongoDB 資料模型
│   ├── routes/                   # API 路由
│   │   ├── auth.py               # 認證路由
│   │   ├── chat.py               # 對話路由
│   │   └── cocktails.py          # 調酒路由
│   └── services/                 # 服務層
│       ├── llm_service.py        # Groq LLM 服務
│       └── sentiment.py          # 情感分析
│
├── frontend/                     # React 前端
│   ├── src/
│   │   ├── components/           # React 組件
│   │   ├── pages/                # 頁面組件
│   │   │   ├── ChatPage.tsx      # AI 對話頁面
│   │   │   └── CocktailsPage.tsx # 調酒瀏覽頁面
│   │   ├── services/             # API 服務
│   │   ├── types/                # TypeScript 型別
│   │   └── App.tsx               # 主應用
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/                      # 工具腳本
│   ├── import_diffordsguide.py   # 資料導入腳本
│   └── cocktail_analysis.ipynb   # 資料分析筆記本
│
├── data/                         # 資料檔案
│   └── diffordsguide/            # Difford's Guide JSON 檔案
│
├── .env.example                  # 環境變數範例
├── requirements.txt              # Python 依賴
├── test_api.py                   # API 測試腳本
├── run.py                        # 後端啟動檔
├── README.md                     # 專案說明（本檔案）
└── QUICKSTART.md                 # 快速開始指南
```

## 🎯 主要功能展示

### 調酒瀏覽頁面

- **多維度篩選**：評分、酒精強度、甜度、卡路里、難度
- **分類瀏覽**：17 個調酒分類
- **搜尋功能**：名稱、材料快速搜尋
- **排序選項**：名稱、評分、強度、卡路里、受歡迎度
- **分頁支援**：每頁 20 筆，流暢載入

### 調酒詳情模態框

10 個資訊區塊：
1. 專業/公眾評分與星級顯示
2. 風味檔案（酒精強度、甜度進度條）
3. 詳細材料清單（含份量）
4. 製作方法步驟
5. 營養與酒精資訊
6. 建議杯具
7. 歷史故事
8. 專業評論
9. 相關變化版本
10. 過敏原警告

### AI 酒保對話

- **專業知識**：基於 6,000+ 調酒資料庫
- **個性化推薦**：考慮評分、難度、風味偏好
- **情感識別**：TextBlob 情感分析
- **對話記憶**：完整上下文理解
- **責任飲酒**：自動識別並提醒

### 資料分析儀表板

Jupyter Notebook 包含：
- 基本統計（unique items 分析）
- 評分系統分析
- 風味聚合氣泡圖（酒精強度 vs 甜度）
- 難度與複雜度分析
- 營養與酒精指標
- 分類、標籤、材料分析
- WordCloud 視覺化

## 🔧 開發指南

### 後端開發

```bash
# 啟動開發模式
python run.py

# 執行測試
python test_api.py

# 資料分析
jupyter notebook scripts/cocktail_analysis.ipynb
```

### 前端開發

```bash
cd frontend

# 安裝依賴
npm install

# 開發模式
npm run dev

# 建置生產版本
npm run build

# 預覽生產版本
npm run preview
```

### 修改 AI 系統提示

編輯 `app/services/llm_service.py` 中的 `base_prompt` 來自訂 AI 酒保的行為。

### 新增調酒資料

1. 準備 JSON 格式資料（參考 `data/diffordsguide/` 格式）
2. 修改 `scripts/import_diffordsguide.py`
3. 執行導入腳本

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

## 🚀 部署

### Docker 部署（推薦）

```bash
# 建置並啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

### 傳統部署

**後端**：
```bash
# 使用 gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

**前端**：
```bash
cd frontend
npm run build
# 將 dist/ 目錄部署到靜態伺服器
```

## 📝 注意事項

1. **Groq API Key**：
   - 到 https://console.groq.com 免費註冊
   - 每月有免費額度限制
   - 使用 llama-3.3-70b-versatile 模型

2. **MongoDB**：
   - 本地安裝或使用 MongoDB Atlas 免費層
   - 資料庫大小約 500MB（6,000+ 調酒）

3. **責任飲酒**：
   - 本應用包含飲酒相關內容
   - 請理性飲酒，未成年請勿飲酒
   - AI 會自動識別過量飲酒風險

4. **資料來源**：
   - 調酒資料來自 Difford's Guide
   - 圖片連結指向 Difford's CDN
   - 僅供學習和參考用途

## 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT License - 詳見 [LICENSE](LICENSE) 檔案

## 🙋 問題回報

如有任何問題或建議，請：
- 開啟 [GitHub Issue](issues)
- 或聯繫開發者

## 🎉 致謝

- [Difford's Guide](https://www.diffordsguide.com/) - 提供專業調酒資料
- [Groq](https://groq.com/) - 提供快速的 LLM API
- [IBA](https://iba-world.com/) - 國際調酒標準

---

**⚠️ 理性飲酒，過量有害健康。飲酒後請勿駕駛。**

**Made with ❤️ and 🍸**
