import React, { useState, useEffect } from 'react';
import { X, Heart, ThumbsUp, Meh, ThumbsDown, MapPin, Calendar, StickyNote } from 'lucide-react';
import type { Cocktail, PreferenceLevel, CreateRecordData, UpdateRecordData, DrinkingRecord } from '../../types';
import { recordsAPI } from '../../services/api';

interface RecordFormProps {
  cocktail: Cocktail;
  existingRecord?: DrinkingRecord | null;
  onClose: () => void;
  onSuccess: () => void;
}

const RecordForm: React.FC<RecordFormProps> = ({ cocktail, existingRecord, onClose, onSuccess }) => {
  const [preference, setPreference] = useState<PreferenceLevel>('neutral');
  const [notes, setNotes] = useState('');
  const [drunkAt, setDrunkAt] = useState('');
  const [location, setLocation] = useState('');
  const [selectedMoodTags, setSelectedMoodTags] = useState<string[]>([]);
  const [availableMoodTags, setAvailableMoodTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 載入預設心情標籤
  useEffect(() => {
    const loadMoodTags = async () => {
      try {
        const response = await recordsAPI.getMoodTags();
        setAvailableMoodTags(response.mood_tags);
      } catch (err) {
        console.error('Failed to load mood tags:', err);
        // 使用預設標籤
        setAvailableMoodTags(['慶祝', '放鬆', '約會', '聚會', '獨飲', '嘗鮮', '工作後', '週末']);
      }
    };
    loadMoodTags();
  }, []);

  // 如果是編輯模式，載入現有資料
  useEffect(() => {
    if (existingRecord) {
      setPreference(existingRecord.preference);
      setNotes(existingRecord.notes);
      // 直接使用後端傳回的時間字串（已經是台灣時間），移除時區資訊
      if (existingRecord.drunk_at) {
        const timeStr = existingRecord.drunk_at.replace('Z', '').replace('+08:00', '').slice(0, 16);
        setDrunkAt(timeStr);
      } else {
        setDrunkAt('');
      }
      setLocation(existingRecord.location || '');
      setSelectedMoodTags(existingRecord.mood_tags || []);
    } else {
      // 新建模式，設定預設時間為現在（本地時間）
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      setDrunkAt(`${year}-${month}-${day}T${hours}:${minutes}`);
    }
  }, [existingRecord]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const recordData = {
        preference,
        notes,
        drunk_at: drunkAt, // 直接使用本地時間字串，不轉換為 ISO
        location: location || undefined,
        mood_tags: selectedMoodTags,
      };

      if (existingRecord) {
        // 更新現有紀錄
        await recordsAPI.update(existingRecord._id, recordData as UpdateRecordData);
      } else {
        // 建立新紀錄
        await recordsAPI.create({
          cocktail_id: cocktail._id,
          ...recordData,
        } as CreateRecordData);
      }

      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || '儲存失敗，請重試');
    } finally {
      setLoading(false);
    }
  };

  const toggleMoodTag = (tag: string) => {
    setSelectedMoodTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const preferenceOptions = [
    { value: 'loved' as PreferenceLevel, icon: Heart, label: '超愛', color: 'text-red-500', bgColor: 'bg-red-50' },
    { value: 'liked' as PreferenceLevel, icon: ThumbsUp, label: '喜歡', color: 'text-green-500', bgColor: 'bg-green-50' },
    { value: 'neutral' as PreferenceLevel, icon: Meh, label: '普通', color: 'text-gray-500', bgColor: 'bg-gray-50' },
    { value: 'disliked' as PreferenceLevel, icon: ThumbsDown, label: '不愛', color: 'text-blue-500', bgColor: 'bg-blue-50' },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-primary-600 text-white px-6 py-4 flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <StickyNote className="w-6 h-6" />
            <h2 className="text-xl font-bold">
              {existingRecord ? '編輯飲用紀錄' : '記錄飲用體驗'}
            </h2>
          </div>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Cocktail Info */}
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
            {cocktail.image_url && (
              <img
                src={cocktail.image_url}
                alt={cocktail.name}
                className="w-20 h-20 object-cover rounded-lg"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
              />
            )}
            <div>
              <h3 className="font-bold text-lg text-gray-900">{cocktail.name}</h3>
              <p className="text-sm text-gray-600">{cocktail.category}</p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Preference Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              你的喜好程度 <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {preferenceOptions.map((option) => {
                const Icon = option.icon;
                const isSelected = preference === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setPreference(option.value)}
                    className={`
                      p-4 rounded-lg border-2 transition-all
                      ${isSelected
                        ? `${option.bgColor} border-current ${option.color} shadow-md`
                        : 'bg-white border-gray-200 hover:border-gray-300'
                      }
                    `}
                  >
                    <Icon className={`w-8 h-8 mx-auto mb-2 ${isSelected ? option.color : 'text-gray-400'}`} />
                    <p className={`text-sm font-medium ${isSelected ? option.color : 'text-gray-600'}`}>
                      {option.label}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              評論與感想
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              placeholder="寫下你的品飲心得、口感描述、或任何想記錄的想法..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Date & Time */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              飲用時間 <span className="text-red-500">*</span>
            </label>
            <input
              type="datetime-local"
              value={drunkAt}
              onChange={(e) => setDrunkAt(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <MapPin className="w-4 h-4 inline mr-1" />
              地點
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="例：家裡、某某酒吧、朋友家..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Mood Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              心情 / 場合標籤
            </label>
            <div className="flex flex-wrap gap-2">
              {availableMoodTags.map((tag) => {
                const isSelected = selectedMoodTags.includes(tag);
                return (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => toggleMoodTag(tag)}
                    className={`
                      px-4 py-2 rounded-full text-sm font-medium transition-colors
                      ${isSelected
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }
                    `}
                  >
                    {tag}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '儲存中...' : existingRecord ? '更新紀錄' : '建立紀錄'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RecordForm;
