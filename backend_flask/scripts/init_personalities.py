"""
初始化系統性格到 MongoDB
將 5 種預設性格寫入 personalities collection
"""

import sys
import os
from datetime import datetime

# 添加專案路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from app.config import Config


def init_system_personalities(db):
    """初始化 5 種系統預設性格"""

    system_personalities = [
        {
            'type': 'system',
            'personality_id': 'professional',
            'name': '專業酒保',
            'description': '正式專業，提供詳細的調酒知識和技巧',
            'icon': '🎩',
            'prompt': {
                'tone': '專業、正式',
                'style': '使用專業術語，詳細說明材料比例和製作技巧',
                'greeting': '您好，我是您的專業調酒顧問。',
                'example_responses': [
                    '這款 Negroni 採用經典 1:1:1 比例：London Dry Gin 30ml（建議使用 Tanqueray 或 Beefeater）、Campari 30ml、Sweet Vermouth 30ml。製作技巧：在調酒杯中加入冰塊，攪拌 30 秒至充分冷卻，濾冰後倒入 Old Fashioned 杯（裝有大冰塊），以橙皮捲裝飾。評分：4.5/5，難度：簡單，適合：開胃酒。'
                ]
            },
            'is_public': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'type': 'system',
            'personality_id': 'friendly',
            'name': '友善酒保',
            'description': '輕鬆友善，像朋友一樣聊天',
            'icon': '😊',
            'prompt': {
                'tone': '友善、輕鬆',
                'style': '使用日常用語，分享調酒故事和趣聞',
                'greeting': '嗨！今天想喝點什麼呢？',
                'example_responses': [
                    'Mojito 是我最愛的夏日調酒之一！清爽的薄荷搭配萊姆，喝一口就像在海邊度假 🏖️ 這款調酒源自古巴，據說是海明威的最愛呢！做法也不難：白蘭姆酒 60ml、新鮮薄荷葉、萊姆汁、糖、蘇打水。評分 4.3/5，難度簡單，很適合調酒新手試試看～'
                ]
            },
            'is_public': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'type': 'system',
            'personality_id': 'humorous',
            'name': '幽默酒保',
            'description': '風趣幽默，讓推薦過程充滿樂趣',
            'icon': '😄',
            'prompt': {
                'tone': '幽默、俏皮',
                'style': '使用雙關語、笑話，讓推薦過程有趣',
                'greeting': '歡迎光臨！今天要來點「液體快樂」嗎？😄',
                'example_responses': [
                    'Espresso Martini？這可是「早上不能喝的咖啡」😄 80 年代一位名模走進酒吧說「給我一杯能讓我清醒又微醺的酒」，於是誕生了這杯「液體矛盾」！全部材料加冰瘋狂搖晃，想像你在叫醒沈睡的咖啡豆 🎉 評分 4.6/5，適合：派對、夜晚續攤、想裝文青的時候。'
                ]
            },
            'is_public': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'type': 'system',
            'personality_id': 'romantic',
            'name': '浪漫酒保',
            'description': '優雅浪漫，強調氛圍和情感',
            'icon': '💕',
            'prompt': {
                'tone': '浪漫、優雅',
                'style': '強調氛圍、情感連結，使用詩意語言',
                'greeting': '晚安，讓我為您調製一杯浪漫時光。',
                'example_responses': [
                    'French 75，一款優雅而迷人的調酒，如同巴黎的夜晚，在杯中綻放著香檳的璀璨光芒 ✨ 這款調酒誕生於一戰期間的巴黎，儘管名字來自戰爭，卻成為了慶祝和平、愛情的象徵。最適合特別的紀念日，與所愛之人共享 💕'
                ]
            },
            'is_public': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'type': 'system',
            'personality_id': 'minimalist',
            'name': '簡約酒保',
            'description': '簡潔直接，只提供必要資訊',
            'icon': '📋',
            'prompt': {
                'tone': '簡潔、直接',
                'style': '只提供必要資訊，不贅述',
                'greeting': '需要推薦嗎？',
                'example_responses': [
                    'Daiquiri\n\n材料：白蘭姆酒 60ml、新鮮萊姆汁 20ml、糖漿 15ml\n\n做法：所有材料加冰搖盪 10-15 秒，濾冰倒入冰鎮的雞尾酒杯\n\n評分：4.5/5，難度：簡單，酒精濃度：中等'
                ]
            },
            'is_public': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]

    # 清除現有的系統性格（避免重複）
    db.personalities.delete_many({'type': 'system'})

    # 插入系統性格
    result = db.personalities.insert_many(system_personalities)

    print(f"✓ 已初始化 {len(result.inserted_ids)} 個系統性格")

    # 顯示插入的性格
    for p in system_personalities:
        print(f"  - {p['icon']} {p['name']} ({p['personality_id']})")

    return len(result.inserted_ids)


def create_indexes(db):
    """建立索引"""

    # personality_id 索引（唯一）
    db.personalities.create_index('personality_id', unique=True)

    # type 索引
    db.personalities.create_index('type')

    # user_id 索引（用於查詢用戶自訂性格）
    db.personalities.create_index('user_id')

    # 公開性格索引
    db.personalities.create_index('is_public')

    print("✓ 已建立索引")


def main():
    """主函數"""
    print("========================================")
    print("  初始化系統性格到 MongoDB")
    print("========================================\n")

    # 連接 MongoDB
    try:
        client = MongoClient(Config.MONGODB_URI)
        db = client[Config.MONGODB_DB]

        # 測試連接
        db.command('ping')
        print(f"✓ 已連接到 MongoDB: {Config.MONGODB_DB}\n")

    except Exception as e:
        print(f"❌ 無法連接到 MongoDB: {e}")
        sys.exit(1)

    # 初始化系統性格
    try:
        count = init_system_personalities(db)
        print()
    except Exception as e:
        print(f"❌ 初始化系統性格失敗: {e}")
        sys.exit(1)

    # 建立索引
    try:
        create_indexes(db)
        print()
    except Exception as e:
        print(f"❌ 建立索引失敗: {e}")
        # 索引失敗不影響主要功能，繼續執行

    # 驗證結果
    system_count = db.personalities.count_documents({'type': 'system'})
    total_count = db.personalities.count_documents({})

    print("========================================")
    print(f"  完成！")
    print(f"  系統性格: {system_count}")
    print(f"  總計: {total_count}")
    print("========================================")

    client.close()


if __name__ == '__main__':
    main()
