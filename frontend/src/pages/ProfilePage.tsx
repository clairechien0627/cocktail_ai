import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authAPI, chatAPI } from '../services/api';
import { User, Settings, MessageCircle, Save } from 'lucide-react';
import type { Conversation } from '../types';

const ProfilePage = () => {
  const { user, updateUser } = useAuth();
  const [skillLevel, setSkillLevel] = useState(user?.preferences.skill_level || 'beginner');
  const [favoriteSpirits, setFavoriteSpirits] = useState<string[]>(
    user?.preferences.favorite_spirits || []
  );
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const spiritOptions = ['琴酒', '伏特加', '威士忌', '蘭姆酒', '龍舌蘭', '白蘭地'];

  // 載入對話歷史
  useEffect(() => {
    const loadConversations = async () => {
      try {
        const response = await chatAPI.getConversations();
        setConversations(response.conversations);
      } catch (error) {
        console.error('載入對話歷史失敗:', error);
      }
    };
    loadConversations();
  }, []);

  const handleSavePreferences = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await authAPI.updatePreferences({
        skill_level: skillLevel,
        favorite_spirits: favoriteSpirits,
      });

      // 更新本地用戶狀態
      if (user) {
        updateUser({
          ...user,
          preferences: {
            skill_level: skillLevel,
            favorite_spirits: favoriteSpirits,
          },
        });
      }

      setSuccess('偏好設定已更新！');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error || '更新失敗');
    } finally {
      setLoading(false);
    }
  };

  const toggleSpirit = (spirit: string) => {
    if (favoriteSpirits.includes(spirit)) {
      setFavoriteSpirits(favoriteSpirits.filter((s) => s !== spirit));
    } else {
      setFavoriteSpirits([...favoriteSpirits, spirit]);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <User className="w-8 h-8 text-primary-600" />
          個人資料
        </h1>
        <p className="text-gray-600">管理您的帳號和偏好設定</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 用戶資訊 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <User className="w-5 h-5" />
            基本資訊
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">用戶名稱</label>
              <input
                type="text"
                value={user?.username || ''}
                disabled
                className="input-field bg-gray-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="input-field bg-gray-50"
              />
            </div>
          </div>
        </div>

        {/* 偏好設定 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5" />
            偏好設定
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">調酒技能等級</label>
              <select
                value={skillLevel}
                onChange={(e) =>
                  setSkillLevel(e.target.value as 'beginner' | 'intermediate' | 'expert')
                }
                className="input-field"
              >
                <option value="beginner">初學者</option>
                <option value="intermediate">中級</option>
                <option value="expert">專家</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">喜愛的基酒</label>
              <div className="flex flex-wrap gap-2">
                {spiritOptions.map((spirit) => (
                  <button
                    key={spirit}
                    type="button"
                    onClick={() => toggleSpirit(spirit)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      favoriteSpirits.includes(spirit)
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {spirit}
                  </button>
                ))}
              </div>
            </div>

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                {success}
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <button
              onClick={handleSavePreferences}
              disabled={loading}
              className="w-full btn-primary disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Save className="w-5 h-5" />
              {loading ? '儲存中...' : '儲存設定'}
            </button>
          </div>
        </div>

        {/* 對話歷史 */}
        <div className="bg-white rounded-lg shadow-md p-6 lg:col-span-2">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <MessageCircle className="w-5 h-5" />
            對話歷史
          </h2>

          {conversations.length === 0 ? (
            <p className="text-gray-500 text-center py-8">尚無對話記錄</p>
          ) : (
            <div className="space-y-3">
              {conversations.map((conversation) => (
                <div
                  key={conversation._id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900">
                      對話 #{conversation._id.slice(-6)}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(conversation.updated_at).toLocaleDateString('zh-TW')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    {conversation.messages.length} 則訊息
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
