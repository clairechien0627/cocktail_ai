"""
對話管理器（完整版 - MongoDB 修復）
合併所有功能，支援 MongoDB 和內存管理
"""

from datetime import datetime
from bson import ObjectId
from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage


class ConversationManager:
    """
    對話管理器
    支援兩種模式：
    1. MongoDB 模式：ConversationManager(db, conversation_id)
    2. 內存模式：ConversationManager()
    """
    
    def __init__(self, db=None, conversation_id=None):
        """
        初始化對話管理器
        
        Args:
            db: MongoDB 資料庫實例（可選）
            conversation_id: 對話 ID（可選）
        """
        self.db = db
        self.conversation_id = ObjectId(conversation_id) if isinstance(conversation_id, str) else conversation_id
        self.conversations = {}  # 內存中的對話歷史
        
        # 對話上下文
        self.context = {
            'current_query': {},
            'recommended_cocktails': [],
            'last_recommendation': {}
        }
        
        # 如果有 db 和 conversation_id，載入現有對話
        if self.db is not None and self.conversation_id is not None:
            self.conversation = self._get_or_create_conversation()
            self.context = self.conversation.get('context', self.context)
    
    def _get_or_create_conversation(self):
        """獲取或建立對話（MongoDB）"""
        if self.db is None or self.conversation_id is None:
            return None
        
        conversation = self.db.conversations.find_one({'_id': self.conversation_id})
        if not conversation:
            conversation = {
                '_id': self.conversation_id,
                'user_id': None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'messages': [],
                'context': {
                    'current_query': {},
                    'recommended_cocktails': [],
                    'last_recommendation': {}
                }
            }
            self.db.conversations.insert_one(conversation)
        return conversation
    
    # ========== 訊息管理 ==========
    
    def save_message(self, role: str, content: str, sentiment_score: float = None):
        """
        儲存訊息
        
        Args:
            role: 'user', 'assistant', 'system', 'tool'
            content: 訊息內容
            sentiment_score: 情感分數（可選）
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow()
        }
        
        if sentiment_score is not None:
            message['sentiment_score'] = sentiment_score
        
        # MongoDB 模式
        if self.db is not None and self.conversation_id is not None:
            self.db.conversations.update_one(
                {'_id': self.conversation_id},
                {
                    '$push': {'messages': message},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
        # 內存模式
        else:
            self.add_message(message=message)
    
    def get_messages(self, as_message_objects=False, limit=None):
        """
        獲取對話訊息
        
        Args:
            as_message_objects: True = 返回 LangChain Message 物件, False = 返回字典
            limit: 限制返回數量
        
        Returns:
            List[Message] 或 List[dict]
        """
        # MongoDB 模式
        if self.db is not None and self.conversation_id is not None:
            conversation = self.db.conversations.find_one({'_id': self.conversation_id})
            if not conversation:
                return []
            
            messages = conversation.get('messages', [])
        # 內存模式
        else:
            messages = self.get_or_create_conversation_memory()
        
        # 限制數量
        if limit:
            messages = messages[-limit:]
        
        # 轉換為 Message 物件
        if as_message_objects:
            return self._convert_to_message_objects(messages)
        
        return messages
    
    def _convert_to_message_objects(self, messages):
        """轉換字典為 LangChain Message 物件"""
        result = []
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'user':
                result.append(HumanMessage(content=content))
            elif role == 'assistant' or role == 'ai':
                result.append(AIMessage(content=content))
            elif role == 'system':
                result.append(SystemMessage(content=content))
            elif role == 'tool':
                result.append(ToolMessage(
                    content=content,
                    tool_call_id=msg.get('tool_call_id', '')
                ))
        
        return result
    
    # ========== 內存模式方法 ==========
    
    def get_or_create_conversation_memory(self, conversation_id: str = None) -> List:
        """取得或建立對話歷史（內存）"""
        if conversation_id is None:
            conversation_id = str(self.conversation_id) if self.conversation_id else 'default'
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        return self.conversations[conversation_id]
    
    def add_message(self, conversation_id: str = None, message=None):
        """加入訊息到對話歷史（內存）"""
        if conversation_id is None:
            conversation_id = str(self.conversation_id) if self.conversation_id else 'default'
        
        history = self.get_or_create_conversation_memory(conversation_id)
        history.append(message)
        
        # 限制歷史長度（保留最近 20 條訊息）
        if len(history) > 20:
            self.conversations[conversation_id] = history[-20:]
    
    def clear_conversation(self, conversation_id: str = None):
        """清除對話歷史（內存）"""
        if conversation_id is None:
            conversation_id = str(self.conversation_id) if self.conversation_id else 'default'
        
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    # ========== 上下文管理 ==========
    
    def update_context(self, ai_response: str = None, tool_results: List = None, **kwargs):
        """
        更新對話上下文
        
        Args:
            ai_response: AI 回應（可選）
            tool_results: 工具結果（可選）
            **kwargs: 其他要更新的上下文
        """
        # 從工具結果中提取調酒名稱
        if tool_results:
            for result in tool_results:
                if isinstance(result, dict):
                    # 單個調酒結果
                    if 'name' in result:
                        cocktail_name = result['name']
                        if cocktail_name not in self.context['recommended_cocktails']:
                            self.context['recommended_cocktails'].append(cocktail_name)
                        self.context['last_recommendation'] = result
                    
                    # 多個調酒結果（列表）
                    elif isinstance(result, list):
                        for item in result:
                            if isinstance(item, dict) and 'name' in item:
                                cocktail_name = item['name']
                                if cocktail_name not in self.context['recommended_cocktails']:
                                    self.context['recommended_cocktails'].append(cocktail_name)
            
            # 限制推薦歷史長度
            if len(self.context['recommended_cocktails']) > 20:
                self.context['recommended_cocktails'] = self.context['recommended_cocktails'][-20:]
        
        # 更新其他上下文
        for key, value in kwargs.items():
            self.context[key] = value
        
        # 如果有 db，同步到 MongoDB
        if self.db is not None and self.conversation_id is not None:
            update_dict = {}
            for key, value in self.context.items():
                update_dict[f'context.{key}'] = value
            
            self.db.conversations.update_one(
                {'_id': self.conversation_id},
                {'$set': update_dict}
            )
    
    def get_context(self, key=None):
        """獲取上下文"""
        if key:
            return self.context.get(key)
        return self.context