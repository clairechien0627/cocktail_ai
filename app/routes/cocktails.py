from flask import Blueprint, request, jsonify
from app.models import Cocktail

cocktails_bp = Blueprint('cocktails', __name__, url_prefix='/api/cocktails')


@cocktails_bp.route('/', methods=['GET'])
def get_all_cocktails():
    """取得所有調酒"""
    try:
        from flask import current_app
        db = current_app.config['DB']

        # 分頁參數
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit

        cocktails = Cocktail.find_all(db, skip, limit)

        # 轉換 ObjectId 為字串
        for cocktail in cocktails:
            cocktail['_id'] = str(cocktail['_id'])

        # 計算總數
        total = db.cocktails.count_documents({})

        return jsonify({
            'cocktails': cocktails,
            'page': page,
            'limit': limit,
            'total': total,
            'total_pages': (total + limit - 1) // limit
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cocktails_bp.route('/<cocktail_id>', methods=['GET'])
def get_cocktail(cocktail_id):
    """取得特定調酒"""
    try:
        from flask import current_app
        db = current_app.config['DB']

        cocktail = Cocktail.find_by_id(db, cocktail_id)
        if not cocktail:
            return jsonify({'error': '調酒不存在'}), 404

        cocktail['_id'] = str(cocktail['_id'])

        return jsonify({'cocktail': cocktail}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cocktails_bp.route('/search', methods=['GET'])
def search_cocktails():
    """搜尋調酒"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': '缺少搜尋關鍵字'}), 400

        from flask import current_app
        db = current_app.config['DB']

        cocktails = Cocktail.search(db, query)

        # 轉換 ObjectId 為字串
        for cocktail in cocktails:
            cocktail['_id'] = str(cocktail['_id'])

        return jsonify({
            'cocktails': cocktails,
            'count': len(cocktails)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cocktails_bp.route('/category/<category>', methods=['GET'])
def get_cocktails_by_category(category):
    """根據分類取得調酒"""
    try:
        from flask import current_app
        db = current_app.config['DB']

        cocktails = Cocktail.find_by_category(db, category)

        # 轉換 ObjectId 為字串
        for cocktail in cocktails:
            cocktail['_id'] = str(cocktail['_id'])

        return jsonify({
            'cocktails': cocktails,
            'category': category,
            'count': len(cocktails)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cocktails_bp.route('/categories', methods=['GET'])
def get_categories():
    """取得所有分類"""
    try:
        from flask import current_app
        db = current_app.config['DB']

        # 取得所有不重複的分類
        categories = db.cocktails.distinct('category')

        return jsonify({'categories': categories}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cocktails_bp.route('/random', methods=['GET'])
def get_random_cocktail():
    """隨機取得一個調酒"""
    try:
        from flask import current_app
        db = current_app.config['DB']

        # 使用聚合管道隨機取得一個調酒
        cocktails = list(db.cocktails.aggregate([{'$sample': {'size': 1}}]))

        if not cocktails:
            return jsonify({'error': '沒有調酒資料'}), 404

        cocktail = cocktails[0]
        cocktail['_id'] = str(cocktail['_id'])

        return jsonify({'cocktail': cocktail}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cocktails_bp.route('/filter', methods=['GET'])
def filter_cocktails():
    """進階篩選調酒

    查詢參數：
    - min_rating: 最低評分 (0-5)
    - max_rating: 最高評分 (0-5)
    - min_strength: 最低酒精強度 (0-10)
    - max_strength: 最高酒精強度 (0-10)
    - min_sweetness: 最低甜度 (0-10)
    - max_sweetness: 最高甜度 (0-10)
    - max_calories: 最大卡路里
    - difficulty: 難度 (easy/medium/hard)
    - category: 分類
    - has_history: 是否有歷史故事 (true/false)
    - sort_by: 排序方式 (rating_desc, strength_desc, calories_asc, popular 等)
    - page: 頁碼 (預設 1)
    - limit: 每頁筆數 (預設 20)
    """
    try:
        from flask import current_app
        db = current_app.config['DB']

        # 建立篩選條件
        filters = {}

        # 評分篩選
        if request.args.get('min_rating'):
            filters['min_rating'] = request.args.get('min_rating')
        if request.args.get('max_rating'):
            filters['max_rating'] = request.args.get('max_rating')

        # 風味篩選
        if request.args.get('min_strength'):
            filters['min_strength'] = request.args.get('min_strength')
        if request.args.get('max_strength'):
            filters['max_strength'] = request.args.get('max_strength')
        if request.args.get('min_sweetness'):
            filters['min_sweetness'] = request.args.get('min_sweetness')
        if request.args.get('max_sweetness'):
            filters['max_sweetness'] = request.args.get('max_sweetness')

        # 其他篩選
        if request.args.get('max_calories'):
            filters['max_calories'] = request.args.get('max_calories')
        if request.args.get('difficulty'):
            filters['difficulty'] = request.args.get('difficulty')
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        if request.args.get('has_history') == 'true':
            filters['has_history'] = True

        # 分頁參數
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit

        # 排序方式
        sort_by = request.args.get('sort_by', 'name')

        # 執行篩選
        cocktails = Cocktail.filter_cocktails(db, filters, skip, limit, sort_by)

        # 轉換 ObjectId 為字串
        for cocktail in cocktails:
            cocktail['_id'] = str(cocktail['_id'])

        return jsonify({
            'cocktails': cocktails,
            'count': len(cocktails),
            'page': page,
            'limit': limit
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cocktails_bp.route('/stats', methods=['GET'])
def get_statistics():
    """取得調酒統計資訊"""
    try:
        from flask import current_app
        db = current_app.config['DB']

        stats = Cocktail.get_statistics(db)

        return jsonify({
            'total_cocktails': stats.get('total', 0),
            'average_rating': round(stats.get('avg_rating', 0), 2) if stats.get('avg_rating') else 0,
            'categories': stats.get('categories', [])
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
