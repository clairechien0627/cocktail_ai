import { useState, useEffect } from 'react';
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
  ChevronLeft,
  ChevronRight,
  Leaf,
  ChefHat,
  GlassWater,
  BookOpen,
  MessageSquare,
  Link as LinkIcon,
  AlertCircle,
  ImageOff,
} from 'lucide-react';
import type { Cocktail } from '../types';
import { TagBadge } from '../utils/tagIcons';

const RecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState<Cocktail[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCocktail, setSelectedCocktail] = useState<Cocktail | null>(null);
  const [showRecordForm, setShowRecordForm] = useState(false);
  const [hasDrunk, setHasDrunk] = useState<boolean>(false);

  useEffect(() => {
    loadRecommendations();
  }, []);

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

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const response = await recordsAPI.getRecommendations(20);
      setRecommendations(response.recommendations);
    } catch (error) {
      console.error('載入推薦失敗:', error);
    } finally {
      setLoading(false);
    }
  };

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
        <div className="text-xl text-gray-600">正在分析你的偏好...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-primary-600" />
              為你推薦
            </h1>
            <p className="text-gray-600">基於你的飲用歷史與口味偏好精心挑選</p>
          </div>
          <button
            onClick={loadRecommendations}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            重新推薦
          </button>
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
              <div
                key={cocktail._id}
                onClick={() => setSelectedCocktail(cocktail)}
                className="relative overflow-hidden rounded-lg cursor-pointer hover:scale-105 transition-transform duration-300 group"
                style={{
                  backgroundImage: cocktail.image_url
                    ? `url(${cocktail.image_url})`
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                  aspectRatio: '3/4',
                }}
              >
                {/* 圖片載入失敗提示 */}
                {!cocktail.image_url && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <ImageOff className="w-16 h-16 text-white/50" />
                  </div>
                )}

                {/* 漸層遮罩 */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />

                {/* 頂部浮層 */}
                <div className="absolute top-3 right-3 flex items-center gap-2">
                  {/* 推薦類型小標籤 */}
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
                  {/* 調酒名稱 */}
                  <h3 className="font-bold text-xl mb-3 line-clamp-2 drop-shadow-lg">
                    {cocktail.name}
                  </h3>

                  {/* 分類標籤 */}
                  {cocktail.tags_categorized && (
                    <div className="flex flex-wrap gap-1 mb-2.5">
                      {/* 基酒標籤 */}
                      {cocktail.tags_categorized.base_spirits?.slice(0, 2).map((tag, index) => (
                        <div key={index} className="bg-white/20 backdrop-blur-sm rounded-full px-2 py-0.5 flex items-center gap-1">
                          <span className="text-[10px] text-white/90 capitalize">{tag.replace(/-/g, ' ')}</span>
                        </div>
                      ))}

                      {/* 風味標籤 */}
                      {cocktail.tags_categorized.flavors?.slice(0, 2).map((tag, index) => (
                        <div key={index} className="bg-white/20 backdrop-blur-sm rounded-full px-2 py-0.5 flex items-center gap-1">
                          <span className="text-[10px] text-white/90 capitalize">{tag.replace(/-/g, ' ')}</span>
                        </div>
                      ))}

                      {/* 風格標籤 */}
                      {cocktail.tags_categorized.styles?.slice(0, 1).map((tag, index) => (
                        <div key={index} className="bg-white/20 backdrop-blur-sm rounded-full px-2 py-0.5 flex items-center gap-1">
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
                    <style dangerouslySetInnerHTML={{ __html: `
                      .bg-black\\/30::-webkit-scrollbar {
                        width: 4px;
                      }
                      .bg-black\\/30::-webkit-scrollbar-track {
                        background: transparent;
                      }
                      .bg-black\\/30::-webkit-scrollbar-thumb {
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 2px;
                      }
                      .bg-black\\/30::-webkit-scrollbar-thumb:hover {
                        background: rgba(255, 255, 255, 0.3);
                      }
                    `}} />
                    <div className="flex items-center gap-1.5 mb-2">
                      <GlassWater className="w-4 h-4 text-white/80" />
                      <span className="text-xs font-semibold text-white/80">材料</span>
                    </div>
                    <ul className="space-y-1 text-xs">
                      {cocktail.ingredients.map((ingredient, index) => (
                        <li key={index} className="flex items-start gap-1.5 text-white/90">
                          <span className="text-white/60 mt-0.5">•</span>
                          <span className="line-clamp-1">{ingredient}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* 調酒詳情模態框 */}
      {selectedCocktail && !showRecordForm && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedCocktail(null)}
        >
          <div
            className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header with Record Button */}
            <div className="sticky top-0 bg-primary-600 text-white px-6 py-4 flex items-center justify-between z-10">
              <div className="flex items-center gap-3 flex-1">
                <h2 className="text-2xl font-bold">{selectedCocktail.name}</h2>
                {hasDrunk && (
                  <span className="flex items-center gap-1.5 px-3 py-1 bg-white bg-opacity-20 rounded-full text-sm">
                    <CheckCircle className="w-4 h-4" />
                    已喝過
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowRecordForm(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-gray-100 transition-colors"
                >
                  <Edit3 className="w-4 h-4" />
                  記錄飲用
                </button>
                <button
                  onClick={() => setSelectedCocktail(null)}
                  className="text-white hover:text-gray-200"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6">
              {/* Image */}
              {selectedCocktail.image_url && (
                <div className="mb-6">
                  <img
                    src={selectedCocktail.image_url}
                    alt={selectedCocktail.name}
                    className="w-full h-auto max-h-96 object-contain rounded-lg"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                </div>
              )}

              {/* 推薦理由與相似度 */}
              {selectedCocktail.recommendation_reason && (
                <div className="mb-4 p-4 bg-primary-50 border-l-4 border-primary-400 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-5 h-5 text-primary-600" />
                    <span className="font-semibold text-primary-900">推薦理由</span>
                  </div>
                  <p className="text-sm text-primary-800 mb-2">
                    {selectedCocktail.recommendation_reason}
                  </p>
                  {selectedCocktail.similarity_score !== undefined && selectedCocktail.similarity_score > 0 && (
                    <div className="flex items-center gap-2 mt-2 pt-2 border-t border-primary-200">
                      <Star className="w-4 h-4 text-primary-600" />
                      <span className="text-xs text-primary-700 font-medium">
                        相似度評分: {selectedCocktail.similarity_score.toFixed(1)} 分
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Ratings & Difficulty */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                {selectedCocktail.ratings?.professional != null && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">專業評分</div>
                    <div className="flex items-center gap-2">
                      {renderStars(selectedCocktail.ratings.professional)}
                      <span className="text-xl font-bold text-gray-900">
                        {selectedCocktail.ratings.professional.toFixed(1)}
                      </span>
                    </div>
                  </div>
                )}

                {selectedCocktail.difficulty && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">難度</div>
                    <div className={`inline-block px-3 py-1 rounded text-sm font-semibold ${
                      selectedCocktail.difficulty === 'easy'
                        ? 'bg-green-100 text-green-700'
                        : selectedCocktail.difficulty === 'medium'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {selectedCocktail.difficulty === 'easy' ? '簡單' : selectedCocktail.difficulty === 'medium' ? '中等' : '困難'}
                    </div>
                  </div>
                )}
              </div>

              {/* Taste Profile */}
              {selectedCocktail.taste_profile && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-3">風味檔案</h3>
                  <div className="space-y-3">
                    {selectedCocktail.taste_profile.strength !== undefined && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Flame className="w-5 h-5 text-orange-500" />
                            <span className="text-sm font-medium text-gray-700">酒精強度</span>
                          </div>
                          <span className="text-sm font-semibold text-gray-900">
                            {selectedCocktail.taste_profile.strength}/10
                          </span>
                        </div>
                        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-orange-500"
                            style={{ width: `${(selectedCocktail.taste_profile.strength / 10) * 100}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {selectedCocktail.taste_profile.sweetness !== undefined && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Droplet className="w-5 h-5 text-blue-500" />
                            <span className="text-sm font-medium text-gray-700">甜度</span>
                          </div>
                          <span className="text-sm font-semibold text-gray-900">
                            {selectedCocktail.taste_profile.sweetness}/10
                          </span>
                        </div>
                        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500"
                            style={{ width: `${(selectedCocktail.taste_profile.sweetness / 10) * 100}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Ingredients */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <GlassWater className="w-5 h-5 text-primary-600" />
                  材料
                </h3>
                <ul className="space-y-2">
                  {(selectedCocktail.ingredients_detail || selectedCocktail.ingredients).map((item, i) => {
                    const name = typeof item === "string" ? item : item.ingredient;
                    const amount = typeof item === "string" ? null : item.amount;
                    return (
                      <li key={i} className="flex justify-between items-start text-gray-700">
                        <div className="flex gap-2">
                          <span className="text-primary-600 font-bold">•</span>
                          <span className="break-words">{name}</span>
                        </div>
                        {amount && <span className="text-gray-500 ml-4 shrink-0">{amount}</span>}
                      </li>
                    );
                  })}
                </ul>
              </div>

              {/* Method */}
              {selectedCocktail.method && selectedCocktail.method.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                    <ChefHat className="w-5 h-5 text-primary-600" />
                    製作步驟
                  </h3>
                  <ol className="space-y-2">
                    {selectedCocktail.method.map((step, index) => (
                      <li key={index} className="flex items-start gap-3 text-gray-700">
                        <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </span>
                        <span className="flex-1 pt-0.5">{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Garnish */}
              {selectedCocktail.garnish && selectedCocktail.garnish.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                    <Leaf className="w-5 h-5 text-green-600" />
                    裝飾
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedCocktail.garnish.map((item, index) => (
                      <span key={index} className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Glass */}
              {selectedCocktail.glass && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Wine className="w-5 h-5 text-gray-600" />
                    <span className="text-sm text-gray-600">使用杯具：</span>
                    <span className="font-semibold text-gray-900">{selectedCocktail.glass}</span>
                  </div>
                </div>
              )}

              {/* Tags */}
              {selectedCocktail.tags_categorized && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-3">分類標籤</h3>
                  <div className="space-y-3">
                    {selectedCocktail.tags_categorized.base_spirits && selectedCocktail.tags_categorized.base_spirits.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-gray-600 mb-2">基酒</div>
                        <div className="flex flex-wrap gap-2">
                          {selectedCocktail.tags_categorized.base_spirits.map((tag, index) => (
                            <span key={index} className="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedCocktail.tags_categorized.flavors && selectedCocktail.tags_categorized.flavors.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-gray-600 mb-2">風味</div>
                        <div className="flex flex-wrap gap-2">
                          {selectedCocktail.tags_categorized.flavors.map((tag, index) => (
                            <span key={index} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedCocktail.tags_categorized.styles && selectedCocktail.tags_categorized.styles.length > 0 && (
                      <div>
                        <div className="text-sm font-medium text-gray-600 mb-2">風格</div>
                        <div className="flex flex-wrap gap-2">
                          {selectedCocktail.tags_categorized.styles.map((tag, index) => (
                            <span key={index} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Source Link */}
              {selectedCocktail.detail_url && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <a
                    href={selectedCocktail.detail_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
                  >
                    <LinkIcon className="w-4 h-4" />
                    查看原始來源
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
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
            loadRecommendations();
          }}
        />
      )}
    </div>
  );
};

export default RecommendationsPage;
