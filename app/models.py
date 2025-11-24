from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """用戶模型"""

    @staticmethod
    def create(db, username, email, password):
        """建立新用戶"""
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'preferences': {
                'favorite_spirits': [],
                'skill_level': 'beginner'
            },
            'created_at': datetime.utcnow()
        }
        result = db.users.insert_one(user_data)
        return result.inserted_id

    @staticmethod
    def find_by_email(db, email):
        """透過 email 查找用戶"""
        return db.users.find_one({'email': email})

    @staticmethod
    def find_by_id(db, user_id):
        """透過 ID 查找用戶"""
        return db.users.find_one({'_id': ObjectId(user_id)})

    @staticmethod
    def verify_password(user, password):
        """驗證密碼"""
        return check_password_hash(user['password_hash'], password)

    @staticmethod
    def update_preferences(db, user_id, preferences):
        """更新用戶偏好"""
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'preferences': preferences}}
        )


class Conversation:
    """對話模型"""

    @staticmethod
    def create(db, user_id):
        """建立新對話"""
        conversation_data = {
            'user_id': ObjectId(user_id),
            'messages': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.conversations.insert_one(conversation_data)
        return result.inserted_id

    @staticmethod
    def add_message(db, conversation_id, role, content, sentiment=None):
        """新增訊息到對話"""
        message = {
            'role': role,  # 'user' 或 'assistant'
            'content': content,
            'sentiment': sentiment,
            'timestamp': datetime.utcnow()
        }
        db.conversations.update_one(
            {'_id': ObjectId(conversation_id)},
            {
                '$push': {'messages': message},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return message

    @staticmethod
    def find_by_user(db, user_id, limit=10):
        """查找用戶的對話記錄"""
        return list(db.conversations.find(
            {'user_id': ObjectId(user_id)}
        ).sort('updated_at', -1).limit(limit))

    @staticmethod
    def find_by_id(db, conversation_id):
        """透過 ID 查找對話"""
        return db.conversations.find_one({'_id': ObjectId(conversation_id)})

    @staticmethod
    def get_recent_messages(db, conversation_id, limit=10):
        """取得最近的訊息"""
        conversation = db.conversations.find_one({'_id': ObjectId(conversation_id)})
        if conversation and 'messages' in conversation:
            return conversation['messages'][-limit:]
        return []


class Cocktail:
    """調酒模型（支援完整 Difford's Guide 資料）"""

    @staticmethod
    def create(db, data):
        """建立新調酒（支援完整 Difford's Guide schema）"""
        cocktail_data = {
            # 基本資訊
            'name': data.get('name'),
            'slug': data.get('slug'),
            'category': data.get('category'),
            'original_url': data.get('original_url') or data.get('url'),
            'detail_url': data.get('detail_url'),
            'image_url': data.get('image_url') or data.get('image'),

            # 材料資訊
            'ingredients': data.get('ingredients', []),  # 簡單列表
            'ingredients_detail': data.get('ingredients_detail', []),  # 詳細配方（含份量）

            # 製作方法
            'method': data.get('method', []),  # 簡單步驟列表
            'method_sections': data.get('method_sections', []),  # 結構化步驟（準備/製作/裝飾）
            'garnish': data.get('garnish', []),

            # 評分系統
            'ratings': {
                'professional': data.get('rating_detail', {}).get('diffords_rating'),
                'public': data.get('rating_detail', {}).get('public_rating'),
                'public_count': data.get('rating_detail', {}).get('public_rating_count', 0)
            } if data.get('rating_detail') else None,

            # 風味檔案
            'taste_profile': {
                'strength': data.get('strength_taste', {}).get('strength', {}).get('value'),
                'sweetness': data.get('strength_taste', {}).get('sweetness', {}).get('value')
            } if data.get('strength_taste') else None,

            # 營養資訊
            'nutrition': {
                'calories': data.get('nutrition', {}).get('calories')
            } if data.get('nutrition') else None,

            # 酒精指標
            'alcohol_metrics': {
                'abv': data.get('alcohol_content', {}).get('abv_percent'),
                'standard_drinks': data.get('alcohol_content', {}).get('standard_drinks'),
                'proof': data.get('alcohol_content', {}).get('proof'),
                'pure_alcohol_grams': data.get('alcohol_content', {}).get('pure_alcohol_grams')
            } if data.get('alcohol_content') and isinstance(data.get('alcohol_content'), dict) else {
                'abv': data.get('alcohol_content') if isinstance(data.get('alcohol_content'), (int, float)) else None
            },

            # 杯具資訊
            'glass': data.get('glass', {}).get('text') if data.get('glass') else None,

            # 歷史與故事
            'history': data.get('history', {}).get('paragraphs', []) if data.get('history') else [],

            # 專業評論
            'review': data.get('review', []),

            # 相關變化版本
            'variants': data.get('variants', []),

            # 過敏原資訊
            'allergens': data.get('allergens', []),

            # 分類與標籤
            'difficulty': data.get('difficulty', 'medium'),
            'tags': data.get('tags', []),

            # 元數據
            'scraped_at': data.get('scraped_at'),
            'created_at': datetime.utcnow()
        }
        result = db.cocktails.insert_one(cocktail_data)
        return result.inserted_id

    @staticmethod
    def find_all(db, skip=0, limit=100):
        """查找所有調酒"""
        return list(db.cocktails.find().skip(skip).limit(limit))

    @staticmethod
    def find_by_id(db, cocktail_id):
        """透過 ID 查找調酒"""
        return db.cocktails.find_one({'_id': ObjectId(cocktail_id)})

    @staticmethod
    def find_by_name(db, name):
        """透過名稱查找調酒（模糊搜尋）"""
        return list(db.cocktails.find({
            'name': {'$regex': name, '$options': 'i'}
        }))

    @staticmethod
    def find_by_category(db, category):
        """透過分類查找調酒"""
        return list(db.cocktails.find({'category': category}))

    @staticmethod
    def search(db, query):
        """搜尋調酒（名稱或材料）"""
        return list(db.cocktails.find({
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'ingredients': {'$regex': query, '$options': 'i'}},
                {'tags': {'$regex': query, '$options': 'i'}}
            ]
        }))

    @staticmethod
    def filter_cocktails(db, filters, skip=0, limit=100, sort_by=None):
        """進階篩選調酒

        Args:
            filters: 篩選條件字典
                - min_rating: 最低評分 (0-5)
                - max_rating: 最高評分 (0-5)
                - min_strength: 最低酒精強度 (0-10)
                - max_strength: 最高酒精強度 (0-10)
                - min_sweetness: 最低甜度 (0-10)
                - max_sweetness: 最高甜度 (0-10)
                - max_calories: 最大卡路里
                - difficulty: 難度（'easy', 'medium', 'hard'）
                - category: 分類
                - has_history: 是否有歷史故事
            sort_by: 排序方式 ('rating_desc', 'rating_asc', 'strength_desc', 'calories_asc' 等)
        """
        query = {}

        # 評分篩選
        if 'min_rating' in filters:
            query['ratings.professional'] = {'$gte': float(filters['min_rating'])}
        if 'max_rating' in filters:
            if 'ratings.professional' in query:
                query['ratings.professional']['$lte'] = float(filters['max_rating'])
            else:
                query['ratings.professional'] = {'$lte': float(filters['max_rating'])}

        # 風味檔案篩選
        if 'min_strength' in filters:
            query['taste_profile.strength'] = {'$gte': int(filters['min_strength'])}
        if 'max_strength' in filters:
            if 'taste_profile.strength' in query:
                query['taste_profile.strength']['$lte'] = int(filters['max_strength'])
            else:
                query['taste_profile.strength'] = {'$lte': int(filters['max_strength'])}

        if 'min_sweetness' in filters:
            query['taste_profile.sweetness'] = {'$gte': int(filters['min_sweetness'])}
        if 'max_sweetness' in filters:
            if 'taste_profile.sweetness' in query:
                query['taste_profile.sweetness']['$lte'] = int(filters['max_sweetness'])
            else:
                query['taste_profile.sweetness'] = {'$lte': int(filters['max_sweetness'])}

        # 卡路里篩選
        if 'max_calories' in filters:
            query['nutrition.calories'] = {'$lte': int(filters['max_calories'])}

        # 難度篩選
        if 'difficulty' in filters:
            query['difficulty'] = filters['difficulty']

        # 分類篩選
        if 'category' in filters:
            query['category'] = filters['category']

        # 歷史故事篩選
        if filters.get('has_history'):
            query['history'] = {'$exists': True, '$ne': []}

        # 排序
        sort_params = []
        if sort_by == 'rating_desc':
            sort_params = [('ratings.professional', -1)]
        elif sort_by == 'rating_asc':
            sort_params = [('ratings.professional', 1)]
        elif sort_by == 'strength_desc':
            sort_params = [('taste_profile.strength', -1)]
        elif sort_by == 'strength_asc':
            sort_params = [('taste_profile.strength', 1)]
        elif sort_by == 'calories_asc':
            sort_params = [('nutrition.calories', 1)]
        elif sort_by == 'calories_desc':
            sort_params = [('nutrition.calories', -1)]
        elif sort_by == 'popular':
            sort_params = [('ratings.public_count', -1)]
        else:
            sort_params = [('name', 1)]  # 預設按名稱排序

        cursor = db.cocktails.find(query).skip(skip).limit(limit)
        if sort_params:
            cursor = cursor.sort(sort_params)

        return list(cursor)

    @staticmethod
    def get_statistics(db):
        """取得調酒統計資訊"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total': {'$sum': 1},
                    'avg_rating': {'$avg': '$ratings.professional'},
                    'categories': {'$addToSet': '$category'}
                }
            }
        ]
        result = list(db.cocktails.aggregate(pipeline))
        if result:
            return result[0]
        return {'total': 0, 'avg_rating': 0, 'categories': []}
