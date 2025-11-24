from groq import Groq
from flask import current_app

class LLMService:
    """Groq LLM 服務"""

    def __init__(self):
        self.client = None

    def initialize(self, api_key):
        """初始化 Groq 客戶端"""
        if not api_key:
            raise ValueError("Groq API Key 未設定")

        try:
            # 使用最簡單的初始化方式
            self.client = Groq(api_key=api_key)
        except TypeError as e:
            # 如果遇到參數錯誤，嘗試不同的初始化方式
            if 'proxies' in str(e):
                # 某些版本的 Groq 可能有不同的初始化方式
                import os
                os.environ['GROQ_API_KEY'] = api_key
                self.client = Groq()
            else:
                raise

    def get_bartender_response(self, user_message, conversation_history=None, user_preferences=None):
        """
        取得 AI 酒保的回應

        Args:
            user_message: 用戶訊息
            conversation_history: 對話歷史
            user_preferences: 用戶偏好

        Returns:
            AI 酒保的回應文字
        """
        if not self.client:
            raise Exception("Groq 客戶端尚未初始化")

        # 建立系統提示詞
        system_prompt = self._build_system_prompt(user_preferences)

        # 建立訊息列表
        messages = [{"role": "system", "content": system_prompt}]

        # 加入對話歷史（最近 10 條）
        if conversation_history:
            messages.extend(conversation_history[-10:])

        # 加入當前用戶訊息
        messages.append({"role": "user", "content": user_message})

        try:
            # 呼叫 Groq API
            # 使用最新的 Llama 3.3 模型
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",  # Groq 最新模型
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9
            )

            response = chat_completion.choices[0].message.content
            return response

        except Exception as e:
            current_app.logger.error(f"Groq API 錯誤: {str(e)}")
            raise

    def _build_system_prompt(self, user_preferences=None):
        """建立系統提示詞"""
        base_prompt = """你是一位專業且友善的 AI 酒保，名叫「調酒大師」。你的任務是：

1. **推薦調酒**：根據用戶的喜好、手邊材料、場景或心情推薦適合的調酒
2. **製作教學**：詳細解釋調酒的製作步驟、技巧和所需工具
3. **閒聊互動**：像真正的酒保一樣與客人聊天，分享調酒知識、趣聞和文化
4. **創意設計**：根據用戶的要求創意設計新的調酒配方

你的知識來源：
你擁有來自 **Difford's Guide** 的專業調酒資料庫，包含 **4,600+ 款精選調酒配方**，涵蓋：
- **經典調酒**：Mojito、Martini、Old Fashioned、Margarita、Negroni 等
- **現代創意調酒**：當代調酒師的創新配方
- **專業評分**：每款調酒都有專業評分（0-5星）和公眾評價
- **風味檔案**：酒精強度（0-10）和甜度（0-10）的精確數據
- **難度分級**：easy（簡單）、medium（中等）、hard（困難）
- **營養資訊**：卡路里含量
- **酒精指標**：ABV（酒精濃度百分比）、標準飲酒量、proof（酒精度數）
- **歷史故事**：調酒的起源和文化背景
- **製作細節**：精確的材料用量和詳細步驟

推薦調酒時，請善用以下資訊：
- 根據難度推薦：新手推薦 easy 級別，專家可推薦 hard 級別
- 根據風味偏好：用酒精強度和甜度數據精確匹配用戶口味
- 根據健康考量：提供卡路里資訊給關注健康的用戶
- 根據評分：優先推薦高評分（4星以上）的經典配方
- 根據場景：派對推薦高評分的 Punch 類，約會推薦優雅的 Martini 類
- 分享歷史：介紹調酒時可以分享其歷史故事和文化背景

重要指導原則：
- 保持友善、專業且有趣的語氣，像真正的專業酒保
- 使用繁體中文回答
- 如果用戶是新手，優先推薦 easy 難度、材料簡單（3-5種）的調酒
- 適時提醒責任飲酒：過量飲酒有害健康，飲酒後不要駕駛
- 如果用戶提到不適合飲酒的情況（如開車、懷孕等），溫和地提醒並推薦無酒精飲料
- 當被問到調酒配方時，提供詳細的材料用量、步驟和裝飾建議
- 能夠識別用戶的情感狀態，並據此調整推薦和語氣
- 推薦時可以提及評分、難度、風味特徵等專業資訊
- 對於關注健康的用戶，可以提供低卡路里或低酒精濃度的選項"""

        # 根據用戶偏好調整提示詞
        if user_preferences:
            skill_level = user_preferences.get('skill_level', 'beginner')
            favorite_spirits = user_preferences.get('favorite_spirits', [])

            if skill_level == 'beginner':
                base_prompt += "\n\n**用戶設定檔**：調酒新手\n- 請優先推薦 easy 難度的調酒\n- 提供簡單易懂的說明和初學者友善的建議\n- 推薦材料少於5種、步驟簡單的配方\n- 避免需要複雜技巧或特殊工具的調酒"
            elif skill_level == 'intermediate':
                base_prompt += "\n\n**用戶設定檔**：中階愛好者\n- 可以推薦 easy 到 medium 難度的調酒\n- 可以討論一些進階技巧和工具\n- 介紹經典調酒的變化版本"
            elif skill_level == 'expert':
                base_prompt += "\n\n**用戶設定檔**：調酒專家\n- 可以推薦任何難度的調酒，包括 hard 級別\n- 可以討論進階技巧、複雜配方和專業工具\n- 可以深入討論風味平衡、材料替代和創意變化"

            if favorite_spirits:
                spirits_str = '、'.join(favorite_spirits)
                base_prompt += f"\n\n**用戶喜好**：{spirits_str}\n- 優先推薦以這些基酒為主的調酒\n- 可以介紹這些基酒的不同品牌和風味特徵"

        return base_prompt

    def analyze_sentiment_with_llm(self, text):
        """
        使用 LLM 分析情感（備用方案）

        Returns:
            情感分數 (-1.0 到 1.0)
        """
        try:
            prompt = f"""分析以下文字的情感傾向，回答一個介於 -1.0（非常負面）到 1.0（非常正面）之間的數字：

文字："{text}"

只回答數字，不要有其他內容。"""

            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",  # 使用與主要功能相同的模型
                temperature=0.3,
                max_tokens=10
            )

            sentiment_score = float(response.choices[0].message.content.strip())
            return max(-1.0, min(1.0, sentiment_score))

        except:
            return 0.0  # 預設中性


# 全域 LLM 服務實例
llm_service = LLMService()
