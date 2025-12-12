from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import random
from collections import Counter

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
    def add_message(db, conversation_id, role, content, sentiment=None, cocktails=None):
        """新增訊息到對話"""
        message = {
            'role': role,  # 'user' 或 'assistant'
            'content': content,
            'sentiment': sentiment,
            'timestamp': datetime.utcnow()
        }

        # 新增：如果有調酒推薦資料，則加入訊息中
        if cocktails is not None:
            message['cocktails'] = cocktails

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
        """建立新調酒（只存英文主資料，中文另外進 cocktails_zh）"""
        cocktail_id = data.get('slug') or data.get('cocktail_id')

        cocktail_data = {
            # 共同 id，之後用來對應 cocktails_zh
            'cocktail_id': cocktail_id,

            # 基本資訊
            'name': data.get('name'),
            'slug': data.get('slug'),
            'category': data.get('category'),
            'original_url': data.get('original_url') or data.get('url'),
            'detail_url': data.get('detail_url'),
            'image_url': data.get('image_url') or data.get('image'),

            # 材料資訊
            'ingredients': data.get('ingredients', []),
            'ingredients_detail': data.get('ingredients_detail', []),

            # 製作方法
            'method_sections': [
                {
                    "title": s.get("title"),
                    "steps": [st for st in s.get("steps", []) if st and st.strip().lower() != "none"]
                }
                for s in data.get("method_sections", [])
                if any(st and st.strip().lower() != "none" for st in s.get("steps", []))
            ],

            # 評分系統
            'ratings': {
                'professional': data.get('rating_detail', {}).get('diffords_rating'),
                'public': data.get('rating_detail', {}).get('public_rating'),
                'public_count': data.get('rating_detail', {}).get('public_rating_count', 0)
            } if data.get('rating_detail') else None,

            # 風味檔案
            'taste_profile': {
                'strength': data.get('strength_taste', {}).get('strength', {}).get('value')
                        if isinstance(data.get('strength_taste', {}).get('strength'), dict)
                        else None,
                'sweetness': data.get('strength_taste', {}).get('sweetness', {}).get('value')
                            if isinstance(data.get('strength_taste', {}).get('sweetness'), dict)
                            else None
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
            'glass': data.get('glass') or None,

            # 歷史與故事
            'history': data.get('history', {}).get('paragraphs', []) if data.get('history') else [],

            # 專業評論
            'review': data.get('review', []),

            # 相關變化版本
            'variants': data.get('variants', []),

            # 過敏原資訊
            'allergens': data.get('allergens', []),

            # COTD 資訊
            'cotd': data.get('cotd'),

            # 分類與標籤
            'difficulty': data.get('difficulty', 'medium'),
            'tags': data.get('tags', []),
            'tags_categorized': data.get('tags_categorized', {}),  # 分類化的 tags
            'more_categories': data.get('more_categories', []),

            # 元數據
            'scraped_at': data.get('scraped_at'),
            'created_at': datetime.utcnow(),
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
                - more_category: More Categories 分類
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

        # More Categories 篩選
        if 'more_category' in filters:
            query['more_categories'] = filters['more_category']

        # Tag 篩選（多選，OR 邏輯）
        if 'tags' in filters and filters['tags']:
            tag_list = filters['tags'] if isinstance(filters['tags'], list) else [filters['tags']]
            query['tags'] = {'$in': tag_list}

        # 分類化 Tag 篩選（精確匹配）
        if 'base_spirit' in filters:
            query['tags_categorized.base_spirits'] = filters['base_spirit']

        if 'flavor' in filters:
            # 支援多選
            if isinstance(filters['flavor'], list):
                query['tags_categorized.flavors'] = {'$in': filters['flavor']}
            else:
                query['tags_categorized.flavors'] = filters['flavor']

        if 'ingredient_tag' in filters:
            query['tags_categorized.ingredients'] = filters['ingredient_tag']

        if 'style' in filters:
            if isinstance(filters['style'], list):
                query['tags_categorized.styles'] = {'$in': filters['style']}
            else:
                query['tags_categorized.styles'] = filters['style']

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

        # 計算符合條件的總數
        total_count = db.cocktails.count_documents(query)

        cursor = db.cocktails.find(query).skip(skip).limit(limit)
        if sort_params:
            cursor = cursor.sort(sort_params)

        return list(cursor), total_count

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


class DrinkingRecord:
    """飲用紀錄模型（私人日記）"""

    # 預設心情標籤選項
    DEFAULT_MOOD_TAGS = [
        "慶祝", "放鬆", "約會", "聚會", "獨飲", "嘗鮮",
        "工作後", "週末", "特殊場合", "日常", "懷舊", "冒險"
    ]

    @staticmethod
    def create(db, user_id, cocktail_id, data):
        """建立新飲用紀錄

        Args:
            user_id: 用戶 ID
            cocktail_id: 調酒 ID
            data: 紀錄資料
                - preference: 喜好程度 ("loved", "liked", "neutral", "disliked")
                - notes: 個人評論與感想
                - drunk_at: 飲用時間（datetime）
                - location: 地點（可選）
                - mood_tags: 心情/場合標籤列表
        """
        # 獲取調酒快照（保存調酒資訊，即使調酒被刪除也能查看）
        cocktail = db.cocktails.find_one({'_id': ObjectId(cocktail_id)})
        if not cocktail:
            raise ValueError("Cocktail not found")

        cocktail_snapshot = {
            'name': cocktail.get('name'),
            'image_url': cocktail.get('image_url'),
            'category': cocktail.get('category'),
            'taste_profile': cocktail.get('taste_profile'),
            'tags_categorized': cocktail.get('tags_categorized', {})
        }

        record_data = {
            'user_id': ObjectId(user_id),
            'cocktail_id': ObjectId(cocktail_id),
            'cocktail_snapshot': cocktail_snapshot,
            'preference': data.get('preference', 'neutral'),  # loved, liked, neutral, disliked
            'notes': data.get('notes', ''),
            'drunk_at': data.get('drunk_at', datetime.utcnow()),
            'location': data.get('location'),
            'mood_tags': data.get('mood_tags', []),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = db.drinking_records.insert_one(record_data)
        return result.inserted_id

    @staticmethod
    def find_by_user(db, user_id, filters=None, skip=0, limit=20, sort_by='drunk_at_desc'):
        """查詢用戶的所有飲用紀錄

        Args:
            filters: 篩選條件
                - preference: 偏好程度
                - start_date: 開始日期
                - end_date: 結束日期
                - mood_tags: 心情標籤
            sort_by: 排序方式 ('drunk_at_desc', 'drunk_at_asc', 'created_desc')
        """
        query = {'user_id': ObjectId(user_id)}

        # 應用篩選條件
        if filters:
            if 'preference' in filters:
                query['preference'] = filters['preference']

            if 'start_date' in filters or 'end_date' in filters:
                query['drunk_at'] = {}
                if 'start_date' in filters:
                    query['drunk_at']['$gte'] = filters['start_date']
                if 'end_date' in filters:
                    query['drunk_at']['$lte'] = filters['end_date']

            if 'mood_tags' in filters and filters['mood_tags']:
                query['mood_tags'] = {'$in': filters['mood_tags']}

        # 排序
        sort_params = []
        if sort_by == 'drunk_at_desc':
            sort_params = [('drunk_at', -1)]
        elif sort_by == 'drunk_at_asc':
            sort_params = [('drunk_at', 1)]
        elif sort_by == 'created_desc':
            sort_params = [('created_at', -1)]
        else:
            sort_params = [('drunk_at', -1)]

        # 計算總數
        total_count = db.drinking_records.count_documents(query)

        # 查詢
        cursor = db.drinking_records.find(query).skip(skip).limit(limit).sort(sort_params)
        return list(cursor), total_count

    @staticmethod
    def find_by_id(db, record_id):
        """透過 ID 查找紀錄"""
        return db.drinking_records.find_one({'_id': ObjectId(record_id)})

    @staticmethod
    def update(db, record_id, user_id, data):
        """更新飲用紀錄（僅允許擁有者更新）"""
        # 驗證擁有者
        record = db.drinking_records.find_one({
            '_id': ObjectId(record_id),
            'user_id': ObjectId(user_id)
        })
        if not record:
            raise ValueError("Record not found or unauthorized")

        update_data = {'updated_at': datetime.utcnow()}

        # 允許更新的欄位
        allowed_fields = ['preference', 'notes', 'drunk_at', 'location', 'mood_tags']
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        db.drinking_records.update_one(
            {'_id': ObjectId(record_id)},
            {'$set': update_data}
        )
        return True

    @staticmethod
    def delete(db, record_id, user_id):
        """刪除飲用紀錄（僅允許擁有者刪除）"""
        result = db.drinking_records.delete_one({
            '_id': ObjectId(record_id),
            'user_id': ObjectId(user_id)
        })
        return result.deleted_count > 0

    @staticmethod
    def get_user_stats(db, user_id):
        """取得用戶的飲用統計資訊

        Returns:
            - total_drinks: 總飲用杯數
            - preference_distribution: 偏好分佈
            - most_drunk_cocktails: 最常喝的調酒 Top 5
            - favorite_cocktails: 最喜歡的調酒 Top 5
            - recent_drinks: 最近 5 杯
        """
        pipeline = [
            {'$match': {'user_id': ObjectId(user_id)}},
            {
                '$facet': {
                    # 總數與偏好分佈
                    'overview': [
                        {
                            '$group': {
                                '_id': None,
                                'total_drinks': {'$sum': 1},
                                'loved_count': {
                                    '$sum': {'$cond': [{'$eq': ['$preference', 'loved']}, 1, 0]}
                                },
                                'liked_count': {
                                    '$sum': {'$cond': [{'$eq': ['$preference', 'liked']}, 1, 0]}
                                },
                                'neutral_count': {
                                    '$sum': {'$cond': [{'$eq': ['$preference', 'neutral']}, 1, 0]}
                                },
                                'disliked_count': {
                                    '$sum': {'$cond': [{'$eq': ['$preference', 'disliked']}, 1, 0]}
                                }
                            }
                        }
                    ],
                    # 最常喝的調酒
                    'most_drunk': [
                        {
                            '$group': {
                                '_id': '$cocktail_id',
                                'count': {'$sum': 1},
                                'cocktail_name': {'$first': '$cocktail_snapshot.name'},
                                'cocktail_image': {'$first': '$cocktail_snapshot.image_url'}
                            }
                        },
                        {'$sort': {'count': -1}},
                        {'$limit': 5}
                    ],
                    # 最喜歡的調酒（loved + liked）
                    'favorites': [
                        {'$match': {'preference': {'$in': ['loved', 'liked']}}},
                        {
                            '$group': {
                                '_id': '$cocktail_id',
                                'preference': {'$first': '$preference'},
                                'cocktail_name': {'$first': '$cocktail_snapshot.name'},
                                'cocktail_image': {'$first': '$cocktail_snapshot.image_url'},
                                'last_drunk': {'$max': '$drunk_at'}
                            }
                        },
                        {'$sort': {'last_drunk': -1}},
                        {'$limit': 5}
                    ]
                }
            }
        ]

        result = list(db.drinking_records.aggregate(pipeline))
        if result:
            stats = result[0]
            return {
                'total_drinks': stats['overview'][0]['total_drinks'] if stats['overview'] else 0,
                'preference_distribution': {
                    'loved': stats['overview'][0]['loved_count'] if stats['overview'] else 0,
                    'liked': stats['overview'][0]['liked_count'] if stats['overview'] else 0,
                    'neutral': stats['overview'][0]['neutral_count'] if stats['overview'] else 0,
                    'disliked': stats['overview'][0]['disliked_count'] if stats['overview'] else 0
                },
                'most_drunk_cocktails': stats['most_drunk'],
                'favorite_cocktails': stats['favorites']
            }

        return {
            'total_drinks': 0,
            'preference_distribution': {'loved': 0, 'liked': 0, 'neutral': 0, 'disliked': 0},
            'most_drunk_cocktails': [],
            'favorite_cocktails': []
        }

    @staticmethod
    def get_user_preferences(db, user_id):
        """分析用戶的口味偏好

        Returns:
            - favorite_tags: 最愛的 base_spirits, flavors, styles
            - taste_range: 口味偏好範圍（甜度、酒精強度）
            - time_distribution: 飲用時段分佈
            - mood_distribution: 心情/場合分佈
        """
        pipeline = [
            {'$match': {
                'user_id': ObjectId(user_id),
                'preference': {'$in': ['loved', 'liked']}  # 只分析喜歡的調酒
            }},
            {
                '$facet': {
                    # Tags 偏好分析
                    'tags_analysis': [
                        {
                            '$project': {
                                'base_spirits': '$cocktail_snapshot.tags_categorized.base_spirits',
                                'flavors': '$cocktail_snapshot.tags_categorized.flavors',
                                'styles': '$cocktail_snapshot.tags_categorized.styles',
                                'strength': '$cocktail_snapshot.taste_profile.strength',
                                'sweetness': '$cocktail_snapshot.taste_profile.sweetness'
                            }
                        },
                        {
                            '$group': {
                                '_id': None,
                                'all_base_spirits': {'$push': '$base_spirits'},
                                'all_flavors': {'$push': '$flavors'},
                                'all_styles': {'$push': '$styles'},
                                'avg_strength': {'$avg': '$strength'},
                                'min_strength': {'$min': '$strength'},
                                'max_strength': {'$max': '$strength'},
                                'avg_sweetness': {'$avg': '$sweetness'},
                                'min_sweetness': {'$min': '$sweetness'},
                                'max_sweetness': {'$max': '$sweetness'}
                            }
                        }
                    ],
                    # 時段分佈
                    'time_distribution': [
                        {
                            '$addFields': {
                                'hour': {'$hour': '$drunk_at'}
                            }
                        },
                        {
                            '$addFields': {
                                'time_period': {
                                    '$switch': {
                                        'branches': [
                                            {
                                                'case': {
                                                    '$and': [
                                                        {'$gte': ['$hour', 0]},
                                                        {'$lt': ['$hour', 6]}
                                                    ]
                                                },
                                                'then': 'late_night'
                                            },
                                            {
                                                'case': {
                                                    '$and': [
                                                        {'$gte': ['$hour', 6]},
                                                        {'$lt': ['$hour', 12]}
                                                    ]
                                                },
                                                'then': 'morning'
                                            },
                                            {
                                                'case': {
                                                    '$and': [
                                                        {'$gte': ['$hour', 12]},
                                                        {'$lt': ['$hour', 18]}
                                                    ]
                                                },
                                                'then': 'afternoon'
                                            },
                                            {
                                                'case': {
                                                    '$and': [
                                                        {'$gte': ['$hour', 18]},
                                                        {'$lt': ['$hour', 24]}
                                                    ]
                                                },
                                                'then': 'evening'
                                            }
                                        ],
                                        'default': 'unknown'
                                    }
                                }
                            }
                        },
                        {
                            '$group': {
                                '_id': '$time_period',
                                'count': {'$sum': 1}
                            }
                        },
                        {'$sort': {'count': -1}}
                    ],
                    # 心情標籤分佈
                    'mood_distribution': [
                        {'$unwind': '$mood_tags'},
                        {
                            '$group': {
                                '_id': '$mood_tags',
                                'count': {'$sum': 1}
                            }
                        },
                        {'$sort': {'count': -1}}
                    ],
                    'location_distribution': [
                        {
                            '$group': {
                                '_id': {'$ifNull': ['$location', '未填寫地點']},
                                'count': {'$sum': 1}
                            }
                        },
                        {'$sort': {'count': -1}}
                    ]
                }
            }
        ]

        result = list(db.drinking_records.aggregate(pipeline))
        if not result or not result[0]['tags_analysis']:
            return {
                'favorite_tags': {
                    'base_spirits': [],
                    'flavors': [],
                    'styles': []
                },
                'taste_range': {
                    'strength': {'min': 0, 'max': 10, 'avg': 5},
                    'sweetness': {'min': 0, 'max': 10, 'avg': 5}
                },
                'time_distribution': [],
                'mood_distribution': [],
                'location_distribution': [] 
            }

        data = result[0]
        tags_data = data['tags_analysis'][0] if data['tags_analysis'] else {}

        # 統計 tags 頻率
        def count_tags(tags_array):
            from collections import Counter
            all_tags = []
            for tags in tags_array:
                if tags:
                    all_tags.extend(tags)
            return Counter(all_tags).most_common(5)

        favorite_base_spirits = count_tags(tags_data.get('all_base_spirits', []))
        favorite_flavors = count_tags(tags_data.get('all_flavors', []))
        favorite_styles = count_tags(tags_data.get('all_styles', []))

        return {
            'favorite_tags': {
                'base_spirits': [{'tag': tag, 'count': count} for tag, count in favorite_base_spirits],
                'flavors': [{'tag': tag, 'count': count} for tag, count in favorite_flavors],
                'styles': [{'tag': tag, 'count': count} for tag, count in favorite_styles]
            },
            'taste_range': {
                'strength': {
                    'min': tags_data.get('min_strength', 0),
                    'max': tags_data.get('max_strength', 10),
                    'avg': tags_data.get('avg_strength', 5)
                },
                'sweetness': {
                    'min': tags_data.get('min_sweetness', 0),
                    'max': tags_data.get('max_sweetness', 10),
                    'avg': tags_data.get('avg_sweetness', 5)
                }
            },
            'time_distribution': data.get('time_distribution', []),
            'mood_distribution': data.get('mood_distribution', []),
            'location_distribution': data.get('location_distribution', [])
        }

    @staticmethod
    def calculate_similarity_score(cocktail, user_preferences):
        """計算調酒與用戶偏好的相似度分數

        評分公式：
        - Tag匹配：基酒(+4分) + 風味(+2分) + 風格(+1分)
        - 口味接近度：10 - (酒精強度差距 + 甜度差距) / 2
        - 品質分數：專業評分 × 2
        - 流行度調整：熱門(+3) 或 隱藏寶石(+2)
        """
        score = 0

        # 1. Tag 匹配分數（最高 20 分）
        favorite_spirits = [item['tag'] for item in user_preferences['favorite_tags']['base_spirits'][:3]]
        favorite_flavors = [item['tag'] for item in user_preferences['favorite_tags']['flavors'][:5]]
        favorite_styles = [item['tag'] for item in user_preferences['favorite_tags']['styles'][:5]]

        cocktail_spirits = cocktail.get('tags_categorized', {}).get('base_spirits', [])
        cocktail_flavors = cocktail.get('tags_categorized', {}).get('flavors', [])
        cocktail_styles = cocktail.get('tags_categorized', {}).get('styles', [])

        for spirit in cocktail_spirits:
            if spirit in favorite_spirits:
                score += 4

        for flavor in cocktail_flavors:
            if flavor in favorite_flavors:
                score += 2

        for style in cocktail_styles:
            if style in favorite_styles:
                score += 1

        # 2. 口味接近度（最高 10 分）
        taste_range = user_preferences['taste_range']
        if (taste_range['strength']['avg'] is not None and
            taste_range['sweetness']['avg'] is not None and
            cocktail.get('taste_profile')):

            # 獲取調酒的口味數值，如果是 None 則使用默認值 5
            cocktail_strength = cocktail['taste_profile'].get('strength')
            if cocktail_strength is None:
                cocktail_strength = 5

            cocktail_sweetness = cocktail['taste_profile'].get('sweetness')
            if cocktail_sweetness is None:
                cocktail_sweetness = 5

            strength_diff = abs(cocktail_strength - taste_range['strength']['avg'])
            sweetness_diff = abs(cocktail_sweetness - taste_range['sweetness']['avg'])
            taste_score = max(0, 10 - (strength_diff + sweetness_diff) / 2)
            score += taste_score * 0.8

        # 3. 品質分數（最高 10 分）
        professional_rating = cocktail.get('ratings', {}).get('professional', 0)
        if professional_rating is None:
            professional_rating = 0
        score += professional_rating * 2 * 0.6

        # 4. 流行度調整
        public_count = cocktail.get('ratings', {}).get('public_count', 0)
        if public_count is None:
            public_count = 0

        if public_count >= 50:
            score += 3 * 0.3  # 熱門
        elif professional_rating >= 4.5 and public_count <= 20:
            score += 2 * 0.3  # 隱藏寶石

        # 添加小隨機值避免完全相同的分數
        score += random.random() * 0.1

        return round(score, 2)

    @staticmethod
    def get_recommendations(db, user_id, limit=20, exclude_ids=None, exploration_mode='balanced'):
        """智能混合推薦引擎

        推薦策略：
        - balanced 模式：40% 安全優先（高相似度）、30% 冒險探索（中等相似度，新類型）、15% 隱藏寶石、15% 熱門推薦
        - adventurous 模式：20% 安全優先、60% 冒險探索、15% 隱藏寶石、5% 熱門推薦

        參數：
        - user_id: 用戶 ID
        - limit: 返回數量
        - exclude_ids: 已推薦過的調酒 ID 列表（用於分頁）
        - exploration_mode: 'balanced' 或 'adventurous'
        """
        # 1. 取得用戶偏好分析
        preferences = DrinkingRecord.get_user_preferences(db, user_id)

        # 2. 取得已喝過的調酒 ID
        drunk_cocktails = db.drinking_records.find(
            {'user_id': ObjectId(user_id)},
            {'cocktail_id': 1}
        )
        drunk_ids = [record['cocktail_id'] for record in drunk_cocktails]

        # 3. 合併排除列表（已喝過 + 已推薦過）
        if exclude_ids:
            exclude_ids_obj = [ObjectId(id_str) if isinstance(id_str, str) else id_str for id_str in exclude_ids]
            drunk_ids.extend(exclude_ids_obj)

        # 去重
        drunk_ids = list(set(drunk_ids))

        # 4. 檢查是否有偏好資料（冷啟動處理）
        has_preferences = (
            len(preferences['favorite_tags']['base_spirits']) > 0 or
            len(preferences['favorite_tags']['flavors']) > 0
        )

        if not has_preferences:
            # 新手推薦：經典、簡單、高評分（使用隨機抽樣）
            newbie_recommendations = list(db.cocktails.aggregate([
                {'$match': {
                    '_id': {'$nin': drunk_ids},
                    'ratings.professional': {'$gte': 4.0},
                    'difficulty': {'$in': ['easy', 'medium']}
                }},
                {'$sample': {'size': limit}}
            ]))

            for cocktail in newbie_recommendations:
                cocktail['recommendation_reason'] = '經典入門推薦'
                cocktail['recommendation_type'] = 'newbie'
                cocktail['similarity_score'] = 0

            return newbie_recommendations

        # 5. 動態隨機抽樣候選調酒（解決字母順序偏差）
        sample_size = random.randint(1000, 2000)
        all_undrunk = list(db.cocktails.aggregate([
            {'$match': {'_id': {'$nin': drunk_ids}}},
            {'$sample': {'size': sample_size}}
        ]))

        if not all_undrunk:
            return []

        # 6. 計算每個調酒的相似度分數
        cocktails_with_scores = []
        for cocktail in all_undrunk:
            similarity_score = DrinkingRecord.calculate_similarity_score(cocktail, preferences)
            cocktail['similarity_score'] = similarity_score
            cocktails_with_scores.append(cocktail)

        # 7. 按相似度排序
        cocktails_with_scores.sort(key=lambda x: x['similarity_score'], reverse=True)

        # 8. 分類到四個互斥的池（避免重複）
        safe_pool = []      # 高相似度 (分數 > 15)
        adventure_pool = []  # 中等相似度 (10 < 分數 <= 15)
        hidden_gems = []     # 專業評分 >= 4.5 且 公眾評論 <= 20
        popular_pool = []    # 公眾評論 >= 50
        added_to_pool = set()  # 追蹤已加入池的調酒 ID

        # 提取用戶已嘗試過的基酒
        tried_spirits = set()
        for item in preferences['favorite_tags']['base_spirits']:
            tried_spirits.add(item['tag'])

        for cocktail in cocktails_with_scores:
            cocktail_id = str(cocktail['_id'])
            if cocktail_id in added_to_pool:
                continue

            score = cocktail['similarity_score']
            public_count = cocktail.get('ratings', {}).get('public_count', 0)
            if public_count is None:
                public_count = 0

            professional_rating = cocktail.get('ratings', {}).get('professional', 0)
            if professional_rating is None:
                professional_rating = 0

            cocktail_spirits = set(cocktail.get('tags_categorized', {}).get('base_spirits', []))

            # 優先級順序：隱藏寶石 > 熱門 > 安全/冒險（確保互斥）
            if professional_rating >= 4.5 and public_count <= 20:
                hidden_gems.append(cocktail)
                added_to_pool.add(cocktail_id)
            elif public_count >= 50:
                popular_pool.append(cocktail)
                added_to_pool.add(cocktail_id)
            elif score > 15:
                safe_pool.append(cocktail)
                added_to_pool.add(cocktail_id)
            elif score > 10 or (cocktail_spirits and not cocktail_spirits.issubset(tried_spirits)):
                adventure_pool.append(cocktail)
                added_to_pool.add(cocktail_id)

        # 9. 根據探索模式調整比例
        if exploration_mode == 'adventurous':
            safe_count = int(limit * 0.2)       # 4 個
            adventure_count = int(limit * 0.6)  # 12 個
            hidden_count = int(limit * 0.15)    # 3 個
            popular_count = limit - safe_count - adventure_count - hidden_count  # 1 個
        else:  # balanced
            safe_count = int(limit * 0.4)       # 8 個
            adventure_count = int(limit * 0.3)  # 6 個
            hidden_count = int(limit * 0.15)    # 3 個
            popular_count = limit - safe_count - adventure_count - hidden_count  # 3 個

        recommendations = []

        # 分散化抽取函數（確保多樣性）
        def diversified_sample(pool, count):
            """從池中分散抽取，確保涵蓋不同基酒/風味"""
            if len(pool) <= count:
                return pool

            selected = []
            selected_spirits = set()
            selected_flavors = set()
            remaining = pool.copy()

            # 第一輪：優先選擇不同基酒的調酒
            for cocktail in remaining[:]:
                if len(selected) >= count:
                    break
                spirits = set(cocktail.get('tags_categorized', {}).get('base_spirits', []))
                if not spirits.intersection(selected_spirits):
                    selected.append(cocktail)
                    selected_spirits.update(spirits)
                    remaining.remove(cocktail)

            # 第二輪：優先選擇不同風味的調酒
            for cocktail in remaining[:]:
                if len(selected) >= count:
                    break
                flavors = set(cocktail.get('tags_categorized', {}).get('flavors', []))
                if not flavors.intersection(selected_flavors):
                    selected.append(cocktail)
                    selected_flavors.update(flavors)
                    remaining.remove(cocktail)

            # 第三輪：從剩餘中均勻間隔抽取
            if len(selected) < count:
                step = max(1, len(remaining) // (count - len(selected)))
                selected.extend(remaining[::step][:count - len(selected)])

            return selected

        # 從安全池抽取（分散化）
        safe_selection = diversified_sample(safe_pool, safe_count)
        for cocktail in safe_selection:
            matching_spirits = [s for s in cocktail.get('tags_categorized', {}).get('base_spirits', [])
                              if s in [item['tag'] for item in preferences['favorite_tags']['base_spirits'][:2]]]
            if matching_spirits:
                cocktail['recommendation_reason'] = f'符合你對 {matching_spirits[0]} 的偏好'
            else:
                cocktail['recommendation_reason'] = '與你喜歡的調酒很相似'
            cocktail['recommendation_type'] = 'safe'
        recommendations.extend(safe_selection)

        # 從冒險池抽取（分散化）
        adventure_selection = diversified_sample(adventure_pool, adventure_count)
        for cocktail in adventure_selection:
            new_spirits = [s for s in cocktail.get('tags_categorized', {}).get('base_spirits', [])
                          if s not in tried_spirits]
            if new_spirits:
                cocktail['recommendation_reason'] = f'嘗試新的 {new_spirits[0]} 基底？'
            else:
                cocktail['recommendation_reason'] = '探索新的風味組合'
            cocktail['recommendation_type'] = 'adventure'
        recommendations.extend(adventure_selection)

        # 從隱藏寶石池抽取（分散化）
        hidden_selection = diversified_sample(hidden_gems, hidden_count)
        for cocktail in hidden_selection:
            rating = cocktail.get('ratings', {}).get('professional', 0)
            if rating is None:
                rating = 0
            cocktail['recommendation_reason'] = f'專業評分 {rating:.1f}★ 的隱藏珍品'
            cocktail['recommendation_type'] = 'hidden_gem'
        recommendations.extend(hidden_selection)

        # 從熱門池抽取（分散化）
        popular_selection = diversified_sample(popular_pool, popular_count)
        for cocktail in popular_selection:
            count = cocktail.get('ratings', {}).get('public_count', 0)
            if count is None:
                count = 0
            cocktail['recommendation_reason'] = f'{count} 人都給了好評！'
            cocktail['recommendation_type'] = 'popular'
        recommendations.extend(popular_selection)

        # 10. 去重檢查（確保推薦結果無重複）
        seen_ids = set()
        unique_recommendations = []
        for cocktail in recommendations:
            cocktail_id = str(cocktail['_id'])
            if cocktail_id not in seen_ids:
                unique_recommendations.append(cocktail)
                seen_ids.add(cocktail_id)

        recommendations = unique_recommendations

        # 11. 如果不足 limit 數量，從剩餘高分調酒補充
        if len(recommendations) < limit:
            remaining_count = limit - len(recommendations)
            remaining_ids = [c['_id'] for c in recommendations]
            additional = [c for c in cocktails_with_scores
                         if c['_id'] not in remaining_ids][:remaining_count]
            for cocktail in additional:
                cocktail['recommendation_reason'] = '高評分推薦'
                cocktail['recommendation_type'] = 'general'
            recommendations.extend(additional)

        # 12. 智能打亂順序（確保連續項目不會有相同基酒）
        def smart_shuffle(items):
            """智能打亂，避免相同基酒連續出現"""
            if len(items) <= 2:
                return items

            shuffled = []
            remaining = items.copy()
            random.shuffle(remaining)

            while remaining:
                # 選擇下一個項目，避免與上一個有相同基酒
                if shuffled:
                    last_spirits = set(shuffled[-1].get('tags_categorized', {}).get('base_spirits', []))
                    for i, cocktail in enumerate(remaining):
                        curr_spirits = set(cocktail.get('tags_categorized', {}).get('base_spirits', []))
                        if not curr_spirits.intersection(last_spirits):
                            shuffled.append(remaining.pop(i))
                            break
                    else:
                        # 找不到不同基酒，直接取第一個
                        shuffled.append(remaining.pop(0))
                else:
                    shuffled.append(remaining.pop(0))

            return shuffled

        recommendations = smart_shuffle(recommendations)

        return recommendations[:limit]

    @staticmethod
    def check_if_drunk(db, user_id, cocktail_id):
        """檢查用戶是否喝過某調酒"""
        record = db.drinking_records.find_one({
            'user_id': ObjectId(user_id),
            'cocktail_id': ObjectId(cocktail_id)
        })
        return record is not None

    @staticmethod
    def get_cocktail_records(db, user_id, cocktail_id):
        """取得用戶對特定調酒的所有紀錄"""
        return list(db.drinking_records.find({
            'user_id': ObjectId(user_id),
            'cocktail_id': ObjectId(cocktail_id)
        }).sort('drunk_at', -1))


class Favorite:
    """收藏模型"""

    @staticmethod
    def add(db, user_id, cocktail_id, conversation_id=None):
        """添加收藏"""
        try:
            favorite_data = {
                'user_id': ObjectId(user_id),
                'cocktail_id': ObjectId(cocktail_id),
                'conversation_id': ObjectId(conversation_id) if conversation_id else None,
                'created_at': datetime.utcnow()
            }
            result = db.favorites.insert_one(favorite_data)
            return result.inserted_id
        except Exception as e:
            # 如果已經存在（違反唯一索引），則忽略
            if 'duplicate key error' in str(e).lower():
                return None
            raise e

    @staticmethod
    def remove(db, user_id, cocktail_id, conversation_id=None):
        """取消收藏"""
        query = {
            'user_id': ObjectId(user_id),
            'cocktail_id': ObjectId(cocktail_id)
        }
        if conversation_id:
            query['conversation_id'] = ObjectId(conversation_id)
        result = db.favorites.delete_one(query)
        return result.deleted_count > 0

    @staticmethod
    def find_by_user(db, user_id, page=1, limit=20, conversation_id=None):
        """查詢用戶的收藏列表（分頁）"""
        skip = (page - 1) * limit

        # 構建匹配條件
        match_query = {'user_id': ObjectId(user_id)}
        if conversation_id:
            match_query['conversation_id'] = ObjectId(conversation_id)

        # 使用聚合管道來 join cocktails 集合
        pipeline = [
            {'$match': match_query},
            {'$sort': {'created_at': -1}},
            {'$skip': skip},
            {'$limit': limit},
            {
                '$lookup': {
                    'from': 'cocktails',
                    'localField': 'cocktail_id',
                    'foreignField': '_id',
                    'as': 'cocktail_info'
                }
            },
            {'$unwind': '$cocktail_info'},
            {
                '$project': {
                    '_id': '$cocktail_info._id',
                    'name': '$cocktail_info.name',
                    'name_zh': '$cocktail_info.name_zh',
                    'image_url': '$cocktail_info.image_url',
                    'ratings': '$cocktail_info.ratings',
                    'taste_profile': '$cocktail_info.taste_profile',
                    'difficulty': '$cocktail_info.difficulty',
                    'ingredients': '$cocktail_info.ingredients',
                    'category': '$cocktail_info.category',
                    'category_zh': '$cocktail_info.category_zh',
                    'tags_categorized': '$cocktail_info.tags_categorized',
                    'favorited_at': '$created_at'
                }
            }
        ]

        favorites = list(db.favorites.aggregate(pipeline))

        # 計算總數
        total = db.favorites.count_documents(match_query)

        return {
            'favorites': favorites,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }

    @staticmethod
    def check_exists(db, user_id, cocktail_id, conversation_id=None):
        """檢查是否已收藏"""
        query = {
            'user_id': ObjectId(user_id),
            'cocktail_id': ObjectId(cocktail_id)
        }
        if conversation_id:
            query['conversation_id'] = ObjectId(conversation_id)
        exists = db.favorites.find_one(query)
        return exists is not None

    @staticmethod
    def get_favorited_ids(db, user_id, conversation_id=None):
        """獲取用戶所有收藏的調酒 ID 列表"""
        query = {'user_id': ObjectId(user_id)}
        if conversation_id:
            query['conversation_id'] = ObjectId(conversation_id)
        favorites = db.favorites.find(query, {'cocktail_id': 1})
        return [str(fav['cocktail_id']) for fav in favorites]
