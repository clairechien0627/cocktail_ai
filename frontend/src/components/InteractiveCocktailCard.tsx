import { useState } from 'react';
import type { CocktailCardData } from '../types/index';
import { Heart, MessageCircle, Repeat, Sparkles, Flame, Droplet } from 'lucide-react';
import { favoritesAPI } from '../services/api';
import { getIcon } from '../utils/tagIcons';

interface InteractiveCocktailCardProps {
  cocktail: CocktailCardData;
  isFavorited?: boolean;
  onFavoriteToggle?: (cocktailId: string, isFavorited: boolean) => void;
  onQuickAction?: (action: 'tell_more' | 'similar' | 'try_this', cocktailId: string) => void;
  onImageClick?: (cocktailId: string) => void;
}

export function InteractiveCocktailCard({
  cocktail,
  isFavorited = false,
  onFavoriteToggle,
  onQuickAction,
  onImageClick,
}: InteractiveCocktailCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isLoadingFavorite, setIsLoadingFavorite] = useState(false);

  // 處理收藏
  const handleFavorite = async (e: React.MouseEvent) => {
    e.stopPropagation();

    if (isLoadingFavorite) return;

    setIsLoadingFavorite(true);

    try {
      if (isFavorited) {
        await favoritesAPI.remove(cocktail._id);
        if (onFavoriteToggle) {
          onFavoriteToggle(cocktail._id, false);
        }
      } else {
        await favoritesAPI.add(cocktail._id);
        if (onFavoriteToggle) {
          onFavoriteToggle(cocktail._id, true);
        }
      }
    } catch (error) {
      console.error('收藏操作失敗:', error);
    } finally {
      setIsLoadingFavorite(false);
    }
  };

  // 快速操作
  const handleQuickAction = (action: 'tell_more' | 'similar' | 'try_this', e: React.MouseEvent) => {
    e.stopPropagation();
    if (onQuickAction) {
      onQuickAction(action, cocktail._id);
    }
  };

  // 點擊圖片查看詳細
  const handleImageClick = () => {
    if (onImageClick) {
      onImageClick(cocktail._id);
    }
  };

  // 酒類 tags（ingredients 子分類）
  const alcoholicBeverages = ['beer', 'vermouth', 'sparkling-wine', 'champagne',
                              'white-wine', 'red-wine', 'port', 'campari'];

  // 風格類型 tags（styles 子分類）
  const styleTypes = ['classic', 'hall-of-fame', 'contemporary', 'tiki', 'negroni',
                      'martini', 'spirit-forward', 'sour', 'dessert', 'short-stirred',
                      'long-drink', 'champagne', 'shot', 'frozen', 'hot-drink', 'layered'];

  // 獲取基酒和風味 tags（全部顯示）
  const baseSpirits = cocktail.tags_categorized?.base_spirits || [];
  const flavors = cocktail.tags_categorized?.flavors || [];

  // 獲取酒類 tags（只顯示酒類相關）
  const ingredientTags = (cocktail.tags_categorized?.ingredients || [])
    .filter(tag => alcoholicBeverages.includes(tag));

  // 獲取風格類型 tags（只顯示風格類型）
  const styleTags = (cocktail.tags_categorized?.styles || [])
    .filter(tag => styleTypes.includes(tag));

  // 計算符號數量（1-10 對應 1-5 個符號）
  const getSymbolCount = (value: number): number => {
    if (value <= 0) return 0;
    return Math.ceil(value / 2); // 1-2→1, 3-4→2, 5-6→3, 7-8→4, 9-10→5
  };

  return (
    <div
      className="rounded-xl shadow-md hover:shadow-2xl transition-all duration-300 overflow-hidden group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 圖片區域 - 所有內容都在圖片上 */}
      <div
        className="relative bg-gradient-to-br from-primary-100 to-primary-200 overflow-hidden cursor-pointer"
        style={{ aspectRatio: '3/3.5' }}
        onClick={handleImageClick}
      >
        {/* 調酒圖片 */}
        {cocktail.image_url ? (
          <img
            src={cocktail.image_url}
            alt={cocktail.name}
            className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            onError={(e) => {
              e.currentTarget.src = 'https://via.placeholder.com/400x300?text=No+Image';
            }}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400">
            <Sparkles size={48} />
          </div>
        )}


        {/* Tags - 左上角垂直堆疊 */}
        {(baseSpirits.length > 0 || flavors.length > 0 || ingredientTags.length > 0 || styleTags.length > 0) && (
          <div className="absolute top-3 left-3 flex flex-col items-start gap-1 z-10">
            {/* 基酒 Tags - 橙色 */}
            {baseSpirits.map((tag, idx) => {
              const Icon = getIcon(tag, 'base_spirits');
              return (
                <div
                  key={`spirit-${idx}`}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-orange-500/50 backdrop-blur-sm text-white text-[10px] font-semibold rounded-full drop-shadow-lg"
                >
                  {Icon && <Icon className="w-3 h-3" />}
                  <span className="capitalize whitespace-nowrap">{tag.replace(/-/g, ' ')}</span>
                </div>
              );
            })}

            {/* 風味 Tags - 綠色 */}
            {flavors.map((tag, idx) => {
              const Icon = getIcon(tag, 'flavors');
              return (
                <div
                  key={`flavor-${idx}`}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/50 backdrop-blur-sm text-white text-[10px] font-semibold rounded-full drop-shadow-lg"
                >
                  {Icon && <Icon className="w-3 h-3" />}
                  <span className="capitalize whitespace-nowrap">{tag.replace(/-/g, ' ')}</span>
                </div>
              );
            })}

            {/* 材料（酒類）Tags - 藍色 */}
            {ingredientTags.map((tag, idx) => {
              const Icon = getIcon(tag, 'ingredients');
              return (
                <div
                  key={`ingredient-${idx}`}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-500/50 backdrop-blur-sm text-white text-[10px] font-semibold rounded-full drop-shadow-lg"
                >
                  {Icon && <Icon className="w-3 h-3" />}
                  <span className="capitalize whitespace-nowrap">{tag.replace(/-/g, ' ')}</span>
                </div>
              );
            })}

            {/* 風格類型 Tags - 紫色 */}
            {styleTags.map((tag, idx) => {
              const Icon = getIcon(tag, 'styles');
              return (
                <div
                  key={`style-${idx}`}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-purple-500/50 backdrop-blur-sm text-white text-[10px] font-semibold rounded-full drop-shadow-lg"
                >
                  {Icon && <Icon className="w-3 h-3" />}
                  <span className="capitalize whitespace-nowrap">{tag.replace(/-/g, ' ')}</span>
                </div>
              );
            })}
          </div>
        )}

        {/* 收藏按鈕 - 右上角（hover 顯示）*/}
        <div
          className={`absolute top-3 right-3 z-20 transition-all duration-300 ${
            isHovered ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4 pointer-events-none'
          }`}
        >
          <button
            onClick={handleFavorite}
            disabled={isLoadingFavorite}
            className={`p-2.5 rounded-full backdrop-blur-sm transition-all shadow-lg ${
              isFavorited
                ? 'bg-red-500 text-white scale-110'
                : 'bg-white/95 text-gray-700 hover:bg-red-500 hover:text-white hover:scale-110'
            } ${isLoadingFavorite ? 'opacity-50 cursor-not-allowed' : ''}`}
            aria-label={isFavorited ? '取消收藏' : '收藏'}
          >
            <Heart
              size={20}
              fill={isFavorited ? 'currentColor' : 'none'}
              className={isLoadingFavorite ? 'animate-pulse' : ''}
              strokeWidth={2.5}
            />
          </button>
        </div>

        {/* 快速操作按鈕 - 右上角垂直排列（hover 顯示，收藏按鈕下方）*/}
        <div
          className={`absolute top-16 right-3 flex flex-col gap-2 z-10 transition-all duration-300 ${
            isHovered ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4 pointer-events-none'
          }`}
        >
          <button
            onClick={(e) => handleQuickAction('tell_more', e)}
            className="p-2.5 bg-white/95 backdrop-blur-sm text-primary-600 rounded-full hover:bg-primary-600 hover:text-white transition-all shadow-lg hover:scale-110"
            title="告訴我更多"
          >
            <MessageCircle size={18} strokeWidth={2.5} />
          </button>
          <button
            onClick={(e) => handleQuickAction('similar', e)}
            className="p-2.5 bg-white/95 backdrop-blur-sm text-gray-700 rounded-full hover:bg-gray-700 hover:text-white transition-all shadow-lg hover:scale-110"
            title="類似的調酒"
          >
            <Repeat size={18} strokeWidth={2.5} />
          </button>
        </div>

        {/* 風味檔案符號 - 右下角（非 hover 時顯示）*/}
        {!isHovered && cocktail.taste_profile && (cocktail.taste_profile.strength !== undefined || cocktail.taste_profile.sweetness !== undefined) && (
          <div className="absolute bottom-16 right-3 flex flex-col items-end gap-1 z-10">
            {/* 酒精強度符號 */}
            {cocktail.taste_profile.strength !== undefined && cocktail.taste_profile.strength > 0 && (
              <div className="flex items-center gap-1 opacity-80">
                {Array.from({ length: getSymbolCount(cocktail.taste_profile.strength) }).map((_, idx) => (
                  <Flame key={idx} className="w-4 h-4 text-orange-400 drop-shadow-lg fill-orange-400" />
                ))}
              </div>
            )}

            {/* 甜度符號 */}
            {cocktail.taste_profile.sweetness !== undefined && cocktail.taste_profile.sweetness > 0 && (
              <div className="flex items-center gap-1 opacity-70">
                {Array.from({ length: getSymbolCount(cocktail.taste_profile.sweetness) }).map((_, idx) => (
                  <Droplet key={idx} className="w-4 h-4 text-blue-400 drop-shadow-lg fill-blue-400" />
                ))}
              </div>
            )}
          </div>
        )}

        {/* 底部資訊 - 左下角 */}
        <div className="absolute bottom-0 left-0 right-0 z-10">

          {/* 主要材料 - hover 時顯示 */}
          {isHovered && cocktail.ingredients && cocktail.ingredients.length > 0 && (
            <div className="px-4 pb-2 animate-fadeIn">
              <div className="bg-black/30 backdrop-blur-sm rounded-lg p-2.5">
                <div className="text-xs font-medium text-white/80 mb-1.5">
                  主要材料 ({cocktail.ingredients_count || cocktail.ingredients.length} 種)
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {cocktail.ingredients.slice(0, 4).map((ingredient, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-white/10 text-white/95 text-xs rounded"
                    >
                      {ingredient}
                    </span>
                  ))}
                  {cocktail.ingredients.length > 4 && (
                    <span className="px-2 py-0.5 bg-white/10 text-white/80 text-xs rounded">
                      +{cocktail.ingredients.length - 4}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 調酒名稱 - 一直顯示，只顯示英文 */}
          <div className="bg-black/70 backdrop-blur-sm px-4 py-3">
            <h3 className="text-base font-bold text-white line-clamp-2">
              {cocktail.name}
            </h3>
          </div>
        </div>
      </div>
    </div>
  );
}
