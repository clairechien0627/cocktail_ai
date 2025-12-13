import { useState, useEffect, useRef, useCallback } from 'react';
import { recordsAPI } from '../services/api';
import { RecordForm } from '../components/Record';
import {
  Sparkles,
  Wine,
  Star,
  Flame,
  Droplet,
  RefreshCw,
  Edit3,
  X,
  CheckCircle,
  Leaf,
  ChefHat,
  GlassWater,
  BookOpen,
  MessageSquare,
  Link as LinkIcon,
  AlertCircle,
  ImageOff,
  Loader2,
  Compass,
  Target,
} from 'lucide-react';
import type { Cocktail } from '../types';
import { TagBadge } from '../utils/tagIcons';
import { CategoryBadge } from '../utils/categoryIcons';

// Session Storage 鍵名
const SESSION_STORAGE_KEY = 'cocktail_recommendations_state';

interface RecommendationState {
  recommendations: Cocktail[];
  allRecommendedIds: string[];
  explorationMode: 'balanced' | 'adventurous';
  hasMore: boolean;
}

const RecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState<Cocktail[]>([]);
  const [allRecommendedIds, setAllRecommendedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedCocktail, setSelectedCocktail] = useState<Cocktail | null>(null);
  const [showRecordForm, setShowRecordForm] = useState(false);
  const [hasDrunk, setHasDrunk] = useState<boolean>(false);
  const [explorationMode, setExplorationMode] = useState<'balanced' | 'adventurous'>('balanced');
  const [hasMore, setHasMore] = useState(true);
  const [langZh, setLangZh] = useState(false); // false=英文, true=中文

  // 圖片懶加載相關
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    // 嘗試從 Session Storage 載入狀態
    const savedState = loadStateFromSession();
    if (savedState && savedState.recommendations.length > 0) {
      setRecommendations(savedState.recommendations);
      setAllRecommendedIds(savedState.allRecommendedIds);
      setExplorationMode(savedState.explorationMode);
      setHasMore(savedState.hasMore);
      setLoading(false);
    } else {
      loadRecommendations(true);
    }
  }, []);

  useEffect(() => {
    // 儲存狀態到 Session Storage
    saveStateToSession({
      recommendations,
      allRecommendedIds,
      explorationMode,
      hasMore,
    });
  }, [recommendations, allRecommendedIds, explorationMode, hasMore]);

  useEffect(() => {
    const checkIfDrunk = async () => {
      if (selectedCocktail) {
        try {
          const response = await recordsAPI.checkIfDrunk(selectedCocktail._id);
          setHasDrunk(response.has_drunk);
        } catch (error) {
          console.error('檢查飲用狀態失敗:', error);
          setHasDrunk(false);
        }
      }
    };
    checkIfDrunk();
  }, [selectedCocktail]);

  // 設置圖片懶加載 Intersection Observer
  useEffect(() => {
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target as HTMLImageElement;
            const src = img.dataset.src;
            if (src) {
              img.src = src;
              img.removeAttribute('data-src');
              observerRef.current?.unobserve(img);
            }
          }
        });
      },
      {
        rootMargin: '50px', // 提前 50px 開始載入
      }
    );

    return () => {
      observerRef.current?.disconnect();
    };
  }, []);

  // Session Storage 操作
  const saveStateToSession = (state: RecommendationState) => {
    try {
      sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(state));
    } catch (error) {
      console.error('儲存狀態失敗:', error);
    }
  };

  const loadStateFromSession = (): RecommendationState | null => {
    try {
      const saved = sessionStorage.getItem(SESSION_STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      console.error('載入狀態失敗:', error);
      return null;
    }
  };

  const clearSessionState = () => {
    try {
      sessionStorage.removeItem(SESSION_STORAGE_KEY);
    } catch (error) {
      console.error('清除狀態失敗:', error);
    }
  };

  const loadRecommendations = async (isRefresh: boolean = false) => {
    if (isRefresh) {
      setLoading(true);
      setAllRecommendedIds([]);
      setRecommendations([]);
      clearSessionState();
    } else {
      setLoadingMore(true);
    }

    try {
      const excludeIds = isRefresh ? undefined : allRecommendedIds;
      const response = await recordsAPI.getRecommendations(20, excludeIds, explorationMode);

      const newRecommendations = response.recommendations;
      const newIds = newRecommendations.map((c) => c._id);

      if (isRefresh) {
        setRecommendations(newRecommendations);
        setAllRecommendedIds(newIds);
      } else {
        setRecommendations((prev) => [...prev, ...newRecommendations]);
        setAllRecommendedIds((prev) => [...prev, ...newIds]);
      }

      // 如果返回的數量少於請求的數量，表示沒有更多了
      setHasMore(newRecommendations.length === 20);
    } catch (error) {
      console.error('載入推薦失敗:', error);
      if (!isRefresh) {
        setHasMore(false);
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const handleExplorationModeChange = (mode: 'balanced' | 'adventurous') => {
    setExplorationMode(mode);
    // 切換模式後重新載入推薦
    loadRecommendations(true);
  };

  const handleRefresh = () => {
    loadRecommendations(true);
  };

  const handleLoadMore = () => {
    if (!loadingMore && hasMore) {
      loadRecommendations(false);
    }
  };

  // 註冊圖片到 Intersection Observer
  const registerImage = useCallback((img: HTMLImageElement | null) => {
    if (img && observerRef.current) {
      observerRef.current.observe(img);
    }
  }, []);

  const renderStars = (rating?: number) => {
    if (!rating) return null;
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  const getRecommendationType = (type?: string) => {
    const types = {
      safe: { label: '安全選擇', className: 'bg-green-100 text-green-700 border-green-300' },
      adventure: { label: '冒險探索', className: 'bg-purple-100 text-purple-700 border-purple-300' },
      hidden_gem: { label: '隱藏寶石', className: 'bg-amber-100 text-amber-700 border-amber-300' },
      popular: { label: '熱門推薦', className: 'bg-red-100 text-red-700 border-red-300' },
      newbie: { label: '新手推薦', className: 'bg-blue-100 text-blue-700 border-blue-300' },
      general: { label: '推薦', className: 'bg-gray-100 text-gray-700 border-gray-300' },
    };
    return types[type as keyof typeof types] || types.general;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <div className="text-xl text-gray-600">正在分析你的偏好...</div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-primary-600" />
              為你推薦
            </h1>
            <p className="text-gray-600">基於你的飲用歷史與口味偏好精心挑選</p>
          </div>
          <button
            onClick={handleRefresh}
            className="btn-secondary flex items-center gap-2"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            重新推薦
          </button>
        </div>

        {/* 探索模式切換 */}
        <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
          <span className="text-sm font-medium text-gray-700">探索模式：</span>
          <div className="flex gap-2">
            <button
              onClick={() => handleExplorationModeChange('balanced')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                explorationMode === 'balanced'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Target className="w-4 h-4" />
              平衡模式
            </button>
            <button
              onClick={() => handleExplorationModeChange('adventurous')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                explorationMode === 'adventurous'
                  ? 'bg-purple-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Compass className="w-4 h-4" />
              冒險模式
            </button>
          </div>
        </div>

        {/* 統計資訊 */}
        <div className="mt-4 text-sm text-gray-500">
          已顯示 {recommendations.length} 款推薦
        </div>
      </div>

      {recommendations.length === 0 && (
        <div className="text-center py-12">
          <Wine className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">目前沒有推薦</p>
          <p className="text-gray-400 text-sm mt-2">
            請先記錄一些飲用體驗，系統將根據你的偏好為你推薦調酒
          </p>
        </div>
      )}

      {recommendations.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {recommendations.map((cocktail) => (
              <CocktailCard
                key={cocktail._id}
                cocktail={cocktail}
                onClick={() => setSelectedCocktail(cocktail)}
                registerImage={registerImage}
                renderStars={renderStars}
                getRecommendationType={getRecommendationType}
              />
            ))}
          </div>

          {/* 載入更多按鈕 */}
          <div className="mt-8 flex justify-center">
            {hasMore ? (
              <button
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loadingMore ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    載入中...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    載入更多推薦
                  </>
                )}
              </button>
            ) : (
              <div className="text-gray-500 text-sm">
                已經顯示所有推薦，試試切換探索模式或重新推薦！
              </div>
            )}
          </div>
        </>
      )}

      {/* 調酒詳情模態框 */}
      {selectedCocktail && !showRecordForm && (
        <CocktailDetailModal
          cocktail={selectedCocktail}
          hasDrunk={hasDrunk}
          onClose={() => setSelectedCocktail(null)}
          onRecord={() => setShowRecordForm(true)}
          renderStars={renderStars}
          langZh={langZh}
          setLangZh={setLangZh}
        />
      )}

      {/* 飲用紀錄表單 */}
      {showRecordForm && selectedCocktail && (
        <RecordForm
          cocktail={selectedCocktail}
          onClose={() => {
            setShowRecordForm(false);
            setSelectedCocktail(null);
          }}
          onSuccess={() => {
            setShowRecordForm(false);
            // Update drunk status
            if (selectedCocktail) {
              recordsAPI.checkIfDrunk(selectedCocktail._id)
                .then(response => setHasDrunk(response.has_drunk))
                .catch(() => setHasDrunk(false));
            }
            // 重新載入推薦（因為已經喝過了）
            handleRefresh();
          }}
        />
      )}
    </div>
  );
};

// 調酒卡片元件（支援圖片懶加載）
const CocktailCard = ({
  cocktail,
  onClick,
  registerImage,
  renderStars,
  getRecommendationType,
}: {
  cocktail: Cocktail;
  onClick: () => void;
  registerImage: (img: HTMLImageElement | null) => void;
  renderStars: (rating?: number) => React.ReactNode;
  getRecommendationType: (type?: string) => { label: string; className: string };
}) => {
  return (
    <div
      onClick={onClick}
      className="relative overflow-hidden rounded-lg cursor-pointer hover:scale-105 transition-transform duration-300 group"
      style={{
        aspectRatio: '3/4',
      }}
    >
      {/* 懶加載圖片背景 */}
      {cocktail.image_url ? (
        <>
          {/* 圖片載入中的靜態背景 */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary-400 to-primary-600" />
          <img
            ref={registerImage}
            data-src={cocktail.image_url}
            alt={cocktail.name}
            className="absolute inset-0 w-full h-full object-cover"
            style={{ backgroundColor: '#667eea' }}
          />
        </>
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
          <ImageOff className="w-16 h-16 text-white/50" />
        </div>
      )}

      {/* 漸層遮罩 */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />

      {/* 頂部浮層 */}
      <div className="absolute top-3 right-3 flex items-center gap-2">
        {cocktail.recommendation_type && (
          <span
            className={`text-xs px-2 py-1 rounded-full backdrop-blur-sm ${
              getRecommendationType(cocktail.recommendation_type).className
            } bg-opacity-90 drop-shadow-lg`}
          >
            {getRecommendationType(cocktail.recommendation_type).label}
          </span>
        )}
      </div>

      {/* 底部資訊浮層 */}
      <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
        <h3 className="font-bold text-xl mb-3 line-clamp-2 drop-shadow-lg">
          {cocktail.name}
        </h3>

        {/* 分類標籤 */}
        {cocktail.tags_categorized && (
          <div className="flex flex-wrap gap-1 mb-2.5">
            {cocktail.tags_categorized.base_spirits?.slice(0, 2).map((tag, index) => (
              <div key={index} className="bg-white/20 backdrop-blur-sm rounded-full px-2">
                <span className="text-[10px] text-white/90 capitalize">{tag.replace(/-/g, ' ')}</span>
              </div>
            ))}
            {cocktail.tags_categorized.flavors?.slice(0, 2).map((tag, index) => (
              <div key={index} className="bg-white/20 backdrop-blur-sm rounded-full px-2">
                <span className="text-[10px] text-white/90 capitalize">{tag.replace(/-/g, ' ')}</span>
              </div>
            ))}
          </div>
        )}

        {/* 專業評分 */}
        {cocktail.ratings?.professional != null && (
          <div className="flex items-center gap-2 mb-2">
            <div className="flex items-center">
              {renderStars(cocktail.ratings.professional)}
            </div>
            <span className="text-sm font-semibold drop-shadow">
              {cocktail.ratings.professional.toFixed(1)}
            </span>
          </div>
        )}

        {/* 風味檔案 */}
        {cocktail.taste_profile && (
          <div className="space-y-1.5 mb-3">
            {cocktail.taste_profile.strength !== undefined && (
              <div className="flex items-center gap-2">
                <Flame className="w-3.5 h-3.5 text-orange-400 drop-shadow" />
                <div className="flex-1 h-1.5 bg-white/20 backdrop-blur-sm rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-orange-400 to-orange-600"
                    style={{
                      width: `${(cocktail.taste_profile.strength / 10) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-xs drop-shadow">
                  {cocktail.taste_profile.strength}/10
                </span>
              </div>
            )}
            {cocktail.taste_profile.sweetness !== undefined && (
              <div className="flex items-center gap-2">
                <Droplet className="w-3.5 h-3.5 text-blue-400 drop-shadow" />
                <div className="flex-1 h-1.5 bg-white/20 backdrop-blur-sm rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-400 to-blue-600"
                    style={{
                      width: `${(cocktail.taste_profile.sweetness / 10) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-xs drop-shadow">
                  {cocktail.taste_profile.sweetness}/10
                </span>
              </div>
            )}
          </div>
        )}

        {/* 材料列表 */}
        <div
          className="bg-black/30 backdrop-blur-sm rounded-lg p-3 max-h-32 overflow-y-auto"
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: 'rgba(255, 255, 255, 0.2) transparent'
          }}
        >
          <div className="flex items-center gap-1.5 mb-2">
            <GlassWater className="w-4 h-4 text-white/80" />
            <span className="text-xs font-semibold text-white/80">材料</span>
          </div>
          <ul className="space-y-1 text-xs">
            {cocktail.ingredients.map((ingredient, index) => (
              <li key={index} className="flex items-start gap-1.5 text-white/90">
                <span className="text-white/60 mt-0.4">•</span>
                <span className="line-clamp-1">{ingredient}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

// 調酒詳情模態框元件（完整版，參考 CocktailsPage）
const CocktailDetailModal = ({
  cocktail,
  hasDrunk,
  onClose,
  onRecord,
  renderStars,
  langZh,
  setLangZh,
}: {
  cocktail: Cocktail;
  hasDrunk: boolean;
  onClose: () => void;
  onRecord: () => void;
  renderStars: (rating?: number) => React.ReactNode;
  langZh: boolean;
  setLangZh: React.Dispatch<React.SetStateAction<boolean>>;
}) => {
  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header with Language Toggle and Record Button */}
        <div className="sticky top-0 bg-primary-600 text-white px-6 py-4 flex items-center justify-between z-10">
          <div className="flex items-center gap-3 flex-1">
            <h2 className="text-2xl font-bold">
              {langZh
                ? cocktail.name_zh
                  ? `${cocktail.name_zh} (${cocktail.name})`
                  : cocktail.name
                : cocktail.name}
            </h2>
            {hasDrunk && (
              <span className="flex items-center gap-1.5 px-3 py-1 bg-white bg-opacity-20 rounded-full text-sm">
                <CheckCircle className="w-4 h-4" />
                已喝過
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                console.log('Language toggle clicked, current langZh:', langZh);
                console.log('setLangZh function:', setLangZh);
                setLangZh((v) => {
                  console.log('Inside setLangZh updater, prev value:', v, 'new value:', !v);
                  return !v;
                });
              }}
              className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-white bg-opacity-20 hover:bg-opacity-30 transition-colors"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-white" />
              {langZh ? '英' : '中'}
            </button>
            <button
              onClick={onRecord}
              className="flex items-center gap-2 px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-gray-100 transition-colors"
            >
              <Edit3 className="w-4 h-4" />
              記錄飲用
            </button>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* 調酒大圖 */}
        {cocktail.image_url && (
          <div className="relative w-full h-96 bg-white overflow-hidden">
            <img
              src={cocktail.image_url}
              alt={cocktail.name}
              className="w-full h-full object-contain"
              onError={(e) => {
                // 圖片載入失敗時顯示佔位符
                e.currentTarget.style.display = 'none';
                const parent = e.currentTarget.parentElement;
                if (parent && !parent.querySelector('.fallback-large')) {
                  parent.className = 'relative w-full h-96 bg-gradient-to-br from-primary-200 to-primary-300 overflow-hidden flex items-center justify-center';
                  const fallback = document.createElement('div');
                  fallback.className = 'fallback-large text-center';
                  fallback.innerHTML = `<svg class="w-32 h-32 text-primary-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg><p class="text-primary-700 text-lg font-medium">${cocktail.name}</p>`;
                  parent.appendChild(fallback);
                }
              }}
            />
          </div>
        )}

        <div className="p-6 space-y-6">
          {/* 推薦理由與相似度（推薦專屬） */}
          {cocktail.recommendation_reason && (
            <div className="bg-primary-50 border-l-4 border-primary-400 rounded p-4">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5 text-primary-600" />
                <span className="font-semibold text-primary-900">推薦理由</span>
              </div>
              <p className="text-sm text-primary-800 mb-2">
                {cocktail.recommendation_reason}
              </p>
              {cocktail.similarity_score !== undefined && cocktail.similarity_score > 0 && (
                <div className="flex items-center gap-2 mt-2 pt-2 border-t border-primary-200">
                  <Star className="w-4 h-4 text-primary-600" />
                  <span className="text-xs text-primary-700 font-medium">
                    相似度評分: {cocktail.similarity_score.toFixed(1)} 分
                  </span>
                </div>
              )}
            </div>
          )}

          {/* COTD 徵章 */}
          {cocktail.cotd?.text && (
            <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-400 rounded-lg p-4 shadow-md">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-5 h-5 text-yellow-600 fill-yellow-400" />
                <h4 className="font-bold text-yellow-900">
                  {cocktail.cotd.title || 'Cocktail of the Day'}
                </h4>
                <Sparkles className="w-5 h-5 text-yellow-600 fill-yellow-400" />
              </div>
              <p className="text-yellow-800 text-sm">{cocktail.cotd.text}</p>
            </div>
          )}

          {/* 1. 評分與基本資訊 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              {cocktail.ratings && (
                <div className="space-y-2">
                  {cocktail.ratings.professional != null && (
                    <div>
                      <p className="text-sm text-gray-600 mb-1">專業評分</p>
                      <div className="flex items-center gap-2">
                        {renderStars(cocktail.ratings.professional)}
                        <span className="font-bold text-lg text-gray-900">
                          {cocktail.ratings.professional.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  )}
                  {cocktail.ratings.public != null && (
                    <div>
                      <p className="text-sm text-gray-600 mb-1">公眾評分</p>
                      <div className="flex items-center gap-2">
                        {renderStars(cocktail.ratings.public)}
                        <span className="font-bold text-lg text-gray-900">
                          {cocktail.ratings.public.toFixed(1)}
                        </span>
                        {cocktail.ratings.public_count && (
                          <span className="text-sm text-gray-500">
                            ({cocktail.ratings.public_count} 則評價)
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
            <div className="flex flex-wrap gap-2 items-start justify-end">
              <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                {langZh && cocktail.category_zh
                  ? cocktail.category_zh
                  : cocktail.category}
              </span>
              {cocktail.difficulty && (
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    cocktail.difficulty === 'easy'
                      ? 'bg-green-100 text-green-700'
                      : cocktail.difficulty === 'medium'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'bg-red-100 text-red-700'
                  }`}
                >
                  {cocktail.difficulty === 'easy'
                    ? '簡單'
                    : cocktail.difficulty === 'medium'
                    ? '中等'
                    : '困難'}
                </span>
              )}
            </div>
          </div>

          {/* 2. 風味檔案 */}
          {cocktail.taste_profile && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-primary-600" />
                風味檔案
              </h3>
              <div className="space-y-4">
                {cocktail.taste_profile.strength !== undefined && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Flame className="w-5 h-5 text-orange-500" />
                        <span className="font-medium">酒精強度</span>
                      </div>
                      <span className="text-lg font-bold text-orange-600">
                        {cocktail.taste_profile.strength}/10
                      </span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-orange-400 to-orange-600"
                        style={{
                          width: `${(cocktail.taste_profile.strength / 10) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
                {cocktail.taste_profile.sweetness !== undefined && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Droplet className="w-5 h-5 text-blue-500" />
                        <span className="font-medium">甜度</span>
                      </div>
                      <span className="text-lg font-bold text-blue-600">
                        {cocktail.taste_profile.sweetness}/10
                      </span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-400 to-blue-600"
                        style={{
                          width: `${(cocktail.taste_profile.sweetness / 10) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 3. 材料 */}
          <div>
            <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
              <Leaf className="w-5 h-5 text-green-600" />
              材料
            </h3>
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <ul className="space-y-2">
                {cocktail.ingredients_detail &&
                cocktail.ingredients_detail.length > 0 ? (
                  cocktail.ingredients_detail.map((detail, i) => {
                    const zhName = langZh && cocktail.ingredients_zh?.[i]
                      ? cocktail.ingredients_zh[i]
                      : null;
                    return (
                      <li key={i} className="flex items-start gap-3">
                        <span className="font-semibold text-primary-600 min-w-[80px]">
                          {detail.amount}
                        </span>
                        <span className="text-gray-900">
                          {zhName ? (
                            <>
                              {zhName}
                              <span className="text-gray-500 text-sm ml-2">({detail.ingredient})</span>
                            </>
                          ) : (
                            detail.ingredient
                          )}
                        </span>
                      </li>
                    );
                  })
                ) : cocktail.ingredients && cocktail.ingredients.length > 0 ? (
                  cocktail.ingredients.map((ing, i) => (
                    <li key={i} className="text-gray-900">
                      {ing}
                    </li>
                  ))
                ) : (
                  <li className="text-gray-500 italic">無材料資訊</li>
                )}
              </ul>
            </div>
          </div>

          {/* 4. 製作方法 */}
          {cocktail.method_sections && (
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <ChefHat className="w-5 h-5 text-purple-600" />
                製作方法
              </h3>
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                {(() => {
                  // 根據語言選擇使用哪個數據源
                  const methodSections = langZh && cocktail.method_sections_zh?.length
                    ? cocktail.method_sections_zh
                    : cocktail.method_sections;

                  if (!methodSections || methodSections.length === 0) {
                    return <p className="text-gray-500 italic">無製作步驟資訊</p>;
                  }

                  return (
                    <div className="space-y-4">
                      {methodSections.map((section: any, i: number) => {
                        // 根據語言獲取標題和步驟
                        const title = langZh
                          ? (section.title_zh || section.title)
                          : section.title;
                        const steps = langZh
                          ? (section.steps_zh || section.steps || [])
                          : (section.steps || []);

                        if (steps.length === 0) return null;

                        return (
                          <div key={i}>
                            <h4 className="font-semibold text-primary-600 mb-2">
                              {title}
                            </h4>
                            <ol className="list-decimal list-inside space-y-1">
                              {steps.map((step: string, j: number) => (
                                <li key={j} className="text-gray-700">
                                  {step}
                                </li>
                              ))}
                            </ol>
                          </div>
                        );
                      })}
                    </div>
                  );
                })()}
              </div>
            </div>
          )}

          {/* 5. 營養與酒精資訊 */}
          {(cocktail.nutrition?.calories || cocktail.alcohol_metrics && (
            cocktail.alcohol_metrics.abv != null ||
            cocktail.alcohol_metrics.standard_drinks != null ||
            cocktail.alcohol_metrics.proof != null ||
            cocktail.alcohol_metrics.pure_alcohol_grams != null
           )) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {cocktail.nutrition?.calories && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 mb-2">營養資訊</h4>
                  <div className="flex items-center justify-between">
                    <span className="text-blue-700">卡路里</span>
                    <span className="text-2xl font-bold text-blue-900">
                      {cocktail.nutrition.calories} cal
                    </span>
                  </div>
                </div>
              )}
              {cocktail.alcohol_metrics && (
                cocktail.alcohol_metrics.abv != null ||
                cocktail.alcohol_metrics.standard_drinks != null ||
                cocktail.alcohol_metrics.proof != null ||
                cocktail.alcohol_metrics.pure_alcohol_grams != null
              ) && (
                <div className="bg-orange-50 rounded-lg p-4">
                  <h4 className="font-semibold text-orange-800 mb-2">酒精指標</h4>
                  <div className="space-y-1 text-sm">
                    {cocktail.alcohol_metrics.abv != null && (
                      <div className="flex justify-between">
                        <span className="text-orange-700">酒精濃度</span>
                        <span className="font-semibold text-orange-900">
                          {cocktail.alcohol_metrics.abv}%
                        </span>
                      </div>
                    )}
                    {cocktail.alcohol_metrics.standard_drinks != null && (
                      <div className="flex justify-between">
                        <span className="text-orange-700">標準飲酒量</span>
                        <span className="font-semibold text-orange-900">
                          {cocktail.alcohol_metrics.standard_drinks}
                        </span>
                      </div>
                    )}
                    {cocktail.alcohol_metrics.proof != null && (
                      <div className="flex justify-between">
                        <span className="text-orange-700">酒精度數</span>
                        <span className="font-semibold text-orange-900">
                          {cocktail.alcohol_metrics.proof} proof
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 6. 杯具資訊 */}
          {cocktail.glass && (
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <GlassWater className="w-5 h-5 text-purple-600" />
                <h4 className="font-semibold text-purple-800">建議杯具</h4>
              </div>
              <p className="text-purple-700">
                {langZh && cocktail.glass_zh
                  ? `${cocktail.glass_zh} (${cocktail.glass})`
                  : cocktail.glass}
              </p>
            </div>
          )}

          {/* 7. 歷史故事 */}
          {cocktail.history && cocktail.history.length > 0 && (
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-amber-600" />
                歷史與故事
              </h3>
              <div className="bg-amber-50 rounded-lg p-4 space-y-2">
                {(langZh && cocktail.history_zh?.length
                  ? cocktail.history_zh
                  : cocktail.history
                ).map((paragraph, i) => (
                  <p key={i} className="text-gray-700 leading-relaxed">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* 8. 專業評論 */}
          {cocktail.review && cocktail.review.length > 0 && (
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-indigo-600" />
                專業評論
              </h3>
              <div className="bg-indigo-50 rounded-lg p-4 space-y-2">
                {(langZh && cocktail.review_zh?.length
                  ? cocktail.review_zh
                  : cocktail.review
                ).map((comment, i) => (
                  <p key={i} className="text-gray-700 italic leading-relaxed">
                    "{comment}"
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* 9. 相關變化版本 */}
          {cocktail.variants && cocktail.variants.length > 0 && (
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <LinkIcon className="w-5 h-5 text-cyan-600" />
                相關變化版本
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {cocktail.variants.map((variant, i) => (
                  <a
                    key={i}
                    href={variant.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 p-3 bg-cyan-50 hover:bg-cyan-100 rounded-lg transition-colors"
                  >
                    <Wine className="w-4 h-4 text-cyan-600" />
                    <span className="text-cyan-800 font-medium">{variant.name}</span>
                    <LinkIcon className="w-3 h-3 text-cyan-600 ml-auto" />
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* 10. 過敏原警告 */}
          {cocktail.allergens && cocktail.allergens.length > 0 && (
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                過敏原警告
              </h3>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <ul className="space-y-2">
                  {cocktail.allergens.map((allergen, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                      <div>
                        <span className="font-semibold text-red-800">
                          {langZh && allergen.item_zh
                            ? `${allergen.item_zh} (${allergen.item})`
                            : allergen.item}
                        </span>
                        <span className="text-red-700">
                          {' - '}
                          {langZh && allergen.allergen_zh
                            ? allergen.allergen_zh
                            : allergen.allergen}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Tags */}
          {cocktail.tags_categorized && (
            <div className="pt-4 border-t border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Tags</h4>
              <div className="flex flex-wrap gap-2">
                {cocktail.tags_categorized.base_spirits?.map((tag) => (
                  <TagBadge key={tag} tag={tag} dimension="base_spirits" showColoredIcons={true} />
                ))}
                {cocktail.tags_categorized.flavors?.map((tag) => (
                  <TagBadge key={tag} tag={tag} dimension="flavors" showColoredIcons={true} />
                ))}
                {cocktail.tags_categorized.ingredients?.map((tag) => (
                  <TagBadge key={tag} tag={tag} dimension="ingredients" showColoredIcons={true} />
                ))}
                {cocktail.tags_categorized.styles?.map((tag) => (
                  <TagBadge key={tag} tag={tag} dimension="styles" showColoredIcons={true} />
                ))}
              </div>
            </div>
          )}

          {/* More Categories */}
          {cocktail.more_categories && cocktail.more_categories.length > 0 && (
            <div className="pt-4 border-t border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">More Categories</h4>
              <div className="flex flex-wrap gap-2">
                {(langZh && cocktail.more_categories_zh?.length
                  ? cocktail.more_categories_zh
                  : cocktail.more_categories
                ).map((category, i) => (
                  <CategoryBadge key={i} categoryName={category} />
                ))}
              </div>
            </div>
          )}

          {/* 來源連結 */}
          {cocktail.detail_url && (
            <div className="pt-4 border-t">
              <a
                href={cocktail.detail_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
              >
                <LinkIcon className="w-4 h-4" />
                查看原始配方
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecommendationsPage;
