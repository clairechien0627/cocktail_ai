from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Conversation, User
from app.services.llm_service import llm_service
from app.services.sentiment import analyze_sentiment, should_warn_about_drinking
from langsmith import traceable

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


# ============== 新增的函數：查詢資料庫 ==============
@traceable(name="query_cocktails_from_db")
def query_cocktails_from_db(db, user_message, limit=3):
    """改進版：更智慧的查詢"""
    try:
        from flask import current_app
        current_app.logger.info(f"🔍 開始查詢資料庫，訊息：{user_message}")
        
        message_lower = user_message.lower()
        query = {}
        search_type = "default"  # 記錄查詢類型
        
        # ============== 優先級 1：搜尋特定調酒名稱 ==============
        # 偵測搜尋關鍵字
        search_keywords = ['找', '搜', '有沒有', '想喝', '來杯', 'search', 'find']
        is_searching = any(kw in message_lower for kw in search_keywords)
        
        if is_searching:
            # 移除搜尋關鍵字，提取調酒名稱
            search_terms = message_lower
            for kw in search_keywords:
                search_terms = search_terms.replace(kw, '')
            
            # 移除常見的無用詞
            for word in ['調酒', '的', '一杯', '給我', '請', '嗎', '呢', '啊']:
                search_terms = search_terms.replace(word, '')
            
            search_terms = search_terms.strip()
            
            if search_terms:
                query = {
                    "$or": [
                        {"name": {"$regex": search_terms, "$options": "i"}},
                        {"description": {"$regex": search_terms, "$options": "i"}},
                        {"ingredients.name": {"$regex": search_terms, "$options": "i"}}
                    ]
                }
                search_type = "name_search"
                current_app.logger.info(f"🔎 名稱搜尋模式，關鍵字：{search_terms}")
        
        # ============== 優先級 2：材料篩選 ==============
        if not query:
            spirits = {
                '威士忌': 'whisky', '伏特加': 'vodka', '琴酒': 'gin',
                '蘭姆': 'rum', '龍舌蘭': 'tequila', 'whisky': 'whisky',
                'vodka': 'vodka', 'gin': 'gin', 'rum': 'rum', 'tequila': 'tequila'
            }
            
            for zh, en in spirits.items():
                if zh in message_lower:
                    query['ingredients.name'] = {'$regex': en, '$options': 'i'}
                    search_type = "ingredient"
                    current_app.logger.info(f"🥃 材料篩選：{zh}")
                    break
        
        # ============== 優先級 3：難度篩選 ==============
        if not query:
            if any(w in message_lower for w in ['簡單', 'easy', '新手']):
                query['difficulty'] = 'easy'
                search_type = "difficulty"
                current_app.logger.info("📊 難度篩選：簡單")
        
        # ============== 優先級 4：預設查詢（放寬條件）==============
        if not query:
            query = {'rating': {'$gte': 3.0}}  # 放寬到 3.0
            search_type = "default_rating"
        
        current_app.logger.info(f"查詢條件：{query}")
        
        # 執行查詢
        cocktails = list(db.cocktails.find(query).sort('rating', -1).limit(limit))
        
        # 如果還是沒找到，最後備用方案
        if not cocktails:
            current_app.logger.warning("未找到符合條件的調酒，使用終極備用查詢")
            cocktails = list(db.cocktails.find({}).sort('rating', -1).limit(limit))
            search_type = "fallback"
        
        # 顯示結果
        if cocktails:
            names = [c['name'] for c in cocktails]
            current_app.logger.info(f"✓ 查詢到 {len(cocktails)} 個調酒（{search_type}）：{names}")
        else:
            current_app.logger.error("❌ 資料庫中沒有任何調酒！")
        
        return cocktails
        
    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"❌ 查詢錯誤: {e}")
        return []


# ====================================================


@traceable(name="process_chat_message",
          run_type="chain",
          metadata={"service": "cocktail_ai", "version": "1.0"})
