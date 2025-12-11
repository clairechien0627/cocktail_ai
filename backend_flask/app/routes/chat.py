"""
Chat API (LangGraph 版本)
整合 LangGraph Agent 的對話 API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Conversation, User
from app.services.sentiment import analyze_sentiment, should_warn_about_drinking
from app.services.langgraph_agent import (
    get_graph,
    extract_cocktails_data_from_result,
    extract_cocktails_from_ai_message
)
from app.services.conversation_manager import ConversationManager
from bson.objectid import ObjectId

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@chat_bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """建立新對話"""
    try:
        user_id = get_jwt_identity()
        from flask import current_app
        db = current_app.config['DB']
        
        conversation_id = Conversation.create(db, user_id)
        
        return jsonify({
            'message': '對話建立成功',
            'conversation_id': str(conversation_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """取得用戶的所有對話"""
    try:
        user_id = get_jwt_identity()
        from flask import current_app
        db = current_app.config['DB']
        
        conversations = Conversation.find_by_user(db, user_id)
        
        # 轉換 ObjectId 為字串
        for conv in conversations:
            conv['_id'] = str(conv['_id'])
            conv['user_id'] = str(conv['user_id'])
        
        return jsonify({'conversations': conversations}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/conversations/<conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """取得特定對話"""
    try:
        from flask import current_app
        db = current_app.config['DB']
        
        conversation = Conversation.find_by_id(db, conversation_id)
        
        if not conversation:
            return jsonify({'error': '對話不存在'}), 404
        
        conversation['_id'] = str(conversation['_id'])
        conversation['user_id'] = str(conversation['user_id'])
        
        return jsonify({'conversation': conversation}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/message', methods=['POST'])
@jwt_required()
def send_message():
    """
    發送訊息並取得 AI 酒保回應（使用 LangGraph）
    
    Request Body:
        {
            "message": "用戶訊息",
            "conversation_id": "對話ID（可選）",
            "personality": "性格ID（可選，預設為用戶偏好或 friendly）"
        }
    
    Response:
        {
            "conversation_id": "對話ID",
            "message": "AI 回應",
            "sentiment": 0.5,
            "warning_issued": false,
            "tool_used": true
        }
    """
    try:
        from flask import current_app
        
        # 檢查服務是否可用
        if not current_app.config.get('GROQ_ENABLED', False):
            return jsonify({
                'error': 'AI 對話服務暫時無法使用',
                'message': '請確認 Groq API Key 已正確設定'
            }), 503
        
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({'error': '缺少訊息內容'}), 400
        
        user_message = data['message']
        conversation_id = data.get('conversation_id')
        personality = data.get('personality')  # 新增：性格參數

        db = current_app.config['DB']

        # 如果沒有指定性格，從用戶偏好中讀取（新增）
        if not personality:
            user_doc = db.users.find_one({'_id': ObjectId(user_id)})
            if user_doc and 'preferences' in user_doc and 'personality' in user_doc['preferences']:
                personality = user_doc['preferences']['personality']
            else:
                personality = 'friendly'  # 預設友善性格
        
        # 如果沒有提供 conversation_id，建立新對話
        if not conversation_id:
            conversation_id = Conversation.create(db, user_id)
        else:
            # 驗證對話是否存在
            conversation = Conversation.find_by_id(db, conversation_id)
            if not conversation:
                return jsonify({'error': '對話不存在'}), 404
        
        # ============== 情感分析 ==============
        sentiment_score = analyze_sentiment(user_message)
        
        # ============== 對話管理器 ==============
        conv_manager = ConversationManager(db, conversation_id)
        
        # 儲存用戶訊息
        conv_manager.save_message('user', user_message, sentiment_score)
        
        # ============== LangGraph Agent ==============
        graph = get_graph()
        
        # 準備狀態（直接獲取 Message 物件）
        messages = conv_manager.get_messages(as_message_objects=True)
        
        state = {
            'messages': messages,
            'user_message': user_message,
            'conversation_id': str(conversation_id),
            'user_id': str(user_id),
            'personality': personality,  # 新增：性格參數
            'current_query': conv_manager.context.get('current_query', {}),
            'recommended_cocktails': conv_manager.context.get('recommended_cocktails', []),
            'last_recommendation': conv_manager.context.get('last_recommendation', {}),
            'response': '',
            'tool_calls': []
        }
        
        # 執行 Graph
        result = graph.invoke(state)
        
        # 取得 AI 回應（支援 Gemini 的 list 格式）
        last_message = result['messages'][-1]
        ai_response = ""
        
        if hasattr(last_message, 'content'):
            content = last_message.content
            
            # 字串格式（OpenAI, Groq）
            if isinstance(content, str):
                ai_response = content
            # List 格式（Gemini）
            elif isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                ai_response = ' '.join(text_parts)
            else:
                ai_response = str(content)
        
        # 後備檢查
        if not ai_response or ai_response.strip() == "":
            ai_response = "抱歉，我目前無法回應。請稍後再試。"
            current_app.logger.warning(f"Empty AI response for: {user_message}")
        
        # 檢查是否使用了工具
        tool_used = False
        tool_results = []
        
        for msg in result['messages']:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_used = True
            # 檢查是否為工具結果訊息
            if hasattr(msg, 'content') and isinstance(msg.content, list):
                for item in msg.content:
                    if isinstance(item, dict):
                        tool_results.append(item)
        
        # 更新上下文
        conv_manager.update_context(ai_response, tool_results)
        
        # ============== 責任飲酒警告 ==============
        needs_warning = should_warn_about_drinking(user_message, sentiment_score)

        if needs_warning and '責任飲酒' not in ai_response:
            ai_response += "\n\n💡 小提醒：請記得理性飲酒，過量飲酒有害健康。如果您要開車或有其他不適合飲酒的情況，我也可以推薦美味的無酒精飲料喔！"

        # ============== 提取調酒資料（新增） ==============
        cocktails = []

        # 優先使用 LLM 輸出提取調酒（更準確）
        cocktails_data = extract_cocktails_from_ai_message(result, db)

        # 如果 LLM 沒有明確提到調酒，回退到 RAG 結果
        if not cocktails_data:
            current_app.logger.info(f"[Chat] LLM 輸出中未找到調酒，使用 RAG 結果作為回退")
            cocktails_data = extract_cocktails_data_from_result(result)
            extraction_method = "RAG"
        else:
            extraction_method = "LLM"

        current_app.logger.info(f"[Chat] 使用 {extraction_method} 提取到 {len(cocktails_data)} 個調酒資料")

        if cocktails_data:
            # 從 MongoDB 查詢調酒資料（精簡版本，只包含卡片需要的欄位）
            for cocktail_info in cocktails_data[:5]:  # 最多返回 5 個調酒
                try:
                    cocktail = None
                    search_id = cocktail_info.get('id')
                    search_name = cocktail_info.get('name')

                    current_app.logger.debug(f"[Chat] 嘗試查詢: id={search_id}, name={search_name}")

                    # 方法 1: 使用 ID 查詢（ObjectId）
                    if search_id:
                        try:
                            cocktail = db.cocktails.find_one(
                                {'_id': ObjectId(search_id)},
                                {
                                    '_id': 1, 'name': 1, 'name_zh': 1, 'image_url': 1,
                                    'ratings': 1, 'taste_profile': 1, 'difficulty': 1,
                                    'ingredients': 1, 'category': 1, 'category_zh': 1,
                                    'tags_categorized': 1
                                }
                            )
                        except:
                            pass

                    # 方法 2: 使用 ID 查詢（字串）
                    if not cocktail and search_id:
                        cocktail = db.cocktails.find_one(
                            {'_id': search_id},
                            {
                                '_id': 1, 'name': 1, 'name_zh': 1, 'image_url': 1,
                                'ratings': 1, 'taste_profile': 1, 'difficulty': 1,
                                'ingredients': 1, 'category': 1, 'category_zh': 1,
                                'tags_categorized': 1
                            }
                        )

                    # 方法 3: 使用調酒名稱查詢（最可靠）
                    if not cocktail and search_name:
                        cocktail = db.cocktails.find_one(
                            {'name': search_name},
                            {
                                '_id': 1, 'name': 1, 'name_zh': 1, 'image_url': 1,
                                'ratings': 1, 'taste_profile': 1, 'difficulty': 1,
                                'ingredients': 1, 'category': 1, 'category_zh': 1,
                                'tags_categorized': 1
                            }
                        )

                    if cocktail:
                        # 轉換 ObjectId 為字串
                        cocktail['_id'] = str(cocktail['_id'])
                        # 計算材料數量
                        cocktail['ingredients_count'] = len(cocktail.get('ingredients', []))
                        cocktails.append(cocktail)
                        current_app.logger.debug(f"[Chat] ✓ 成功查詢調酒: {cocktail.get('name_zh') or cocktail.get('name')}")
                    else:
                        current_app.logger.warning(f"[Chat] ✗ 調酒不存在於資料庫: id={search_id}, name={search_name}")
                except Exception as e:
                    current_app.logger.error(f"[Chat] ✗ 查詢調酒失敗: {str(e)}")
                    import traceback
                    current_app.logger.debug(traceback.format_exc())
                    continue

        current_app.logger.info(f"[Chat] ✓ 對話完成 (ID: {conversation_id}, 工具使用: {tool_used}, 調酒數量: {len(cocktails)})")
        if cocktails:
            cocktail_names = [c.get('name_zh') or c.get('name') for c in cocktails]
            current_app.logger.info(f"[Chat] 返回的調酒: {cocktail_names}")

        # ============== 儲存 AI 回應 ==============
        # 儲存 AI 回應（包含調酒推薦資料）
        conv_manager.save_message('assistant', ai_response, cocktails=cocktails if cocktails else None)

        return jsonify({
            'conversation_id': str(conversation_id),
            'message': ai_response,
            'sentiment': sentiment_score,
            'warning_issued': needs_warning,
            'tool_used': tool_used,
            'cocktails': cocktails,  # 新增：調酒卡片資料
            'mode': 'langgraph',
            'langsmith_traced': current_app.config.get('LANGCHAIN_TRACING_V2') == 'true'
        }), 200
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"發送訊息錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'發送訊息失敗: {str(e)}'}), 500


@chat_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    """刪除對話"""
    try:
        from flask import current_app
        from bson.objectid import ObjectId
        
        db = current_app.config['DB']
        user_id = get_jwt_identity()
        
        # 轉換 ID 為 ObjectId
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        if isinstance(conversation_id, str):
            conversation_id = ObjectId(conversation_id)
        
        # 刪除對話（確保是該用戶的）
        result = db.conversations.delete_one({
            '_id': conversation_id,
            'user_id': user_id
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': '對話不存在或無權限刪除'}), 404
        
        current_app.logger.info(f"✓ 已刪除對話: {conversation_id}")
        return jsonify({'message': '對話已刪除'}), 200
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"❌ 刪除對話錯誤: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/context/<conversation_id>', methods=['GET'])
@jwt_required()
def get_context(conversation_id):
    """
    取得對話上下文（除錯用）
    
    Returns:
        {
            "current_query": {...},
            "recommended_cocktails": [...],
            "last_recommendation": {...}
        }
    """
    try:
        from flask import current_app
        db = current_app.config['DB']
        
        conv_manager = ConversationManager(db, conversation_id)
        
        return jsonify({
            'context': conv_manager.context
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500