import { useState } from 'react';
import type { Cocktail } from '../types';
import { CategoryBadge } from '../utils/categoryIcons';
import { TagBadge } from '../utils/tagIcons';
import {
  X,
  Star,
  Flame,
  Droplet,
  GlassWater,
  ChefHat,
  AlertCircle,
  BookOpen,
  MessageSquare,
  Link as LinkIcon,
  Sparkles,
  Leaf,
  CheckCircle,
  Edit3,
  Heart,
  Wine,
} from 'lucide-react';

interface CocktailDetailModalProps {
  cocktail: Cocktail;
  isOpen: boolean;
  isFavorited?: boolean;
  hasDrunk?: boolean;
  langZh?: boolean;
  onClose: () => void;
  onLangChange?: (value: boolean) => void;
  onRecord?: () => void;
  onFavoriteToggle?: () => void;
}

export function CocktailDetailModal({
  cocktail,
  isOpen,
  isFavorited = false,
  hasDrunk = false,
  langZh = false,
  onClose,
  onLangChange,
  onRecord,
  onFavoriteToggle,
}: CocktailDetailModalProps) {
  const [isLoadingFavorite, setIsLoadingFavorite] = useState(false);

  if (!isOpen) return null;

  // 渲染星星評分
  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <Star key={i} className="w-5 h-5 text-yellow-500 fill-yellow-500" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <Star key={i} className="w-5 h-5 text-yellow-500" style={{ fill: 'url(#halfStar)' }} />
        );
      } else {
        stars.push(
          <Star key={i} className="w-5 h-5 text-gray-300" />
        );
      }
    }
    return stars;
  };

  const handleFavoriteClick = async () => {
    if (onFavoriteToggle && !isLoadingFavorite) {
      setIsLoadingFavorite(true);
      await onFavoriteToggle();
      setIsLoadingFavorite(false);
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 標題欄 - Sticky */}
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
            {/* 語言切換 */}
            {onLangChange && (
              <button
                onClick={() => onLangChange(!langZh)}
                className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-white bg-opacity-20 hover:bg-opacity-30 transition-colors"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-white" />
                {langZh ? '英' : '中'}
              </button>
            )}

            {/* 收藏按鈕 */}
            {onFavoriteToggle && (
              <button
                onClick={handleFavoriteClick}
                disabled={isLoadingFavorite}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  isFavorited
                    ? 'bg-red-500 text-white hover:bg-red-600'
                    : 'bg-white text-red-500 hover:bg-gray-100'
                } ${isLoadingFavorite ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Heart
                  className="w-4 h-4"
                  fill={isFavorited ? 'currentColor' : 'none'}
                />
                {isFavorited ? '已收藏' : '收藏'}
              </button>
            )}

            {/* 記錄飲用按鈕 */}
            {onRecord && (
              <button
                onClick={onRecord}
                className="flex items-center gap-2 px-4 py-2 bg-white text-primary-600 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              >
                <Edit3 className="w-4 h-4" />
                記錄飲用
              </button>
            )}

            {/* 關閉按鈕 */}
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
          {/* COTD 徽章 */}
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
                  const methodSections = langZh && cocktail.method_sections_zh?.length
                    ? cocktail.method_sections_zh
                    : cocktail.method_sections;

                  if (!methodSections || methodSections.length === 0) {
                    return <p className="text-gray-500 italic">無製作步驟資訊</p>;
                  }

                  return (
                    <div className="space-y-4">
                      {methodSections.map((section: any, i: number) => {
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
                {cocktail.tags_categorized.base_spirits?.map((tag, idx) => (
                  <TagBadge
                    key={tag}
                    tag={tag}
                    dimension="base_spirits"
                    showColoredIcons={true}
                    langZh={langZh}
                    tagZh={cocktail.tags_categorized_zh?.base_spirits?.[idx]}
                  />
                ))}
                {cocktail.tags_categorized.flavors?.map((tag, idx) => (
                  <TagBadge
                    key={tag}
                    tag={tag}
                    dimension="flavors"
                    showColoredIcons={true}
                    langZh={langZh}
                    tagZh={cocktail.tags_categorized_zh?.flavors?.[idx]}
                  />
                ))}
                {cocktail.tags_categorized.ingredients?.map((tag, idx) => (
                  <TagBadge
                    key={tag}
                    tag={tag}
                    dimension="ingredients"
                    showColoredIcons={true}
                    langZh={langZh}
                    tagZh={cocktail.tags_categorized_zh?.ingredients?.[idx]}
                  />
                ))}
                {cocktail.tags_categorized.styles?.map((tag, idx) => (
                  <TagBadge
                    key={tag}
                    tag={tag}
                    dimension="styles"
                    showColoredIcons={true}
                    langZh={langZh}
                    tagZh={cocktail.tags_categorized_zh?.styles?.[idx]}
                  />
                ))}
              </div>
            </div>
          )}

          {/* More Categories */}
          {cocktail.more_categories && cocktail.more_categories.length > 0 && (
            <div className="pt-4 border-t border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">More Categories</h4>
              <div className="flex flex-wrap gap-2">
                {cocktail.more_categories.map((categoryEn, i) => {
                  const categoryDisplay = langZh && cocktail.more_categories_zh?.[i]
                    ? cocktail.more_categories_zh[i]
                    : categoryEn;

                  return (
                    <CategoryBadge
                      key={i}
                      categoryName={categoryDisplay}
                      categoryNameEn={categoryEn}
                    />
                  );
                })}
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
}
