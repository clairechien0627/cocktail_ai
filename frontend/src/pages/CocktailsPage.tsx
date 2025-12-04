import { useState, useEffect } from 'react';
import { cocktailAPI, recordsAPI } from '../services/api';
import { CategoryBadge } from '../utils/categoryIcons';
import TagFilter from '../components/Cocktail/TagFilter';
import { TagBadge } from '../utils/tagIcons';
import { RecordForm } from '../components/Record';
import {
  Search,
  Wine,
  X,
  ChevronLeft,
  ChevronRight,
  Star,
  SlidersHorizontal,
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
} from 'lucide-react';
import type { Cocktail } from '../types';

const CocktailsPage = () => {
  const [cocktails, setCocktails] = useState<Cocktail[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [categories, setCategories] = useState<string[]>([]);
  const [moreCategories, setMoreCategories] = useState<string[]>([]);
  const [selectedMoreCategory, setSelectedMoreCategory] = useState<string>('all');
  const [selectedTags, setSelectedTags] = useState<{
    base_spirits: string[];
    flavors: string[];
    ingredients: string[];
    styles: string[];
  }>({
    base_spirits: [],
    flavors: [],
    ingredients: [],
    styles: [],
  });
  const [selectedCocktail, setSelectedCocktail] = useState<Cocktail | null>(null);
  const [langZh, setLangZh] = useState(false); // false=英文, true=中文
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  // 飲用紀錄相關狀態
  const [showRecordForm, setShowRecordForm] = useState(false);
  const [hasDrunk, setHasDrunk] = useState<boolean>(false);

  // 篩選條件
  const [filters, setFilters] = useState({
    minRating: 0,
    maxRating: 5,
    minStrength: 0,
    maxStrength: 10,
    minSweetness: 0,
    maxSweetness: 10,
    maxCalories: 500,
    difficulty: 'all' as 'all' | 'easy' | 'medium' | 'hard',
    sortBy: 'name' as 'name' | 'rating_desc' | 'rating_asc' | 'strength_desc' | 'calories_asc' | 'popular',
  });

  // 載入分類和 More Categories
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await cocktailAPI.getCategories();
        setCategories(response.categories.filter((c) => c));
      } catch (error) {
        console.error('載入分類失敗:', error);
      }
    };

    const loadMoreCategories = async () => {
      try {
        const response = await cocktailAPI.getMoreCategories();
        setMoreCategories(response.more_categories.filter((c) => c));
      } catch (error) {
        console.error('載入 More Categories 失敗:', error);
      }
    };

    loadCategories();
    loadMoreCategories();
  }, []);

  // 載入調酒
  useEffect(() => {
    const loadCocktails = async () => {
      setLoading(true);
      try {
        if (searchQuery) {
          // 搜尋模式
          const response = await cocktailAPI.search(searchQuery);
          setCocktails(response.cocktails);
          setTotalPages(1);
        } else {
          // 使用 filter API
          const params = new URLSearchParams({
            page: page.toString(),
            limit: '20',
            sort_by: filters.sortBy,
          });

          if (selectedCategory !== 'all') {
            params.append('category', selectedCategory);
          }
          if (selectedMoreCategory !== 'all') {
            params.append('more_category', selectedMoreCategory);
          }
          // Tag 篩選
          if (selectedTags.base_spirits.length > 0) {
            params.append('base_spirit', selectedTags.base_spirits[0]); // 基酒單選
          }
          if (selectedTags.flavors.length > 0) {
            params.append('flavor', selectedTags.flavors.join(','));
          }
          if (selectedTags.ingredients.length > 0) {
            params.append('ingredient_tag', selectedTags.ingredients[0]); // 材料單選
          }
          if (selectedTags.styles.length > 0) {
            params.append('style', selectedTags.styles.join(','));
          }
          if (filters.minRating > 0) {
            params.append('min_rating', filters.minRating.toString());
          }
          if (filters.maxRating < 5) {
            params.append('max_rating', filters.maxRating.toString());
          }
          if (filters.minStrength > 0) {
            params.append('min_strength', filters.minStrength.toString());
          }
          if (filters.maxStrength < 10) {
            params.append('max_strength', filters.maxStrength.toString());
          }
          if (filters.minSweetness > 0) {
            params.append('min_sweetness', filters.minSweetness.toString());
          }
          if (filters.maxSweetness < 10) {
            params.append('max_sweetness', filters.maxSweetness.toString());
          }
          if (filters.maxCalories < 500) {
            params.append('max_calories', filters.maxCalories.toString());
          }
          if (filters.difficulty !== 'all') {
            params.append('difficulty', filters.difficulty);
          }

          const response = await fetch(
            `${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/cocktails/filter?${params}`,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`,
              },
            }
          );

          const data = await response.json();
          setCocktails(data.cocktails || []);
          setTotalPages(Math.ceil((data.count || 0) / 20));
        }
      } catch (error) {
        console.error('載入調酒失敗:', error);
        setCocktails([]);
      } finally {
        setLoading(false);
      }
    };

    loadCocktails();
  }, [searchQuery, selectedCategory, selectedMoreCategory, selectedTags, page, filters]);

  // 檢查是否喝過當前選中的調酒
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

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    setSearchQuery('');
    setPage(1);
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

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <Wine className="w-8 h-8 text-primary-600" />
          調酒瀏覽
        </h1>
        <p className="text-gray-600">探索超過 6,000 種專業調酒配方</p>
      </div>

      {/* 搜尋和篩選 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <form onSubmit={handleSearch} className="mb-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜尋調酒名稱或材料..."
                className="w-full pl-10 input-field"
              />
            </div>
            <button type="submit" className="btn-primary px-6">
              搜尋
            </button>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="btn-secondary px-6 flex items-center gap-2"
            >
              <SlidersHorizontal className="w-5 h-5" />
              篩選
            </button>
          </div>
        </form>

        {/* 進階篩選面板 */}
        {showFilters && (
          <div className="border-t pt-4 mt-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* 評分篩選 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  評分 ({filters.minRating} - {filters.maxRating} 星)
                </label>
                <div className="flex gap-2">
                  <input
                    type="range"
                    min="0"
                    max="5"
                    step="0.5"
                    value={filters.minRating}
                    onChange={(e) =>
                      setFilters({ ...filters, minRating: parseFloat(e.target.value) })
                    }
                    className="flex-1"
                  />
                  <input
                    type="range"
                    min="0"
                    max="5"
                    step="0.5"
                    value={filters.maxRating}
                    onChange={(e) =>
                      setFilters({ ...filters, maxRating: parseFloat(e.target.value) })
                    }
                    className="flex-1"
                  />
                </div>
              </div>

              {/* 酒精強度 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  酒精強度 ({filters.minStrength} - {filters.maxStrength})
                </label>
                <div className="flex gap-2">
                  <input
                    type="range"
                    min="0"
                    max="10"
                    value={filters.minStrength}
                    onChange={(e) =>
                      setFilters({ ...filters, minStrength: parseInt(e.target.value) })
                    }
                    className="flex-1"
                  />
                  <input
                    type="range"
                    min="0"
                    max="10"
                    value={filters.maxStrength}
                    onChange={(e) =>
                      setFilters({ ...filters, maxStrength: parseInt(e.target.value) })
                    }
                    className="flex-1"
                  />
                </div>
              </div>

              {/* 甜度 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  甜度 ({filters.minSweetness} - {filters.maxSweetness})
                </label>
                <div className="flex gap-2">
                  <input
                    type="range"
                    min="0"
                    max="10"
                    value={filters.minSweetness}
                    onChange={(e) =>
                      setFilters({ ...filters, minSweetness: parseInt(e.target.value) })
                    }
                    className="flex-1"
                  />
                  <input
                    type="range"
                    min="0"
                    max="10"
                    value={filters.maxSweetness}
                    onChange={(e) =>
                      setFilters({ ...filters, maxSweetness: parseInt(e.target.value) })
                    }
                    className="flex-1"
                  />
                </div>
              </div>

              {/* 卡路里 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  最大卡路里 ({filters.maxCalories})
                </label>
                <input
                  type="range"
                  min="0"
                  max="500"
                  step="10"
                  value={filters.maxCalories}
                  onChange={(e) =>
                    setFilters({ ...filters, maxCalories: parseInt(e.target.value) })
                  }
                  className="w-full"
                />
              </div>

              {/* 難度 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">難度</label>
                <select
                  value={filters.difficulty}
                  onChange={(e) =>
                    setFilters({
                      ...filters,
                      difficulty: e.target.value as typeof filters.difficulty,
                    })
                  }
                  className="input-field"
                >
                  <option value="all">全部</option>
                  <option value="easy">簡單</option>
                  <option value="medium">中等</option>
                  <option value="hard">困難</option>
                </select>
              </div>

              {/* 排序 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">排序</label>
                <select
                  value={filters.sortBy}
                  onChange={(e) =>
                    setFilters({
                      ...filters,
                      sortBy: e.target.value as typeof filters.sortBy,
                    })
                  }
                  className="input-field"
                >
                  <option value="name">名稱</option>
                  <option value="rating_desc">評分（高→低）</option>
                  <option value="rating_asc">評分（低→高）</option>
                  <option value="strength_desc">酒精強度（高→低）</option>
                  <option value="calories_asc">卡路里（低→高）</option>
                  <option value="popular">最受歡迎</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* 分類篩選 */}
        <div className="flex flex-wrap gap-2 mt-4">
          <button
            onClick={() => handleCategoryChange('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedCategory === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            全部
          </button>
          {categories.slice(0, 10).map((category) => (
            <button
              key={category}
              onClick={() => handleCategoryChange(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Tag 篩選器 */}
      <div className="mb-6">
        <TagFilter
          selectedTags={selectedTags}
          onTagChange={(dimension, tags) => {
            setSelectedTags((prev) => ({
              ...prev,
              [dimension]: tags,
            }));
            setPage(1);
          }}
          onReset={() => {
            setSelectedTags({
              base_spirits: [],
              flavors: [],
              ingredients: [],
              styles: [],
            });
            setPage(1);
          }}
        />
      </div>

      {/* 載入中 */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-xl text-gray-600">載入中...</div>
        </div>
      )}

      {/* 列表語言切換按鈕 */}
      <div className="flex justify-end mb-4">
        <button
          onClick={() => setLangZh((v) => !v)}
          className="inline-flex items-center gap-1 text-xs px-3 py-1 rounded-full border border-rose-300 text-rose-700 bg-white hover:bg-rose-50 shadow-sm"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
          {langZh ? '顯示英文' : '顯示中文'}
        </button>
      </div>

      {/* 調酒網格 */}
      {!loading && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-6">
            {cocktails.map((cocktail) => (
              <div
                key={cocktail._id}
                onClick={() => setSelectedCocktail(cocktail)}
                className="card p-4 cursor-pointer hover:shadow-lg transition-shadow"
              >
                {/* 調酒名稱 */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3 flex-1">
                    <Wine className="w-8 h-8 text-primary-600 flex-shrink-0" />
                    <h3 className="font-bold text-lg text-gray-900 line-clamp-2">
                      {langZh && cocktail.name_zh
                        ? cocktail.name_zh
                        : cocktail.name}
                    </h3>
                  </div>
                </div>

                {/* 評分 */}
                {cocktail.ratings?.professional != null && (
                  <div className="mb-2">
                    {renderStars(cocktail.ratings.professional)}
                    <span className="text-xs text-gray-500 ml-2">
                      {cocktail.ratings.professional.toFixed(1)}
                      {cocktail.ratings.public_count && ` (${cocktail.ratings.public_count})`}
                    </span>
                  </div>
                )}

                {/* 分類與難度 */}
                <div className="flex items-center gap-2 mb-3">
                <span className="text-xs px-2 py-1 bg-primary-100 text-primary-700 rounded">
                  {langZh && cocktail.category_zh
                    ? cocktail.category_zh
                    : cocktail.category}
                </span>
                  {cocktail.difficulty && (
                    <span
                      className={`text-xs px-2 py-1 rounded ${
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

                {/* 風味指標 */}
                {cocktail.taste_profile && (
                  <div className="space-y-2 mb-3">
                    {cocktail.taste_profile.strength !== undefined && (
                      <div className="flex items-center gap-2">
                        <Flame className="w-4 h-4 text-orange-500" />
                        <div className="flex-1">
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-orange-500"
                              style={{ width: `${(cocktail.taste_profile.strength / 10) * 100}%` }}
                            />
                          </div>
                        </div>
                        <span className="text-xs text-gray-600">
                          {cocktail.taste_profile.strength}/10
                        </span>
                      </div>
                    )}
                    {cocktail.taste_profile.sweetness !== undefined && (
                      <div className="flex items-center gap-2">
                        <Droplet className="w-4 h-4 text-blue-500" />
                        <div className="flex-1">
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-500"
                              style={{
                                width: `${(cocktail.taste_profile.sweetness / 10) * 100}%`,
                              }}
                            />
                          </div>
                        </div>
                        <span className="text-xs text-gray-600">
                          {cocktail.taste_profile.sweetness}/10
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* 營養與材料 */}
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{cocktail.ingredients.length} 種材料</span>
                  {cocktail.nutrition?.calories && (
                    <span>{cocktail.nutrition.calories} cal</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {cocktails.length === 0 && (
            <div className="text-center py-12 text-gray-500">找不到符合條件的調酒</div>
          )}

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

      {/* 調酒詳情模態框 - 將在下一步擴充 */}
      {selectedCocktail && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedCocktail(null)}
        >
          <div
            className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* 詳細內容將在下一個文件中實作 */}
            <div className="sticky top-0 bg-primary-600 text-white px-6 py-4 flex items-center justify-between z-10">
              <div className="flex items-center gap-3 flex-1">
                <h2 className="text-2xl font-bold">
                  {langZh
                    ? selectedCocktail.name_zh
                      ? `${selectedCocktail.name_zh} (${selectedCocktail.name})`
                      : selectedCocktail.name
                    : selectedCocktail.name}
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
                  onClick={() => setLangZh((v) => !v)}
                  className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg bg-white bg-opacity-20 hover:bg-opacity-30 transition-colors"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-white" />
                  {langZh ? '英' : '中'}
                </button>
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

            {/* 調酒大圖 */}
            {selectedCocktail.image_url && (
              <div className="relative w-full h-96 bg-white overflow-hidden">

                <img
                  src={selectedCocktail.image_url}
                  alt={selectedCocktail.name}
                  className="w-full h-full object-contain"
                  onError={(e) => {
                    // 圖片載入失敗時顯示佔位符
                    e.currentTarget.style.display = 'none';
                    const parent = e.currentTarget.parentElement;
                    if (parent && !parent.querySelector('.fallback-large')) {
                      parent.className = 'relative w-full h-96 bg-gradient-to-br from-primary-200 to-primary-300 overflow-hidden flex items-center justify-center';
                      const fallback = document.createElement('div');
                      fallback.className = 'fallback-large text-center';
                      fallback.innerHTML = `<svg class="w-32 h-32 text-primary-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg><p class="text-primary-700 text-lg font-medium">${selectedCocktail.name}</p>`;
                      parent.appendChild(fallback);
                    }
                  }}
                />
              </div>
            )}

            <div className="p-6 space-y-6">
              {/* COTD 徵章 */}
              {selectedCocktail.cotd?.text && (
                <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-400 rounded-lg p-4 shadow-md">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-5 h-5 text-yellow-600 fill-yellow-400" />
                    <h4 className="font-bold text-yellow-900">
                      {selectedCocktail.cotd.title || 'Cocktail of the Day'}
                    </h4>
                    <Sparkles className="w-5 h-5 text-yellow-600 fill-yellow-400" />
                  </div>
                  <p className="text-yellow-800 text-sm">{selectedCocktail.cotd.text}</p>
                </div>
              )}

              {/* 1. 評分與基本資訊 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  {selectedCocktail.ratings && (
                    <div className="space-y-2">
                      {selectedCocktail.ratings.professional != null && (
                        <div>
                          <p className="text-sm text-gray-600 mb-1">專業評分</p>
                          <div className="flex items-center gap-2">
                            {renderStars(selectedCocktail.ratings.professional)}
                            <span className="font-bold text-lg text-gray-900">
                              {selectedCocktail.ratings.professional.toFixed(1)}
                            </span>
                          </div>
                        </div>
                      )}
                      {selectedCocktail.ratings.public != null && (
                        <div>
                          <p className="text-sm text-gray-600 mb-1">公眾評分</p>
                          <div className="flex items-center gap-2">
                            {renderStars(selectedCocktail.ratings.public)}
                            <span className="font-bold text-lg text-gray-900">
                              {selectedCocktail.ratings.public.toFixed(1)}
                            </span>
                            {selectedCocktail.ratings.public_count && (
                              <span className="text-sm text-gray-500">
                                ({selectedCocktail.ratings.public_count} 則評價)
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
                  {langZh && selectedCocktail.category_zh
                    ? selectedCocktail.category_zh
                    : selectedCocktail.category}
                </span>
                  {selectedCocktail.difficulty && (
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        selectedCocktail.difficulty === 'easy'
                          ? 'bg-green-100 text-green-700'
                          : selectedCocktail.difficulty === 'medium'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {selectedCocktail.difficulty === 'easy'
                        ? '簡單'
                        : selectedCocktail.difficulty === 'medium'
                        ? '中等'
                        : '困難'}
                    </span>
                  )}
                </div>
              </div>

              {/* 2. 風味檔案 */}
              {selectedCocktail.taste_profile && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-primary-600" />
                    風味檔案
                  </h3>
                  <div className="space-y-4">
                    {selectedCocktail.taste_profile.strength !== undefined && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Flame className="w-5 h-5 text-orange-500" />
                            <span className="font-medium">酒精強度</span>
                          </div>
                          <span className="text-lg font-bold text-orange-600">
                            {selectedCocktail.taste_profile.strength}/10
                          </span>
                        </div>
                        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-orange-400 to-orange-600"
                            style={{
                              width: `${(selectedCocktail.taste_profile.strength / 10) * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                    )}
                    {selectedCocktail.taste_profile.sweetness !== undefined && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Droplet className="w-5 h-5 text-blue-500" />
                            <span className="font-medium">甜度</span>
                          </div>
                          <span className="text-lg font-bold text-blue-600">
                            {selectedCocktail.taste_profile.sweetness}/10
                          </span>
                        </div>
                        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-blue-400 to-blue-600"
                            style={{
                              width: `${(selectedCocktail.taste_profile.sweetness / 10) * 100}%`,
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
                    {selectedCocktail.ingredients_detail &&
                    selectedCocktail.ingredients_detail.length > 0 ? (
                      selectedCocktail.ingredients_detail.map((detail, i) => {
                        const zhName = langZh && selectedCocktail.ingredients_zh?.[i]
                          ? selectedCocktail.ingredients_zh[i]
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
                    ) : selectedCocktail.ingredients && selectedCocktail.ingredients.length > 0 ? (
                      selectedCocktail.ingredients.map((ing, i) => (
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
              {selectedCocktail.method_sections && (
                <div>
                  <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                    <ChefHat className="w-5 h-5 text-purple-600" />
                    製作方法
                  </h3>
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    {(() => {
                      // 根據語言選擇使用哪個數據源
                      const methodSections = langZh && selectedCocktail.method_sections_zh?.length
                        ? selectedCocktail.method_sections_zh
                        : selectedCocktail.method_sections;

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
              {(selectedCocktail.nutrition?.calories || selectedCocktail.alcohol_metrics && (
                selectedCocktail.alcohol_metrics.abv != null ||
                selectedCocktail.alcohol_metrics.standard_drinks != null ||
                selectedCocktail.alcohol_metrics.proof != null ||
                selectedCocktail.alcohol_metrics.pure_alcohol_grams != null
               )) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedCocktail.nutrition?.calories && (
                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-800 mb-2">營養資訊</h4>
                      <div className="flex items-center justify-between">
                        <span className="text-blue-700">卡路里</span>
                        <span className="text-2xl font-bold text-blue-900">
                          {selectedCocktail.nutrition.calories} cal
                        </span>
                      </div>
                    </div>
                  )}
                  {selectedCocktail.alcohol_metrics && (
                    selectedCocktail.alcohol_metrics.abv != null ||
                    selectedCocktail.alcohol_metrics.standard_drinks != null ||
                    selectedCocktail.alcohol_metrics.proof != null ||
                    selectedCocktail.alcohol_metrics.pure_alcohol_grams != null
                  ) && (
                    <div className="bg-orange-50 rounded-lg p-4">
                      <h4 className="font-semibold text-orange-800 mb-2">酒精指標</h4>
                      <div className="space-y-1 text-sm">
                        {selectedCocktail.alcohol_metrics.abv != null && (
                          <div className="flex justify-between">
                            <span className="text-orange-700">酒精濃度</span>
                            <span className="font-semibold text-orange-900">
                              {selectedCocktail.alcohol_metrics.abv}%
                            </span>
                          </div>
                        )}
                        {selectedCocktail.alcohol_metrics.standard_drinks != null && (
                          <div className="flex justify-between">
                            <span className="text-orange-700">標準飲酒量</span>
                            <span className="font-semibold text-orange-900">
                              {selectedCocktail.alcohol_metrics.standard_drinks}
                            </span>
                          </div>
                        )}
                        {selectedCocktail.alcohol_metrics.proof != null && (
                          <div className="flex justify-between">
                            <span className="text-orange-700">酒精度數</span>
                            <span className="font-semibold text-orange-900">
                              {selectedCocktail.alcohol_metrics.proof} proof
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* 6. 杯具資訊 */}
              {selectedCocktail.glass && (
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <GlassWater className="w-5 h-5 text-purple-600" />
                    <h4 className="font-semibold text-purple-800">建議杯具</h4>
                  </div>
                  <p className="text-purple-700">
                    {langZh && selectedCocktail.glass_zh
                      ? `${selectedCocktail.glass_zh} (${selectedCocktail.glass})`
                      : selectedCocktail.glass}
                  </p>
                </div>
              )}

              {/* 7. 歷史故事 */}
              {selectedCocktail.history && selectedCocktail.history.length > 0 && (
                <div>
                  <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-amber-600" />
                    歷史與故事
                  </h3>
                  <div className="bg-amber-50 rounded-lg p-4 space-y-2">
                    {(langZh && selectedCocktail.history_zh?.length
                      ? selectedCocktail.history_zh
                      : selectedCocktail.history
                    ).map((paragraph, i) => (
                      <p key={i} className="text-gray-700 leading-relaxed">
                        {paragraph}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {/* 8. 專業評論 */}
              {selectedCocktail.review && selectedCocktail.review.length > 0 && (
                <div>
                  <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-indigo-600" />
                    專業評論
                  </h3>
                  <div className="bg-indigo-50 rounded-lg p-4 space-y-2">
                    {(langZh && selectedCocktail.review_zh?.length
                      ? selectedCocktail.review_zh
                      : selectedCocktail.review
                    ).map((comment, i) => (
                      <p key={i} className="text-gray-700 italic leading-relaxed">
                        "{comment}"
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {/* 9. 相關變化版本 */}
              {selectedCocktail.variants && selectedCocktail.variants.length > 0 && (
                <div>
                  <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                    <LinkIcon className="w-5 h-5 text-cyan-600" />
                    相關變化版本
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {selectedCocktail.variants.map((variant, i) => (
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
              {selectedCocktail.allergens && selectedCocktail.allergens.length > 0 && (
                <div>
                  <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                    過敏原警告
                  </h3>
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <ul className="space-y-2">
                      {selectedCocktail.allergens.map((allergen, i) => (
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
              {selectedCocktail.tags_categorized && (
                <div className="pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedCocktail.tags_categorized.base_spirits?.map((tag) => (
                      <TagBadge key={tag} tag={tag} dimension="base_spirits" showColoredIcons={true} />
                    ))}
                    {selectedCocktail.tags_categorized.flavors?.map((tag) => (
                      <TagBadge key={tag} tag={tag} dimension="flavors" showColoredIcons={true} />
                    ))}
                    {selectedCocktail.tags_categorized.ingredients?.map((tag) => (
                      <TagBadge key={tag} tag={tag} dimension="ingredients" showColoredIcons={true} />
                    ))}
                    {selectedCocktail.tags_categorized.styles?.map((tag) => (
                      <TagBadge key={tag} tag={tag} dimension="styles" showColoredIcons={true} />
                    ))}
                  </div>
                </div>
              )}

              {/* More Categories */}
              {selectedCocktail.more_categories && selectedCocktail.more_categories.length > 0 && (
                <div className="pt-4 border-t border-gray-200">
                  <h4 className="text-sm font-semibold text-gray-700 mb-3">More Categories</h4>
                  <div className="flex flex-wrap gap-2">
                    {(langZh && selectedCocktail.more_categories_zh?.length
                      ? selectedCocktail.more_categories_zh
                      : selectedCocktail.more_categories
                    ).map((category, i) => (
                      <CategoryBadge key={i} categoryName={category} />
                    ))}
                  </div>
                </div>
              )}

              {/* 來源連結 */}
              {selectedCocktail.detail_url && (
                <div className="pt-4 border-t">
                  <a
                    href={selectedCocktail.detail_url}
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
      )}

      {/* 飲用紀錄表單 */}
      {showRecordForm && selectedCocktail && (
        <RecordForm
          cocktail={selectedCocktail}
          onClose={() => setShowRecordForm(false)}
          onSuccess={() => {
            setShowRecordForm(false);
            // 重新檢查是否已喝過
            if (selectedCocktail) {
              recordsAPI.checkIfDrunk(selectedCocktail._id)
                .then(response => setHasDrunk(response.has_drunk))
                .catch(() => setHasDrunk(false));
            }
          }}
        />
      )}
    </div>
  );
};

export default CocktailsPage;
