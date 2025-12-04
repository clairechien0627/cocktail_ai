"""
LangGraph Agent（支援多 LLM 切換）
使用 LangGraph 建立智能調酒師 Agent
支援：Gemini、Groq、OpenAI
"""

from typing import TypedDict, List, Annotated
from operator import add  # ← 加入 add operator
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from datetime import datetime
from flask import current_app
import os


# ============== 配置：選擇 LLM ==============
# 選項: "gemini", "groq", "openai"
DEFAULT_LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')


# ============== 狀態定義 ==============
class BartenderState(TypedDict):
    """調酒師 Agent 狀態"""
    # 輸入
    messages: Annotated[List, add]  # ← 使用 add 累積訊息
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


# ============== System Prompt ==============
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

💡 智能組合工具：
- 可以先用 RAG 找相似，再用 filter 精確篩選
- 可以同時使用多個工具來得到更好的結果
- 如果第一次查詢結果不理想，可以調整參數再試

🎯 回應原則：
1. 使用繁體中文
2. 保持友善、專業的酒保語氣
3. **如果使用了工具，必須基於查詢結果回答，絕對不能沉默或回應空白**
4. **如果工具返回了調酒資料，你必須介紹這款調酒的名稱、特色、材料和做法**
5. 如果沒用工具（閒聊），展現親切感
6. 推薦時提供：名稱、評分、風味特徵、材料、製作方法
7. 適時提醒責任飲酒
8. 避免推薦重複的調酒（檢查 recommended_cocktails）

⚠️ 重要：當你收到工具執行結果（ToolMessage）時，你**必須**根據結果生成完整的回應，不能返回空內容！

🔄 多輪對話記憶：
- 記住用戶之前的偏好和查詢條件
- 如果用戶說"換一個"，使用相同條件但排除已推薦的
- 如果用戶補充新條件，更新查詢參數

當前對話上下文：
- 已推薦過: {recommended_cocktails}
- 當前查詢參數: {current_query}
- 最後推薦: {last_recommendation}
"""


# ============== LLM 初始化函數 ==============
def get_llm(provider: str = None):
    """
    取得 LLM 實例
    
    Args:
        provider: LLM 提供商 ("gemini", "groq", "openai")
    
    Returns:
        LLM 實例
    """
    if provider is None:
        provider = DEFAULT_LLM_PROVIDER
    
    provider = provider.lower()
    
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.7,
            convert_system_message_to_human=True  # Gemini 需要這個
        )
    
    elif provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            groq_api_key=os.getenv('GROQ_API_KEY'),
            model_name="llama-3.3-70b-versatile",
            temperature=0.7
        )
    
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name="gpt-4o-mini",  # 或 gpt-4o
            temperature=0.7
        )
    
    else:
        raise ValueError(f"不支援的 LLM 提供商: {provider}")


def call_model(state: BartenderState, config: RunnableConfig):
    """
    Agent 節點：呼叫 LLM
    
    訊息已經是 LangChain Message 物件，直接使用即可
    """
    # 獲取 LLM 和工具
    llm = get_llm()
    from app.services.tools import ALL_TOOLS
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
    
    # 建立 System Message（注入上下文）
    system_message = SystemMessage(content=BARTENDER_SYSTEM_PROMPT.format(
        recommended_cocktails=state.get('recommended_cocktails', []),
        current_query=state.get('current_query', {}),
        last_recommendation=state.get('last_recommendation', {}).get('name', 'None')
    ))
    
    # 獲取訊息（已經是 Message 物件）
    state_messages = state.get('messages', [])
    
    # 建立最終訊息列表
    messages = [system_message] + state_messages
    
    # 呼叫 LLM
    response = llm_with_tools.invoke(messages, config)
    
    # 簡化的 Debug
    print(f"[Agent] 訊息: {len(messages)}, 工具: {len(response.tool_calls) if hasattr(response, 'tool_calls') and response.tool_calls else 0}")
    
    return {'messages': [response]}




def should_continue(state: BartenderState):
    """
    判斷是否需要呼叫工具
    
    邏輯：
    1. 有 tool_calls → 執行工具
    2. 但如果重複調用超過 3 次 → 結束（防止無限循環）
    """
    messages = state.get('messages', [])
    if not messages:
        return END
    
    last_message = messages[-1]
    
    # 檢查是否有 tool_calls
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        tool_names = [tc.get('name', 'unknown') for tc in last_message.tool_calls]
        
        # 檢查重複調用
        tool_call_history = []
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_call_history.append(tc.get('name'))
        
        from collections import Counter
        tool_counts = Counter(tool_call_history)
        max_calls = max(tool_counts.values()) if tool_counts else 0
        
        # 防止無限循環
        if max_calls > 3:
            print(f"[Agent] 工具調用次數過多 ({max_calls}), 強制結束")
            return END
        
        print(f"[Agent] → 執行工具: {', '.join(tool_names)}")
        return "tools"
    
    print(f"[Agent] → 結束")
    return END


def process_tool_results(state: BartenderState):
    """
    處理工具執行結果，更新對話上下文
    這個節點在工具執行後、返回 LLM 前執行
    """
    # 這裡可以加入邏輯來更新 recommended_cocktails 等
    # 目前先簡單返回
    return state


# ============== 建立 Graph ==============
def create_bartender_graph():
    """建立調酒師 Agent Graph"""
    # 建立工具節點
    from app.services.tools import ALL_TOOLS
    tool_node = ToolNode(ALL_TOOLS)
    
    # 建立 Graph
    workflow = StateGraph(BartenderState)
    
    # 加入節點
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("process_results", process_tool_results)
    
    # 設定入口點
    workflow.set_entry_point("agent")
    
    # 加入條件邊
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
    
    return graph


# ============== 全域 Graph 實例 ==============
bartender_graph = None


# ============== 對話管理器 ==============


def initialize_graph():
    """初始化 Graph（應用啟動時呼叫）"""
    global bartender_graph
    bartender_graph = create_bartender_graph()
    from flask import current_app
    current_app.logger.info(f"✓ LangGraph Agent 已初始化 (使用 {DEFAULT_LLM_PROVIDER.upper()})")


def get_graph():
    """取得 Graph 實例"""
    global bartender_graph
    if bartender_graph is None:
        bartender_graph = create_bartender_graph()
    return bartender_graph