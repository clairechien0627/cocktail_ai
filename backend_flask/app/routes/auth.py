from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """用戶註冊"""
    try:
        data = request.get_json()

        # 驗證必要欄位
        if not all(key in data for key in ['username', 'email', 'password']):
            return jsonify({'error': '缺少必要欄位'}), 400

        # 檢查 email 是否已被使用
        from flask import current_app
        db = current_app.config['DB']

        existing_user = User.find_by_email(db, data['email'])
        if existing_user:
            return jsonify({'error': '此 Email 已被使用'}), 400

        # 建立用戶
        user_id = User.create(db, data['username'], data['email'], data['password'])

        # 生成 JWT token
        access_token = create_access_token(identity=str(user_id))

        return jsonify({
            'message': '註冊成功',
            'access_token': access_token,
            'user_id': str(user_id)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用戶登入"""
    try:
        data = request.get_json()

        # 驗證必要欄位
        if not all(key in data for key in ['email', 'password']):
            return jsonify({'error': '缺少必要欄位'}), 400

        # 查找用戶
        from flask import current_app
        db = current_app.config['DB']

        user = User.find_by_email(db, data['email'])
        if not user:
            return jsonify({'error': 'Email 或密碼錯誤'}), 401

        # 驗證密碼
        if not User.verify_password(user, data['password']):
            return jsonify({'error': 'Email 或密碼錯誤'}), 401

        # 生成 JWT token
        access_token = create_access_token(identity=str(user['_id']))

        return jsonify({
            'message': '登入成功',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'preferences': user.get('preferences', {})
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """取得當前用戶資訊"""
    try:
        user_id = get_jwt_identity()

        from flask import current_app
        db = current_app.config['DB']

        user = User.find_by_id(db, user_id)
        if not user:
            return jsonify({'error': '用戶不存在'}), 404

        return jsonify({
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'preferences': user.get('preferences', {})
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """更新用戶偏好"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        from flask import current_app
        db = current_app.config['DB']

        # 更新偏好
        User.update_preferences(db, user_id, data.get('preferences', {}))

        return jsonify({'message': '偏好更新成功'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
