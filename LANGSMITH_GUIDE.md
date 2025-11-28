# LangSmith 整合指南

## 概述

LangSmith 已成功整合到 AI 調酒大師專案中，提供完整的對話流程追蹤和監控功能。

## 整合內容

### 1. 追蹤範圍

已實現完整對話流程追蹤，包括：

- **LLM 呼叫追蹤** (`app/services/llm_service.py`)
  - `get_bartender_response()` - AI 酒保回應生成
  - `analyze_sentiment_with_llm()` - LLM 情感分析

- **對話流程追蹤** (`app/routes/chat.py`)
  - `process_chat_message()` - 完整對話處理流程
  - `query_cocktails_from_db()` - 資料庫調酒查詢

### 2. 追蹤元數據

每次對話都會記錄：
- 用戶 ID
- 情感分數
- 推薦調酒數量
- 對話長度
- 是否觸發警告
- 系統提示詞內容
- 對話歷史

## 使用方法

### 1. 環境配置

已在 `.env` 檔案中配置：

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=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
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=cocktail_ai
```

### 2. 啟用/停用追蹤

修改 `.env` 檔案中的 `LANGSMITH_TRACING` 值：

```env
# 啟用追蹤
LANGSMITH_TRACING=true

# 停用追蹤
LANGSMITH_TRACING=false
```

### 3. 測試整合

運行測試腳本：

```bash
python test_langsmith.py
```

應該看到所有測試通過：

```
✓ 通過: 配置測試
✓ 通過: 導入測試
✓ 通過: 應用初始化測試
✓ 通過: LLM 服務測試

總計: 4/4 測試通過
🎉 所有測試通過！LangSmith 整合成功！
```

### 4. 啟動應用

```bash
python run.py
```

啟動時會看到：

```
✓ MongoDB 連接成功
✓ Groq LLM 服務初始化成功
✓ LangSmith 追蹤已啟用
```

## 查看追蹤資料

### 1. 前往 LangSmith Dashboard

訪問：https://smith.langchain.com

### 2. 登入帳號

使用您的 LangSmith 帳號登入

### 3. 選擇專案

在 Dashboard 中選擇 `cocktail_ai` 專案

### 4. 查看追蹤資料

您可以看到：

#### 對話追蹤 (Traces)
- 每次對話的完整流程
- 各步驟的執行時間
- 輸入/輸出內容
- 錯誤和異常

#### 關鍵指標
- **延遲 (Latency)**: 各步驟執行時間
- **Token 使用量**: LLM 呼叫的 token 數量
- **成本**: API 呼叫成本（如果配置）
- **成功率**: API 呼叫成功/失敗比例

#### 追蹤層級結構

```
process_chat_message (完整對話流程)
├── query_cocktails_from_db (資料庫查詢)
└── get_bartender_response (LLM 回應生成)
```

## 實際應用

### 1. 對話品質監控

在 LangSmith Dashboard 中：
- 查看 AI 回應內容
- 檢查是否有不當回應
- 分析用戶滿意度

### 2. 性能優化

監控各步驟耗時：
- LLM 呼叫延遲
- 資料庫查詢效率
- 完整對話處理時間

### 3. 錯誤追蹤

快速定位問題：
- API 錯誤
- 資料庫連接問題
- 異常情況

### 4. 成本控制

追蹤 API 使用量：
- Token 消耗統計
- 高頻用戶識別
- 成本預測

## 追蹤資料範例

### 典型對話追蹤

```
Trace ID: abc123xyz
Duration: 1.2s

└── process_chat_message (1.2s)
    ├── Input:
    │   ├── user_message: "推薦一款威士忌調酒"
    │   ├── user_id: "user_123"
    │   └── user_preferences: {"skill_level": "beginner"}
    │
    ├── query_cocktails_from_db (0.1s)
    │   ├── Input: "推薦一款威士忌調酒"
    │   └── Output: [
    │       {"name": "Old Fashioned", "rating": 4.8},
    │       {"name": "Whiskey Sour", "rating": 4.6}
    │   ]
    │
    ├── get_bartender_response (1.0s)
    │   ├── Model: llama-3.3-70b-versatile
    │   ├── Tokens: 512 input / 256 output
    │   └── Output: "我推薦您試試 Old Fashioned..."
    │
    └── Output:
        ├── ai_response: "我推薦您試試 Old Fashioned..."
        ├── sentiment_score: 0.8
        ├── recommended_cocktails_count: 2
        └── needs_warning: false
```

## 進階功能

### 1. 自定義標籤

可在程式碼中添加更多元數據：

```python
@traceable(
    name="custom_function",
    metadata={
        "user_type": "premium",
        "feature": "advanced_search"
    }
)
def custom_function():
    pass
```

### 2. A/B 測試

使用不同的追蹤名稱或標籤來區分實驗版本

### 3. 資料集評估

在 LangSmith 中創建測試資料集，進行批量評估

## 注意事項

### 1. 隱私保護

- LangSmith 會記錄所有對話內容
- 確保符合隱私政策
- 避免追蹤敏感用戶資料

### 2. 成本考量

- LangSmith 免費方案有追蹤數量限制
- 監控追蹤量避免超出配額
- 可選擇性啟用追蹤（如僅開發環境）

### 3. 性能影響

- 追蹤會增加少量延遲（通常 < 50ms）
- 在高負載環境下監控性能影響

## 故障排除

### 問題 1: 看不到追蹤資料

**解決方案：**
1. 確認 `.env` 中 `LANGSMITH_TRACING=true`
2. 檢查 API Key 是否正確
3. 確認網路連接正常
4. 查看應用日誌是否有錯誤

### 問題 2: 追蹤不完整

**解決方案：**
1. 確認所有相關函數都添加了 `@traceable` 裝飾器
2. 檢查是否有異常導致追蹤中斷
3. 查看 LangSmith 日誌

### 問題 3: 追蹤延遲高

**解決方案：**
1. 檢查網路連接
2. 考慮使用異步追蹤
3. 減少追蹤的元數據量

## 相關資源

- **LangSmith 文檔**: https://docs.smith.langchain.com
- **LangSmith Dashboard**: https://smith.langchain.com
- **LangChain Python 文檔**: https://python.langchain.com/docs/langsmith

## 總結

LangSmith 整合為 AI 調酒大師專案提供了：

✅ 完整的對話流程可視化
✅ 詳細的性能指標
✅ 錯誤追蹤和除錯能力
✅ 對話品質監控
✅ 成本和使用量分析

開始使用：
1. 啟動應用 `python run.py`
2. 測試對話功能
3. 前往 https://smith.langchain.com 查看追蹤資料

祝您使用愉快！🍸
