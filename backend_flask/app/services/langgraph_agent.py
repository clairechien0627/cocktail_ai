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
    personality: str  # 性格 ID（新增）

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

    # 載入性格 Prompt（新增）
    personality_id = state.get('personality', 'friendly')  # 預設友善性格
    user_id = state.get('user_id')

    from app.services.personality_manager import PersonalityManager
    from flask import current_app
    db = current_app.config.get('DB') if current_app else None

    personality_manager = PersonalityManager(db)
    personality_prompt = personality_manager.load_personality(personality_id, user_id)

    # 格式化 Prompt（注入對話上下文）
    system_content = personality_prompt.format(
        recommended_cocktails=state.get('recommended_cocktails', []),
        current_query=state.get('current_query', {}),
        last_recommendation=state.get('last_recommendation', {}).get('name', 'None')
    )

    # 建立 System Message
    system_message = SystemMessage(content=system_content)

    # 獲取訊息（已經是 Message 物件）
    state_messages = state.get('messages', [])

    # 建立最終訊息列表
    messages = [system_message] + state_messages

    # 呼叫 LLM
    response = llm_with_tools.invoke(messages, config)

    # 簡化的 Debug
    print(f"[Agent] 性格: {personality_id}, 訊息: {len(messages)}, 工具: {len(response.tool_calls) if hasattr(response, 'tool_calls') and response.tool_calls else 0}")

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


def extract_cocktails_from_ai_message(result: dict, db) -> List[dict]:
    """
    從 LLM 的 AIMessage 中提取調酒名稱並匹配資料庫

    此函數分析 LLM 的實際輸出文本，提取其中提到的調酒名稱，
    然後與資料庫進行匹配，確保返回 LLM 真正推薦的調酒。

    Args:
        result: LangGraph 執行結果
        db: MongoDB 資料庫實例

    Returns:
        調酒資料列表（包含 id 和 name）
    """
    from langchain_core.messages import AIMessage
    from flask import current_app
    import re

    # 1. 提取所有 AIMessage
    ai_messages = [msg for msg in result.get('messages', [])
                   if isinstance(msg, AIMessage)]

    if not ai_messages:
        current_app.logger.debug("[LLM提取] 沒有找到 AIMessage")
        return []

    # 2. 取最後一個 AIMessage（LLM 的最終回答）
    last_message = ai_messages[-1]
    content = last_message.content if hasattr(last_message, 'content') else str(last_message)

    current_app.logger.info(f"[LLM提取] AIMessage 內容長度: {len(content)} 字元")

    # 3. 使用多種正則模式提取調酒名稱
    patterns = [
        r'["""]([^"""]+?)["""]',           # 中英文引號內的內容
        r'名為\s*["""]([^"""]+?)["""]',    # "名為 'XXX'"
        r'推薦\s*["""]([^"""]+?)["""]',    # "推薦 'XXX'"
        r'介紹\s*["""]([^"""]+?)["""]',    # "介紹 'XXX'"
        r'這款\s*["""]([^"""]+?)["""]',    # "這款 'XXX'"
        r'\*\*([A-Z][a-zA-Z0-9\s&\'-]+)\*\*',  # **Bold Text** 格式
    ]

    extracted_names = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        extracted_names.extend(matches)

    # 去重並過濾掉太短或太長的名稱
    extracted_names = list(set([
        name.strip() for name in extracted_names
        if 3 <= len(name.strip()) <= 50
    ]))

    current_app.logger.info(f"[LLM提取] 提取到候選名稱: {extracted_names}")

    if not extracted_names:
        return []

    # 4. 與資料庫匹配
    cocktails = []
    for name in extracted_names:
        cocktail = fuzzy_match_cocktail_name(name, db)
        if cocktail:
            cocktails.append({
                'id': str(cocktail['_id']),
                'name': cocktail['name']
            })
            current_app.logger.info(f"[LLM提取] 匹配成功: '{name}' -> '{cocktail['name']}'")
        else:
            current_app.logger.debug(f"[LLM提取] 無法匹配: '{name}'")

    return cocktails


