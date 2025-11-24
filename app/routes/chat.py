from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Conversation, User
from app.services.llm_service import llm_service
from app.services.sentiment import analyze_sentiment, should_warn_about_drinking

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

        # 情感分析
        sentiment_score = analyze_sentiment(user_message)

        # 儲存用戶訊息
        Conversation.add_message(db, conversation_id, 'user', user_message, sentiment_score)

        # 取得用戶偏好
        user = User.find_by_id(db, user_id)
        user_preferences = user.get('preferences', {}) if user else {}

        # 取得對話歷史
        conversation_history = Conversation.get_recent_messages(db, conversation_id)
        formatted_history = [
            {'role': msg['role'], 'content': msg['content']}
            for msg in conversation_history[:-1]  # 排除剛剛加入的訊息
        ]

        # 取得 AI 酒保回應
        ai_response = llm_service.get_bartender_response(
            user_message,
            formatted_history,
            user_preferences
        )

        # 檢查是否需要責任飲酒警告
        needs_warning = should_warn_about_drinking(user_message, sentiment_score)
        if needs_warning and '責任飲酒' not in ai_response:
            ai_response += "\n\n💡 小提醒：請記得理性飲酒，過量飲酒有害健康。如果您要開車或有其他不適合飲酒的情況，我也可以推薦美味的無酒精飲料喔！"

        # 儲存 AI 回應
        Conversation.add_message(db, conversation_id, 'assistant', ai_response)

        return jsonify({
            'conversation_id': str(conversation_id),
            'message': ai_response,
            'sentiment': sentiment_score,
            'warning_issued': needs_warning
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
        db = current_app.config['DB']

        result = db.conversations.delete_one({'_id': conversation_id})

        if result.deleted_count == 0:
            return jsonify({'error': '對話不存在'}), 404

        return jsonify({'message': '對話已刪除'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
