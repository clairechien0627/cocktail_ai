from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import DrinkingRecord
from bson.objectid import ObjectId
from datetime import datetime

records_bp = Blueprint('records', __name__, url_prefix='/api/records')


@records_bp.route('/', methods=['POST'])
@jwt_required()
def create_record():
    """建立新飲用紀錄"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        db = current_app.config['DB']

        # 驗證必要欄位
        if 'cocktail_id' not in data:
            return jsonify({'error': '缺少 cocktail_id'}), 400

        # 處理時間欄位
        if 'drunk_at' in data and isinstance(data['drunk_at'], str):
            try:
                data['drunk_at'] = datetime.fromisoformat(data['drunk_at'].replace('Z', '+00:00'))
            except:
                data['drunk_at'] = datetime.utcnow()

        # 建立紀錄
        record_id = DrinkingRecord.create(db, user_id, data['cocktail_id'], data)

        return jsonify({
            'message': '飲用紀錄建立成功',
            'record_id': str(record_id)
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/', methods=['GET'])
@jwt_required()
def get_records():
    """取得我的飲用紀錄（支援篩選、分頁）"""
    try:
        user_id = get_jwt_identity()
        db = current_app.config['DB']

        # 取得查詢參數
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit

        # 篩選條件
        filters = {}
        if 'preference' in request.args:
            filters['preference'] = request.args.get('preference')

        if 'start_date' in request.args:
            try:
                filters['start_date'] = datetime.fromisoformat(
                    request.args.get('start_date').replace('Z', '+00:00')
                )
            except:
                pass

        if 'end_date' in request.args:
            try:
                filters['end_date'] = datetime.fromisoformat(
                    request.args.get('end_date').replace('Z', '+00:00')
                )
            except:
                pass

        if 'mood_tags' in request.args:
            mood_tags = request.args.get('mood_tags').split(',')
            filters['mood_tags'] = mood_tags

        # 排序
        sort_by = request.args.get('sort_by', 'drunk_at_desc')

        # 查詢紀錄
        records, total_count = DrinkingRecord.find_by_user(
            db, user_id, filters, skip, limit, sort_by
        )

        # 轉換 ObjectId 為字串
        for record in records:
            record['_id'] = str(record['_id'])
            record['user_id'] = str(record['user_id'])
            record['cocktail_id'] = str(record['cocktail_id'])
            # 轉換時間為 ISO 格式
            if 'drunk_at' in record:
                record['drunk_at'] = record['drunk_at'].isoformat()
            if 'created_at' in record:
                record['created_at'] = record['created_at'].isoformat()
            if 'updated_at' in record:
                record['updated_at'] = record['updated_at'].isoformat()

        return jsonify({
            'records': records,
            'total': total_count,
            'page': page,
            'limit': limit,
            'pages': (total_count + limit - 1) // limit
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/<record_id>', methods=['GET'])
@jwt_required()
def get_record(record_id):
    """取得特定飲用紀錄"""
    try:
        user_id = get_jwt_identity()
        db = current_app.config['DB']

        record = DrinkingRecord.find_by_id(db, record_id)
        if not record:
            return jsonify({'error': '找不到紀錄'}), 404

        # 驗證擁有者
        if str(record['user_id']) != user_id:
            return jsonify({'error': '無權限查看此紀錄'}), 403

        # 轉換 ObjectId 為字串
        record['_id'] = str(record['_id'])
        record['user_id'] = str(record['user_id'])
        record['cocktail_id'] = str(record['cocktail_id'])
        if 'drunk_at' in record:
            record['drunk_at'] = record['drunk_at'].isoformat()
        if 'created_at' in record:
            record['created_at'] = record['created_at'].isoformat()
        if 'updated_at' in record:
            record['updated_at'] = record['updated_at'].isoformat()

        return jsonify(record), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/<record_id>', methods=['PUT'])
@jwt_required()
def update_record(record_id):
    """更新飲用紀錄"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        db = current_app.config['DB']

        # 處理時間欄位
        if 'drunk_at' in data and isinstance(data['drunk_at'], str):
            try:
                data['drunk_at'] = datetime.fromisoformat(data['drunk_at'].replace('Z', '+00:00'))
            except:
                pass

        # 更新紀錄
        DrinkingRecord.update(db, record_id, user_id, data)

        return jsonify({'message': '紀錄更新成功'}), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/<record_id>', methods=['DELETE'])