def process_chat_message(db, user_id, user_message, conversation_id, user_preferences):
    """
    處理對話訊息的核心邏輯（帶 LangSmith 追蹤）

    Args:
        db: MongoDB 資料庫實例
        user_id: 用戶 ID
        user_message: 用戶訊息
        conversation_id: 對話 ID
        user_preferences: 用戶偏好設定

    Returns:
        dict: 包含 AI 回應、情感分數和警告狀態
    """
    from flask import current_app

    # 1. 情感分析
    sentiment_score = analyze_sentiment(user_message)
    current_app.logger.info(f"情感分析結果: {sentiment_score}")

    # 2. 儲存用戶訊息
    Conversation.add_message(db, conversation_id, 'user', user_message, sentiment_score)

    # 3. 取得對話歷史
    conversation_history = Conversation.get_recent_messages(db, conversation_id)
    formatted_history = [
        {'role': msg['role'], 'content': msg['content']}
        for msg in conversation_history[:-1]  # 排除剛剛加入的訊息
    ]

    # 4. 查詢資料庫獲取推薦調酒
    cocktails = query_cocktails_from_db(db, user_message, limit=3)

    if cocktails:
        cocktail_info = "\n\n可推薦的調酒：\n"
        for i, c in enumerate(cocktails, 1):
            cocktail_info += f"{i}. {c['name']} (評分: {c.get('rating', 'N/A')}/5)\n"
        user_preferences['available_cocktails'] = cocktail_info
        current_app.logger.info(f"找到 {len(cocktails)} 個推薦調酒")

    # 5. 取得 AI 酒保回應
    ai_response = llm_service.get_bartender_response(
        user_message,
        formatted_history,
        user_preferences
    )

    # 6. 檢查是否需要責任飲酒警告
    needs_warning = should_warn_about_drinking(user_message, sentiment_score)

    if needs_warning and '責任飲酒' not in ai_response:
        ai_response += "\n\n💡 小提醒：請記得理性飲酒，過量飲酒有害健康。如果您要開車或有其他不適合飲酒的情況，我也可以推薦美味的無酒精飲料喔！"

    # 7. 儲存 AI 回應
    Conversation.add_message(db, conversation_id, 'assistant', ai_response)

    # 返回結果（包含追蹤元數據）
    return {
        'ai_response': ai_response,
        'sentiment_score': sentiment_score,
        'needs_warning': needs_warning,
        'recommended_cocktails_count': len(cocktails) if cocktails else 0,
        'conversation_length': len(formatted_history) + 2,
        'user_id': str(user_id)
    }


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
    """發送訊息並取得 AI 酒保回應"""
    try:
        from flask import current_app
        
        # 檢查 Groq 服務是否可用
        if not current_app.config.get('GROQ_ENABLED', False):
            return jsonify({
                'error': 'AI 對話服務暫時無法使用',
                'message': '請確認 Groq API Key 已正確設定',
                'tip': '請在 .env 檔案中設定 GROQ_API_KEY'
            }), 503
        
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({'error': '缺少訊息內容'}), 400
        
        user_message = data['message']
        conversation_id = data.get('conversation_id')
        
        db = current_app.config['DB']
        
        # 如果沒有提供 conversation_id，建立新對話
        if not conversation_id:
            conversation_id = Conversation.create(db, user_id)
        else:
            # 驗證對話是否存在
            conversation = Conversation.find_by_id(db, conversation_id)
            if not conversation:
                return jsonify({'error': '對話不存在'}), 404

        # 取得用戶偏好
        user = User.find_by_id(db, user_id)
        user_preferences = user.get('preferences', {}) if user else {}

        # 使用 LangSmith 追蹤的對話處理函數
        result = process_chat_message(
            db=db,
            user_id=user_id,
            user_message=user_message,
            conversation_id=conversation_id,
            user_preferences=user_preferences
        )

        return jsonify({
            'conversation_id': str(conversation_id),
            'message': result['ai_response'],
            'sentiment': result['sentiment_score'],
            'warning_issued': result['needs_warning']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"發送訊息錯誤: {str(e)}")
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

