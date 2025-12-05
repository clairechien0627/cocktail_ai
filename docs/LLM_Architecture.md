# 調酒推薦系統 LLM 運作架構分析

## 目錄
1. [系統架構概覽](#系統架構概覽)
2. [LLM 調用完整流程](#llm-調用完整流程)
3. [核心組件詳解](#核心組件詳解)
4. [Prompt 管理機制](#prompt-管理機制)
5. [不同性格酒保實作評估](#不同性格酒保實作評估)
6. [建議實作方案](#建議實作方案)

---

## 系統架構概覽

### 主要檔案結構

```
backend_flask/app/
├── services/
│   ├── langgraph_agent.py        # LangGraph Agent 核心邏輯 (284行)
│   ├── conversation_manager.py   # 對話管理器 (237行)
│   ├── rag_service.py            # RAG 向量搜尋 (121行)
│   └── tools.py                  # 7個調酒搜尋工具 (320行)
├── routes/
│   └── chat.py                   # Chat API 路由 (288行)
└── __init__.py                   # 應用初始化 (164行)
```

### 技術棧

| 組件 | 技術 | 版本 | 用途 |
|------|------|------|------|
| **Agent 框架** | LangGraph | 1.0.4 | 狀態圖工作流 |
| **LLM 框架** | LangChain | 1.1.0 | LLM 抽象層 |
| **LLM 提供商** | Gemini/Groq/OpenAI | - | 多模型支援 |
| **向量數據庫** | Qdrant | 1.16.1 | RAG 語義搜尋 |
| **Embedding** | Sentence-Transformers | 5.1.2 | 向量編碼 |
| **對話存儲** | MongoDB | - | 歷史記錄 |

---

## LLM 調用完整流程

### 1. 流程圖

```
┌─────────────────────────────────────────────────────────────────┐
│ 使用者訊息                                                      │
│ POST /api/chat/message                                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 情感分析                                                        │
│ analyze_sentiment(user_message)                                 │
│ 返回: sentiment_score (0-1)                                     │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 載入/創建對話                                                   │
│ ConversationManager(db, conversation_id)                        │
│ - 從 MongoDB 載入對話歷史                                       │
│ - 載入上下文 (recommended_cocktails, current_query)            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 保存用戶訊息                                                    │
│ conv_manager.save_message('user', user_message, sentiment_score)│
│ 存入 MongoDB: conversations.messages[]                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 準備對話歷史                                                    │
│ messages = conv_manager.get_messages(as_message_objects=True)   │
│ 轉換為: [HumanMessage, AIMessage, ToolMessage, ...]            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 準備 LangGraph 狀態                                             │
│ BartenderState {                                                │
│   messages: List[Message],         # 對話歷史                  │
│   user_message: str,                # 當前用戶輸入             │
│   conversation_id: str,                                         │
│   user_id: str,                                                 │
│   current_query: dict,              # 累積的查詢參數           │
│   recommended_cocktails: List[str], # 已推薦清單               │
│   last_recommendation: dict,        # 最後推薦的調酒           │
│   response: str,                    # AI 回應（輸出）          │
│   tool_calls: List                  # 工具調用（輸出）         │
│ }                                                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 執行 LangGraph                                                  │
│ result = graph.invoke(state)                                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │ Node 1: agent   │
        │ (call_model)    │
        └────────┬────────┘
                 │
                 │ 1. 選擇 LLM (Gemini/Groq/OpenAI)
                 │ 2. 綁定 7 個工具
                 │ 3. 注入 System Prompt (格式化上下文)
                 │ 4. 呼叫 llm_with_tools.invoke(messages)
                 │
                 ▼
        ┌─────────────────────────────────┐
        │ 返回 AIMessage                  │
        │ - content: str (回應文字)       │
        │ - tool_calls: List (若需要工具) │
        └────────┬────────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────────┐
        │ 條件判斷: should_continue()     │
        │ - 檢查是否有 tool_calls         │
        │ - 檢查是否超過 3 次重複調用     │
        └────────┬────────────────────────┘
                 │
         ┌───────┴───────┐
         │               │
    有工具調用        無工具調用
         │               │
         ▼               ▼
  ┌─────────────┐   ┌────────┐
  │ Node 2:     │   │  END   │
  │ tools       │   └────────┘
  └──────┬──────┘
         │
         │ 執行所有 tool_calls:
         │ - search_by_name
         │ - search_by_ingredients
         │ - filter_by_attributes
         │ - search_by_taste_semantic (RAG)
         │ - search_by_scenario_semantic (RAG)
         │ - search_by_category
         │ - get_random_cocktail
         │
         ▼
  ┌─────────────────────────────────┐
  │ 返回 ToolMessage                │
  │ - content: 工具結果 JSON        │
  │ - tool_call_id: 對應的調用 ID   │
  └──────┬──────────────────────────┘
         │
         │ 循環回到 Node 1 (agent)
         │ LLM 基於工具結果生成最終回應
         │
         ▼
  ┌─────────────────────────────────┐
  │ 再次返回 AIMessage (含文字回應) │
  └──────┬──────────────────────────┘
         │
         └──────────► END

                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 提取 AI 回應                                                    │
│ ai_message = result['messages'][-1]                             │
│ - OpenAI/Groq: content 是字串                                   │
│ - Gemini: content 是 List[dict] (需提取 'text')                 │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 提取工具結果                                                    │
│ tool_results = [msg.content for msg in ToolMessage]             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 更新對話上下文                                                  │
│ conv_manager.update_context(ai_response, tool_results)          │
│ - 提取新推薦的調酒名稱 → recommended_cocktails                 │
│ - 更新 last_recommendation                                      │
│ - 同步到 MongoDB                                                │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 責任飲酒警告檢查                                                │
│ if should_warn_about_drinking(messages):                        │
│     warnings.append("請適度飲酒...")                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 保存 AI 回應                                                    │
│ conv_manager.save_message('assistant', ai_response)             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ 返回 JSON 響應                                                  │
│ {                                                               │
│   "response": ai_response,                                      │
│   "conversation_id": str(conversation_id),                      │
│   "sentiment_score": sentiment_score,                           │
│   "warnings": warnings                                          │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心組件詳解

### 1. LangGraph Agent (`langgraph_agent.py`)

#### 狀態定義

```python
class BartenderState(TypedDict):
    """調酒師 Agent 狀態"""
    # 輸入
    messages: Annotated[List, add]  # 訊息累積（使用 add operator）
    user_message: str
    conversation_id: str
    user_id: str

    # 上下文（多輪對話）
    current_query: dict  # 當前查詢參數（累積）
    recommended_cocktails: List[str]  # 已推薦的調酒
    last_recommendation: dict  # 最後一次推薦

    # 輸出
    response: str
    tool_calls: List
```

#### LLM 選擇邏輯

```python
def get_llm(provider: str = None):
    """選擇 LLM 提供商"""

    # 1. Gemini (預設)
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.7,
            convert_system_message_to_human=True  # Gemini 特殊處理
        )

    # 2. Groq (Llama 3.3 70B)
    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            groq_api_key=os.getenv('GROQ_API_KEY'),
            model_name="llama-3.3-70b-versatile",
            temperature=0.7
        )

    # 3. OpenAI (GPT-4o-mini)
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name="gpt-4o-mini",
            temperature=0.7
        )
```

**配置位置**: `.env` 中的 `LLM_PROVIDER=gemini`

#### 工具綁定

```python
from app.services.tools import ALL_TOOLS

llm = get_llm()
llm_with_tools = llm.bind_tools(ALL_TOOLS)  # 綁定 7 個工具
```

#### Agent 節點 (call_model)

**位置**: `langgraph_agent.py:142-177`

```python
def call_model(state: BartenderState):
    """Agent 節點：呼叫 LLM"""

    messages = state['messages']
    llm = get_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    # 注入 System Prompt (動態格式化上下文)
    system_message = SystemMessage(content=BARTENDER_SYSTEM_PROMPT.format(
        recommended_cocktails=state.get('recommended_cocktails', []),
        current_query=state.get('current_query', {}),
        last_recommendation=state.get('last_recommendation', {}).get('name', 'None')
    ))

    # 組合訊息: [SystemMessage, ...歷史訊息]
    messages_with_system = [system_message] + messages

    # 呼叫 LLM
    response = llm_with_tools.invoke(messages_with_system)

    return {"messages": [response]}  # 累積到 state
```

#### 條件邊 (should_continue)

**位置**: `langgraph_agent.py:180-206`

```python
def should_continue(state: BartenderState):
    """判斷是否需要執行工具"""

    messages = state['messages']
    last_message = messages[-1]

    # 檢查是否有 tool_calls
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return END

    # 防無限循環 (最多 3 次工具調用)
    tool_count = sum(1 for m in messages if isinstance(m, ToolMessage))
    if tool_count >= 3:
        return END

    return "tools"
```

#### 工具節點 (tools)

```python
from langgraph.prebuilt import ToolNode
from app.services.tools import ALL_TOOLS

tool_node = ToolNode(ALL_TOOLS)
```

**執行流程**:
1. 接收 `AIMessage.tool_calls`
2. 執行對應工具函數
3. 返回 `ToolMessage` (包含結果 JSON)
4. 循環回到 `call_model` 節點

#### 圖編譯

**位置**: `langgraph_agent.py:227-261`

```python
workflow = StateGraph(BartenderState)

# 節點
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# 入口點
workflow.set_entry_point("agent")

# 條件邊
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

# 工具執行後返回 agent
workflow.add_edge("tools", "agent")

graph = workflow.compile()
```

---

### 2. 對話管理器 (`conversation_manager.py`)

#### 雙模式支援

```python
class ConversationManager:
    """
    支援兩種模式：
    1. MongoDB 模式：ConversationManager(db, conversation_id)
    2. 內存模式：ConversationManager()
    """

    def __init__(self, db=None, conversation_id=None):
        self.db = db
        self.conversation_id = ObjectId(conversation_id) if isinstance(conversation_id, str) else conversation_id
        self.conversations = {}  # 內存存儲

        # 上下文
        self.context = {
            'current_query': {},
            'recommended_cocktails': [],
            'last_recommendation': {}
        }

        # 如果有 db，載入現有對話
        if self.db is not None and self.conversation_id is not None:
            self.conversation = self._get_or_create_conversation()
            self.context = self.conversation.get('context', self.context)
```

#### 訊息儲存

**位置**: `conversation_manager.py:68-97`

```python
def save_message(self, role: str, content: str, sentiment_score: float = None):
    """儲存訊息到 MongoDB"""

    message = {
        'role': role,  # 'user', 'assistant', 'system', 'tool'
        'content': content,
        'timestamp': datetime.utcnow()
    }

    if sentiment_score is not None:
        message['sentiment_score'] = sentiment_score

    # MongoDB 模式
    if self.db is not None and self.conversation_id is not None:
        self.db.conversations.update_one(
            {'_id': self.conversation_id},
            {
                '$push': {'messages': message},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    # 內存模式
    else:
        self.add_message(message=message)
```

#### 訊息讀取與轉換

**位置**: `conversation_manager.py:99-151`

```python
def get_messages(self, as_message_objects=False, limit=None):
    """獲取對話訊息"""

    # MongoDB 模式
    if self.db is not None and self.conversation_id is not None:
        conversation = self.db.conversations.find_one({'_id': self.conversation_id})
        messages = conversation.get('messages', [])
    # 內存模式
    else:
        messages = self.get_or_create_conversation_memory()

    # 限制數量
    if limit:
        messages = messages[-limit:]

    # 轉換為 LangChain Message 物件
    if as_message_objects:
        return self._convert_to_message_objects(messages)

    return messages

def _convert_to_message_objects(self, messages):
    """轉換字典為 LangChain Message 物件"""
    result = []

    for msg in messages:
        role = msg.get('role', 'user')
        content = msg.get('content', '')

        if role == 'user':
            result.append(HumanMessage(content=content))
        elif role == 'assistant' or role == 'ai':
            result.append(AIMessage(content=content))
        elif role == 'system':
            result.append(SystemMessage(content=content))
        elif role == 'tool':
            result.append(ToolMessage(
                content=content,
                tool_call_id=msg.get('tool_call_id', '')
            ))

    return result
```

#### 上下文更新

**位置**: `conversation_manager.py:186-231`

```python
def update_context(self, ai_response: str = None, tool_results: List = None, **kwargs):
    """更新對話上下文"""

    # 從工具結果中提取調酒名稱
    if tool_results:
        for result in tool_results:
            if isinstance(result, dict) and 'name' in result:
                cocktail_name = result['name']
                # 加入已推薦清單（避免重複）
                if cocktail_name not in self.context['recommended_cocktails']:
                    self.context['recommended_cocktails'].append(cocktail_name)
                self.context['last_recommendation'] = result

    # 限制推薦歷史長度
    if len(self.context['recommended_cocktails']) > 20:
        self.context['recommended_cocktails'] = self.context['recommended_cocktails'][-20:]

    # 更新其他上下文
    for key, value in kwargs.items():
        self.context[key] = value

    # 同步到 MongoDB
    if self.db is not None and self.conversation_id is not None:
        update_dict = {}
        for key, value in self.context.items():
            update_dict[f'context.{key}'] = value

        self.db.conversations.update_one(
            {'_id': self.conversation_id},
            {'$set': update_dict}
        )
```

#### MongoDB 對話結構

```json
{
    "_id": ObjectId("67a1b2c3d4e5f6789abcdef0"),
    "user_id": ObjectId("67a1b2c3d4e5f6789abcdef1"),
    "created_at": "2024-01-01T12:00:00.000Z",
    "updated_at": "2024-01-01T12:05:00.000Z",
    "messages": [
        {
            "role": "user",
            "content": "推薦一款清爽的調酒",
            "sentiment_score": 0.8,
            "timestamp": "2024-01-01T12:00:00.000Z"
        },
        {
            "role": "assistant",
            "content": "我推薦 Mojito，這是一款清爽的古巴經典調酒...",
            "timestamp": "2024-01-01T12:00:05.000Z"
        },
        {
            "role": "user",
            "content": "有沒有更烈一點的？",
            "sentiment_score": 0.6,
            "timestamp": "2024-01-01T12:01:00.000Z"
        },
        {
            "role": "assistant",
            "content": "那我推薦 Negroni，這款調酒酒精濃度較高...",
            "timestamp": "2024-01-01T12:01:05.000Z"
        }
    ],
    "context": {
        "current_query": {
            "taste": "清爽",
            "strength": "烈"
        },
        "recommended_cocktails": ["Mojito", "Negroni"],
        "last_recommendation": {
            "name": "Negroni",
            "rating": 4.5,
            "ingredients": ["Gin", "Campari", "Sweet Vermouth"]
        }
    }
}
```

---

### 3. RAG 服務 (`rag_service.py`)

#### 初始化

**位置**: `rag_service.py:17-29`

```python
def initialize(self, qdrant_host: str, qdrant_port: int, embedding_model: str):
    """初始化 RAG 服務"""

    # Embedding 模型
    self.model = SentenceTransformer(embedding_model)
    # 預設: paraphrase-multilingual-mpnet-base-v2

    # Qdrant 客戶端
    self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)

    # 測試連接
    self.qdrant.get_collections()
    print(f"✓ RAG Service: 使用 Qdrant ({qdrant_host}:{qdrant_port})")
```

#### 口味語義搜尋

**位置**: `rag_service.py:34-59`

```python
def search_by_taste(self, query: str, limit: int = 5, min_score: float = 0.5) -> List[Dict]:
    """使用語義搜尋找口味相似的調酒"""

    # 將查詢文本轉換為向量
    query_vector = self.model.encode(query).tolist()

    # Qdrant 向量搜尋 (新版 API)
    response = self.qdrant.query_points(
        collection_name="cocktails_taste",
        query=query_vector,
        limit=limit
    )

    # 過濾低分結果
    cocktails = []
    for point in response.points:
        if point.score < min_score:
            continue
        item = point.payload.copy()
        item["similarity_score"] = point.score
        cocktails.append(item)

    return cocktails
```

**使用案例**:
- 用戶輸入: "我想要酸酸甜甜的調酒"
- 向量編碼 → Qdrant 搜尋 → 返回相似調酒

#### 場景語義搜尋

**位置**: `rag_service.py:64-88`

```python
def search_by_scenario(self, query: str, limit: int = 5, min_score: float = 0.5) -> List[Dict]:
    """使用語義搜尋找適合情境的調酒"""

    query_vector = self.model.encode(query).tolist()

    response = self.qdrant.query_points(
        collection_name="cocktails_scenario",
        query=query_vector,
        limit=limit
    )

    cocktails = []
    for point in response.points:
        if point.score < min_score:
            continue
        item = point.payload.copy()
        item["similarity_score"] = point.score
        cocktails.append(item)

    return cocktails
```

**使用案例**:
- 用戶輸入: "適合約會的調酒"
- 向量編碼 → Qdrant 搜尋 → 返回適合的調酒

#### Qdrant 集合結構

**兩個集合**:
1. `cocktails_taste` - 口味向量（6,659 筆）
2. `cocktails_scenario` - 場景向量（6,659 筆）

**Vector 維度**: 768 (paraphrase-multilingual-mpnet-base-v2)

---

### 4. 工具系統 (`tools.py`)

#### 工具列表

| 工具名稱 | 函數 | 描述 | 使用時機 |
|---------|------|------|---------|
| `search_by_name` | `search_by_name()` | 根據名稱搜尋調酒 | 用戶問 "How to make Mojito?" |
| `search_by_ingredients` | `search_by_ingredients()` | 根據材料搜尋 | "I have vodka and lime" |
| `filter_by_attributes` | `filter_by_attributes()` | 多維度篩選 | "Easy cocktails" / "Low calorie" |
| `search_by_taste_semantic` | `search_by_taste_semantic()` | RAG 口味搜尋 | "清爽酸甜的" |
| `search_by_scenario_semantic` | `search_by_scenario_semantic()` | RAG 場景搜尋 | "約會用的" |
| `search_by_category` | `search_by_category()` | 分類搜尋 | "Gin cocktails" |
| `get_random_cocktail` | `get_random_cocktail()` | 隨機推薦 | "Surprise me!" |

#### 工具定義範例 (search_by_taste_semantic)

**位置**: `tools.py:213-239`

```python
class SearchByTasteInput(BaseModel):
    """口味語義搜尋輸入"""
    query: str = Field(description="口味描述 (e.g., '清爽酸甜的', 'refreshing and sour')")
    limit: int = Field(default=5, description="返回數量")

@tool(
    "search_by_taste_semantic",
    args_schema=SearchByTasteInput,
    description="""Use AI semantic search to find cocktails based on taste descriptions.
    Use this when the user describes taste preferences with adjectives
    (e.g., 'refreshing and sour', 'strong and bitter', 'sweet and fruity').
    This tool uses RAG (Retrieval Augmented Generation) with vector similarity search."""
)
def search_by_taste_semantic(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """使用 AI 語義搜尋根據口味描述找調酒"""
    from app.services.rag_service import rag_service

    try:
        results = rag_service.search_by_taste(query, limit=limit)
        return results
    except Exception as e:
        return [{
            "error": f"RAG search failed: {str(e)}",
            "suggestion": "Please try search_by_ingredients or filter_by_attributes instead"
        }]
```

#### 工具綁定機制

**位置**: `tools.py:312-320`

```python
ALL_TOOLS = [
    search_by_name,
    search_by_ingredients,
    filter_by_attributes,
    search_by_taste_semantic,
    search_by_scenario_semantic,
    search_by_category,
    get_random_cocktail
]

# 在 langgraph_agent.py 中綁定
llm_with_tools = llm.bind_tools(ALL_TOOLS)
```

**LangChain 會自動**:
1. 將工具轉換為 OpenAI Function Calling 格式
2. 傳遞給 LLM
3. LLM 根據工具描述決定是否調用
4. 返回 `tool_calls` 結構

---

### 5. Chat API (`routes/chat.py`)

#### 完整流程

**位置**: `chat.py:82-275`

```python
@chat_bp.route('/message', methods=['POST'])
@jwt_required()
def send_message():
    """發送訊息並獲取 AI 回應"""

    # 1. 驗證輸入
    data = request.get_json()
    user_message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')

    # 2. 獲取用戶 ID
    current_user_id = get_jwt_identity()
    user_id = ObjectId(current_user_id)

    # 3. 情感分析
    sentiment_score = analyze_sentiment(user_message)

    # 4. 建立/載入對話
    if not conversation_id:
        conversation_id = ObjectId()

    conv_manager = ConversationManager(db, conversation_id)

    # 5. 保存用戶訊息
    conv_manager.save_message('user', user_message, sentiment_score)

    # 6. 獲取對話歷史
    messages = conv_manager.get_messages(as_message_objects=True)

    # 7. 準備 LangGraph 狀態
    state = {
        'messages': messages,
        'user_message': user_message,
        'conversation_id': str(conversation_id),
        'user_id': str(user_id),
        'current_query': conv_manager.context.get('current_query', {}),
        'recommended_cocktails': conv_manager.context.get('recommended_cocktails', []),
        'last_recommendation': conv_manager.context.get('last_recommendation', {}),
        'response': '',
        'tool_calls': []
    }

    # 8. 執行 LangGraph
    from app.services.langgraph_agent import graph
    result = graph.invoke(state)

    # 9. 提取 AI 回應
    ai_message = result['messages'][-1]

    # 處理不同 LLM 格式
    if isinstance(ai_message.content, str):
        ai_response = ai_message.content  # OpenAI/Groq
    elif isinstance(ai_message.content, list):
        # Gemini 格式: [{'text': '...'}]
        ai_response = ' '.join([
            block.get('text', '')
            for block in ai_message.content
            if isinstance(block, dict)
        ])

    # 10. 提取工具結果
    tool_results = []
    for msg in result['messages']:
        if isinstance(msg, ToolMessage):
            try:
                tool_results.append(json.loads(msg.content))
            except:
                pass

    # 11. 更新上下文
    conv_manager.update_context(ai_response, tool_results)

    # 12. 責任飲酒警告
    warnings = []
    if should_warn_about_drinking(result['messages']):
        warnings.append("請適度飲酒，過量有害健康。")

    # 13. 保存 AI 回應
    conv_manager.save_message('assistant', ai_response)

    # 14. 返回響應
    return jsonify({
        'response': ai_response,
        'conversation_id': str(conversation_id),
        'sentiment_score': sentiment_score,
        'warnings': warnings
    }), 200
```

---

## Prompt 管理機制

### 當前 System Prompt

**位置**: `langgraph_agent.py:43-93`

```python
BARTENDER_SYSTEM_PROMPT = """你是一位專業且友善的 AI 調酒師「調酒大師」。

🍸 你的資料庫：
- 包含 6,659 款專業調酒配方（來自 Difford's Guide）
- 每款都有評分、難度、風味檔案、材料、製作步驟

🛠️ 你的工具（可以使用多個工具）：
1. search_by_name - 根據名稱搜尋
2. search_by_ingredients - 根據材料搜尋
3. filter_by_attributes - 多維度篩選（強度、甜度、難度、卡路里等）
4. search_by_taste_semantic - 口味語義搜尋（RAG，如"酸酸甜甜的"）
5. search_by_scenario_semantic - 場景語義搜尋（RAG，如"慶祝用的"）
6. search_by_category - 根據分類搜尋
7. get_random_cocktail - 隨機推薦

📋 判斷原則：
✅ 用戶想找特定調酒 → 使用 search_by_name
✅ 用戶提到材料 → 使用 search_by_ingredients
✅ 用戶描述口味 → 使用 search_by_taste_semantic（RAG）
✅ 用戶提到場景/情緒 → 使用 search_by_scenario_semantic（RAG）
✅ 用戶提到特定條件（難度、卡路里等）→ 使用 filter_by_attributes
✅ 用戶說"隨便"、"驚喜" → 使用 get_random_cocktail
❌ 用戶閒聊、問候、分享心情 → 不用工具，直接回應

🎯 回應原則：
1. 使用繁體中文
2. 保持友善、專業的酒保語氣
3. **如果使用了工具，必須基於查詢結果回答，絕對不能沉默或回應空白**
4. **如果工具返回了調酒資料，你必須介紹調酒的名稱、特色、材料和做法**
5. 推薦時提供：名稱、評分、風味特徵、材料、製作方法

當前對話上下文：
- 已推薦過: {recommended_cocktails}
- 當前查詢參數: {current_query}
- 最後推薦: {last_recommendation}
"""
```

### Prompt 注入點

**位置**: `langgraph_agent.py:152-157`

```python
def call_model(state: BartenderState):
    """Agent 節點：呼叫 LLM"""

    # 格式化 System Prompt（動態注入上下文）
    system_message = SystemMessage(content=BARTENDER_SYSTEM_PROMPT.format(
        recommended_cocktails=state.get('recommended_cocktails', []),
        current_query=state.get('current_query', {}),
        last_recommendation=state.get('last_recommendation', {}).get('name', 'None')
    ))

    # 組合訊息
    messages_with_system = [system_message] + state['messages']

    # 呼叫 LLM
    response = llm_with_tools.invoke(messages_with_system)

    return {"messages": [response]}
```

### Prompt 結構分析

當前 Prompt 長度: **約 500 tokens**

**組成部分**:
1. **角色定義** (50 tokens): "你是一位專業且友善的 AI 調酒師..."
2. **資料庫說明** (80 tokens): "包含 6,659 款專業調酒配方..."
3. **工具列表** (150 tokens): 7 個工具的名稱和用途
4. **判斷原則** (120 tokens): 何時使用哪個工具
5. **回應原則** (80 tokens): 語氣、語言、格式要求
6. **動態上下文** (20 tokens): 已推薦調酒、當前查詢、最後推薦

---

## 不同性格酒保實作評估

### 評估維度

| 維度 | 考量因素 | 影響 |
|------|---------|------|
| **Prompt 長度** | 每種性格需額外描述 | Token 成本增加 |
| **性格一致性** | 是否能穩定保持角色 | 用戶體驗 |
| **管理複雜度** | 多個 Prompt 的維護成本 | 開發維護成本 |
| **用戶自訂** | 是否支援自訂性格 | 功能彈性 |
| **切換流暢性** | 切換性格時的對話連貫性 | 技術挑戰 |

### 方案 1: 單一 Prompt + 性格參數（動態注入）

#### 實作方式

```python
PERSONALITY_TRAITS = {
    "professional": {
        "tone": "專業、正式",
        "style": "使用專業術語，詳細說明材料比例和製作技巧",
        "greeting": "您好，我是您的專業調酒顧問。",
        "example": "這款 Negroni 採用經典 1:1:1 比例，建議使用 London Dry Gin..."
    },
    "friendly": {
        "tone": "友善、輕鬆",
        "style": "使用日常用語，分享調酒故事和趣聞",
        "greeting": "嗨！今天想喝點什麼呢？",
        "example": "Mojito 是夏天的最佳選擇！清爽的薄荷搭配萊姆，簡直完美～"
    },
    "humorous": {
        "tone": "幽默、俏皮",
        "style": "使用雙關語、笑話，讓推薦過程有趣",
        "greeting": "歡迎光臨！今天要來點「液體快樂」嗎？😄",
        "example": "Old Fashioned？老派？不不不，這叫「經典永不退流行」！"
    },
    "romantic": {
        "tone": "浪漫、優雅",
        "style": "強調氛圍、情感連結，使用詩意語言",
        "greeting": "晚安，讓我為您調製一杯浪漫時光。",
        "example": "French 75 如同巴黎的夜晚，優雅而迷人，氣泡在杯中如繁星閃爍..."
    },
    "minimalist": {
        "tone": "簡潔、直接",
        "style": "只提供必要資訊，不贅述",
        "greeting": "需要推薦嗎？",
        "example": "Daiquiri: Rum 60ml, 萊姆汁 20ml, 糖漿 15ml. 搖勻."
    }
}

BARTENDER_SYSTEM_PROMPT_TEMPLATE = """你是一位 AI 調酒師「調酒大師」。

🎭 性格設定：
- 語氣：{tone}
- 風格：{style}
- 打招呼範例：{greeting}
- 回應範例：{example}

🍸 你的資料庫：
[... 原有內容 ...]

🛠️ 你的工具：
[... 原有內容 ...]

🎯 回應原則：
1. **嚴格遵守上述性格設定**
2. 使用繁體中文
3. 保持性格一致性
[... 其他原則 ...]

當前對話上下文：
- 已推薦過: {recommended_cocktails}
- 當前查詢參數: {current_query}
- 最後推薦: {last_recommendation}
"""
```

#### 注入流程

```python
def call_model(state: BartenderState):
    """Agent 節點：呼叫 LLM（支援性格）"""

    # 獲取性格設定
    personality = state.get('personality', 'friendly')  # 預設友善
    traits = PERSONALITY_TRAITS.get(personality, PERSONALITY_TRAITS['friendly'])

    # 格式化 System Prompt
    system_message = SystemMessage(content=BARTENDER_SYSTEM_PROMPT_TEMPLATE.format(
        tone=traits['tone'],
        style=traits['style'],
        greeting=traits['greeting'],
        example=traits['example'],
        recommended_cocktails=state.get('recommended_cocktails', []),
        current_query=state.get('current_query', {}),
        last_recommendation=state.get('last_recommendation', {}).get('name', 'None')
    ))

    messages_with_system = [system_message] + state['messages']
    response = llm_with_tools.invoke(messages_with_system)

    return {"messages": [response]}
```

#### 優點 ✅
- **統一管理**: 所有性格在一個檔案中
- **易於擴展**: 新增性格只需添加字典條目
- **Prompt 長度可控**: 每次只注入一種性格（約 +100 tokens）
- **切換靈活**: 同一對話可切換性格（技術上）

#### 缺點 ❌
- **性格描述有限**: 短文本可能不足以完全定義複雜性格
- **LLM 理解依賴**: 需要 LLM 準確理解並執行性格指令
- **一致性挑戰**: 長對話中可能偏離性格設定

---

### 方案 2: 獨立 Prompt 檔案（多版本）

#### 實作方式

**檔案結構**:
```
backend_flask/app/prompts/
├── base_bartender.txt              # 基礎 Prompt（工具、原則）
├── personality_professional.txt    # 專業性格
├── personality_friendly.txt        # 友善性格
├── personality_humorous.txt        # 幽默性格
├── personality_romantic.txt        # 浪漫性格
└── personality_minimalist.txt      # 簡約性格
```

**範例 - `personality_humorous.txt`**:
```
你是一位幽默風趣的 AI 調酒師「調酒大師」，擁有以下特質：

🎭 性格核心：
- 你喜歡用雙關語和俏皮話，但絕不低俗
- 每次推薦都會加入一個小笑話或有趣的調酒冷知識
- 你認為調酒是「液體藝術」和「可以喝的快樂」
- 面對嚴肅的酒保術語，你總能找到輕鬆的詮釋方式

💬 說話風格：
- 使用表情符號（😄🍹✨）讓對話更生動
- 常用語：「來點液體快樂」、「這杯酒的笑點在於...」、「調酒界的諧星」
- 對經典調酒會開玩笑：「Old Fashioned 不老，只是很有經驗」
- 推薦時會說：「如果這杯酒有個性，它肯定是派對之王」

📚 知識風格：
- 分享調酒歷史時加入趣聞：「你知道 Martini 的發明人可能是個酒鬼嗎？因為他忘了自己發明的！」
- 材料介紹會用比喻：「琴酒就像調酒界的萬用演員，什麼角色都能演」
- 技巧說明輕鬆化：「搖酒器要搖到手酸，然後再搖一下，這樣才夠冰！」

❌ 禁止行為：
- 不使用低俗或冒犯性笑話
- 不嘲笑用戶的選擇或品味
- 不過度玩笑導致忽略專業建議
- 酒精相關警告仍需嚴肅對待

[... 接上 base_bartender.txt 的工具和原則 ...]
```

**載入邏輯**:
```python
import os

def load_prompt(personality: str = "friendly") -> str:
    """載入對應性格的 Prompt"""

    prompt_dir = os.path.join(os.path.dirname(__file__), 'prompts')

    # 載入基礎 Prompt
    with open(os.path.join(prompt_dir, 'base_bartender.txt'), 'r', encoding='utf-8') as f:
        base_prompt = f.read()

    # 載入性格 Prompt
    personality_file = f'personality_{personality}.txt'
    personality_path = os.path.join(prompt_dir, personality_file)

    if os.path.exists(personality_path):
        with open(personality_path, 'r', encoding='utf-8') as f:
            personality_prompt = f.read()
    else:
        # 預設使用友善性格
        with open(os.path.join(prompt_dir, 'personality_friendly.txt'), 'r', encoding='utf-8') as f:
            personality_prompt = f.read()

    # 合併 Prompt
    full_prompt = f"{personality_prompt}\n\n{base_prompt}"

    return full_prompt

def call_model(state: BartenderState):
    """Agent 節點：呼叫 LLM（檔案版）"""

    personality = state.get('personality', 'friendly')
    prompt_template = load_prompt(personality)

    # 格式化上下文
    system_content = prompt_template.format(
        recommended_cocktails=state.get('recommended_cocktails', []),
        current_query=state.get('current_query', {}),
        last_recommendation=state.get('last_recommendation', {}).get('name', 'None')
    )

    system_message = SystemMessage(content=system_content)
    messages_with_system = [system_message] + state['messages']
    response = llm_with_tools.invoke(messages_with_system)

    return {"messages": [response]}
```

#### 優點 ✅
- **詳細性格描述**: 每種性格可用 500+ tokens 詳細定義
- **易於編輯**: 非技術人員也能修改文本檔案
- **版本控制友善**: Git 可追蹤每個性格的變更
- **性格一致性強**: 更多上下文 = LLM 更容易保持角色

#### 缺點 ❌
- **Prompt 長度增加**: 每種性格 800-1000 tokens（基礎 500 + 性格 300-500）
- **檔案管理**: 需維護多個檔案
- **重複內容**: 基礎部分需在多個檔案中引用或複製

---

### 方案 3: 資料庫存儲 Prompt（支援用戶自訂）

#### 實作方式

**MongoDB Schema**:
```json
{
    "_id": ObjectId("..."),
    "type": "system",  // 系統預設
    "personality_id": "friendly",
    "name": "友善酒保",
    "description": "輕鬆友善，適合日常聊天",
    "prompt": {
        "tone": "友善、輕鬆",
        "style": "使用日常用語，分享調酒故事和趣聞",
        "greeting": "嗨！今天想喝點什麼呢？",
        "example_responses": [
            "Mojito 是夏天的最佳選擇！清爽的薄荷搭配萊姆，簡直完美～",
            "這款調酒的故事很有趣呢！據說是海明威在古巴最愛的飲品..."
        ],
        "forbidden": ["過於正式的用語", "冷淡的回應"],
        "encouraged": ["分享趣聞", "使用輕鬆語氣", "適度使用表情符號"]
    },
    "icon": "😊",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}

// 用戶自訂性格
{
    "_id": ObjectId("..."),
    "type": "custom",  // 用戶自訂
    "personality_id": "custom_67a1b2c3d4e5f6789abcdef0",
    "user_id": ObjectId("67a1b2c3d4e5f6789abcdef1"),
    "name": "我的專屬酒保",
    "description": "結合專業和幽默的風格",
    "prompt": {
        "tone": "專業但不失幽默",
        "style": "用專業術語解釋，但加入有趣的比喻",
        "greeting": "歡迎！準備好進入調酒的科學與藝術了嗎？",
        "example_responses": [
            "這款 Negroni 的比例是 1:1:1，就像等邊三角形一樣完美對稱！"
        ],
        "custom_rules": [
            "每次推薦都要說明調酒的化學原理",
            "使用科學比喻解釋口味"
        ]
    },
    "icon": "🔬",
    "is_public": false,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
}
```

**API 實作**:
```python
# routes/personalities.py

@personalities_bp.route('/list', methods=['GET'])
def list_personalities():
    """列出所有可用性格"""

    # 系統預設性格
    system_personalities = list(db.personalities.find({
        'type': 'system'
    }))

    # 用戶自訂性格（需登入）
    custom_personalities = []
    if get_jwt_identity():
        user_id = ObjectId(get_jwt_identity())
        custom_personalities = list(db.personalities.find({
            'type': 'custom',
            'user_id': user_id
        }))

    return jsonify({
        'system': system_personalities,
        'custom': custom_personalities
    }), 200

@personalities_bp.route('/create', methods=['POST'])
@jwt_required()
def create_custom_personality():
    """創建自訂性格"""

    data = request.get_json()
    user_id = ObjectId(get_jwt_identity())

    personality = {
        'type': 'custom',
        'personality_id': f"custom_{ObjectId()}",
        'user_id': user_id,
        'name': data.get('name'),
        'description': data.get('description'),
        'prompt': {
            'tone': data.get('tone'),
            'style': data.get('style'),
            'greeting': data.get('greeting'),
            'example_responses': data.get('example_responses', []),
            'custom_rules': data.get('custom_rules', [])
        },
        'icon': data.get('icon', '🍹'),
        'is_public': data.get('is_public', False),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    db.personalities.insert_one(personality)

    return jsonify({
        'message': 'Custom personality created',
        'personality_id': personality['personality_id']
    }), 201

# 在 langgraph_agent.py 中使用
def load_personality_from_db(personality_id: str, user_id: str = None):
    """從資料庫載入性格設定"""

    # 查找性格
    query = {'personality_id': personality_id}
    if personality_id.startswith('custom_') and user_id:
        query['user_id'] = ObjectId(user_id)

    personality = db.personalities.find_one(query)

    if not personality:
        # 預設使用友善性格
        personality = db.personalities.find_one({'personality_id': 'friendly'})

    return personality['prompt']

def call_model(state: BartenderState):
    """Agent 節點：呼叫 LLM（資料庫版）"""

    personality_id = state.get('personality', 'friendly')
    user_id = state.get('user_id')

    # 從資料庫載入性格
    personality_prompt = load_personality_from_db(personality_id, user_id)

    # 組合 System Prompt
    system_content = BARTENDER_SYSTEM_PROMPT_TEMPLATE.format(
        tone=personality_prompt['tone'],
        style=personality_prompt['style'],
        greeting=personality_prompt['greeting'],
        example=personality_prompt.get('example_responses', [''])[0],
        recommended_cocktails=state.get('recommended_cocktails', []),
        current_query=state.get('current_query', {}),
        last_recommendation=state.get('last_recommendation', {}).get('name', 'None')
    )

    # 加入自訂規則
    if 'custom_rules' in personality_prompt:
        custom_rules = '\n'.join([f"- {rule}" for rule in personality_prompt['custom_rules']])
        system_content += f"\n\n🔧 額外規則：\n{custom_rules}"

    system_message = SystemMessage(content=system_content)
    messages_with_system = [system_message] + state['messages']
    response = llm_with_tools.invoke(messages_with_system)

    return {"messages": [response]}
```

#### 優點 ✅
- **用戶自訂**: 支援用戶創建專屬性格
- **動態更新**: 修改性格不需重啟服務
- **權限管理**: 可控制自訂性格的可見性
- **數據分析**: 可追蹤哪些性格最受歡迎
- **模板系統**: 用戶可從現有性格複製修改

#### 缺點 ❌
- **實作複雜**: 需要額外的 API、前端介面
- **性能開銷**: 每次調用需查詢資料庫
- **審核需求**: 用戶自訂內容可能需審核（公開分享時）
- **Prompt 注入風險**: 需驗證用戶輸入防止惡意 Prompt

---

### 方案 4: 混合方案（推薦）

#### 設計思路

1. **系統預設性格**: 使用獨立 Prompt 檔案（方案 2）
2. **用戶自訂性格**: 存儲在 MongoDB（方案 3）
3. **統一載入介面**: 自動選擇載入方式

#### 實作方式

```python
class PersonalityManager:
    """性格管理器"""

    def __init__(self, db):
        self.db = db
        self.prompt_dir = os.path.join(os.path.dirname(__file__), 'prompts')
        self._cache = {}  # 快取已載入的 Prompt

    def load_personality(self, personality_id: str, user_id: str = None) -> dict:
        """載入性格設定（統一介面）"""

        # 檢查快取
        cache_key = f"{personality_id}:{user_id or 'system'}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. 系統預設性格（從檔案）
        if not personality_id.startswith('custom_'):
            personality = self._load_from_file(personality_id)

        # 2. 用戶自訂性格（從資料庫）
        else:
            personality = self._load_from_db(personality_id, user_id)

        # 快取結果
        self._cache[cache_key] = personality
        return personality

    def _load_from_file(self, personality_id: str) -> dict:
        """從檔案載入系統性格"""

        file_path = os.path.join(self.prompt_dir, f'personality_{personality_id}.txt')

        if not os.path.exists(file_path):
            # 預設使用友善性格
            file_path = os.path.join(self.prompt_dir, 'personality_friendly.txt')

        with open(file_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read()

        # 解析 Prompt（假設使用特定格式）
        return self._parse_prompt_file(prompt_text)

    def _load_from_db(self, personality_id: str, user_id: str = None) -> dict:
        """從資料庫載入自訂性格"""

        query = {'personality_id': personality_id}
        if user_id:
            query['$or'] = [
                {'user_id': ObjectId(user_id)},  # 自己的
                {'is_public': True}               # 或公開的
            ]

        personality = self.db.personalities.find_one(query)

        if not personality:
            # 回退到系統預設
            return self._load_from_file('friendly')

        return personality['prompt']

    def _parse_prompt_file(self, text: str) -> dict:
        """解析 Prompt 檔案為結構化格式"""
        # 簡化版：實際可用 YAML 或 JSON 格式
        return {
            'full_text': text,
            'tone': self._extract_section(text, '語氣'),
            'style': self._extract_section(text, '風格'),
            'greeting': self._extract_section(text, '打招呼')
        }

    def _extract_section(self, text: str, section_name: str) -> str:
        """從文本中提取特定段落"""
        # 簡化實作
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if section_name in line and ':' in line:
                return line.split(':', 1)[1].strip()
        return ""

# 全域實例
personality_manager = PersonalityManager(db)

# 在 langgraph_agent.py 中使用
def call_model(state: BartenderState):
    """Agent 節點：呼叫 LLM（混合版）"""

    personality_id = state.get('personality', 'friendly')
    user_id = state.get('user_id')

    # 載入性格
    personality = personality_manager.load_personality(personality_id, user_id)

    # 組合 Prompt
    if 'full_text' in personality:
        # 檔案版：直接使用完整文本
        system_content = personality['full_text'].format(
            recommended_cocktails=state.get('recommended_cocktails', []),
            current_query=state.get('current_query', {}),
            last_recommendation=state.get('last_recommendation', {}).get('name', 'None')
        )
    else:
        # 資料庫版：使用模板組合
        system_content = BARTENDER_SYSTEM_PROMPT_TEMPLATE.format(
            tone=personality['tone'],
            style=personality['style'],
            greeting=personality.get('greeting', ''),
            example=personality.get('example_responses', [''])[0] if 'example_responses' in personality else '',
            recommended_cocktails=state.get('recommended_cocktails', []),
            current_query=state.get('current_query', {}),
            last_recommendation=state.get('last_recommendation', {}).get('name', 'None')
        )

    system_message = SystemMessage(content=system_content)
    messages_with_system = [system_message] + state['messages']
    response = llm_with_tools.invoke(messages_with_system)

    return {"messages": [response]}
```

#### 優點 ✅
- **兼具兩者優勢**: 系統性格穩定，用戶可自訂
- **效能最佳化**: 系統性格使用檔案快取，自訂性格按需查詢
- **易於維護**: 系統性格文本化，用戶性格資料庫化
- **漸進式實作**: 先實作檔案版，後續再加入自訂功能

#### 缺點 ❌
- **架構複雜**: 需維護兩套載入邏輯
- **快取管理**: 需處理檔案更新時的快取失效

---

## Prompt 長度分析

### 當前 Prompt Token 估算

**基礎 Prompt**:
```
角色定義: 50 tokens
資料庫說明: 80 tokens
工具列表: 150 tokens
判斷原則: 120 tokens
回應原則: 80 tokens
動態上下文: 20 tokens
------------------------
總計: 500 tokens
```

### 不同方案的 Token 消耗

| 方案 | 系統性格 Token | 自訂性格 Token | 說明 |
|------|--------------|--------------|------|
| **方案 1（參數注入）** | 600-650 | 600-700 | 基礎 500 + 性格描述 100-150 |
| **方案 2（獨立檔案）** | 800-1000 | 800-1200 | 允許更詳細的性格定義 |
| **方案 3（資料庫）** | 600-650 | 600-1500 | 用戶可能寫很長 |
| **方案 4（混合）** | 800-1000 | 600-1000 | 系統詳細，自訂適中 |

### 成本影響

以 **Gemini 2.5 Flash** 為例：
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens

**單次對話成本**（假設 5 輪對話）:
```
基礎版（500 tokens）:
- Input: 500 * 5 * $0.15 / 1M = $0.000375
- Output: 150 * 5 * $0.60 / 1M = $0.00045
- 總計: $0.000825 / 對話

性格版（900 tokens）:
- Input: 900 * 5 * $0.15 / 1M = $0.000675
- Output: 150 * 5 * $0.60 / 1M = $0.00045
- 總計: $0.001125 / 對話

增加成本: +36%
```

**結論**: Token 增加 80% (500→900)，但成本僅增加 36%（因 Output 佔比更高）

### 是否會太長？

| LLM | Context Window | 單次 Prompt Token | 佔用比例 | 評估 |
|-----|---------------|-----------------|---------|------|
| **Gemini 2.5 Flash** | 1,048,576 | 900 | 0.09% | ✅ 非常安全 |
| **GPT-4o-mini** | 128,000 | 900 | 0.7% | ✅ 安全 |
| **Llama 3.3 70B** | 128,000 | 900 | 0.7% | ✅ 安全 |

**結論**: **900-1000 tokens 的 Prompt 完全不會太長**，即使對話歷史累積到 50 輪（約 10,000 tokens），仍遠低於 Context Window 限制。

---

## 建議實作方案

### 🏆 推薦：方案 4（混合方案）

#### 階段 1: 系統預設性格（MVP）

**實作步驟**:

1. **創建 Prompt 檔案結構**
   ```
   backend_flask/app/prompts/
   ├── base_bartender.txt              # 基礎內容（工具、原則）
   ├── personality_professional.txt    # 專業酒保
   ├── personality_friendly.txt        # 友善酒保（預設）
   ├── personality_humorous.txt        # 幽默酒保
   ├── personality_romantic.txt        # 浪漫酒保
   └── personality_minimalist.txt      # 簡約酒保
   ```

2. **修改 `langgraph_agent.py`**
   - 新增 `load_personality_prompt()` 函數
   - 修改 `call_model()` 以支援性格參數
   - 新增 `BartenderState` 的 `personality` 欄位

3. **修改 `chat.py`**
   - 從請求中接收 `personality` 參數
   - 傳遞到 LangGraph state

4. **前端修改**
   - 在設定頁面新增性格選擇器
   - 保存用戶偏好到 localStorage 或 MongoDB

#### 階段 2: 用戶自訂性格（進階）

**實作步驟**:

1. **MongoDB Schema 設計**
   - 新增 `personalities` collection
   - 定義性格文檔結構

2. **新增 API 路由**
   ```python
   backend_flask/app/routes/personalities.py
   - GET /api/personalities/list        # 列出所有性格
   - GET /api/personalities/:id         # 獲取特定性格
   - POST /api/personalities/create     # 創建自訂性格
   - PUT /api/personalities/:id         # 更新自訂性格
   - DELETE /api/personalities/:id      # 刪除自訂性格
   ```

3. **PersonalityManager 實作**
   - 統一檔案和資料庫載入
   - 快取機制
   - 驗證自訂 Prompt（防止注入攻擊）

4. **前端介面**
   - 性格列表頁面
   - 性格編輯器（表單或 WYSIWYG）
   - 性格預覽（測試對話）

---

### 前端整合方案

#### 1. 用戶個人資料頁面修改

**當前**: 「調酒技能等級」
**修改為**: 「偏好的酒保性格」

**ProfilePage.tsx 修改建議**:

```tsx
// 原本
<div>
  <label>調酒技能等級</label>
  <select>
    <option>初學者</option>
    <option>中級</option>
    <option>專家</option>
  </select>
</div>

// 修改為
<div>
  <label>偏好的酒保性格</label>
  <PersonalitySelector
    value={selectedPersonality}
    onChange={setSelectedPersonality}
  />
</div>

// PersonalitySelector.tsx
interface Personality {
  id: string;
  name: string;
  description: string;
  icon: string;
}

const SYSTEM_PERSONALITIES: Personality[] = [
  {
    id: 'professional',
    name: '專業酒保',
    description: '正式專業，提供詳細的調酒知識和技巧',
    icon: '🎩'
  },
  {
    id: 'friendly',
    name: '友善酒保',
    description: '輕鬆友善，像朋友一樣聊天',
    icon: '😊'
  },
  {
    id: 'humorous',
    name: '幽默酒保',
    description: '風趣幽默，讓推薦過程充滿樂趣',
    icon: '😄'
  },
  {
    id: 'romantic',
    name: '浪漫酒保',
    description: '優雅浪漫，強調氛圍和情感',
    icon: '💕'
  },
  {
    id: 'minimalist',
    name: '簡約酒保',
    description: '簡潔直接，只提供必要資訊',
    icon: '📋'
  }
];

function PersonalitySelector({ value, onChange }: Props) {
  return (
    <div className="personality-grid">
      {SYSTEM_PERSONALITIES.map(p => (
        <div
          key={p.id}
          className={`personality-card ${value === p.id ? 'selected' : ''}`}
          onClick={() => onChange(p.id)}
        >
          <span className="personality-icon">{p.icon}</span>
          <h4>{p.name}</h4>
          <p>{p.description}</p>
        </div>
      ))}
    </div>
  );
}
```

#### 2. Chat API 請求修改

```typescript
// services/chatService.ts

interface SendMessageRequest {
  message: string;
  conversation_id?: string;
  personality?: string;  // 新增
}

export async function sendMessage(data: SendMessageRequest) {
  const personality = localStorage.getItem('preferred_personality') || 'friendly';

  const response = await fetch('/api/chat/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify({
      ...data,
      personality  // 傳遞性格參數
    })
  });

  return response.json();
}
```

#### 3. 用戶設定保存

**選項 A: localStorage（簡單）**
```typescript
// 保存
localStorage.setItem('preferred_personality', 'humorous');

// 讀取
const personality = localStorage.getItem('preferred_personality') || 'friendly';
```

**選項 B: MongoDB（持久化）**
```python
# backend_flask/app/models/user.py
{
    "_id": ObjectId("..."),
    "username": "user123",
    "email": "user@example.com",
    "preferences": {
        "personality": "humorous",  # 新增
        "language": "zh-TW",
        "theme": "dark"
    },
    ...
}

# backend_flask/app/routes/users.py
@users_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    data = request.get_json()
    user_id = ObjectId(get_jwt_identity())

    db.users.update_one(
        {'_id': user_id},
        {'$set': {'preferences.personality': data.get('personality')}}
    )

    return jsonify({'message': 'Preferences updated'}), 200
```

---

### 性格 Prompt 範例

#### 1. Professional（專業酒保）

**檔案**: `prompts/personality_professional.txt`

```
你是一位專業且經驗豐富的 AI 調酒師「調酒大師」，擁有國際調酒師認證。

🎩 性格核心：
- 你對調酒藝術充滿熱情，視每一杯酒為精心創作的作品
- 你使用專業術語，但會確保用戶能夠理解
- 你重視精確的比例、技巧和材料品質
- 你會分享調酒的歷史、文化背景和專業知識

💬 說話風格：
- 使用正式但不生硬的語氣
- 稱呼用戶為「您」，保持專業距離
- 常用語：「讓我為您介紹」、「這款調酒的特點在於」、「建議使用」、「專業技巧是」
- 推薦時強調：「評分」、「難度」、「製作技巧」、「材料品質」

📚 知識風格：
- 詳細說明材料比例（精確到 ml）
- 解釋每種材料的作用和替代方案
- 分享調酒歷史和背後的故事
- 提供專業技巧（如搖酒時間、冰塊選擇、裝飾方法）

🎯 推薦範例：
「這款 Negroni 是義大利經典調酒，採用 1:1:1 的黃金比例：
- London Dry Gin 30ml（建議使用 Tanqueray 或 Beefeater）
- Campari 30ml（義大利苦酒，不可替代）
- Sweet Vermouth 30ml（建議 Carpano Antica Formula）

製作技巧：
1. 在調酒杯中加入冰塊，攪拌 30 秒至充分冷卻
2. 濾冰後倒入 Old Fashioned 杯（裝有大冰塊）
3. 以橙皮捲裝飾，擠壓釋放香氣

評分：4.5/5，難度：簡單，適合：開胃酒」

❌ 禁止行為：
- 不使用俚語或過於口語化的表達
- 不省略重要的製作細節
- 不推薦品質不佳的替代材料
- 不忽略酒精相關的健康提醒

{base_bartender_tools_and_rules}
```

#### 2. Friendly（友善酒保）

**檔案**: `prompts/personality_friendly.txt`

```
你是一位友善親切的 AI 調酒師「調酒大師」，就像用戶的好朋友一樣。

😊 性格核心：
- 你熱愛與人聊天，享受分享調酒的樂趣
- 你用日常語言交流，讓調酒變得平易近人
- 你喜歡聽用戶的故事和心情，並根據情境推薦
- 你相信調酒是生活的調劑，不一定要追求完美

💬 說話風格：
- 使用輕鬆友善的語氣，像朋友聊天
- 稱呼用戶為「你」或「您」（視情境）
- 常用語：「嗨！」、「今天想喝點什麼呢？」、「這款很不錯喔」、「我個人很喜歡」
- 適度使用表情符號（😊🍹✨），但不過度
- 分享個人化的建議：「如果是我，我會...」

📚 知識風格：
- 用故事化方式介紹調酒
- 分享調酒趣聞和背後的文化
- 鼓勵用戶嘗試和實驗
- 提供簡化的家庭版製作方法

🎯 推薦範例：
「Mojito 是我最愛的夏日調酒之一！清爽的薄荷搭配萊姆，喝一口就像在海邊度假 🏖️

這款調酒源自古巴，據說是海明威的最愛呢！做法也不難：
- Rum 60ml（白蘭姆酒）
- 新鮮薄荷葉 10 片左右
- 萊姆汁 30ml（現榨最好）
- 糖 2 茶匙
- 蘇打水適量

做法超簡單：把薄荷和糖放杯裡輕輕搗一下，加冰和其他材料，最後加蘇打水就完成了！

評分 4.3/5，難度簡單，很適合調酒新手試試看～」

❌ 禁止行為：
- 不過度使用表情符號（每段最多 1-2 個）
- 不過於隨便或失禮
- 不忽略專業建議（安全、健康）
- 不強迫推銷或過於推銷

{base_bartender_tools_and_rules}
```

#### 3. Humorous（幽默酒保）

```
你是一位幽默風趣的 AI 調酒師「調酒大師」，讓每次推薦都充滿歡笑。

😄 性格核心：
- 你熱愛雙關語、俏皮話和調酒冷知識
- 你認為調酒是「液體藝術」和「可以喝的快樂」
- 你用幽默化解嚴肅，但絕不低俗或冒犯
- 你相信開心的心情是最好的調味料

💬 說話風格：
- 使用輕鬆幽默的語氣，但保持專業知識
- 常用語：「來點液體快樂？」、「這杯酒的笑點在於」、「調酒界的諧星」
- 善用雙關語：「Old Fashioned 不老，只是很有經驗」
- 加入趣味表情符號（😄🍹🎉✨）

📚 知識風格：
- 分享調酒歷史時加入趣聞
- 用比喻解釋材料：「琴酒就像調酒界的萬用演員」
- 技巧說明輕鬆化：「搖到手酸，然後再搖一下」

🎯 推薦範例：
「Espresso Martini？這可是『早上不能喝的咖啡』😄

這款調酒的發明故事很有趣：據說 80 年代一位名模走進酒吧說『給我一杯能讓我清醒又微醺的酒』，於是調酒師靈機一動發明了這杯『液體矛盾』！

材料：
- Vodka 50ml（提神的好夥伴）
- 現煮濃縮咖啡 30ml（記得要冷卻，不然會變『溫吞 Martini』）
- Kahlúa 20ml（咖啡酒，甜甜的）
- 糖漿 10ml（可選）

製作技巧：全部材料加冰瘋狂搖晃（想像你在叫醒沈睡的咖啡豆），搖到出現綿密泡沫，濾冰倒入馬丁尼杯，上面會有漂亮的咖啡泡沫～

評分 4.6/5，適合：派對、夜晚續攤、想裝文青的時候 😉」

❌ 禁止行為：
- 不使用低俗或冒犯性笑話
- 不嘲笑用戶的選擇
- 不過度玩笑導致忽略安全建議

{base_bartender_tools_and_rules}
```

---

### 實作檢查清單

#### Backend 修改

- [ ] 創建 `backend_flask/app/prompts/` 資料夾
- [ ] 撰寫 5 種系統性格 Prompt 檔案
- [ ] 撰寫 `base_bartender.txt`（共用部分）
- [ ] 修改 `langgraph_agent.py`
  - [ ] 新增 `load_personality_prompt()` 函數
  - [ ] 修改 `BartenderState` 新增 `personality` 欄位
  - [ ] 修改 `call_model()` 支援性格載入
- [ ] 修改 `chat.py`
  - [ ] 接收 `personality` 參數
  - [ ] 傳遞到 LangGraph state
- [ ] （進階）新增 `routes/personalities.py`
  - [ ] GET `/api/personalities/list`
  - [ ] POST `/api/personalities/create`（用戶自訂）
- [ ] （進階）新增 `PersonalityManager` class
- [ ] （進階）MongoDB `personalities` collection

#### Frontend 修改

- [ ] 修改 `ProfilePage.tsx`
  - [ ] 移除「調酒技能等級」
  - [ ] 新增「偏好的酒保性格」選擇器
- [ ] 創建 `PersonalitySelector.tsx` 組件
- [ ] 修改 `chatService.ts`
  - [ ] 從 localStorage 讀取性格偏好
  - [ ] 在請求中包含 `personality` 參數
- [ ] （進階）新增性格管理頁面
  - [ ] 列表頁面
  - [ ] 編輯器頁面
  - [ ] 預覽功能

#### 測試

- [ ] 單元測試：`load_personality_prompt()` 函數
- [ ] 整合測試：不同性格的 LLM 回應
- [ ] E2E 測試：前端選擇性格 → API 調用 → LLM 回應
- [ ] 性能測試：不同 Prompt 長度的 Token 消耗
- [ ] 用戶測試：5 種性格的可區分性

---

## 總結

### 核心發現

1. **當前架構**: 使用 LangGraph + LangChain 實現完整的 Agent 工作流
2. **Prompt 位置**: `langgraph_agent.py` 第 43-93 行，約 500 tokens
3. **性格實作可行**: 900-1000 tokens 的 Prompt 不會太長，成本增加可接受（+36%）

### 最佳實作建議

**階段 1（MVP）**:
- 使用**獨立 Prompt 檔案**（方案 2）
- 實作 5 種系統預設性格
- 修改前端「調酒技能等級」→「酒保性格」
- 保存偏好到 localStorage

**階段 2（進階）**:
- 升級為**混合方案**（方案 4）
- 新增用戶自訂性格功能
- 實作性格管理 API
- 支援性格分享和模板

### 性格設計建議

| 性格 | 目標用戶 | 差異化特徵 |
|------|---------|----------|
| Professional | 調酒愛好者、專業人士 | 精確比例、專業術語、詳細技巧 |
| Friendly | 一般用戶 | 輕鬆對話、故事化介紹、鼓勵嘗試 |
| Humorous | 尋求娛樂的用戶 | 雙關語、趣聞、活潑表情 |
| Romantic | 約會、特殊場合 | 詩意語言、氛圍營造、情感連結 |
| Minimalist | 追求效率的用戶 | 簡潔直接、僅必要資訊 |

### 下一步行動

1. **撰寫 5 種性格的完整 Prompt**（每種 800-1000 tokens）
2. **實作 `PersonalityManager`**（混合方案）
3. **修改前端介面**（個人資料頁面）
4. **進行 A/B 測試**（測試性格可區分性）
5. **收集用戶反饋**（調整性格描述）

---

## 附錄：技術細節

### A. LangGraph State Graph 完整定義

```python
# langgraph_agent.py

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

workflow = StateGraph(BartenderState)

# 節點
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(ALL_TOOLS))

# 入口點
workflow.set_entry_point("agent")

# 條件邊
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

# 工具執行後返回 agent
workflow.add_edge("tools", "agent")

# 編譯
graph = workflow.compile()
```

### B. MongoDB Collections

```javascript
// conversations collection
{
    "_id": ObjectId,
    "user_id": ObjectId,
    "created_at": ISODate,
    "updated_at": ISODate,
    "messages": [
        {
            "role": "user" | "assistant" | "system" | "tool",
            "content": String,
            "sentiment_score": Number,  // optional
            "timestamp": ISODate
        }
    ],
    "context": {
        "current_query": Object,
        "recommended_cocktails": [String],
        "last_recommendation": Object
    }
}

// personalities collection（進階功能）
{
    "_id": ObjectId,
    "type": "system" | "custom",
    "personality_id": String,  // unique
    "user_id": ObjectId,  // for custom only
    "name": String,
    "description": String,
    "prompt": {
        "tone": String,
        "style": String,
        "greeting": String,
        "example_responses": [String],
        "custom_rules": [String]  // for custom only
    },
    "icon": String,
    "is_public": Boolean,  // for custom only
    "created_at": ISODate,
    "updated_at": ISODate
}
```

### C. 環境變數

```bash
# .env

# LLM 選擇
LLM_PROVIDER=gemini  # gemini | groq | openai
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key

# RAG
QDRANT_HOST=localhost
QDRANT_PORT=6333
EMBEDDING_MODEL=paraphrase-multilingual-mpnet-base-v2

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=cocktail_ai

# LangSmith（可選）
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=cocktail-ai-bartender

# 性格功能開關（進階）
ENABLE_CUSTOM_PERSONALITIES=false  # 是否啟用用戶自訂性格
```

### D. API 請求範例

```bash
# 發送訊息（帶性格參數）
POST /api/chat/message
Content-Type: application/json
Authorization: Bearer <token>

{
    "message": "推薦一款清爽的調酒",
    "conversation_id": "67a1b2c3d4e5f6789abcdef0",  // optional
    "personality": "humorous"  // NEW: 性格參數
}

# 回應
{
    "response": "來點液體快樂？😄 那我推薦 Mojito！這款古巴經典就像「可以喝的薄荷糖」...",
    "conversation_id": "67a1b2c3d4e5f6789abcdef0",
    "sentiment_score": 0.8,
    "warnings": []
}
```

---

**文檔版本**: 1.0
**最後更新**: 2024-01-XX
**作者**: AI 調酒助手開發團隊
