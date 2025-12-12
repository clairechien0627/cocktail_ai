import { useState, useEffect } from 'react';
import { recordsAPI } from '../services/api';
import {
  TrendingUp,
  Heart,
  Wine,
  Clock,
  Smile,
  BarChart3,
  Target,
  Flame,
  Droplet,
} from 'lucide-react';
import type { DrinkingStats, UserPreferencesAnalysis } from '../types';
import { MapPin } from "lucide-react";

const PreferenceAnalysisPage = () => {
  const [stats, setStats] = useState<DrinkingStats | null>(null);
  const [preferences, setPreferences] = useState<UserPreferencesAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsData, preferencesData] = await Promise.all([
        recordsAPI.getStats(),
        recordsAPI.getPreferences(),
      ]);
      setStats(statsData);
      setPreferences(preferencesData);
    } catch (error) {
      console.error('載入分析資料失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPreferenceColor = (preference: string) => {
    const colors = {
      loved: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' },
      liked: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
      neutral: { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300' },
      disliked: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
    };
    return colors[preference as keyof typeof colors] || colors.neutral;
  };

  const getPreferenceBarColor = (preference: string) => {
    const colors = {
      loved: 'bg-red-500',
      liked: 'bg-green-500',
      neutral: 'bg-gray-500',
      disliked: 'bg-blue-500',
    };
    return colors[preference as keyof typeof colors] || 'bg-gray-500';
  };

  const getTimeLabel = (period: string) => {
    const labels: { [key: string]: string } = {
      'late_night': '深夜 (00:00-05:59)',
      'morning': '早上 (06:00-11:59)',
      'afternoon': '下午 (12:00-17:59)',
      'evening': '晚上 (18:00-23:59)',
    };
    return labels[period] || period;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-xl text-gray-600">載入中...</div>
      </div>
    );
  }

  if (!stats || !preferences) {
    return (
      <div className="text-center py-12">
        <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500 text-lg">無法載入分析資料</p>
        <p className="text-gray-400 text-sm mt-2">請稍後再試</p>
      </div>
    );
  }

  if (stats.total_drinks === 0) {
    return (
      <div className="text-center py-12">
        <Wine className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500 text-lg">還沒有足夠的飲用紀錄</p>
        <p className="text-gray-400 text-sm mt-2">至少需要一筆飲用紀錄才能進行偏好分析</p>
      </div>
    );
  }

  const totalPreferences = stats.preference_distribution.loved +
                          stats.preference_distribution.liked +
                          stats.preference_distribution.neutral +
                          stats.preference_distribution.disliked;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <TrendingUp className="w-8 h-8 text-primary-600" />
          我的口味偏好分析
        </h1>
        <p className="text-gray-600">基於 {stats.total_drinks} 筆飲用紀錄的智能分析</p>
      </div>

      <div className="space-y-6">
        {/* 統計概覽 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">總飲用杯數</h3>
              <Wine className="w-8 h-8 text-primary-600" />
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.total_drinks}</p>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">超愛的調酒</h3>
              <Heart className="w-8 h-8 text-red-500" />
            </div>
            <p className="text-3xl font-bold text-red-500">{stats.preference_distribution.loved}</p>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">喜歡的調酒</h3>
              <Target className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-green-500">{stats.preference_distribution.liked}</p>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">喜愛度</h3>
              <BarChart3 className="w-8 h-8 text-primary-600" />
            </div>
            <p className="text-3xl font-bold text-primary-600">
              {totalPreferences > 0
                ? Math.round(((stats.preference_distribution.loved + stats.preference_distribution.liked) / totalPreferences) * 100)
                : 0}%
            </p>
          </div>
        </div>

        {/* 偏好分佈 */}
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">偏好分佈</h2>
          <div className="space-y-3">
            {Object.entries(stats.preference_distribution).map(([key, value]) => {
              const color = getPreferenceColor(key);
              const percentage = totalPreferences > 0 ? (value / totalPreferences) * 100 : 0;
              const label = key === 'loved' ? '超愛' : key === 'liked' ? '喜歡' : key === 'neutral' ? '普通' : '不愛';

              return (
                <div key={key}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">{label}</span>
                    <span className={`text-sm font-semibold ${color.text}`}>
                      {value} 杯 ({percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getPreferenceBarColor(key)} transition-all duration-500`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        {/* 飲用地點分析 */}
        {preferences.location_distribution && preferences.location_distribution.length > 0 && (
            <div className="card p-6">
            <div className="flex items-center gap-2 mb-4">
              <MapPin className="w-6 h-6 text-primary-600" />
              <h2 className="text-xl font-bold text-gray-900">飲用地點分析</h2>
            </div>

           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {preferences.location_distribution.map((loc) => (
                <div
                  key={loc._id}
                  className="p-4 bg-gray-50 rounded-lg flex items-center justify-between"
                >
            <div>
              <p className="text-sm text-gray-600">{loc._id || '未填寫地點'}</p>
              <p className="text-2xl font-bold text-primary-600">{loc.count}</p>
            </div>
          <p className="text-xs text-gray-500">次</p>
        </div>
      ))}
    </div>
  </div>
)}


        {/* 最愛的 Tags */}
        {(preferences.favorite_tags.base_spirits.length > 0 ||
          preferences.favorite_tags.flavors.length > 0 ||
          preferences.favorite_tags.styles.length > 0) && (
          <div className="card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">我最愛的風格</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* 基酒偏好 */}
              {preferences.favorite_tags.base_spirits.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">喜愛的基酒</h3>
                  <div className="space-y-2">
                    {preferences.favorite_tags.base_spirits.map((item) => (
                      <div key={item.tag} className="flex items-center justify-between p-2 bg-amber-50 rounded-lg">
                        <span className="text-sm text-gray-700 capitalize">{item.tag.replace(/-/g, ' ')}</span>
                        <span className="text-xs font-semibold text-amber-700">{item.count}x</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 風味偏好 */}
              {preferences.favorite_tags.flavors.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">喜愛的風味</h3>
                  <div className="space-y-2">
                    {preferences.favorite_tags.flavors.map((item) => (
                      <div key={item.tag} className="flex items-center justify-between p-2 bg-green-50 rounded-lg">
                        <span className="text-sm text-gray-700 capitalize">{item.tag.replace(/-/g, ' ')}</span>
                        <span className="text-xs font-semibold text-green-700">{item.count}x</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 風格偏好 */}
              {preferences.favorite_tags.styles.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">喜愛的風格</h3>
                  <div className="space-y-2">
                    {preferences.favorite_tags.styles.map((item) => (
                      <div key={item.tag} className="flex items-center justify-between p-2 bg-purple-50 rounded-lg">
                        <span className="text-sm text-gray-700 capitalize">{item.tag.replace(/-/g, ' ')}</span>
                        <span className="text-xs font-semibold text-purple-700">{item.count}x</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 口味偏好範圍 */}
        <div className="card p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">口味偏好範圍</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 酒精強度 */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Flame className="w-5 h-5 text-orange-500" />
                <h3 className="text-sm font-semibold text-gray-700">酒精強度偏好</h3>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">平均偏好</span>
                  <span className="font-semibold text-orange-600">
                    {preferences.taste_range.strength.avg?.toFixed(1) || 'N/A'} / 10
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">偏好範圍</span>
                  <span className="font-semibold text-gray-700">
                    {preferences.taste_range.strength.min?.toFixed(1) || 0} - {preferences.taste_range.strength.max?.toFixed(1) || 10}
                  </span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden mt-3">
                  <div
                    className="h-full bg-gradient-to-r from-orange-400 to-orange-600"
                    style={{ width: `${((preferences.taste_range.strength.avg || 5) / 10) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* 甜度 */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Droplet className="w-5 h-5 text-blue-500" />
                <h3 className="text-sm font-semibold text-gray-700">甜度偏好</h3>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">平均偏好</span>
                  <span className="font-semibold text-blue-600">
                    {preferences.taste_range.sweetness.avg?.toFixed(1) || 'N/A'} / 10
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">偏好範圍</span>
                  <span className="font-semibold text-gray-700">
                    {preferences.taste_range.sweetness.min?.toFixed(1) || 0} - {preferences.taste_range.sweetness.max?.toFixed(1) || 10}
                  </span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden mt-3">
                  <div
                    className="h-full bg-gradient-to-r from-blue-400 to-blue-600"
                    style={{ width: `${((preferences.taste_range.sweetness.avg || 5) / 10) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 飲用時段分析 */}
        {preferences.time_distribution && preferences.time_distribution.length > 0 && (
          <div className="card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Clock className="w-6 h-6 text-primary-600" />
              <h2 className="text-xl font-bold text-gray-900">飲用時段分析</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {preferences.time_distribution.slice(0, 8).map((item) => (
                <div key={item._id} className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">{getTimeLabel(item._id)}</p>
                  <p className="text-2xl font-bold text-primary-600">{item.count}</p>
                  <p className="text-xs text-gray-500">次</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 心情/場合分析 */}
        {preferences.mood_distribution && preferences.mood_distribution.length > 0 && (
          <div className="card p-6">
            <div className="flex items-center gap-2 mb-4">
              <Smile className="w-6 h-6 text-primary-600" />
              <h2 className="text-xl font-bold text-gray-900">飲用場合分析</h2>
            </div>
            <div className="flex flex-wrap gap-3">
              {preferences.mood_distribution.map((item) => (
                <div
                  key={item._id}
                  className="px-4 py-2 bg-primary-50 text-primary-700 rounded-full font-medium"
                >
                  {item._id} <span className="text-primary-900 font-bold">×{item.count}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 最常喝的調酒 */}
        {stats.most_drunk_cocktails && stats.most_drunk_cocktails.length > 0 && (
          <div className="card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">最常喝的調酒 Top 5</h2>
            <div className="space-y-3">
              {stats.most_drunk_cocktails.map((cocktail, index) => (
                <div key={cocktail._id} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-center w-8 h-8 bg-primary-600 text-white rounded-full font-bold text-sm">
                    {index + 1}
                  </div>
                  {cocktail.cocktail_image && (
                    <img
                      src={cocktail.cocktail_image}
                      alt={cocktail.cocktail_name}
                      className="w-12 h-12 object-cover rounded-lg"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  )}
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">{cocktail.cocktail_name}</p>
                    <p className="text-sm text-gray-600">喝了 {cocktail.count} 次</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PreferenceAnalysisPage;
