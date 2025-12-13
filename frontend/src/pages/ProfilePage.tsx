import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authAPI, personalitiesAPI } from '../services/api';
import { User, Settings, Save, Sparkles, Plus, Edit2, Trash2 } from 'lucide-react';
import type { Personality } from '../types';
import PersonalitySelector from '../components/PersonalitySelector';
import PersonalityFormSection from '../components/PersonalityFormSection';

const ProfilePage = () => {
  const { user, updateUser } = useAuth();
  const [personality, setPersonality] = useState(user?.preferences.personality || 'friendly');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  // 自訂性格管理狀態
  const [customPersonalities, setCustomPersonalities] = useState<Personality[]>([]);
  const [showPersonalityForm, setShowPersonalityForm] = useState(false);
  const [editingPersonality, setEditingPersonality] = useState<Personality | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  // 載入自訂性格
  useEffect(() => {
    const loadCustomPersonalities = async () => {
      try {
        const data = await personalitiesAPI.getPersonalities();
        setCustomPersonalities(data.custom);
      } catch (error) {
        console.error('載入自訂性格失敗:', error);
      }
    };

    loadCustomPersonalities();
  }, []);

  const handleSavePreferences = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await authAPI.updatePreferences({
        personality: personality,
      });

      // 更新本地用戶狀態
      if (user) {
        updateUser({
          ...user,
          preferences: {
            ...user.preferences,
            personality: personality,
          },
        });
      }

      setSuccess('性格設定已更新！');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error || '更新失敗');
    } finally {
      setLoading(false);
    }
  };

  // 自訂性格管理函數
  const handleCreatePersonality = async (data: any) => {
    try {
      await personalitiesAPI.createPersonality({
        name: data.name,
        description: data.description,
        icon: data.icon,
        prompt: {
          tone: data.tone,
          style: data.style,
          greeting: data.greeting || '',
          example_responses: data.exampleResponses || [],
          custom_rules: data.customRules || [],
        },
      });

      // 重新載入自訂性格列表
      const personalitiesData = await personalitiesAPI.getPersonalities();
      setCustomPersonalities(personalitiesData.custom);
      setShowPersonalityForm(false);
      setSuccess('自訂性格建立成功！');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      throw new Error(err.response?.data?.error || '建立失敗');
    }
  };

  const handleUpdatePersonality = async (data: any) => {
    if (!editingPersonality) return;

    try {
      await personalitiesAPI.updatePersonality(editingPersonality.personality_id, {
        name: data.name,
        description: data.description,
        icon: data.icon,
        prompt: {
          tone: data.tone,
          style: data.style,
          greeting: data.greeting || '',
          example_responses: data.exampleResponses || [],
          custom_rules: data.customRules || [],
        },
      });

      // 重新載入自訂性格列表
      const personalitiesData = await personalitiesAPI.getPersonalities();
      setCustomPersonalities(personalitiesData.custom);
      setShowPersonalityForm(false);
      setEditingPersonality(null);
      setSuccess('自訂性格更新成功！');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      throw new Error(err.response?.data?.error || '更新失敗');
    }
  };

  const handleDeletePersonality = async (personalityId: string) => {
    try {
      await personalitiesAPI.deletePersonality(personalityId);

      // 重新載入自訂性格列表
      const personalitiesData = await personalitiesAPI.getPersonalities();
      setCustomPersonalities(personalitiesData.custom);
      setDeleteConfirm(null);
      setSuccess('自訂性格刪除成功！');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error || '刪除失敗');
    }
  };

  const handleEditClick = async (personalityId: string) => {
    try {
      const personality = await personalitiesAPI.getPersonality(personalityId);
      setEditingPersonality(personality as any);
      setShowPersonalityForm(true);
    } catch (err) {
      setError('載入性格詳情失敗');
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <User className="w-8 h-8 text-primary-600" />
          個人資料
        </h1>
        <p className="text-gray-600">管理您的帳號和性格設定</p>
      </div>

      <div className="space-y-8">
        {/* 基本資訊 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <User className="w-5 h-5" />
            基本資訊
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">用戶名稱</label>
              <input
                type="text"
                value={user?.username || ''}
                disabled
                className="input-field bg-gray-50"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="input-field bg-gray-50"
              />
            </div>
          </div>
        </div>

        {/* 性格設定 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Settings className="w-5 h-5" />
              性格設定
            </h2>
            <button
              onClick={handleSavePreferences}
              disabled={loading}
              className="btn-primary disabled:opacity-50 flex items-center gap-2 px-6 py-2"
            >
              <Save className="w-5 h-5" />
              {loading ? '儲存中...' : '儲存設定'}
            </button>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                AI 酒保性格
              </label>
              <PersonalitySelector value={personality} onChange={setPersonality} />
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
          </div>
        </div>

        {/* 自訂性格管理 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary-600" />
              自訂性格管理
              <span className="text-sm font-normal text-gray-500">
                ({customPersonalities.length}/10)
              </span>
            </h2>
            {customPersonalities.length < 10 && (
              <button
                onClick={() => {
                  setEditingPersonality(null);
                  setShowPersonalityForm(true);
                }}
                className="btn-primary flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                建立自訂性格
              </button>
            )}
          </div>

          {/* 性格建立/編輯表單 */}
          <PersonalityFormSection
            isOpen={showPersonalityForm}
            onClose={() => {
              setShowPersonalityForm(false);
              setEditingPersonality(null);
            }}
            onSubmit={editingPersonality ? handleUpdatePersonality : handleCreatePersonality}
            initialData={
              editingPersonality
                ? {
                    name: editingPersonality.name,
                    description: editingPersonality.description || '',
                    icon: editingPersonality.icon,
                    tone: (editingPersonality as any).prompt?.tone || '',
                    style: (editingPersonality as any).prompt?.style || '',
                    greeting: (editingPersonality as any).prompt?.greeting || '',
                    exampleResponses: (editingPersonality as any).prompt?.example_responses || ['', '', ''],
                    customRules: (editingPersonality as any).prompt?.custom_rules || [''],
                  }
                : undefined
            }
            mode={editingPersonality ? 'edit' : 'create'}
          />

          {/* 自訂性格列表 */}
          {customPersonalities.length === 0 && !showPersonalityForm ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 mb-2">尚未建立自訂性格</p>
              <p className="text-sm text-gray-500">
                點擊「建立自訂性格」按鈕開始自訂您的專屬 AI 酒保
              </p>
            </div>
          ) : (
            !showPersonalityForm && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {customPersonalities.map((p) => (
                  <div
                    key={p.personality_id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow relative group"
                  >
                    {/* 操作按鈕 */}
                    <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => handleEditClick(p.personality_id)}
                        className="p-1.5 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 transition-colors"
                        title="編輯"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteConfirm(p.personality_id)}
                        className="p-1.5 bg-red-50 text-red-600 rounded-md hover:bg-red-100 transition-colors"
                        title="刪除"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    {/* 性格資訊 */}
                    <div className="text-center mb-3">
                      <div className="text-4xl mb-2 flex justify-center">{p.icon}</div>
                      <h3 className="font-semibold text-gray-900">{p.name}</h3>
                      {p.description && (
                        <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                          {p.description}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )
          )}

          {/* 刪除確認對話框 */}
          {deleteConfirm && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">確認刪除</h3>
                <p className="text-gray-600 mb-6">
                  您確定要刪除這個自訂性格嗎？此操作無法復原。
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => setDeleteConfirm(null)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    取消
                  </button>
                  <button
                    onClick={() => handleDeletePersonality(deleteConfirm)}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    刪除
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
