import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Save, X, Sparkles } from 'lucide-react';

interface PersonalityFormData {
  name: string;
  description: string;
  icon: string;
  tone: string;
  style: string;
  greeting?: string;
  exampleResponses?: string[];
  customRules?: string[];
}

interface PersonalityFormSectionProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PersonalityFormData) => Promise<void>;
  initialData?: PersonalityFormData;
  mode: 'create' | 'edit';
}

// 預設圖標選項
const DEFAULT_ICONS = [
  '🎭', '🎨', '🎪', '🎯', '🔬', '🌟', '💫', '✨',
  '🎬', '🎸', '🍸', '🍹', '🥃', '🍷', '🍾', '🎵',
  '🔮', '🎩', '🎓', '🎖️'
];

const PersonalityFormSection: React.FC<PersonalityFormSectionProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  mode,
}) => {
  // 表單狀態
  const [formData, setFormData] = useState<PersonalityFormData>(
    initialData || {
      name: '',
      description: '',
      icon: '🎭',
      tone: '',
      style: '',
      greeting: '',
      exampleResponses: ['', '', ''],
      customRules: [''],
    }
  );

  // UI 狀態
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 監聽 initialData 變化，更新表單資料
  useEffect(() => {
    if (isOpen && initialData) {
      // 打開表單且有初始資料時，更新 formData
      setFormData(initialData);
      // 如果有進階選項資料，自動展開進階區塊
      if (initialData.greeting || initialData.exampleResponses?.some(r => r) || initialData.customRules?.some(r => r)) {
        setShowAdvanced(true);
      }
    } else if (!isOpen) {
      // 關閉表單時，重置為空白表單
      setFormData({
        name: '',
        description: '',
        icon: '🎭',
        tone: '',
        style: '',
        greeting: '',
        exampleResponses: ['', '', ''],
        customRules: [''],
      });
      setShowAdvanced(false);
      setError('');
    }
  }, [isOpen, initialData]);

  // 更新表單欄位
  const updateField = (field: keyof PersonalityFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // 更新陣列欄位
  const updateArrayField = (field: 'exampleResponses' | 'customRules', index: number, value: string) => {
    setFormData((prev) => {
      const array = [...(prev[field] || [])];
      array[index] = value;
      return { ...prev, [field]: array };
    });
  };

  // 新增陣列項目
  const addArrayItem = (field: 'exampleResponses' | 'customRules') => {
    setFormData((prev) => ({
      ...prev,
      [field]: [...(prev[field] || []), ''],
    }));
  };

  // 刪除陣列項目
  const removeArrayItem = (field: 'exampleResponses' | 'customRules', index: number) => {
    setFormData((prev) => ({
      ...prev,
      [field]: (prev[field] || []).filter((_, i) => i !== index),
    }));
  };

  // 表單驗證
  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError('請輸入性格名稱');
      return false;
    }
    if (!formData.tone.trim()) {
      setError('請輸入語氣設定');
      return false;
    }
    if (!formData.style.trim()) {
      setError('請輸入風格設定');
      return false;
    }
    return true;
  };

  // 提交表單
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      // 過濾空的陣列項目
      const cleanedData = {
        ...formData,
        exampleResponses: (formData.exampleResponses || []).filter((r) => r.trim()),
        customRules: (formData.customRules || []).filter((r) => r.trim()),
      };

      await onSubmit(cleanedData);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || '操作失敗');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6 border-2 border-primary-200">
      {/* 標題列 */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary-600" />
          {mode === 'create' ? '建立自訂性格' : '編輯自訂性格'}
        </h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
          type="button"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      {/* 錯誤提示 */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 基礎資訊 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 性格名稱 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              性格名稱 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="例如：專業調酒師"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              maxLength={50}
            />
          </div>

          {/* Icon 選擇器 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">圖標</label>
            <div className="grid grid-cols-10 gap-2">
              {DEFAULT_ICONS.map((icon) => (
                <button
                  key={icon}
                  type="button"
                  onClick={() => updateField('icon', icon)}
                  className={`
                    text-2xl p-2 rounded-lg transition-all flex items-center justify-center
                    ${
                      formData.icon === icon
                        ? 'bg-primary-100 ring-2 ring-primary-500 scale-110'
                        : 'bg-gray-100 hover:bg-gray-200'
                    }
                  `}
                >
                  {icon}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 描述 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">描述</label>
          <textarea
            value={formData.description}
            onChange={(e) => updateField('description', e.target.value)}
            placeholder="簡短描述這個性格的特點..."
            rows={2}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            maxLength={200}
          />
        </div>

        {/* Prompt 基礎設定 */}
        <div className="border-t pt-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Prompt 設定</h4>

          <div className="space-y-4">
            {/* Tone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                語氣 (Tone) <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.tone}
                onChange={(e) => updateField('tone', e.target.value)}
                placeholder="例如：專業但不失幽默"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                maxLength={100}
              />
            </div>

            {/* Style */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                風格 (Style) <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.style}
                onChange={(e) => updateField('style', e.target.value)}
                placeholder="例如：用專業術語解釋，但加入有趣的比喻"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                maxLength={200}
              />
            </div>
          </div>
        </div>

        {/* 進階選項 */}
        <div className="border-t pt-4">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
          >
            {showAdvanced ? (
              <>
                <ChevronUp className="w-5 h-5" />
                隱藏進階選項
              </>
            ) : (
              <>
                <ChevronDown className="w-5 h-5" />
                顯示進階選項
              </>
            )}
          </button>

          {showAdvanced && (
            <div className="mt-4 space-y-4 pl-4 border-l-2 border-primary-200">
              {/* Greeting */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  打招呼語 (Greeting)
                </label>
                <input
                  type="text"
                  value={formData.greeting}
                  onChange={(e) => updateField('greeting', e.target.value)}
                  placeholder="例如：歡迎！準備好探索調酒的藝術了嗎？"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  maxLength={200}
                />
              </div>

              {/* Example Responses */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  回應範例 (最多 3 個)
                </label>
                {(formData.exampleResponses || []).slice(0, 3).map((response, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={response}
                      onChange={(e) => updateArrayField('exampleResponses', index, e.target.value)}
                      placeholder={`範例 ${index + 1}`}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      maxLength={300}
                    />
                  </div>
                ))}
              </div>

              {/* Custom Rules */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  自訂規則
                </label>
                {(formData.customRules || []).map((rule, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={rule}
                      onChange={(e) => updateArrayField('customRules', index, e.target.value)}
                      placeholder={`規則 ${index + 1}`}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      maxLength={200}
                    />
                    {(formData.customRules || []).length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeArrayItem('customRules', index)}
                        className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    )}
                  </div>
                ))}
                {(formData.customRules || []).length < 5 && (
                  <button
                    type="button"
                    onClick={() => addArrayItem('customRules')}
                    className="text-sm text-primary-600 hover:text-primary-700"
                  >
                    + 新增規則
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* 操作按鈕 */}
        <div className="flex gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            disabled={loading}
          >
            取消
          </button>
          <button
            type="submit"
            className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading}
          >
            <Save className="w-5 h-5" />
            {loading ? '儲存中...' : mode === 'create' ? '建立性格' : '更新性格'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PersonalityFormSection;
