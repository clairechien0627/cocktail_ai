"""
性格管理 API 路由
提供系統性格列表和用戶自訂性格的 CRUD 操作
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime

personalities_bp = Blueprint('personalities', __name__, url_prefix='/api/personalities')


@personalities_bp.route('/list', methods=['GET'])
def list_personalities():
    """
    列出所有可用性格

    Response:
        {
            "system": [...],  # 系統預設性格
            "custom": [...]   # 用戶自訂性格（需登入）
        }
    """
    db = current_app.config['DB']

    # 1. 系統預設性格
    from app.services.personality_manager import PersonalityManager
    personality_manager = PersonalityManager(db)
    system_personalities = personality_manager.get_system_personalities()

    # 2. 用戶自訂性格（需登入）
    custom_personalities = []
    try:
        # 如果有 JWT token，載入用戶自訂性格
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()

        if user_id:
            custom_docs = db.personalities.find({
                'type': 'custom',
                'user_id': ObjectId(user_id)
            })

            for doc in custom_docs:
                custom_personalities.append({
                    'personality_id': doc['personality_id'],
                    'name': doc['name'],
                    'description': doc['description'],
                    'icon': doc.get('icon', '🍹'),
                    'type': 'custom'
                })
    except:
        # 未登入或 JWT 無效，只返回系統性格
        pass

    return jsonify({
        'system': system_personalities,
        'custom': custom_personalities
    }), 200


@personalities_bp.route('/<personality_id>', methods=['GET'])
def get_personality(personality_id):
    """
    獲取特定性格的詳細資訊

    Args:
        personality_id: 性格 ID

    Response:
        性格完整資訊（包含 prompt 細節）
    """
    db = current_app.config['DB']

    # 系統性格
    if not personality_id.startswith('custom_'):
        from app.services.personality_manager import PersonalityManager
        personality_manager = PersonalityManager(db)
        system_list = personality_manager.get_system_personalities()

        for p in system_list:
            if p['personality_id'] == personality_id:
                return jsonify(p), 200

        return jsonify({'error': '找不到該性格'}), 404

    # 自訂性格
    personality = db.personalities.find_one({'personality_id': personality_id})

    if not personality:
        return jsonify({'error': '找不到該性格'}), 404

    # 轉換 ObjectId 為字串
    personality['_id'] = str(personality['_id'])
    if 'user_id' in personality:
        personality['user_id'] = str(personality['user_id'])

    return jsonify(personality), 200


@personalities_bp.route('/create', methods=['POST'])
@jwt_required()
def create_custom_personality():
    """
    創建自訂性格

    Request Body:
        {
            "name": "我的專屬酒保",
            "description": "結合專業和幽默",
            "icon": "🔬",
            "prompt": {
                "tone": "專業但不失幽默",
                "style": "用專業術語解釋，但加入有趣的比喻",
                "greeting": "歡迎！準備好進入調酒的科學與藝術了嗎？",
                "example_responses": ["..."],
                "custom_rules": ["..."]
            },
            "is_public": false
        }
    """
    db = current_app.config['DB']
    user_id = ObjectId(get_jwt_identity())
    data = request.get_json()

    # 驗證必要欄位
    if not data.get('name'):
        return jsonify({'error': '缺少性格名稱'}), 400

    if not data.get('prompt'):
        return jsonify({'error': '缺少性格設定'}), 400

    prompt = data.get('prompt', {})
    if not prompt.get('tone') or not prompt.get('style'):
        return jsonify({'error': 'Prompt 必須包含 tone 和 style'}), 400

    # 限制自訂性格數量（每個用戶最多 10 個）
    user_custom_count = db.personalities.count_documents({
        'type': 'custom',
        'user_id': user_id
    })

    if user_custom_count >= 10:
        return jsonify({'error': '已達到自訂性格上限（10 個）'}), 400

    # 創建性格文檔
    personality_id = f"custom_{ObjectId()}"
    personality = {
        'type': 'custom',
        'personality_id': personality_id,
        'user_id': user_id,
        'name': data.get('name'),
        'description': data.get('description', ''),
        'icon': data.get('icon', '🍹'),
        'prompt': {
            'tone': prompt.get('tone'),
            'style': prompt.get('style'),
            'greeting': prompt.get('greeting', ''),
            'example_responses': prompt.get('example_responses', []),
            'custom_rules': prompt.get('custom_rules', [])
        },
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

    # 插入資料庫
    result = db.personalities.insert_one(personality)

    return jsonify({
        'message': '自訂性格創建成功',
        'personality_id': personality_id
    }), 201


@personalities_bp.route('/<personality_id>', methods=['PUT'])
@jwt_required()
def update_custom_personality(personality_id):
    """
    更新自訂性格

    Args:
        personality_id: 性格 ID

    Request Body:
        要更新的欄位（與創建相同）
    """
    db = current_app.config['DB']
    user_id = ObjectId(get_jwt_identity())
    data = request.get_json()

    # 檢查性格是否存在且屬於該用戶
    personality = db.personalities.find_one({
        'personality_id': personality_id,
        'type': 'custom',
        'user_id': user_id
    })

    if not personality:
        return jsonify({'error': '找不到該性格或無權限修改'}), 404

    # 準備更新資料
    update_data = {'updated_at': datetime.utcnow()}

    if 'name' in data:
        update_data['name'] = data['name']

    if 'description' in data:
        update_data['description'] = data['description']

    if 'icon' in data:
        update_data['icon'] = data['icon']

    if 'prompt' in data:
        prompt = data['prompt']
        update_data['prompt'] = {
            'tone': prompt.get('tone', personality['prompt'].get('tone', '')),
            'style': prompt.get('style', personality['prompt'].get('style', '')),
            'greeting': prompt.get('greeting', personality['prompt'].get('greeting', '')),
            'example_responses': prompt.get('example_responses', personality['prompt'].get('example_responses', [])),
            'custom_rules': prompt.get('custom_rules', personality['prompt'].get('custom_rules', []))
        }

    # 更新資料庫
    db.personalities.update_one(
        {'_id': personality['_id']},
        {'$set': update_data}
    )

    return jsonify({'message': '性格更新成功'}), 200


@personalities_bp.route('/<personality_id>', methods=['DELETE'])
@jwt_required()
def delete_custom_personality(personality_id):
    """
    刪除自訂性格

    Args:
        personality_id: 性格 ID
    """
    db = current_app.config['DB']
    user_id = ObjectId(get_jwt_identity())

    # 檢查性格是否存在且屬於該用戶
    result = db.personalities.delete_one({
        'personality_id': personality_id,
        'type': 'custom',
        'user_id': user_id
    })

    if result.deleted_count == 0:
        return jsonify({'error': '找不到該性格或無權限刪除'}), 404

    return jsonify({'message': '性格刪除成功'}), 200


