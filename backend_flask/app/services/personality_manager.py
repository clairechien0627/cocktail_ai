"""
性格管理器
混合式 Prompt 管理：系統性格從檔案載入，用戶自訂從 MongoDB 載入
"""

import os
from typing import Dict, Optional
from bson import ObjectId


class PersonalityManager:
    """
    性格管理器
    支援兩種載入方式：
    1. 系統預設性格 - 從 prompts/ 資料夾的 .txt 檔案載入
    2. 用戶自訂性格 - 從 MongoDB personalities collection 載入
    """

    def __init__(self, db=None):
        """
        初始化性格管理器

        Args:
            db: MongoDB 資料庫實例（用於載入自訂性格）
        """
        self.db = db
        self.prompt_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
        self._cache = {}  # 快取已載入的 Prompt（格式: {personality_id: prompt_text}）

    def load_personality(self, personality_id: str, user_id: str = None) -> str:
        """
        載入性格 Prompt（統一介面）

        Args:
            personality_id: 性格 ID（如 'friendly', 'custom_123...'）
            user_id: 用戶 ID（載入自訂性格時需要）

        Returns:
            完整的 System Prompt 文本
        """
        # 檢查快取
        cache_key = f"{personality_id}:{user_id or 'system'}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. 系統預設性格（從檔案）
        if not personality_id.startswith('custom_'):
            prompt_text = self._load_from_file(personality_id)
        # 2. 用戶自訂性格（從資料庫）
        else:
            prompt_text = self._load_from_db(personality_id, user_id)

        # 快取結果
        self._cache[cache_key] = prompt_text
        return prompt_text

    def _load_from_file(self, personality_id: str) -> str:
        """
        從檔案載入系統性格

        Args:
            personality_id: 性格 ID（friendly, professional, humorous, romantic, minimalist）

        Returns:
            完整的 System Prompt 文本
        """
        # 載入性格 Prompt
        personality_file = f'personality_{personality_id}.txt'
        personality_path = os.path.join(self.prompt_dir, personality_file)

        if not os.path.exists(personality_path):
            print(f"⚠️  性格檔案不存在: {personality_file}，使用預設性格 'friendly'")
            # 預設使用友善性格
            personality_path = os.path.join(self.prompt_dir, 'personality_friendly.txt')

        # 載入基礎 Prompt
        base_path = os.path.join(self.prompt_dir, 'base_bartender.txt')

        try:
            with open(personality_path, 'r', encoding='utf-8') as f:
                personality_prompt = f.read()

            with open(base_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read()

            # 合併 Prompt（性格 + 基礎）
            full_prompt = f"{personality_prompt}\n\n{base_prompt}"
            return full_prompt

        except Exception as e:
            print(f"❌ 載入性格檔案失敗: {e}")
            # 回退到最簡單的 Prompt
            return self._get_fallback_prompt()

    def _load_from_db(self, personality_id: str, user_id: str = None) -> str:
        """
        從資料庫載入自訂性格

        Args:
            personality_id: 自訂性格 ID（格式: 'custom_<ObjectId>'）
            user_id: 用戶 ID

        Returns:
            完整的 System Prompt 文本
        """
        if self.db is None:
            print("⚠️  未提供資料庫實例，無法載入自訂性格，使用預設性格")
            return self._load_from_file('friendly')

        try:
            # 查詢性格
            query = {'personality_id': personality_id}

            # 只能載入自己的或公開的自訂性格
            if user_id:
                query['$or'] = [
                    {'user_id': ObjectId(user_id)},  # 自己的
                    {'is_public': True}               # 或公開的
                ]

            personality = self.db.personalities.find_one(query)

            if not personality:
                print(f"⚠️  找不到自訂性格: {personality_id}，使用預設性格")
                return self._load_from_file('friendly')

            # 組合 Prompt
            prompt_data = personality.get('prompt', {})
            full_prompt = self._build_custom_prompt(prompt_data)

            return full_prompt

        except Exception as e:
            print(f"❌ 載入自訂性格失敗: {e}")
            return self._load_from_file('friendly')

    def _build_custom_prompt(self, prompt_data: Dict) -> str:
        """
        從資料庫的 prompt 物件建構完整 Prompt

        Args:
            prompt_data: 包含 tone, style, greeting, example_responses, custom_rules 的字典

        Returns:
            完整的 System Prompt 文本
        """
        tone = prompt_data.get('tone', '友善、專業')
        style = prompt_data.get('style', '使用清晰的語言')
        greeting = prompt_data.get('greeting', '嗨！有什麼我能幫忙的嗎？')
        example_responses = prompt_data.get('example_responses', [])
        custom_rules = prompt_data.get('custom_rules', [])

        # 組合自訂性格 Prompt
        custom_prompt = f"""你是一位 AI 調酒師「調酒大師」，擁有以下性格特質：

🎭 性格設定：
- 語氣：{tone}
- 風格：{style}
- 打招呼範例：{greeting}

"""

        # 加入範例回應
        if example_responses:
            custom_prompt += "💬 回應範例：\n"
            for i, example in enumerate(example_responses[:3], 1):  # 最多 3 個範例
                custom_prompt += f"{i}. {example}\n"
            custom_prompt += "\n"

        # 加入自訂規則
        if custom_rules:
            custom_prompt += "🔧 額外規則：\n"
            for rule in custom_rules:
                custom_prompt += f"- {rule}\n"
            custom_prompt += "\n"

        custom_prompt += "請嚴格遵守上述性格設定，保持一致性。\n"

        # 載入基礎 Prompt
        base_path = os.path.join(self.prompt_dir, 'base_bartender.txt')
        try:
            with open(base_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
            full_prompt = f"{custom_prompt}\n{base_prompt}"
        except:
            full_prompt = custom_prompt

        return full_prompt

    def _get_fallback_prompt(self) -> str:
        """
        回退 Prompt（當所有載入方式都失敗時使用）

        Returns:
            最基本的 System Prompt
        """
        return """你是一位友善的 AI 調酒師「調酒大師」。

請根據用戶需求推薦調酒，提供名稱、材料和做法。
使用繁體中文，保持友善專業的語氣。

當前對話上下文：
- 已推薦過: {recommended_cocktails}
- 當前查詢參數: {current_query}
- 最後推薦: {last_recommendation}
"""

    def clear_cache(self):
        """清除所有快取"""
        self._cache = {}

    def get_system_personalities(self) -> list:
        """
        獲取所有系統預設性格的資訊

        Returns:
            系統性格列表
        """
        return [
            {
                'personality_id': 'professional',
                'name': '專業酒保',
                'description': '正式專業，提供詳細的調酒知識和技巧',
                'icon': '🎩',
                'type': 'system'
            },
            {
                'personality_id': 'friendly',
                'name': '友善酒保',
                'description': '輕鬆友善，像朋友一樣聊天',
                'icon': '😊',
                'type': 'system'
            },
            {
                'personality_id': 'humorous',
                'name': '幽默酒保',
                'description': '風趣幽默，讓推薦過程充滿樂趣',
                'icon': '😄',
                'type': 'system'
            },
            {
                'personality_id': 'romantic',
                'name': '浪漫酒保',
                'description': '優雅浪漫，強調氛圍和情感',
                'icon': '💕',
                'type': 'system'
            },
            {
                'personality_id': 'minimalist',
                'name': '簡約酒保',
                'description': '簡潔直接，只提供必要資訊',
                'icon': '📋',
                'type': 'system'
            }
        ]
