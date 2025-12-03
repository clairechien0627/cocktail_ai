/**
 * Tag 子分類配置（簡化版，統一灰色）
 *
 * 每個維度（base_spirits, flavors, ingredients, styles）都分成若干子分類
 * 篩選器中所有 tag 使用統一的灰色
 * 詳情頁可選使用非常淡的灰色系區分
 *
 * 總共 12 個子分類（從原本的 19 個簡化）
 */

export interface TagSubcategory {
  key: string;           // 子分類唯一標識
  label: string;         // 子分類顯示名稱
  tags: string[];        // 該子分類包含的所有 tag
  bgColor: string;       // 背景色 (Tailwind class)
  textColor: string;     // 文字色 (Tailwind class)
  borderColor: string;   // 邊框色 (Tailwind class)
  detailBgColor?: string; // 詳情頁專用背景色（可選，非常淡的灰色系）
}

export interface TagSubcategories {
  base_spirits: TagSubcategory[];
  flavors: TagSubcategory[];
  ingredients: TagSubcategory[];
  styles: TagSubcategory[];
}

/**
 * 完整的子分類配置（簡化版）
 * - 篩選器：統一 gray-50 背景
 * - 詳情頁：可選用 gray-50 到 gray-100 的淡灰色系
 */
export const TAG_SUBCATEGORIES: TagSubcategories = {
  // ==================== BASE_SPIRITS (2 個子分類) ====================
  base_spirits: [
    {
      key: 'mainstream',
      label: '主流烈酒',
      tags: ['gin', 'vodka', 'rum', 'whiskey', 'tequila', 'brandy'],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-50',
    },
    {
      key: 'others',
      label: '其他',
      tags: ['mezcal', 'cachaca', 'pisco', 'genever', 'non-alcoholic'],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-100',
    },
  ],

  // ==================== FLAVORS (3 個子分類，移除動態標籤) ====================
  flavors: [
    {
      key: 'fruity',
      label: '果香類',
      tags: ['citrusy', 'fruity', 'tropical', 'berry', 'peachy'],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-50',
    },
    {
      key: 'herbal-spicy',
      label: '草本辛香',
      tags: ['herbal', 'floral', 'minty', 'bittersweet', 'spicy'],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-75',
    },
    {
      key: 'rich',
      label: '濃郁風味',
      tags: ['chocolate', 'coffee', 'vanilla', 'nutty', 'smoky', 'creamy'],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-100',
    },
  ],

  // ==================== INGREDIENTS (4 個子分類) ====================
  ingredients: [
    {
      key: 'citrus',
      label: '柑橘類',
      tags: ['lime', 'lemon', 'orange', 'grapefruit'],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-50',
    },
    {
      key: 'alcoholic-beverages',
      label: '酒類',
      tags: ['beer', 'vermouth', 'sparkling-wine', 'white-wine', 'red-wine', 'port', 'campari'],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-75',
    },
    {
      key: 'seasonings',
      label: '調味料',
      tags: [
        'triple-sec', 'grenadine', 'honey', 'orgeat', 'maple', 'falernum',
        'aromatic-bitters', 'orange-bitters', 'absinthe'
      ],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-100',
    },
    {
      key: 'others',
      label: '其他材料',
      tags: [
        'soda-water', 'egg-white', 'chartreuse', 'amaretto', 'tonic-water', 'coffee-liqueur',
        'cherry-brandy', 'elderflower', 'raspberry', 'fresh-mint', 'basil'
      ],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-50',
    },
  ],

  // ==================== STYLES (3 個子分類) ====================
  styles: [
    {
      key: 'time-occasion',
      label: '時段場合',
      tags: ['aperitif', 'nightcap', 'digestif', 'afternoon', 'brunch', 'anytime', 'party'],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-50',
    },
    {
      key: 'seasonal',
      label: '季節節日',
      tags: ['summer', 'autumn', 'winter', 'spring', 'christmas', 'halloween', 'valentines'],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-75',
    },
    {
      key: 'style-type',
      label: '風格類型',
      tags: [
        'classic', 'hall-of-fame', 'contemporary', 'tiki', 'negroni', 'martini',
        'spirit-forward', 'sour', 'dessert',
        'short-stirred', 'long-drink', 'champagne', 'shot', 'frozen', 'hot-drink', 'layered'
      ],
      bgColor: 'bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-200',
      detailBgColor: 'bg-gray-100',
    },
  ],
};

/**
 * 根據 tag 和維度查找對應的顏色配置
 * @param tag - tag 名稱
 * @param dimension - 維度名稱
 * @param useDetailColors - 是否使用詳情頁顏色（淡灰色系區分）
 * @returns 顏色配置對象
 */
export function getTagColors(
  tag: string,
  dimension: 'base_spirits' | 'flavors' | 'ingredients' | 'styles',
  useDetailColors: boolean = false
): { bgColor: string; textColor: string; borderColor: string } {
  const subcategories = TAG_SUBCATEGORIES[dimension];

  for (const subcategory of subcategories) {
    if (subcategory.tags.includes(tag)) {
      return {
        bgColor: useDetailColors && subcategory.detailBgColor
          ? subcategory.detailBgColor
          : subcategory.bgColor,
        textColor: subcategory.textColor,
        borderColor: subcategory.borderColor,
      };
    }
  }

  // 默認灰色（如果找不到）
  return {
    bgColor: 'bg-gray-50',
    textColor: 'text-gray-700',
    borderColor: 'border-gray-200',
  };
}

/**
 * 獲取子分類的顯示順序（用於排序）
 * @param dimension - 維度名稱
 * @returns 排序後的 tag 列表
 */
export function getSortedTags(dimension: 'base_spirits' | 'flavors' | 'ingredients' | 'styles'): string[] {
  const subcategories = TAG_SUBCATEGORIES[dimension];
  const sortedTags: string[] = [];

  // 按子分類順序展開所有 tags
  for (const subcategory of subcategories) {
    sortedTags.push(...subcategory.tags);
  }

  return sortedTags;
}