def fuzzy_match_cocktail_name(query_name: str, db) -> dict:
    """
    模糊匹配調酒名稱

    使用多種策略匹配調酒名稱：
    1. 精確匹配
    2. 不區分大小寫匹配
    3. 部分匹配 + 相似度計算

    Args:
        query_name: 要查詢的調酒名稱
        db: MongoDB 資料庫實例

    Returns:
        匹配的調酒文檔，若無匹配則返回 None
    """
    from flask import current_app
    from difflib import SequenceMatcher
    import re

    # 1. 精確匹配
    exact = db.cocktails.find_one({'name': query_name})
    if exact:
        current_app.logger.debug(f"[模糊匹配] 精確匹配成功: '{query_name}'")
        return exact

    # 2. 不區分大小寫匹配
    case_insensitive = db.cocktails.find_one(
        {'name': {'$regex': f'^{re.escape(query_name)}$', '$options': 'i'}}
    )
    if case_insensitive:
        current_app.logger.debug(f"[模糊匹配] 不區分大小寫匹配成功: '{query_name}'")
        return case_insensitive

    # 3. 部分匹配 + 相似度計算
    try:
        partial_matches = list(db.cocktails.find(
            {'name': {'$regex': re.escape(query_name), '$options': 'i'}},
            limit=10
        ))

        if not partial_matches:
            # 嘗試反向匹配（查詢詞包含在調酒名稱中）
            words = query_name.split()
            if len(words) > 1:
                # 嘗試用主要詞彙搜索
                for word in words:
                    if len(word) >= 3:  # 至少3個字元
                        partial_matches = list(db.cocktails.find(
                            {'name': {'$regex': re.escape(word), '$options': 'i'}},
                            limit=10
                        ))
                        if partial_matches:
                            break

        if not partial_matches:
            current_app.logger.debug(f"[模糊匹配] 無部分匹配結果: '{query_name}'")
            return None

        # 計算相似度，選擇最佳匹配
        def similarity(a: str, b: str) -> float:
            return SequenceMatcher(None, a.lower(), b.lower()).ratio()

        best_match = max(
            partial_matches,
            key=lambda x: similarity(query_name, x['name'])
        )

        best_score = similarity(query_name, best_match['name'])

        # 只返回相似度 >= 0.6 的匹配
        if best_score >= 0.6:
            current_app.logger.debug(
                f"[模糊匹配] 部分匹配成功: '{query_name}' -> '{best_match['name']}' "
                f"(相似度: {best_score:.2f})"
            )
            return best_match
        else:
            current_app.logger.debug(
                f"[模糊匹配] 最佳匹配相似度過低: '{query_name}' -> '{best_match['name']}' "
                f"(相似度: {best_score:.2f})"
            )
            return None

    except Exception as e:
        current_app.logger.error(f"[模糊匹配] 異常: {str(e)}")
        return None


