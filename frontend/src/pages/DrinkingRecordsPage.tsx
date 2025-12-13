import { useState, useEffect } from 'react';
import { recordsAPI } from '../services/api';
import { RecordForm } from '../components/Record';
import {
  BookOpen,
  Heart,
  ThumbsUp,
  Meh,
  ThumbsDown,
  MapPin,
  Calendar,
  Filter,
  Edit2,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Wine,
} from 'lucide-react';
import type { DrinkingRecord, PreferenceLevel } from '../types';

const DrinkingRecordsPage = () => {
  const [records, setRecords] = useState<DrinkingRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  // 篩選條件
  const [filterPreference, setFilterPreference] = useState<string>('');
  const [filterStartDate, setFilterStartDate] = useState('');
  const [filterEndDate, setFilterEndDate] = useState('');
  const [filterMoodTags, setFilterMoodTags] = useState<string[]>([]);
  const [availableMoodTags, setAvailableMoodTags] = useState<string[]>([]);

  // 編輯模式
  const [editingRecord, setEditingRecord] = useState<DrinkingRecord | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);

  // 載入心情標籤選項
  useEffect(() => {
    const loadMoodTags = async () => {
      try {
        const response = await recordsAPI.getMoodTags();
        setAvailableMoodTags(response.mood_tags);
      } catch (err) {
        console.error('Failed to load mood tags:', err);
      }
    };
    loadMoodTags();
  }, []);

  // 載入紀錄
  useEffect(() => {
    loadRecords();
  }, [page, filterPreference, filterStartDate, filterEndDate, filterMoodTags]);

  const loadRecords = async () => {
    setLoading(true);
    try {
      const params: any = { page, limit: 12 };

      if (filterPreference) params.preference = filterPreference;
      if (filterStartDate) params.start_date = filterStartDate; // 直接使用日期字串，不轉換
      if (filterEndDate) params.end_date = filterEndDate; // 直接使用日期字串，不轉換
      if (filterMoodTags.length > 0) params.mood_tags = filterMoodTags.join(',');

      const response = await recordsAPI.getAll(params);
      setRecords(response.records);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('載入紀錄失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (recordId: string) => {
    if (!window.confirm('確定要刪除這筆紀錄嗎？此操作無法復原。')) {
      return;
    }

    try {
      await recordsAPI.delete(recordId);
      loadRecords(); // 重新載入列表
    } catch (error) {
      console.error('刪除失敗:', error);
      alert('刪除失敗，請重試');
    }
  };

  const handleEdit = (record: DrinkingRecord) => {
    setEditingRecord(record);
    setShowEditForm(true);
  };

  const getPreferenceIcon = (preference: PreferenceLevel) => {
    const icons = {
      loved: { Icon: Heart, color: 'text-red-500', bg: 'bg-red-50' },
      liked: { Icon: ThumbsUp, color: 'text-green-500', bg: 'bg-green-50' },
      neutral: { Icon: Meh, color: 'text-gray-500', bg: 'bg-gray-50' },
      disliked: { Icon: ThumbsDown, color: 'text-blue-500', bg: 'bg-blue-50' },
    };
    return icons[preference];
  };

  const formatDate = (dateString: string) => {
    // 移除時區資訊（Z 或 +08:00），將字串視為本地時間
    const cleanDateStr = dateString.replace('Z', '').replace('+08:00', '');
    const date = new Date(cleanDateStr);
    return new Intl.DateTimeFormat('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const toggleMoodTagFilter = (tag: string) => {
    setFilterMoodTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
    setPage(1); // 重置到第一頁
  };

  const resetFilters = () => {
    setFilterPreference('');
    setFilterStartDate('');
    setFilterEndDate('');
    setFilterMoodTags([]);
    setPage(1);
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-primary-600" />
          我的飲用紀錄
        </h1>
        <p className="text-gray-600">追蹤你的調酒品飲歷程與心得</p>
      </div>

      {/* 篩選器 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">篩選條件</h2>
          <div className="flex gap-2">
            {(filterPreference || filterStartDate || filterEndDate || filterMoodTags.length > 0) && (
              <button
                onClick={resetFilters}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                清除篩選
              </button>
            )}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-secondary px-4 flex items-center gap-2"
            >
              <Filter className="w-4 h-4" />
              {showFilters ? '隱藏' : '顯示'}
            </button>
          </div>
        </div>

        {showFilters && (
          <div className="space-y-4">
            {/* 偏好程度篩選 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">偏好程度</label>
              <div className="flex flex-wrap gap-2">
                {['', 'loved', 'liked', 'neutral', 'disliked'].map((pref) => (
                  <button
                    key={pref}
                    onClick={() => {
                      setFilterPreference(pref);
                      setPage(1);
                    }}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      filterPreference === pref
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {pref === '' ? '全部' : pref === 'loved' ? '超愛' : pref === 'liked' ? '喜歡' : pref === 'neutral' ? '普通' : '不愛'}
                  </button>
                ))}
              </div>
            </div>

            {/* 日期範圍篩選 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">開始日期</label>
                <input
                  type="date"
                  value={filterStartDate}
                  onChange={(e) => {
                    setFilterStartDate(e.target.value);
                    setPage(1);
                  }}
                  className="w-full input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">結束日期</label>
                <input
                  type="date"
                  value={filterEndDate}
                  onChange={(e) => {
                    setFilterEndDate(e.target.value);
                    setPage(1);
                  }}
                  className="w-full input-field"
                />
              </div>
            </div>

            {/* 心情標籤篩選 */}
            {availableMoodTags.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">心情 / 場合</label>
                <div className="flex flex-wrap gap-2">
                  {availableMoodTags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => toggleMoodTagFilter(tag)}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                        filterMoodTags.includes(tag)
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 載入中 */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-xl text-gray-600">載入中...</div>
        </div>
      )}

      {/* 紀錄列表 */}
      {!loading && records.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">還沒有任何飲用紀錄</p>
          <p className="text-gray-400 text-sm mt-2">去調酒瀏覽頁面記錄你的第一杯吧！</p>
        </div>
      )}

      {!loading && records.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {records.map((record) => {
              const preferenceConfig = getPreferenceIcon(record.preference);
              const PreferenceIcon = preferenceConfig.Icon;

              return (
                <div key={record._id} className="card p-4 hover:shadow-lg transition-shadow">
                  {/* Cocktail Info */}
                  <div className="flex items-start gap-3 mb-4">
                    {record.cocktail_snapshot.image_url && (
                      <img
                        src={record.cocktail_snapshot.image_url}
                        alt={record.cocktail_snapshot.name}
                        className="w-16 h-16 object-cover rounded-lg flex-shrink-0"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-gray-900 line-clamp-2">
                        {record.cocktail_snapshot.name}
                      </h3>
                      <p className="text-sm text-gray-600">{record.cocktail_snapshot.category}</p>
                    </div>
                  </div>

                  {/* Preference Badge */}
                  <div className={`flex items-center gap-2 px-3 py-2 ${preferenceConfig.bg} rounded-lg mb-3`}>
                    <PreferenceIcon className={`w-5 h-5 ${preferenceConfig.color}`} />
                    <span className={`text-sm font-medium ${preferenceConfig.color}`}>
                      {record.preference === 'loved' ? '超愛' : record.preference === 'liked' ? '喜歡' : record.preference === 'neutral' ? '普通' : '不愛'}
                    </span>
                  </div>

                  {/* Notes */}
                  {record.notes && (
                    <p className="text-sm text-gray-700 mb-3 line-clamp-3">{record.notes}</p>
                  )}

                  {/* Meta Info */}
                  <div className="space-y-2 text-sm text-gray-600 mb-4">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDate(record.drunk_at)}</span>
                    </div>
                    {record.location && (
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4" />
                        <span>{record.location}</span>
                      </div>
                    )}
                  </div>

                  {/* Mood Tags */}
                  {record.mood_tags && record.mood_tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {record.mood_tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2 pt-3 border-t border-gray-200">
                    <button
                      onClick={() => handleEdit(record)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                      編輯
                    </button>
                    <button
                      onClick={() => handleDelete(record._id)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      刪除
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* 分頁 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-gray-700">
                第 {page} 頁 / 共 {totalPages} 頁
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="btn-secondary disabled:opacity-50"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </>
      )}

      {/* 編輯表單 */}
      {showEditForm && editingRecord && (
        <RecordForm
          cocktail={{
            _id: editingRecord.cocktail_id,
            name: editingRecord.cocktail_snapshot.name,
            category: editingRecord.cocktail_snapshot.category,
            image_url: editingRecord.cocktail_snapshot.image_url,
            ingredients: [],
            method: [],
            garnish: [],
          }}
          existingRecord={editingRecord}
          onClose={() => {
            setShowEditForm(false);
            setEditingRecord(null);
          }}
          onSuccess={() => {
            loadRecords();
          }}
        />
      )}
    </div>
  );
};

export default DrinkingRecordsPage;
