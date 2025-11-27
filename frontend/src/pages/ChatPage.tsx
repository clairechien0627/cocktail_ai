import { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';
import { Send, Bot, User as UserIcon, AlertCircle, Menu, Plus, MessageCircle, X, Trash2 } from 'lucide-react';
import type { Message, Conversation } from '../types';


const ChatPage = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);


  // 自動滾動到最新訊息
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };


  // 載入所有對話
  const loadConversations = async () => {
    try {
      const response = await chatAPI.getConversations();
      setConversations(response.conversations);
    } catch (error) {
      console.error('載入對話列表失敗:', error);
    }
  };


  // 選擇並載入特定對話
  const selectConversation = async (convId: string) => {
    try {
      setLoading(true);
      const response = await chatAPI.getConversation(convId);
      setConversationId(convId);


      // 轉換對話訊息格式
      const conversationMessages: Message[] = response.conversation.messages.map((msg) => ({
        role: msg.role as 'user' | 'assistant',
        content: msg.content,
        sentiment: msg.sentiment,
      }));


      setMessages(conversationMessages);
      setError('');
    } catch (err: any) {
      setError('載入對話失敗');
      console.error('載入對話失敗:', err);
    } finally {
      setLoading(false);
    }
  };


  // 開始新對話
  const startNewConversation = () => {
    setConversationId(null);
    setMessages([
      {
        role: 'assistant',
        content:
          '您好！我是 AI 酒保「調酒大師」🍸\n\n我可以幫您：\n✨ 推薦適合的調酒\n📚 教您如何製作調酒\n💬 聊聊調酒文化和知識\n🎨 設計創意調酒配方\n\n請告訴我，今天想喝點什麼呢？',
      },
    ]);
    setError('');
  };

  // 🗑️ 刪除對話功能（新增）
  const deleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!window.confirm('確定要刪除這個對話嗎？')) {
      return;
    }
    
    try {
      await chatAPI.deleteConversation(convId);
      await loadConversations();
      
      if (convId === conversationId) {
        startNewConversation();
      }
    } catch (error) {
      console.error('刪除對話失敗:', error);
      setError('刪除對話失敗');
    }
  };


  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  // 初始化：載入對話列表和歡迎訊息
  useEffect(() => {
    loadConversations();
    startNewConversation();
  }, []);


  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();


    if (!inputMessage.trim() || loading) return;


    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError('');


    // 加入用戶訊息到介面
    const newUserMessage: Message = {
      role: 'user',
      content: userMessage,
    };
    setMessages((prev) => [...prev, newUserMessage]);
    setLoading(true);


    try {
      // 呼叫 API
      const response = await chatAPI.sendMessage(userMessage, conversationId || undefined);


      // 儲存 conversation ID
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }


      // 加入 AI 回應
      const aiMessage: Message = {
        role: 'assistant',
        content: response.message,
        sentiment: response.sentiment,
      };
      setMessages((prev) => [...prev, aiMessage]);


      // 重新載入對話列表以更新側邊欄
      loadConversations();
    } catch (err: any) {
      setError(err.response?.data?.error || '發送訊息失敗，請稍後再試');


      // 顯示錯誤訊息
      const errorMessage: Message = {
        role: 'assistant',
        content: `抱歉，我現在無法回應。錯誤：${err.response?.data?.error || '連接失敗'}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="flex gap-4 h-[calc(100vh-8rem)]">
      {/* 側邊欄 - 對話列表 */}
      <div
        className={`bg-white rounded-lg shadow-lg transition-all duration-300 ${
          sidebarOpen ? 'w-80' : 'w-0 overflow-hidden'
        }`}
      >
        <div className="h-full flex flex-col">
          {/* 側邊欄標題 */}
          <div className="bg-primary-600 text-white px-4 py-4 flex items-center justify-between">
            <h2 className="font-semibold flex items-center gap-2">
              <MessageCircle className="w-5 h-5" />
              對話記錄
            </h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="hover:bg-primary-700 p-1 rounded transition-colors lg:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>


          {/* 新對話按鈕 */}
          <div className="p-3 border-b border-gray-200">
            <button
              onClick={startNewConversation}
              className="w-full btn-primary flex items-center justify-center gap-2"
            >
              <Plus className="w-5 h-5" />
              新對話
            </button>
          </div>


          {/* 對話列表 */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {conversations.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-8">尚無對話記錄</p>
            ) : (
              conversations.map((conv) => {
                const lastMessage = conv.messages[conv.messages.length - 1];
                const preview = lastMessage?.content.substring(0, 30) + '...' || '新對話';
                const isActive = conv._id === conversationId;


                return (
                  <div key={conv._id} className="relative group">
                    <button
                      onClick={() => selectConversation(conv._id)}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        isActive
                          ? 'bg-primary-100 border-2 border-primary-500'
                          : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-1">
                        <span className="text-xs font-medium text-gray-500">
                          #{conv._id.slice(-6)}
                        </span>
                        <span className="text-xs text-gray-400">
                          {new Date(conv.updated_at).toLocaleDateString('zh-TW', {
                            month: 'short',
                            day: 'numeric',
                          })}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 line-clamp-2">{preview}</p>
                      <p className="text-xs text-gray-500 mt-1">{conv.messages.length} 則訊息</p>
                    </button>

                    {/* 🗑️ 刪除按鈕（新增）*/}
                    <button
                      onClick={(e) => deleteConversation(conv._id, e)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 
                                 opacity-0 group-hover:opacity-100 
                                 transition-opacity duration-200
                                 p-2 hover:bg-red-100 rounded-lg"
                      title="刪除對話"
                    >
                      <Trash2 className="w-4 h-4 text-red-500 hover:text-red-700" />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>


      {/* 主聊天區域 */}
      <div className="flex-1 bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
        {/* 標題 */}
        <div className="bg-primary-600 text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="hover:bg-primary-700 p-2 rounded transition-colors"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Bot className="w-8 h-8" />
                AI 酒保對話
              </h1>
              <p className="text-primary-100 text-sm mt-1">與專業 AI 酒保聊天，探索調酒世界</p>
            </div>
          </div>
        </div>


        {/* 訊息區域 */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
            >
              {/* 頭像 */}
              <div
                className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                  message.role === 'user'
                    ? 'bg-primary-100 text-primary-600'
                    : 'bg-gray-200 text-gray-700'
                }`}
              >
                {message.role === 'user' ? (
                  <UserIcon className="w-5 h-5" />
                ) : (
                  <Bot className="w-5 h-5" />
                )}
              </div>


              {/* 訊息氣泡 */}
              <div
                className={`max-w-[70%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-900 shadow-md'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>


                {/* 情感分數（僅顯示用戶訊息） */}
                {message.role === 'user' && message.sentiment !== undefined && (
                  <div className="mt-2 text-xs opacity-75">
                    情感：
                    {message.sentiment > 0.3
                      ? '😊 正面'
                      : message.sentiment < -0.3
                      ? '😔 負面'
                      : '😐 中性'}
                  </div>
                )}
              </div>
            </div>
          ))}


          {/* 載入中指示 */}
          {loading && (
            <div className="flex gap-3">
              <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                <Bot className="w-5 h-5 text-gray-700" />
              </div>
              <div className="bg-white rounded-lg px-4 py-3 shadow-md">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                  <span
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.1s' }}
                  ></span>
                  <span
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  ></span>
                </div>
              </div>
            </div>
          )}


          <div ref={messagesEndRef} />
        </div>


        {/* 錯誤提示 */}
        {error && (
          <div className="px-6 py-3 bg-red-50 border-t border-red-200">
            <div className="flex items-center gap-2 text-red-700 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          </div>
        )}


        {/* 輸入區域 */}
        <form onSubmit={handleSendMessage} className="border-t border-gray-200 p-4 bg-white">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="輸入訊息... (例如：推薦我一款適合夏天的調酒)"
              className="flex-1 input-field"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
              發送
            </button>
          </div>


          <p className="text-xs text-gray-500 mt-2">
            💡 提示：可以問我關於調酒的任何問題，或告訴我您的喜好讓我推薦
          </p>
        </form>
      </div>
    </div>
  );
};


export default ChatPage;
