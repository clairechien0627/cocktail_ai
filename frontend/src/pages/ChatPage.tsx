import { useState, useEffect, useRef } from 'react';
import { chatAPI, cocktailAPI, favoritesAPI, authAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Send, Bot, User as UserIcon, AlertCircle, Menu, Plus, MessageCircle, X, Trash2, Wine, Sparkles, Heart } from 'lucide-react';
import type { Message, Conversation, CocktailCardData, Cocktail, FavoriteItem } from '../types';
import { InteractiveCocktailCard } from '../components/InteractiveCocktailCard';
import { RecordForm } from '../components/Record';
import { CocktailDetailModal } from '../components/CocktailDetailModal';
import { MarkdownMessage } from '../components/MarkdownMessage';
import PersonalityQuickSelector from '../components/PersonalityQuickSelector';


const ChatPage = () => {
  const { user, updateUser } = useAuth();  // 新增：獲取用戶資訊和更新函數
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);  // 預設關閉，給推薦區更多空間
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 性格選擇狀態
  const [selectedPersonality, setSelectedPersonality] = useState<string>(
    user?.preferences.personality || 'friendly'
  );

  // 新增：推薦卡片相關狀態
  const [recommendedCocktails, setRecommendedCocktails] = useState<CocktailCardData[]>([]);
  const [showRecordForm, setShowRecordForm] = useState(false);
  const [selectedCocktailForRecord, setSelectedCocktailForRecord] = useState<Cocktail | null>(null);

  // 收藏相關狀態
  const [activeTab, setActiveTab] = useState<'recommendations' | 'favorites'>('recommendations');
  const [favoritedCocktails, setFavoritedCocktails] = useState<FavoriteItem[]>([]);
  const [favoritedIds, setFavoritedIds] = useState<Set<string>>(new Set());
  const [loadingFavorites, setLoadingFavorites] = useState(false);

  // 詳細視圖相關狀態
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedCocktailDetail, setSelectedCocktailDetail] = useState<Cocktail | null>(null);
  const [langZh, setLangZh] = useState(false);

  // 小視窗顯示推薦/收藏側邊欄
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);


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
        cocktails: msg.cocktails || [],  // 新增：映射 cocktails 欄位
      }));


      setMessages(conversationMessages);
      setError('');

      // 新增：提取所有歷史推薦到右側卡片區
      const allCocktails = conversationMessages
        .filter(msg => msg.cocktails && msg.cocktails.length > 0)
        .flatMap(msg => msg.cocktails!);
      setRecommendedCocktails(allCocktails);

      console.log('[ChatPage] 載入對話，提取到', allCocktails.length, '個歷史推薦');

      // 新增：載入該對話的收藏
      await loadFavorites(convId);
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
    // 新增：清空右側推薦卡片
    setRecommendedCocktails([]);
    // 新增：清空收藏列表（新對話沒有對話 ID，所以收藏為空）
    setFavoritedCocktails([]);
    setFavoritedIds(new Set());
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

  // 性格切換處理函數
  const handlePersonalityChange = async (newPersonality: string) => {
    // 立即更新本地狀態
    setSelectedPersonality(newPersonality);
    console.log('[ChatPage] 切換性格至:', newPersonality);

    // 自動保存到用戶偏好
    try {
      if (user) {
        await authAPI.updatePreferences({
          ...user.preferences,
          personality: newPersonality,
        });

        // 更新本地用戶狀態
        updateUser({
          ...user,
          preferences: {
            ...user.preferences,
            personality: newPersonality,
          },
        });

        console.log('[ChatPage] 性格偏好已保存');
      }
    } catch (error) {
      console.error('[ChatPage] 保存性格偏好失敗:', error);
      // 不顯示錯誤，保持 UX 流暢
    }
  };


  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  // 載入收藏列表
  const loadFavorites = async (convId?: string | null) => {
    try {
      setLoadingFavorites(true);
      const conversationIdToUse = convId || conversationId;

      if (!conversationIdToUse) {
        // 沒有對話 ID 時，清空收藏
        setFavoritedCocktails([]);
        setFavoritedIds(new Set());
        console.log('[ChatPage] 無對話 ID，清空收藏列表');
        return;
      }

      const [favoritesResponse, idsResponse] = await Promise.all([
        favoritesAPI.getAll(1, 100, conversationIdToUse),  // 載入前 100 個收藏
        favoritesAPI.getIds(conversationIdToUse)
      ]);

      setFavoritedCocktails(favoritesResponse.favorites);
      setFavoritedIds(new Set(idsResponse.favorited_ids));

      console.log('[ChatPage] 載入對話', conversationIdToUse, '的收藏:', favoritesResponse.total, '個');
    } catch (error) {
      console.error('載入收藏失敗:', error);
    } finally {
      setLoadingFavorites(false);
    }
  };

  // 處理收藏切換
  const handleFavoriteToggle = async (cocktailId: string, isFavorited: boolean) => {
    try {
      // 先執行 API 調用（但不等待）
      // InteractiveCocktailCard 會處理實際的 API 調用

      // 樂觀更新：立即更新 UI
      if (isFavorited) {
        // 添加到本地狀態
        setFavoritedIds(prev => new Set(prev).add(cocktailId));
        console.log('[ChatPage] 樂觀更新：添加收藏', cocktailId);
      } else {
        // 從本地狀態移除
        setFavoritedIds(prev => {
          const newSet = new Set(prev);
          newSet.delete(cocktailId);
          return newSet;
        });
        // 從收藏列表移除
        setFavoritedCocktails(prev => prev.filter(c => c._id !== cocktailId));
        console.log('[ChatPage] 樂觀更新：移除收藏', cocktailId);
      }

      // 延遲重新載入收藏列表（給 API 時間完成）
      if (isFavorited) {
        setTimeout(async () => {
          console.log('[ChatPage] 重新載入收藏列表');
          await loadFavorites();
        }, 1000); // 增加到 1 秒
      }
    } catch (error) {
      console.error('[ChatPage] 收藏切換失敗:', error);
      // 如果失敗，回滾狀態
      if (isFavorited) {
        setFavoritedIds(prev => {
          const newSet = new Set(prev);
          newSet.delete(cocktailId);
          return newSet;
        });
      } else {
        setFavoritedIds(prev => new Set(prev).add(cocktailId));
      }
    }
  };

  // 初始化：載入對話列表、歡迎訊息和收藏
  useEffect(() => {
    loadConversations();
    startNewConversation();
    loadFavorites();
  }, []);


  // 處理卡片快速操作
  const handleCardQuickAction = (action: 'tell_more' | 'similar' | 'try_this', cocktailId: string) => {
    // 從推薦列表或收藏列表中找到調酒資訊
    const cocktail = recommendedCocktails.find(c => c._id === cocktailId)
      || favoritedCocktails.find(c => c._id === cocktailId);
    const cocktailName = cocktail?.name_zh || cocktail?.name || '這款調酒';

    let message = '';
    switch (action) {
      case 'tell_more':
        message = `告訴我更多關於 ${cocktailName} 的資訊`;
        break;
      case 'similar':
        message = `推薦類似 ${cocktailName} 的調酒`;
        break;
      case 'try_this':
        message = `我想試試 ${cocktailName}，需要準備什麼？`;
        break;
    }

    setInputMessage(message);
    // 可選：自動發送
    // document.getElementById('chat-form')?.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  };

  // 處理查看調酒詳細
  const handleViewDetails = async (cocktailId: string) => {
    try {
      setLoading(true);
      const response = await cocktailAPI.getById(cocktailId);
      setSelectedCocktailDetail(response.cocktail);
      setShowDetailModal(true);
    } catch (error) {
      console.error('載入調酒資訊失敗:', error);
      setError('載入調酒資訊失敗');
    } finally {
      setLoading(false);
    }
  };

  // 處理詳細視圖中的收藏切換
  const handleDetailFavoriteToggle = async () => {
    if (!selectedCocktailDetail) return;
    const cocktailId = selectedCocktailDetail._id;
    const currentlyFavorited = favoritedIds.has(cocktailId);

    try {
      // 樂觀更新 UI
      if (currentlyFavorited) {
        // 取消收藏
        setFavoritedIds(prev => {
          const newSet = new Set(prev);
          newSet.delete(cocktailId);
          return newSet;
        });
        setFavoritedCocktails(prev => prev.filter(c => c._id !== cocktailId));
        console.log('[ChatPage] 詳細視圖：取消收藏', cocktailId);

        // 調用 API
        await favoritesAPI.remove(cocktailId);
      } else {
        // 添加收藏
        setFavoritedIds(prev => new Set(prev).add(cocktailId));
        console.log('[ChatPage] 詳細視圖：添加收藏', cocktailId);

        // 調用 API
        await favoritesAPI.add(cocktailId);

        // 等待 API 完成後重新載入收藏列表
        setTimeout(async () => {
          console.log('[ChatPage] 重新載入收藏列表（從詳細視圖）');
          await loadFavorites();
        }, 1000);
      }
    } catch (error) {
      console.error('[ChatPage] 詳細視圖收藏切換失敗:', error);
      // 回滾狀態
      if (currentlyFavorited) {
        setFavoritedIds(prev => new Set(prev).add(cocktailId));
      } else {
        setFavoritedIds(prev => {
          const newSet = new Set(prev);
          newSet.delete(cocktailId);
          return newSet;
        });
      }
    }
  };

  // 新增：處理記錄飲用
  const handleRecord = async (cocktailId?: string) => {
    try {
      setLoading(true);
      // 如果沒有傳入 cocktailId，使用當前詳細視圖的調酒
      const targetId = cocktailId || selectedCocktailDetail?._id;
      if (!targetId) return;

      const response = await cocktailAPI.getById(targetId);
      setSelectedCocktailForRecord(response.cocktail);
      setShowRecordForm(true);
      // 如果是從詳細視圖打開的，關閉詳細視圖
      if (!cocktailId && selectedCocktailDetail) {
        setShowDetailModal(false);
      }
    } catch (error) {
      console.error('載入調酒資訊失敗:', error);
      setError('載入調酒資訊失敗');
    } finally {
      setLoading(false);
    }
  };

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
      // 呼叫 API（使用當前選中的性格）
      const response = await chatAPI.sendMessage(
        userMessage,
        conversationId || undefined,
        selectedPersonality
      );

      // Debug 日誌
      console.log('[ChatPage] API 回應:', {
        conversation_id: response.conversation_id,
        message_length: response.message.length,
        has_cocktails: !!response.cocktails,
        cocktails_count: response.cocktails?.length || 0,
        cocktails: response.cocktails
      });

      // 儲存 conversation ID
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }


      // 加入 AI 回應（包含調酒卡片資料）
      const aiMessage: Message = {
        role: 'assistant',
        content: response.message,
        sentiment: response.sentiment,
        cocktails: response.cocktails,  // 新增：調酒卡片資料
      };

      console.log('[ChatPage] 新增的訊息:', {
        role: aiMessage.role,
        content_length: aiMessage.content.length,
        has_cocktails: !!aiMessage.cocktails,
        cocktails_count: aiMessage.cocktails?.length || 0
      });

      setMessages((prev) => [...prev, aiMessage]);

      // 新增：累積新推薦到右側卡片區
      if (response.cocktails && response.cocktails.length > 0) {
        setRecommendedCocktails((prev) => [...prev, ...response.cocktails]);
        console.log('[ChatPage] 累積推薦，目前共', recommendedCocktails.length + response.cocktails.length, '個調酒');
      }

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
    <>
      <div className="flex gap-4 h-[calc(100vh-8rem)]">
        {/* 左側邊欄 - 對話列表 */}
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

                      {/* 刪除按鈕 */}
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


        {/* 中間 - 主聊天區域 */}
        <div className="flex-1 bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
          {/* 標題 */}
          <div className="bg-primary-600 text-white px-4 py-2.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="hover:bg-primary-700 p-1.5 rounded transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>
              <h1 className="text-xl font-bold flex items-center gap-2">
                <Bot className="w-6 h-6" />
                AI 酒保
              </h1>
            </div>

            {/* 中間 - 性格選擇器 (桌面版) */}
            <div className="hidden md:block">
              <PersonalityQuickSelector
                value={selectedPersonality}
                onChange={handlePersonalityChange}
              />
            </div>

            {/* 小視窗推薦/收藏按鈕 */}
            <button
              onClick={() => setShowMobileSidebar(!showMobileSidebar)}
              className="lg:hidden flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
            >
              {activeTab === 'recommendations' ? (
                <>
                  <Wine className="w-5 h-5" />
                  <span className="text-sm font-medium">推薦 ({recommendedCocktails.length})</span>
                </>
              ) : (
                <>
                  <Heart className="w-5 h-5" />
                  <span className="text-sm font-medium">收藏 ({favoritedCocktails.length})</span>
                </>
              )}
            </button>
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
                <div className="max-w-[70%]">
                  <div
                    className={`rounded-lg px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-white text-gray-900 shadow-md'
                    }`}
                  >
                    {/* AI 訊息使用 Markdown 渲染，用戶訊息使用純文字 */}
                    {message.role === 'assistant' ? (
                      <MarkdownMessage content={message.content} />
                    ) : (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    )}

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
          <form id="chat-form" onSubmit={handleSendMessage} className="border-t border-gray-200 p-4 bg-white">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="輸入訊息..."
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
          </form>
        </div>


        {/* 右側 - 推薦/收藏卡片區域 */}
        <div className="hidden lg:flex lg:w-96 bg-white rounded-lg shadow-lg overflow-hidden flex-col">
          {/* Tab 切換按鈕 */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white px-4 py-3">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('recommendations')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                  activeTab === 'recommendations'
                    ? 'bg-white text-primary-600 shadow-md'
                    : 'bg-white/10 text-white hover:bg-white/20'
                }`}
              >
                <div className="flex items-center justify-center gap-1.5">
                  <Wine className="w-4 h-4" />
                  <span>推薦</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                    activeTab === 'recommendations'
                      ? 'bg-primary-100 text-primary-700'
                      : 'bg-white/20'
                  }`}>
                    {recommendedCocktails.length}
                  </span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('favorites')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                  activeTab === 'favorites'
                    ? 'bg-white text-primary-600 shadow-md'
                    : 'bg-white/10 text-white hover:bg-white/20'
                }`}
              >
                <div className="flex items-center justify-center gap-1.5">
                  <Heart className="w-4 h-4" />
                  <span>收藏</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                    activeTab === 'favorites'
                      ? 'bg-primary-100 text-primary-700'
                      : 'bg-white/20'
                  }`}>
                    {favoritedCocktails.length}
                  </span>
                </div>
              </button>
            </div>
          </div>

          {/* 卡片列表 */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
            {activeTab === 'recommendations' ? (
              // 推薦列表
              recommendedCocktails.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center px-6">
                  <div className="bg-gradient-to-br from-primary-100 to-primary-200 rounded-full p-6 mb-4">
                    <Sparkles className="w-12 h-12 text-primary-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">尚無推薦</h3>
                  <p className="text-sm text-gray-500">
                    向 AI 酒保詢問推薦，推薦的調酒卡片將會顯示在這裡
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {recommendedCocktails.map((cocktail, index) => (
                    <InteractiveCocktailCard
                      key={`rec-${cocktail._id}-${index}`}
                      cocktail={cocktail}
                      isFavorited={favoritedIds.has(cocktail._id)}
                      conversationId={conversationId}
                      onFavoriteToggle={handleFavoriteToggle}
                      onQuickAction={handleCardQuickAction}
                      onImageClick={handleViewDetails}
                    />
                  ))}
                </div>
              )
            ) : (
              // 收藏列表
              loadingFavorites ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-gray-500">載入中...</div>
                </div>
              ) : favoritedCocktails.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center px-6">
                  <div className="bg-gradient-to-br from-red-100 to-pink-200 rounded-full p-6 mb-4">
                    <Heart className="w-12 h-12 text-red-500" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-2">尚無收藏</h3>
                  <p className="text-sm text-gray-500">
                    點擊調酒卡片上的愛心按鈕來收藏您喜歡的調酒
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {favoritedCocktails.map((cocktail, index) => (
                    <InteractiveCocktailCard
                      key={`fav-${cocktail._id}-${index}`}
                      cocktail={cocktail as CocktailCardData}
                      isFavorited={true}
                      conversationId={conversationId}
                      onFavoriteToggle={handleFavoriteToggle}
                      onQuickAction={handleCardQuickAction}
                      onImageClick={handleViewDetails}
                    />
                  ))}
                </div>
              )
            )}
          </div>
        </div>
      </div>

      {/* 小視窗推薦/收藏側邊欄 */}
      {showMobileSidebar && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-50"
          onClick={() => setShowMobileSidebar(false)}
        >
          <div
            className="absolute right-0 top-0 bottom-0 w-full max-w-sm bg-white shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="h-full flex flex-col">
              {/* Tab 切換按鈕 */}
              <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white px-4 py-3">
                <div className="flex gap-2 flex-1">
                  <button
                    onClick={() => setActiveTab('recommendations')}
                    className={`flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                      activeTab === 'recommendations'
                        ? 'bg-white text-primary-600 shadow-md'
                        : 'bg-white/10 text-white hover:bg-white/20'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-1.5">
                      <Wine className="w-4 h-4" />
                      <span>推薦</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                        activeTab === 'recommendations'
                          ? 'bg-primary-100 text-primary-700'
                          : 'bg-white/20'
                      }`}>
                        {recommendedCocktails.length}
                      </span>
                    </div>
                  </button>
                  <button
                    onClick={() => setActiveTab('favorites')}
                    className={`flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                      activeTab === 'favorites'
                        ? 'bg-white text-primary-600 shadow-md'
                        : 'bg-white/10 text-white hover:bg-white/20'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-1.5">
                      <Heart className="w-4 h-4" />
                      <span>收藏</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                        activeTab === 'favorites'
                          ? 'bg-primary-100 text-primary-700'
                          : 'bg-white/20'
                      }`}>
                        {favoritedCocktails.length}
                      </span>
                    </div>
                  </button>
                </div>
                <button
                  onClick={() => setShowMobileSidebar(false)}
                  className="hover:bg-white/20 p-2 rounded transition-colors ml-2"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* 卡片列表 */}
              <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                {activeTab === 'recommendations' ? (
                  // 推薦列表
                  recommendedCocktails.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center px-6">
                      <div className="bg-gradient-to-br from-primary-100 to-primary-200 rounded-full p-6 mb-4">
                        <Sparkles className="w-12 h-12 text-primary-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-700 mb-2">尚無推薦</h3>
                      <p className="text-sm text-gray-500">
                        向 AI 酒保詢問推薦，推薦的調酒卡片將會顯示在這裡
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {recommendedCocktails.map((cocktail, index) => (
                        <InteractiveCocktailCard
                          key={`mobile-rec-${cocktail._id}-${index}`}
                          cocktail={cocktail}
                          isFavorited={favoritedIds.has(cocktail._id)}
                          conversationId={conversationId}
                          onFavoriteToggle={handleFavoriteToggle}
                          onQuickAction={handleCardQuickAction}
                          onImageClick={handleViewDetails}
                        />
                      ))}
                    </div>
                  )
                ) : (
                  // 收藏列表
                  loadingFavorites ? (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-gray-500">載入中...</div>
                    </div>
                  ) : favoritedCocktails.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center px-6">
                      <div className="bg-gradient-to-br from-red-100 to-pink-200 rounded-full p-6 mb-4">
                        <Heart className="w-12 h-12 text-red-500" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-700 mb-2">尚無收藏</h3>
                      <p className="text-sm text-gray-500">
                        點擊調酒卡片上的愛心按鈕來收藏您喜歡的調酒
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {favoritedCocktails.map((cocktail, index) => (
                        <InteractiveCocktailCard
                          key={`mobile-fav-${cocktail._id}-${index}`}
                          cocktail={cocktail as CocktailCardData}
                          isFavorited={true}
                          conversationId={conversationId}
                          onFavoriteToggle={handleFavoriteToggle}
                          onQuickAction={handleCardQuickAction}
                          onImageClick={handleViewDetails}
                        />
                      ))}
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 調酒詳細視圖 */}
      {showDetailModal && selectedCocktailDetail && (
        <CocktailDetailModal
          cocktail={selectedCocktailDetail}
          isOpen={showDetailModal}
          isFavorited={favoritedIds.has(selectedCocktailDetail._id)}
          langZh={langZh}
          onClose={() => {
            setShowDetailModal(false);
            setSelectedCocktailDetail(null);
          }}
          onLangChange={setLangZh}
          onRecord={() => handleRecord()}
          onFavoriteToggle={handleDetailFavoriteToggle}
        />
      )}

      {/* RecordForm 彈窗 */}
      {showRecordForm && selectedCocktailForRecord && (
        <RecordForm
          cocktail={selectedCocktailForRecord}
          onClose={() => {
            setShowRecordForm(false);
            setSelectedCocktailForRecord(null);
          }}
          onSuccess={() => {
            setShowRecordForm(false);
            setSelectedCocktailForRecord(null);
          }}
        />
      )}
    </>
  );
};


export default ChatPage;
