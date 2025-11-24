# 🚀 快速開始指南

這份指南將幫助你在 10 分鐘內啟動 AI 調酒大師應用！

## 📋 前置需求檢查

在開始之前，請確認你已安裝：

- [ ] **Python 3.8+** - [下載連結](https://www.python.org/downloads/)
- [ ] **Node.js 18+** 和 npm - [下載連結](https://nodejs.org/)
- [ ] **MongoDB** - 本地安裝或 MongoDB Atlas 帳號
- [ ] **Git** - [下載連結](https://git-scm.com/)

## 第一步：安裝 MongoDB

### 選項 A：本地安裝 MongoDB（推薦測試用）

**Windows:**
1. 下載：https://www.mongodb.com/try/download/community
2. 執行安裝程式，選擇「Complete」安裝
3. 勾選「Install MongoDB as a Service」
4. 完成後，MongoDB 會自動在背景運行

**Mac:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu):**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 選項 B：使用 MongoDB Atlas（推薦生產用）

1. 前往 https://www.mongodb.com/cloud/atlas
2. 註冊免費帳號（選擇 FREE tier）
3. 建立叢集（選擇最近的區域）
4. 設定資料庫用戶（記住帳號密碼）
5. 設定網路存取（選擇「Allow access from anywhere」或你的 IP）
6. 取得連接字串（類似：`mongodb+srv://user:password@cluster.mongodb.net/`）

## 第二步：取得 Groq API Key

1. 前往 https://console.groq.com
2. 使用 Google/GitHub 帳號註冊（完全免費）
3. 點擊左側 **API Keys**
4. 點擊 **Create API Key**
5. 複製 API Key（格式：`gsk_...`）

> 💡 **提示**：Groq 提供免費的 LLM API，速度快且額度充足！

## 第三步：克隆並設定專案

```bash
# 克隆專案
git clone <repository-url>
cd 期末demo

# 安裝 Python 依賴
pip install -r requirements.txt

# 下載 TextBlob 語料庫
python -m textblob.download_corpora
```

如果 `pip install` 遇到問題，請逐個安裝：

```bash
pip install Flask Flask-CORS Flask-JWT-Extended pymongo dnspython groq textblob python-dotenv requests pandas matplotlib seaborn plotly wordcloud scikit-learn jupyter nbformat
```

## 第四步：設定環境變數

複製環境變數範例檔案：

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

用文字編輯器開啟 `.env`，填入你的設定：

```env
# MongoDB 設定
# 本地 MongoDB：
MONGODB_URI=mongodb://localhost:27017/
# 或 MongoDB Atlas：
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

MONGODB_DB=cocktail_db

# Groq API 設定（填入你的 API Key）
GROQ_API_KEY=gsk_your_groq_api_key_here

# Flask 設定（隨機生成字串）
SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-random-jwt-secret-key-here

FLASK_ENV=development
FLASK_DEBUG=True
```

> 💡 **提示**：用 Python 生成隨機密鑰：
> ```python
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

## 第五步：導入調酒資料

確保你有 Difford's Guide 調酒資料（應該在 `data/diffordsguide/` 目錄下）：

```bash
# 檢查資料目錄
ls data/diffordsguide/  # Mac/Linux
dir data\diffordsguide\  # Windows

# 導入調酒資料到 MongoDB
python scripts/import_diffordsguide.py
```

你應該會看到：

```
正在掃描目錄: data/diffordsguide
找到 6659 個 JSON 檔案
成功解析 4606 個調酒
開始導入到 MongoDB...
✓ 成功導入 4606 筆調酒資料
建立索引完成
```

> ⚠️ **注意**：如果沒有 `data/diffordsguide/` 資料夾，請聯繫專案維護者取得資料檔案。

## 第六步：啟動後端服務

```bash
python run.py
```

看到這些訊息表示成功：

```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

> 💡 **提示**：保持這個終端視窗開啟！

## 第七步：測試後端 API

開啟**新的終端視窗**，執行測試腳本：

```bash
python test_api.py
```

你應該會看到各種 API 測試結果。如果全部通過，表示後端運行正常！

或者在瀏覽器中測試：

- http://localhost:5000/health （健康檢查）
- http://localhost:5000/api/cocktails/?limit=5 （取得 5 個調酒）

## 第八步：設定並啟動前端

開啟**新的終端視窗**：

```bash
# 進入前端目錄
cd frontend

# 安裝 npm 依賴
npm install

# 啟動開發伺服器
npm run dev
```

看到這些訊息表示成功：

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

## 第九步：開始使用！

在瀏覽器中開啟 **http://localhost:5173**

你會看到：

1. **導航列**：調酒瀏覽 / AI 對話 / 登入/註冊
2. **首頁**：歡迎訊息
3. **調酒瀏覽**：4,600+ 調酒資料庫
4. **AI 對話**：智能酒保對話（需要先登入）

### 快速測試流程

1. **註冊帳號**：
   - 點擊右上角「註冊」
   - 填寫用戶名、Email、密碼
   - 註冊成功後會自動登入

2. **瀏覽調酒**：
   - 點擊「調酒瀏覽」
   - 使用篩選器：評分、酒精強度、甜度、難度等
   - 點擊任一調酒查看詳細資訊（包含圖片！）

3. **與 AI 對話**：
   - 點擊「AI 對話」
   - 嘗試問：「推薦我一款適合夏天的調酒」
   - 或：「Mojito 怎麼做？」

## ⚠️ 常見問題排除

### 問題 1：`ModuleNotFoundError: No module named 'xxx'`

**解決方案**：
```bash
pip install -r requirements.txt
# 或
pip install <缺少的模組名稱>
```

### 問題 2：MongoDB 連接失敗

**症狀**：
```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 111] Connection refused
```

**解決方案**：

**Windows:**
- 開啟「服務」應用程式（Win+R → `services.msc`）
- 找到「MongoDB Server」，點擊「啟動」

**Mac:**
```bash
brew services start mongodb-community
```

**Linux:**
```bash
sudo systemctl start mongodb
```

**MongoDB Atlas:**
- 檢查 `.env` 中的 `MONGODB_URI` 是否正確
- 確認網路存取設定允許你的 IP

### 問題 3：Groq API 錯誤

**症狀**：AI 對話無法使用

**解決方案**：
1. 檢查 `.env` 中的 `GROQ_API_KEY` 是否正確
2. 到 https://console.groq.com 確認 API Key 有效
3. 檢查是否超過免費額度限制
4. 重新啟動後端：`Ctrl+C` 停止，然後 `python run.py` 重啟

### 問題 4：埠號被佔用

**症狀**：
```
OSError: [Errno 98] Address already in use
```

**解決方案**：

**後端（5000 埠）：**
編輯 `run.py`，更改埠號：
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**前端（5173 埠）：**
編輯 `frontend/vite.config.ts`，更改埠號：
```typescript
server: {
  port: 3000
}
```

### 問題 5：前端無法連接後端

**症狀**：前端顯示網路錯誤

**解決方案**：
1. 確認後端正在運行（http://localhost:5000/health）
2. 檢查前端環境變數：
   - 建立 `frontend/.env` 檔案
   - 添加：`VITE_API_URL=http://localhost:5000`
3. 重新啟動前端

### 問題 6：沒有調酒資料

**症狀**：調酒瀏覽頁面顯示「找不到符合條件的調酒」

**解決方案**：
1. 確認已執行資料導入：`python scripts/import_diffordsguide.py`
2. 檢查 MongoDB 中是否有資料：
   ```bash
   mongosh
   use cocktail_db
   db.cocktails.countDocuments()  # 應該顯示 4606
   ```
3. 如果沒有資料，重新執行導入腳本

### 問題 7：圖片無法顯示

**原因**：Difford's Guide CDN 可能有存取限制

**解決方案**：
- 圖片連結指向 `https://cdn.diffordsguide.com/`
- 如果無法載入，會自動顯示 Wine 圖標佔位符
- 確認網路連線正常

## 📚 下一步學習

### 1. 探索 API 文檔
查看完整的 API 文檔：[README.md](README.md#-api-文檔)

### 2. 自訂 AI 酒保
編輯 `app/services/llm_service.py` 中的系統提示詞，打造專屬的 AI 酒保個性！

### 3. 資料分析
執行 Jupyter Notebook 探索調酒資料：
```bash
jupyter notebook scripts/cocktail_analysis.ipynb
```

### 4. 修改前端樣式
編輯 `frontend/src/` 下的 React 組件，客製化 UI！

### 5. 部署到雲端
- 使用 **Vercel** 部署前端（免費）
- 使用 **Render** 或 **Railway** 部署後端（免費層）
- 使用 **MongoDB Atlas** 作為雲端資料庫（免費）

## 🎓 學習資源

- **Flask 文檔**：https://flask.palletsprojects.com/
- **React 文檔**：https://react.dev/
- **MongoDB 文檔**：https://www.mongodb.com/docs/
- **Groq API 文檔**：https://console.groq.com/docs
- **Difford's Guide**：https://www.diffordsguide.com/

## 💬 需要協助？

如果遇到其他問題：

1. 檢查完整的 [README.md](README.md) 文檔
2. 開啟 GitHub Issue 回報問題
3. 提供錯誤訊息和環境資訊（Python 版本、OS 等）

---

**🎉 恭喜！你已成功設定 AI 調酒大師應用！**

現在開始探索 4,600+ 種調酒，與 AI 酒保聊天吧！🍸

**⚠️ 提醒：理性飲酒，過量有害健康。**
