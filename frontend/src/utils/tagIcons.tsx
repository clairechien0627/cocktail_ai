import React from 'react';
import {
  Wine,
  Droplet,
  Flame,
  Leaf,
  Sparkles,
  Coffee,
  Beer,
  GlassWater,
  Cherry,
  Sun,
  Snowflake,
  Clock,
  Zap,
  Heart,
  Star,
  Trophy,
  Moon,
  Gift,
  Tag as TagIcon,
} from 'lucide-react';

/**
 * Tag 圖標組件系統（與 CategoryBadge 一致的簡潔版本）
 *
 * - 圖標統一使用灰色 (text-gray-600)
 * - 背景統一灰色 (bg-gray-50 hover:bg-gray-100)
 * - 無邊框，與 CategoryBadge 格式完全一致
 * - 只用圖標做視覺識別
 */

type IconType = React.ComponentType<{ className?: string }>;

// ==================== 基酒圖標映射 ====================
const BASE_SPIRIT_ICONS: { [key: string]: IconType } = {
  'gin': Wine,
  'vodka': GlassWater,
  'rum': Droplet,
  'whiskey': Flame,
  'tequila': Sun,
  'brandy': Wine,
  'mezcal': Flame,
  'cachaca': Droplet,
  'pisco': Wine,
  'genever': Wine,
  'non-alcoholic': Droplet,
};

// ==================== 風味圖標映射 ====================
const FLAVOR_ICONS: { [key: string]: IconType } = {
  'citrusy': Sun,
  'fruity': Cherry,
  'tropical': Sun,
  'berry': Cherry,
  'peachy': Cherry,
  'bittersweet': Heart,
  'spicy': Flame,
  'herbal': Leaf,
  'floral': Sparkles,
  'minty': Leaf,
  'nutty': Coffee,
  'smoky': Flame,
  'creamy': Droplet,
  'chocolate': Coffee,
  'coffee': Coffee,
  'vanilla': Sparkles,
  'savory': Droplet,
};

// ==================== 材料圖標映射 ====================
const INGREDIENT_ICONS: { [key: string]: IconType } = {
  // 柑橘類
  'lime': Sun,
  'lemon': Sun,
  'orange': Sun,
  'grapefruit': Sun,

  // 酒類
  'beer': Beer,
  'vermouth': Wine,
  'sparkling-wine': Sparkles,
  'white-wine': Wine,
  'red-wine': Wine,
  'port': Wine,
  'campari': Droplet,

  // 甜味劑
  'triple-sec': Droplet,
  'grenadine': Droplet,
  'honey': Droplet,
  'orgeat': Droplet,
  'maple': Droplet,
  'falernum': Droplet,

  // 苦味劑
  'aromatic-bitters': Droplet,
  'orange-bitters': Droplet,
  'absinthe': Sparkles,

  // 水果花草
  'cherry-brandy': Cherry,
  'elderflower': Sparkles,
  'raspberry': Cherry,
  'fresh-mint': Leaf,
  'basil': Leaf,

  // 其他材料
  'soda-water': Droplet,
  'egg-white': Droplet,
  'chartreuse': Sparkles,
  'amaretto': Coffee,
  'tonic-water': Droplet,
  'coffee-liqueur': Coffee,
  'ice-cream': Sparkles,
  'champagne': Sparkles,
};

// ==================== 風格圖標映射 ====================
const STYLE_ICONS: { [key: string]: IconType } = {
  // 時段場合
  'aperitif': Sun,
  'nightcap': Moon,
  'digestif': Moon,
  'afternoon': Sun,
  'brunch': Coffee,
  'anytime': Clock,
  'party': Sparkles,

  // 季節節日
  'summer': Sun,
  'autumn': Leaf,
  'winter': Snowflake,
  'spring': Cherry,
  'christmas': Gift,
  'halloween': Flame,
  'valentines': Heart,

  // 經典風格
  'classic': Star,
  'hall-of-fame': Trophy,
  'contemporary': Zap,
  'tiki': Leaf,
  'negroni': Wine,
  'martini': Wine,

  // 風味類型
  'spirit-forward': Flame,
  'sour': Droplet,
  'dessert': Sparkles,

  // 製作方式
  'short-stirred': GlassWater,
  'long-drink': GlassWater,
  'champagne': Sparkles,
  'shot': Zap,
  'frozen': Snowflake,
  'hot-drink': Flame,
  'layered': GlassWater,
};

/**
 * 獲取 tag 對應的圖標
 * @param tag - tag 名稱
 * @param dimension - 維度名稱
 * @returns 圖標組件
 */
export const getIcon = (
  tag: string,
  dimension: 'base_spirits' | 'flavors' | 'ingredients' | 'styles'
): IconType => {
  const maps = {
    base_spirits: BASE_SPIRIT_ICONS,
    flavors: FLAVOR_ICONS,
    ingredients: INGREDIENT_ICONS,
    styles: STYLE_ICONS,
  };

  const iconMap = maps[dimension];
  return iconMap[tag] || TagIcon; // 默認使用 TagIcon
};

/**
 * Tag 維度中文標籤
 * @param dimension - 維度名稱
 * @returns 中文標籤
 */
export const getDimensionLabel = (dimension: string): string => {
  const labels: { [key: string]: string } = {
    'base_spirits': '基酒',
    'flavors': '風味',
    'ingredients': '材料',
    'styles': '風格',
  };

  return labels[dimension] || dimension;
};

/**
 * Tag 徽章組件
 * - 背景統一灰色 (bg-gray-50 hover:bg-gray-100)
 * - 圖標顏色：
 *   - 篩選器：統一灰色 (text-gray-600)
 *   - 詳細頁：按維度分色 (showColoredIcons=true)
 */
interface TagProps {
  tag: string;
  dimension: 'base_spirits' | 'flavors' | 'ingredients' | 'styles';
  onClick?: () => void;
  selected?: boolean;
  showColoredIcons?: boolean; // 詳細頁使用彩色圖標
  langZh?: boolean; // 是否顯示中文
  tagZh?: string; // 中文翻譯
}

/**
 * 獲取維度對應的圖標顏色
 */
const getDimensionIconColor = (dimension: 'base_spirits' | 'flavors' | 'ingredients' | 'styles'): string => {
  const colorMap = {
    base_spirits: 'text-amber-600',   // 基酒：橙色
    flavors: 'text-green-600',        // 風味：綠色
    ingredients: 'text-blue-600',     // 材料：藍色
    styles: 'text-purple-600',        // 風格：紫色
  };
  return colorMap[dimension];
};

export const TagBadge: React.FC<TagProps> = ({ tag, dimension, onClick, selected = false, showColoredIcons = false, langZh = false, tagZh }) => {
  const Icon = getIcon(tag, dimension);
  const selectedClass = selected ? 'ring-2 ring-offset-1 ring-blue-500' : '';
  const iconColor = showColoredIcons ? getDimensionIconColor(dimension) : 'text-gray-600';

  // 根據語言狀態決定顯示的文字
  const displayText = langZh && tagZh ? tagZh : tag.replace(/-/g, ' ');

  return (
    <span
      onClick={onClick}
      className={`
        inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 hover:bg-gray-100 rounded-full text-sm transition-colors
        ${selectedClass}
        ${onClick ? 'cursor-pointer' : ''}
      `}
    >
      <Icon className={`w-4 h-4 ${iconColor}`} />
      <span className="text-gray-700 capitalize">{displayText}</span>
    </span>
  );
};

export default TagBadge;