def extract_cocktails_data_from_result(result: dict) -> List[dict]:
    """
    從 LangGraph 執行結果中提取調酒資料（完整版）

    Args:
        result: LangGraph 執行結果

    Returns:
        調酒資料列表（包含 _id/id 和 name）
    """
    from flask import current_app
    import json
    import ast

    cocktails_data = []
    tool_message_count = 0

    for msg in result.get('messages', []):
        # 檢查是否為 ToolMessage
        if isinstance(msg, ToolMessage):
            tool_message_count += 1
            content = msg.content

            # Debug 日誌：記錄 ToolMessage 內容
            content_preview = str(content)[:200] if content else 'None'
            current_app.logger.debug(f"[提取調酒資料] ToolMessage #{tool_message_count} 類型: {type(content).__name__}, 內容預覽: {content_preview}")

            # 嘗試解析 JSON 格式的工具結果
            try:
                data = None

                # 1. 如果是字串，嘗試 JSON 解析
                if isinstance(content, str):
                    try:
                        data = json.loads(content)
                        current_app.logger.debug(f"[提取調酒資料] 使用 json.loads 成功解析")
                    except json.JSONDecodeError:
                        # 備用方案 1：將單引號替換為雙引號後再嘗試 JSON 解析
                        try:
                            # 簡單的單引號轉雙引號（處理 Python dict 字串表示）
                            import re
                            # 替換字典鍵值的單引號為雙引號
                            fixed_content = content.replace("'", '"')
                            data = json.loads(fixed_content)
                            current_app.logger.warning(f"[提取調酒資料] json.loads 失敗，使用單引號替換後成功解析")
                        except json.JSONDecodeError:
                            # 備用方案 2：使用正則提取 _id 和 name
                            try:
                                # 直接從字串中提取 _id 和 name 值
                                id_match = re.search(r"['\"](?:_id|id)['\"]\s*:\s*['\"]([^'\"]+)['\"]", content)
                                name_match = re.search(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", content)
                                if id_match:
                                    extracted_id = id_match.group(1)
                                    extracted_name = name_match.group(1) if name_match else None
                                    current_app.logger.warning(f"[提取調酒資料] JSON 解析失敗，使用正則提取到 _id: {extracted_id}, name: {extracted_name}")
                                    # 創建一個簡單的 dict 來後續處理
                                    data = {'_id': extracted_id, 'id': extracted_id, 'name': extracted_name}
                                else:
                                    current_app.logger.error(f"[提取調酒資料] 無法解析且無法提取資料，內容: {content[:200]}")
                                    continue
                            except Exception as e:
                                current_app.logger.error(f"[提取調酒資料] 所有解析方法都失敗: {str(e)}, 內容: {content[:100]}")
                                continue

                # 2. 如果是 dict 或 list，直接使用
                elif isinstance(content, dict):
                    data = content
                    current_app.logger.debug(f"[提取調酒資料] ToolMessage.content 已經是 dict")
                elif isinstance(content, list):
                    data = content
                    current_app.logger.debug(f"[提取調酒資料] ToolMessage.content 已經是 list")
                else:
                    current_app.logger.warning(f"[提取調酒資料] 不支援的 content 類型: {type(content)}")
                    continue

                # 3. 從解析後的資料中提取調酒資料
                extracted_count = 0

                # 情況 A：單個調酒物件
                if isinstance(data, dict) and ('_id' in data or 'id' in data or 'name' in data):
                    cocktail_info = {
                        'id': data.get('_id') or data.get('id'),
                        'name': data.get('name')
                    }
                    if cocktail_info['id'] or cocktail_info['name']:
                        cocktails_data.append(cocktail_info)
                        extracted_count += 1

                # 情況 B：調酒陣列包裝
                elif isinstance(data, dict) and 'cocktails' in data:
                    for cocktail in data.get('cocktails', []):
                        if isinstance(cocktail, dict):
                            cocktail_info = {
                                'id': cocktail.get('_id') or cocktail.get('id'),
                                'name': cocktail.get('name')
                            }
                            if cocktail_info['id'] or cocktail_info['name']:
                                cocktails_data.append(cocktail_info)
                                extracted_count += 1

                # 情況 C：直接是調酒陣列
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            cocktail_info = {
                                'id': item.get('_id') or item.get('id'),
                                'name': item.get('name')
                            }
                            if cocktail_info['id'] or cocktail_info['name']:
                                cocktails_data.append(cocktail_info)
                                extracted_count += 1

                current_app.logger.debug(f"[提取調酒資料] 從本 ToolMessage 提取到 {extracted_count} 個調酒")

            except Exception as e:
                current_app.logger.error(f"[提取調酒資料] 解析異常: {str(e)}, 類型: {type(e).__name__}")
                import traceback
                current_app.logger.debug(traceback.format_exc())
                continue

    # 去重（基於 id 或 name）
    seen = set()
    unique_cocktails = []
    for cocktail in cocktails_data:
        key = cocktail.get('id') or cocktail.get('name')
        if key and key not in seen:
            seen.add(key)
            unique_cocktails.append(cocktail)

    # 總結日誌
    current_app.logger.info(f"[提取調酒資料] 總共處理 {tool_message_count} 個 ToolMessage，提取到 {len(unique_cocktails)} 個唯一調酒")

    return unique_cocktails


# 保留舊函數以保持向後兼容
def extract_cocktail_ids_from_result(result: dict) -> List[str]:
    """
    從 LangGraph 執行結果中提取調酒 ID（向後兼容版本）

    Args:
        result: LangGraph 執行結果

    Returns:
        調酒 ID 列表（_id 字串）
    """
    from flask import current_app
    import json
    import ast

    cocktail_ids = []
    tool_message_count = 0

    for msg in result.get('messages', []):
        # 檢查是否為 ToolMessage
        if isinstance(msg, ToolMessage):
            tool_message_count += 1
            content = msg.content

            # Debug 日誌：記錄 ToolMessage 內容
            content_preview = str(content)[:200] if content else 'None'
            current_app.logger.debug(f"[提取調酒ID] ToolMessage #{tool_message_count} 類型: {type(content).__name__}, 內容預覽: {content_preview}")

            # 嘗試解析 JSON 格式的工具結果
            try:
                data = None

                # 1. 如果是字串，嘗試 JSON 解析
                if isinstance(content, str):
                    try:
                        data = json.loads(content)
                        current_app.logger.debug(f"[提取調酒ID] 使用 json.loads 成功解析")
                    except json.JSONDecodeError:
                        # 備用方案 1：將單引號替換為雙引號後再嘗試 JSON 解析
                        try:
                            # 簡單的單引號轉雙引號（處理 Python dict 字串表示）
                            import re
                            # 替換字典鍵值的單引號為雙引號
                            fixed_content = content.replace("'", '"')
                            data = json.loads(fixed_content)
                            current_app.logger.warning(f"[提取調酒ID] json.loads 失敗，使用單引號替換後成功解析")
                        except json.JSONDecodeError:
                            # 備用方案 2：使用正則提取 _id
                            try:
                                # 直接從字串中提取 _id 值
                                match = re.search(r"['\"]_id['\"]\s*:\s*['\"]([^'\"]+)['\"]", content)
                                if match:
                                    extracted_id = match.group(1)
                                    current_app.logger.warning(f"[提取調酒ID] JSON 解析失敗，使用正則提取到 _id: {extracted_id}")
                                    # 創建一個簡單的 dict 來後續處理
                                    data = {'_id': extracted_id}
                                else:
                                    current_app.logger.error(f"[提取調酒ID] 無法解析且無法提取 _id，內容: {content[:200]}")
                                    continue
                            except Exception as e:
                                current_app.logger.error(f"[提取調酒ID] 所有解析方法都失敗: {str(e)}, 內容: {content[:100]}")
                                continue

                # 2. 如果是 dict 或 list，直接使用
                elif isinstance(content, dict):
                    data = content
                    current_app.logger.debug(f"[提取調酒ID] ToolMessage.content 已經是 dict")
                elif isinstance(content, list):
                    data = content
                    current_app.logger.debug(f"[提取調酒ID] ToolMessage.content 已經是 list")
                else:
                    current_app.logger.warning(f"[提取調酒ID] 不支援的 content 類型: {type(content)}")
                    continue

                # 3. 從解析後的資料中提取 _id 或 id
                extracted_count = 0

                # 情況 A：單個調酒物件 {'_id': 'xxx', 'name': 'Mojito', ...} 或 {'id': 'xxx', ...}
                if isinstance(data, dict) and ('_id' in data or 'id' in data):
                    cocktail_id = data.get('_id') or data.get('id')
                    cocktail_ids.append(str(cocktail_id))
                    extracted_count += 1

                # 情況 B：調酒陣列包裝 {'cocktails': [...]}
                elif isinstance(data, dict) and 'cocktails' in data:
                    for cocktail in data.get('cocktails', []):
                        if isinstance(cocktail, dict):
                            cocktail_id = cocktail.get('_id') or cocktail.get('id')
                            if cocktail_id:
                                cocktail_ids.append(str(cocktail_id))
                                extracted_count += 1

                # 情況 C：直接是調酒陣列 [{'_id': 'xxx', ...}, ...] 或 [{'id': 'xxx', ...}, ...]
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            cocktail_id = item.get('_id') or item.get('id')
                            if cocktail_id:
                                cocktail_ids.append(str(cocktail_id))
                                extracted_count += 1

                current_app.logger.debug(f"[提取調酒ID] 從本 ToolMessage 提取到 {extracted_count} 個調酒 ID")

            except Exception as e:
                current_app.logger.error(f"[提取調酒ID] 解析異常: {str(e)}, 類型: {type(e).__name__}")
                import traceback
                current_app.logger.debug(traceback.format_exc())
                continue

    # 去重並保持順序
    seen = set()
    unique_ids = []
    for cid in cocktail_ids:
        if cid not in seen:
            seen.add(cid)
            unique_ids.append(cid)

    # 總結日誌
    current_app.logger.info(f"[提取調酒ID] 總共處理 {tool_message_count} 個 ToolMessage，提取到 {len(unique_ids)} 個唯一調酒 ID: {unique_ids}")

    return unique_ids