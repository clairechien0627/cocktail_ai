import {
  Wine,
  Palmtree,
  Trophy,
  Star,
  Clock,
  Sparkles,
  Leaf,
  Flame,
  Snowflake,
  Coffee,
  Sun,
  Moon,
  Heart,
  Gift,
  PartyPopper,
  Salad,
  Cherry,
  Droplet,
  GlassWater,
  Tag,
} from 'lucide-react';

/**
 * More Categories 圖標映射
 * 根據分類名稱的關鍵字返回對應的圖標組件
 */

interface CategoryIconMapping {
  [key: string]: {
    icon: React.ComponentType<{ className?: string }>;
    color: string;  // Tailwind 顏色類別
  };
}

// 分類關鍵字 → 圖標映射表
const CATEGORY_ICON_MAP: CategoryIconMapping = {
  // 經典與名人堂
  'hall of fame': { icon: Trophy, color: 'text-yellow-600' },
  'must know': { icon: Star, color: 'text-yellow-500' },
  'classic': { icon: Clock, color: 'text-blue-600' },
  'vintage': { icon: Clock, color: 'text-blue-600' },
  'contemporary': { icon: Sparkles, color: 'text-purple-600' },

  // 類型與風格
  'tiki': { icon: Palmtree, color: 'text-green-600' },
  'aperitivo': { icon: Wine, color: 'text-red-600' },
  'aperitif': { icon: Wine, color: 'text-red-600' },
  'bittersweet': { icon: Heart, color: 'text-pink-600' },
  'negroni': { icon: Wine, color: 'text-red-700' },
  'sour': { icon: Droplet, color: 'text-yellow-600' },
  'punch': { icon: GlassWater, color: 'text-orange-500' },

  // 季節
  'summer': { icon: Sun, color: 'text-orange-500' },
  'winter': { icon: Snowflake, color: 'text-blue-400' },
  'spring': { icon: Cherry, color: 'text-pink-500' },
  'autumn': { icon: Leaf, color: 'text-orange-700' },
  'fall': { icon: Leaf, color: 'text-orange-700' },
  'christmas': { icon: Gift, color: 'text-red-600' },

  // 時段與場合
  'nightcap': { icon: Moon, color: 'text-indigo-600' },
  'sipping': { icon: Moon, color: 'text-indigo-600' },
  'party': { icon: PartyPopper, color: 'text-pink-500' },
  'brunch': { icon: Coffee, color: 'text-amber-600' },
  'afternoon': { icon: Sun, color: 'text-yellow-500' },
  'elevenses': { icon: Coffee, color: 'text-amber-500' },

  // 風味特徵
  'herbal': { icon: Leaf, color: 'text-green-600' },
  'fruity': { icon: Cherry, color: 'text-red-500' },
  'citrus': { icon: Droplet, color: 'text-yellow-500' },
  'creamy': { icon: GlassWater, color: 'text-amber-300' },
  'spicy': { icon: Flame, color: 'text-red-600' },
  'refreshing': { icon: Snowflake, color: 'text-blue-500' },
  'healthy': { icon: Salad, color: 'text-green-500' },
};

/**
 * 根據分類名稱獲取圖標和顏色
 * @param categoryName - 分類名稱
 * @returns 圖標組件和顏色類別
 */
export const getCategoryIcon = (categoryName: string): {
  icon: React.ComponentType<{ className?: string }>;
  color: string;
} => {
  const lowerName = categoryName.toLowerCase();

  // 嘗試匹配關鍵字
  for (const [keyword, iconData] of Object.entries(CATEGORY_ICON_MAP)) {
    if (lowerName.includes(keyword)) {
      return iconData;
    }
  }

  // 預設圖標
  return { icon: Tag, color: 'text-gray-600' };
};

/**
 * 渲染帶圖標的分類標籤
 * @param categoryName - 分類名稱
 * @param className - 額外的 CSS 類別
 * @returns JSX 元素
 */
export const CategoryBadge = ({ categoryName, className = '' }: { categoryName: string; className?: string }) => {
  const { icon: Icon, color } = getCategoryIcon(categoryName);

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 hover:bg-gray-100 rounded-full text-sm transition-colors ${className}`}>
      <Icon className={`w-4 h-4 ${color}`} />
      <span className="text-gray-700">{categoryName}</span>
    </span>
  );
};
