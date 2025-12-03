import React, { useState, useEffect } from 'react';
import { cocktailAPI } from '../../services/api';
import { TagBadge, getDimensionLabel } from '../../utils/tagIcons';
import { TAG_SUBCATEGORIES } from '../../utils/tagSubcategories';

// 將所有需要的類型直接定義在此，以進行隔離
interface TagsCategorized {
  base_spirits: string[];
  flavors: string[];
  ingredients: string[];
  styles: string[];
}

interface TagsResponse {
  tags: TagsCategorized;
  counts: {
    base_spirits: { [key: string]: number };
    flavors: { [key: string]: number };
    ingredients: { [key: string]: number };
    styles: { [key: string]: number };
  };
}

/**
 * Tag 篩選器組件
 *
 * 提供四個維度的 tag 篩選功能：
 * - 基酒類型 (base_spirits)
 * - 風味特徵 (flavors)
 * - 主要材料 (ingredients)
 * - 風格/類型 (styles)
 *
 * 支援多選、顯示每個 tag 的調酒數量
 */

interface TagFilterProps {
  selectedTags: {
    base_spirits: string[];
    flavors: string[];
    ingredients: string[];
    styles: string[];
  };
  onTagChange: (dimension: keyof TagFilterProps['selectedTags'], tags: string[]) => void;
  onReset?: () => void;
}

const TagFilter: React.FC<TagFilterProps> = ({ selectedTags, onTagChange, onReset }) => {
  const [tagsData, setTagsData] = useState<TagsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedDimensions, setExpandedDimensions] = useState<{
    [key: string]: boolean;
  }>({
    base_spirits: true,
    flavors: false,
    ingredients: false,
    styles: false,
  });

  // 載入所有 tags
  useEffect(() => {
    const fetchTags = async () => {
      try {
        setLoading(true);
        const data = await cocktailAPI.getTags();
        setTagsData(data);
      } catch (err) {
        setError('無法載入 Tags');
        console.error('Error fetching tags:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTags();
  }, []);

  // 切換維度展開/收合
  const toggleDimension = (dimension: string) => {
    setExpandedDimensions((prev) => ({
      ...prev,
      [dimension]: !prev[dimension],
    }));
  };

  // 切換 tag 選擇
  const toggleTag = (
    dimension: keyof TagFilterProps['selectedTags'],
    tag: string
  ) => {
    const currentTags = selectedTags[dimension];
    const newTags = currentTags.includes(tag)
      ? currentTags.filter((t) => t !== tag)
      : [...currentTags, tag];

    onTagChange(dimension, newTags);
  };

  // 計算已選擇的 tag 總數
  const totalSelectedTags = Object.values(selectedTags).reduce(
    (sum, tags) => sum + tags.length,
    0
  );

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !tagsData) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-red-500">{error || '無法載入 Tags'}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          篩選條件
          {totalSelectedTags > 0 && (
            <span className="ml-2 text-sm text-blue-600">
              ({totalSelectedTags} 個已選)
            </span>
          )}
        </h3>
        {totalSelectedTags > 0 && (
          <button
            onClick={onReset}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            清除全部
          </button>
        )}
      </div>

      {/* Tag Dimensions */}
      <div className="space-y-4">
        {(['base_spirits', 'flavors', 'ingredients', 'styles'] as const).map(
          (dimension) => {
            const tags = tagsData.tags[dimension];
            const counts = tagsData.counts[dimension];
            const isExpanded = expandedDimensions[dimension];
            const selectedCount = selectedTags[dimension].length;

            return (
              <div key={dimension} className="border-b border-gray-200 pb-4 last:border-b-0">
                {/* Dimension Header */}
                <button
                  onClick={() => toggleDimension(dimension)}
                  className="w-full flex items-center justify-between py-2 text-left hover:bg-gray-50 rounded transition-colors"
                >
                  <span className="font-medium text-gray-900">
                    {getDimensionLabel(dimension)}
                    {selectedCount > 0 && (
                      <span className="ml-2 text-sm text-blue-600">
                        ({selectedCount})
                      </span>
                    )}
                  </span>
                  <svg
                    className={`w-5 h-5 text-gray-500 transition-transform ${
                      isExpanded ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>

                {/* Tag List - 按子分類分組顯示 */}
                {isExpanded && (
                  <div className="mt-2 space-y-3">
                    {TAG_SUBCATEGORIES[dimension].map((subcategory) => (
                      <div key={subcategory.key}>
                        {/* 子分類標題 + 顏色指示 */}
                        <div className="flex items-center gap-2 mb-1.5">
                          <div className={`w-2 h-2 rounded-full ${subcategory.bgColor}`} />
                          <p className="text-xs font-medium text-gray-600">
                            {subcategory.label}
                          </p>
                        </div>

                        {/* 該子分類下的所有 tags */}
                        <div className="flex flex-wrap gap-1.5">
                          {subcategory.tags.map((tag) => (
                            <TagBadge
                              key={tag}
                              tag={tag}
                              dimension={dimension}
                              selected={selectedTags[dimension].includes(tag)}
                              onClick={() => toggleTag(dimension, tag)}
                            />
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          }
        )}
      </div>
    </div>
  );
};

export default TagFilter;