@jwt_required()
def delete_record(record_id):
    """刪除飲用紀錄"""
    try:
        user_id = get_jwt_identity()
        db = current_app.config['DB']

        # 刪除紀錄
        success = DrinkingRecord.delete(db, record_id, user_id)

        if not success:
            return jsonify({'error': '找不到紀錄或無權限刪除'}), 404

        return jsonify({'message': '紀錄刪除成功'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """取得我的飲用統計資訊"""
    try:
        user_id = get_jwt_identity()
        db = current_app.config['DB']

        stats = DrinkingRecord.get_user_stats(db, user_id)

        # 轉換 ObjectId 為字串
        for cocktail in stats.get('most_drunk_cocktails', []):
            if '_id' in cocktail:
                cocktail['_id'] = str(cocktail['_id'])

        for cocktail in stats.get('favorite_cocktails', []):
            if '_id' in cocktail:
                cocktail['_id'] = str(cocktail['_id'])
            if 'last_drunk' in cocktail:
                cocktail['last_drunk'] = cocktail['last_drunk'].isoformat()

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """分析我的口味偏好"""
    try:
        user_id = get_jwt_identity()
        db = current_app.config['DB']

        preferences = DrinkingRecord.get_user_preferences(db, user_id)

        return jsonify(preferences), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """取得個人化推薦調酒

    查詢參數：
    - limit: 返回數量（預設 20）
    - exclude_ids: 已推薦過的調酒 ID 列表（逗號分隔）
    - exploration_mode: 'balanced' 或 'adventurous'（預設 balanced）
    """
    try:
        user_id = get_jwt_identity()
        db = current_app.config['DB']

        limit = int(request.args.get('limit', 20))

        # 解析 exclude_ids 參數
        exclude_ids_str = request.args.get('exclude_ids', '')
        exclude_ids = [id.strip() for id in exclude_ids_str.split(',') if id.strip()] if exclude_ids_str else None

        # 解析 exploration_mode 參數
        exploration_mode = request.args.get('exploration_mode', 'balanced')
        if exploration_mode not in ['balanced', 'adventurous']:
            exploration_mode = 'balanced'

        recommendations = DrinkingRecord.get_recommendations(
            db,
            user_id,
            limit,
            exclude_ids=exclude_ids,
            exploration_mode=exploration_mode
        )

        # 轉換 ObjectId 為字串
        for cocktail in recommendations:
            cocktail['_id'] = str(cocktail['_id'])
            if 'created_at' in cocktail and hasattr(cocktail['created_at'], 'isoformat'):
                cocktail['created_at'] = cocktail['created_at'].isoformat()
            if 'scraped_at' in cocktail and hasattr(cocktail['scraped_at'], 'isoformat'):
                cocktail['scraped_at'] = cocktail['scraped_at'].isoformat()

        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations),
            'exploration_mode': exploration_mode
        }), 200

    except Exception as e:
        import traceback
        print(f"推薦系統錯誤: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@records_bp.route('/cocktail/<cocktail_id>/check', methods=['GET'])
@jwt_required()
def check_drunk(cocktail_id):
    """檢查是否喝過某調酒"""
    try:
        user_id = get_jwt_identity()
        db = current_app.config['DB']

        # 先查詢調酒取得 ObjectId（支援 slug 或 ObjectId）
        cocktail = None

        # 嘗試用 slug 查詢
        cocktail = db.cocktails.find_one({"cocktail_id": cocktail_id})

        # 如果找不到，嘗試用 ObjectId 查詢
        if not cocktail:
            try:
                cocktail = db.cocktails.find_one({"_id": ObjectId(cocktail_id)})
            except:
                pass

        if not cocktail:
            return jsonify({'has_drunk': False}), 200  # 調酒不存在，視為未喝過

        # 使用調酒的 _id 檢查
        has_drunk = DrinkingRecord.check_if_drunk(db, user_id, str(cocktail['_id']))

        return jsonify({'has_drunk': has_drunk}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/cocktail/<cocktail_id>', methods=['GET'])
@jwt_required()
def get_cocktail_records(cocktail_id):
    """取得我對特定調酒的所有紀錄"""
    try:
        user_id = get_jwt_identity()
        db = current_app.config['DB']

        # 先查詢調酒取得 ObjectId（支援 slug 或 ObjectId）
        cocktail = db.cocktails.find_one({"cocktail_id": cocktail_id})
        if not cocktail:
            try:
                cocktail = db.cocktails.find_one({"_id": ObjectId(cocktail_id)})
            except:
                pass

        if not cocktail:
            return jsonify({'records': [], 'count': 0}), 200  # 調酒不存在

        # 使用調酒的 _id 查詢紀錄
        records = DrinkingRecord.get_cocktail_records(db, user_id, str(cocktail['_id']))

        # 轉換 ObjectId 為字串
        for record in records:
            record['_id'] = str(record['_id'])
            record['user_id'] = str(record['user_id'])
            record['cocktail_id'] = str(record['cocktail_id'])
            if 'drunk_at' in record:
                record['drunk_at'] = record['drunk_at'].isoformat()
            if 'created_at' in record:
                record['created_at'] = record['created_at'].isoformat()
            if 'updated_at' in record:
                record['updated_at'] = record['updated_at'].isoformat()

        return jsonify({
            'records': records,
            'count': len(records)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@records_bp.route('/mood-tags', methods=['GET'])
def get_mood_tags():
    """取得預設心情標籤選項（公開）"""
    return jsonify({'mood_tags': DrinkingRecord.DEFAULT_MOOD_TAGS}), 200
