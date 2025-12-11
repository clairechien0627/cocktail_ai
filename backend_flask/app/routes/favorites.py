"""
收藏 API
提供調酒收藏功能的 REST API
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Favorite
from bson.objectid import ObjectId

favorites_bp = Blueprint('favorites', __name__, url_prefix='/api/favorites')


@favorites_bp.route('/', methods=['POST'])
@jwt_required()
def add_favorite():
    """添加收藏"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if 'cocktail_id' not in data:
            return jsonify({'error': '缺少調酒 ID'}), 400

        cocktail_id = data['cocktail_id']

        from flask import current_app
        db = current_app.config['DB']

        # 檢查調酒是否存在
        cocktail = db.cocktails.find_one({'_id': ObjectId(cocktail_id)})
        if not cocktail:
            return jsonify({'error': '調酒不存在'}), 404

        # 添加收藏
        result = Favorite.add(db, user_id, cocktail_id)

        if result is None:
            # 已經收藏過了
            return jsonify({'message': '已經收藏過此調酒'}), 200

        current_app.logger.info(f"✓ 用戶 {user_id} 收藏了調酒 {cocktail_id}")

        return jsonify({
            'message': '收藏成功',
            'favorite_id': str(result)
        }), 201

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"❌ 添加收藏失敗: {str(e)}")
        return jsonify({'error': f'添加收藏失敗: {str(e)}'}), 500


@favorites_bp.route('/<cocktail_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(cocktail_id):
    """取消收藏"""
    try:
        user_id = get_jwt_identity()

        from flask import current_app
        db = current_app.config['DB']

        # 取消收藏
        success = Favorite.remove(db, user_id, cocktail_id)

        if not success:
            return jsonify({'error': '未收藏此調酒'}), 404

        current_app.logger.info(f"✓ 用戶 {user_id} 取消收藏調酒 {cocktail_id}")

        return jsonify({'message': '取消收藏成功'}), 200

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"❌ 取消收藏失敗: {str(e)}")
        return jsonify({'error': f'取消收藏失敗: {str(e)}'}), 500


@favorites_bp.route('/', methods=['GET'])
@jwt_required()
def get_favorites():
    """獲取收藏列表（分頁）"""
    try:
        user_id = get_jwt_identity()

        # 獲取分頁參數
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # 限制 limit 範圍
        limit = min(max(limit, 1), 100)

        from flask import current_app
        db = current_app.config['DB']

        # 獲取收藏列表
        result = Favorite.find_by_user(db, user_id, page, limit)

        # 轉換 ObjectId 為字串
        for favorite in result['favorites']:
            favorite['_id'] = str(favorite['_id'])
            # 計算材料數量
            if 'ingredients' in favorite:
                favorite['ingredients_count'] = len(favorite['ingredients'])

        current_app.logger.info(f"✓ 用戶 {user_id} 查詢收藏列表: {result['total']} 個")

        return jsonify(result), 200

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"❌ 獲取收藏列表失敗: {str(e)}")
        return jsonify({'error': f'獲取收藏列表失敗: {str(e)}'}), 500


@favorites_bp.route('/<cocktail_id>/check', methods=['GET'])
@jwt_required()
def check_favorite(cocktail_id):
    """檢查是否已收藏"""
    try:
        user_id = get_jwt_identity()

        from flask import current_app
        db = current_app.config['DB']

        # 檢查是否已收藏
        is_favorited = Favorite.check_exists(db, user_id, cocktail_id)

        return jsonify({'is_favorited': is_favorited}), 200

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"❌ 檢查收藏狀態失敗: {str(e)}")
        return jsonify({'error': f'檢查收藏狀態失敗: {str(e)}'}), 500


@favorites_bp.route('/ids', methods=['GET'])
@jwt_required()
def get_favorited_ids():
    """獲取所有收藏的調酒 ID 列表"""
    try:
        user_id = get_jwt_identity()

        from flask import current_app
        db = current_app.config['DB']

        # 獲取所有收藏的調酒 ID
        favorited_ids = Favorite.get_favorited_ids(db, user_id)

        return jsonify({
            'favorited_ids': favorited_ids,
            'count': len(favorited_ids)
        }), 200

    except Exception as e:
        from flask import current_app
        current_app.logger.error(f"❌ 獲取收藏 ID 列表失敗: {str(e)}")
        return jsonify({'error': f'獲取收藏 ID 列表失敗: {str(e)}'}), 500
