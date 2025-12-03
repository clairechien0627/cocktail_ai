import { useState, useEffect } from 'react';
import { cocktailAPI } from '../services/api';
import { CategoryBadge } from '../utils/categoryIcons';
import {
  Search,
  Wine,
  X,
  ChevronLeft,
  ChevronRight,
  Star,
  Filter,
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
  const [selectedCocktail, setSelectedCocktail] = useState<Cocktail | null>(null);
  const [langZh, setLangZh] = useState(false); // false=英文, true=中文
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const baseAllergens: Allergen[] = selectedCocktail?.allergens || [];
  const zhAllergens: AllergenZh[] = selectedCocktail?.allergens_zh || [];

  const allergensToShow: Allergen[] = baseAllergens.map((a, idx) => ({
    ...a,
    item_zh: a.item_zh ?? zhAllergens[idx]?.item_zh,
    allergen_zh: a.allergen_zh ?? zhAllergens[idx]?.allergen_zh,
  }));


  useEffect(() => {
  if (selectedCocktail) {
    console.log('selectedCocktail zh fields:', {
      name_zh: selectedCocktail.name_zh,
      ingredients_zh: selectedCocktail.ingredients_zh,
      method_sections_zh: selectedCocktail.method_sections_zh,
      history_zh: selectedCocktail.history_zh,
      review_zh: selectedCocktail.review_zh,
      glass_zh: selectedCocktail.glass_zh,
    });
  }
}, [selectedCocktail]);


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
  }, [searchQuery, selectedCategory, selectedMoreCategory, page, filters]);

  const handleCocktailClick = (cocktail: Cocktail) => {
    console.log('CLICK cocktail =', cocktail);   // 點卡片時你會看到整筆資料
    setSelectedCocktail(cocktail);
  };


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

              {/* More Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">More Category</label>
                <select
                  value={selectedMoreCategory}
                  onChange={(e) => {
                    setSelectedMoreCategory(e.target.value);
                    setPage(1);
                  }}
                  className="input-field"
                >
                  <option value="all">全部</option>
                  {moreCategories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
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
                onClick={() => handleCocktailClick(cocktail)}
                className="card p-4 cursor-pointer hover:shadow-lg transition-shadow"
              >

                {/* 調酒名稱 */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3 flex-1">
                    <Wine className="w-8 h-8 text-primary-600 flex-shrink-0" />
                      <h3 className="font-bold text-lg text-gray-900 line-clamp-2">
                        {langZh
                          ? cocktail.name_zh
                            ? `${cocktail.name_zh} (${cocktail.name})`
                            : cocktail.name
                          : cocktail.name}
                      </h3>
                  </div>
                  {/* COTD 標記 */}
                  {cocktail.cotd?.text && (
                    <div className="flex-shrink-0">
                      <Sparkles className="w-5 h-5 text-yellow-500 fill-yellow-400" />
                    </div>
                  )}
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
                    {langZh && cocktail.more_categories_zh?.[0]
                      ? cocktail.more_categories_zh[0]
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

      {/* 調酒詳情模態框 */}
      {selectedCocktail && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedCocktail(null)}
        >
          <div
            className="bg-white/90 backdrop-blur-md rounded-3xl shadow-[0_20px_60px_rgba(15,23,42,0.25)] border border-white/70 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* 頂部：標題＋圖片 */}
            <div className="border-b border-white/70 bg-gradient-to-b from-white to-slate-50/60 px-8 pt-6 pb-4">
              <div className="flex flex-col items-center gap-3">
                <h2 className="text-[24px] font-semibold tracking-tight text-slate-900 text-center leading-snug">
                  {langZh
                    ? selectedCocktail.name_zh
                      ? `${selectedCocktail.name_zh} (${selectedCocktail.name})`
                      : selectedCocktail.name
                    : selectedCocktail.name}
                </h2>

                <button
                  onClick={() => setLangZh((v) => !v)}
                  className="inline-flex items-center gap-1 text-[11px] px-3 py-1 rounded-full border border-rose-300 text-rose-700 bg-white/90 hover:bg-rose-50 shadow-sm"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                  {langZh ? '顯示英文' : '顯示中文'}
                </button>

                {selectedCocktail.image_url && (
                  <div className="mt-2 flex justify-center">
                    <div className="rounded-2xl bg-slate-50 border border-slate-100 p-4">
                      <img
                        src={selectedCocktail.image_url}
                        alt={selectedCocktail.name}
                        className="w-[260px] h-[260px] object-contain"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                          const parent = e.currentTarget.parentElement;
                          if (parent && !parent.querySelector('.fallback-large')) {
                            const fallback = document.createElement('div');
                            fallback.className =
                              'fallback-large text-center text-slate-600';
                            fallback.innerHTML = `<svg class="w-16 h-16 text-slate-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg><p class="text-sm font-medium">${selectedCocktail.name}</p>`;
                            parent.appendChild(fallback);
                          }
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 內容區塊 */}
            <div className="px-8 py-6 space-y-8 bg-white/85">

              {/* COTD 徽章 */}
              {selectedCocktail.cotd?.text && (
                <div className="rounded-2xl bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 px-4 py-3 flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-amber-500 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-semibold text-amber-900 mb-1">
                      {selectedCocktail.cotd.title || 'Cocktail of the Day'}
                    </h4>
                    <p className="text-xs text-amber-800 leading-relaxed">
                      {selectedCocktail.cotd.text}
                    </p>
                  </div>
                </div>
              )}

              {/* 1. 評分與標籤 */}
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                {/* 左：評分 */}
                <div className="space-y-1">
                  {selectedCocktail.ratings?.professional != null && (
                    <div className="flex items-center gap-3">
                      <p className="text-[11px] text-gray-500 w-16 shrink-0">專業評分</p>
                      <div className="flex items-center gap-2">
                        {renderStars(selectedCocktail.ratings.professional)}
                        <span className="font-semibold text-base text-gray-900">
                          {selectedCocktail.ratings.professional.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  )}
                  {selectedCocktail.ratings?.public != null && (
                    <div className="flex items-center gap-3">
                      <p className="text-[11px] text-gray-500 w-16 shrink-0">公眾評分</p>
                      <div className="flex items-center gap-2">
                        {renderStars(selectedCocktail.ratings.public)}
                        <span className="font-semibold text-base text-gray-900">
                          {selectedCocktail.ratings.public.toFixed(1)}
                        </span>
                        {selectedCocktail.ratings.public_count && (
                          <span className="text-[11px] text-gray-500">
                            ({selectedCocktail.ratings.public_count} 則評價)
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* 右：類型 / 難度 / 標籤 */}
                <div className="flex flex-wrap gap-2 justify-start md:justify-end">
                  <span className="px-3 py-1 bg-rose-50 text-rose-700 rounded-full text-xs font-medium">
                    {selectedCocktail.category}
                  </span>
                  {selectedCocktail.difficulty && (
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        selectedCocktail.difficulty === 'easy'
                          ? 'bg-green-50 text-green-700'
                          : selectedCocktail.difficulty === 'medium'
                          ? 'bg-yellow-50 text-yellow-700'
                          : 'bg-red-50 text-red-700'
                      }`}
                    >
                      {selectedCocktail.difficulty === 'easy'
                        ? '簡單'
                        : selectedCocktail.difficulty === 'medium'
                        ? '中等'
                        : '困難'}
                    </span>
                  )}
                  {selectedCocktail.tags?.slice(0, 5).map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-slate-50 text-slate-700 rounded-full text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* 2. 風味檔案 */}
              {selectedCocktail.taste_profile && (
                <section>
                  <h3 className="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 mb-2">
                    風味檔案
                  </h3>
                  <div className="rounded-2xl bg-slate-50 px-4 py-3 space-y-3">
                    {selectedCocktail.taste_profile.strength !== undefined && (
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2 text-sm text-slate-800">
                            <Flame className="w-4 h-4 text-orange-500" />
                            酒精強度
                          </div>
                          <span className="text-sm font-semibold text-orange-600">
                            {selectedCocktail.taste_profile.strength}/10
                          </span>
                        </div>
                        <div className="h-2.5 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-orange-400 to-orange-600"
                            style={{
                              width: `${
                                (selectedCocktail.taste_profile.strength / 10) * 100
                              }%`,
                            }}
                          />
                        </div>
                      </div>
                    )}
                    {selectedCocktail.taste_profile.sweetness !== undefined && (
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2 text-sm text-slate-800">
                            <Droplet className="w-4 h-4 text-blue-500" />
                            甜度
                          </div>
                          <span className="text-sm font-semibold text-blue-600">
                            {selectedCocktail.taste_profile.sweetness}/10
                          </span>
                        </div>
                        <div className="h-2.5 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-blue-400 to-blue-600"
                            style={{
                              width: `${
                                (selectedCocktail.taste_profile.sweetness / 10) * 100
                              }%`,
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* 3. 材料 */}
              <section>
                <h3 className="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 mb-2">
                  材料
                </h3>
                {selectedCocktail.ingredients_detail?.length ? (
                  <div className="space-y-2">
                    {selectedCocktail.ingredients_detail.map((detail: any, i: number) => {
                      const zhName =
                        langZh &&
                        selectedCocktail.ingredients_zh &&
                        selectedCocktail.ingredients_zh[i]
                          ? selectedCocktail.ingredients_zh[i]
                          : null;
                      return (
                        <div
                          key={i}
                          className="relative flex justify-between gap-4 rounded-2xl bg-white/95 px-4 py-2 border border-slate-100 shadow-sm"
                        >
                          <div className="text-sm text-rose-700 font-medium w-24 shrink-0">
                            {detail.amount || ''}
                          </div>
                          <div className="flex-1 text-sm">
                            {langZh && zhName && (
                              <div className="text-slate-900">{zhName}</div>
                            )}
                            <div
                              className={`text-[11px] text-slate-500 ${
                                langZh && zhName ? 'mt-0.5' : ''
                              }`}
                            >
                              {detail.ingredient}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">無材料資訊</p>
                )}
              </section>

              {/* 4. 製作方法 */}
              <section>
                <h3 className="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 mb-2">
                  製作方法
                </h3>
                {selectedCocktail.method_sections &&
                selectedCocktail.method_sections.length > 0 ? (
                  <div className="space-y-3">
                    {selectedCocktail.method_sections.map((section: any, i: number) => {
                      const zhSectionsClean =
                        selectedCocktail.method_sections_zh?.filter(
                          (s: any) => s.steps_zh && s.steps_zh.length > 0
                        ) ?? [];
                      const zhSection = zhSectionsClean[i];

                      const hasZhSteps =
                        !!(zhSection?.steps_zh && zhSection.steps_zh.length > 0);
                      const hasEnSteps =
                        !!(section.steps && section.steps.length > 0);
                      const hasSteps = hasZhSteps || hasEnSteps;
                      if (!hasSteps) return null;

                      return (
                        <div
                          key={i}
                          className="rounded-2xl px-4 py-3 bg-rose-50/80 border border-rose-100"
                        >
                          <div className="mb-2">
                            {langZh && zhSection?.title_zh && (
                              <p className="text-sm font-semibold text-rose-900">
                                {zhSection.title_zh}
                              </p>
                            )}
                            {section.title && (
                              <p className="text-[11px] text-rose-700">
                                {section.title}
                              </p>
                            )}
                          </div>

                          {hasZhSteps ? (
                            <div className="space-y-2">
                              {(zhSection?.steps_zh ?? []).map(
                                (stepZh: string, j: number) => {
                                  const stepEn =
                                    Array.isArray(section.steps) && section.steps[j]
                                      ? section.steps[j]
                                      : null;
                                  return (
                                    <div
                                      key={j}
                                      className="rounded-xl bg-white/90 px-3 py-2 text-sm shadow-[0_0_0_1px_rgba(248,113,113,0.12)]"
                                    >
                                      {langZh && (
                                        <div className="text-slate-900 mb-0.5">
                                          {stepZh}
                                        </div>
                                      )}
                                      {stepEn && (
                                        <div className="text-[11px] text-slate-500">
                                          {stepEn}
                                        </div>
                                      )}
                                    </div>
                                  );
                                }
                              )}
                            </div>
                          ) : (
                            hasEnSteps && (
                              <div className="space-y-2">
                                {(section.steps ?? []).map(
                                  (step: string, j: number) => (
                                    <div
                                      key={j}
                                      className="rounded-xl bg-white/90 px-3 py-2 text-sm shadow-[0_0_0_1px_rgba(148,163,184,0.25)]"
                                    >
                                      {step}
                                    </div>
                                  )
                                )}
                              </div>
                            )
                          )}
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">無製作步驟資訊</p>
                )}
              </section>

              {/* 5. 營養與酒精資訊 */}
              {(selectedCocktail.nutrition?.calories ||
                (selectedCocktail.alcohol_metrics &&
                  (selectedCocktail.alcohol_metrics.abv != null ||
                    selectedCocktail.alcohol_metrics.standard_drinks != null ||
                    selectedCocktail.alcohol_metrics.proof != null))) && (
                <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedCocktail.nutrition?.calories && (
                    <div className="rounded-2xl bg-blue-50 px-4 py-3">
                      <h4 className="text-sm font-semibold text-blue-800 mb-2">
                        營養資訊
                      </h4>
                      <div className="flex items-center justify-between">
                        <span className="text-[11px] text-blue-700">卡路里</span>
                        <span className="text-xl font-bold text-blue-900">
                          {selectedCocktail.nutrition.calories} cal
                        </span>
                      </div>
                    </div>
                  )}
                  {selectedCocktail.alcohol_metrics &&
                    (selectedCocktail.alcohol_metrics.abv != null ||
                      selectedCocktail.alcohol_metrics.standard_drinks != null ||
                      selectedCocktail.alcohol_metrics.proof != null) && (
                      <div className="rounded-2xl bg-orange-50 px-4 py-3">
                        <h4 className="text-sm font-semibold text-orange-800 mb-2">
                          酒精指標
                        </h4>
                        <div className="space-y-1 text-[11px]">
                          {selectedCocktail.alcohol_metrics.abv != null && (
                            <div className="flex justify-between">
                              <span className="text-orange-700">酒精濃度</span>
                              <span className="font-semibold text-orange-900">
                                {selectedCocktail.alcohol_metrics.abv}%
                              </span>
                            </div>
                          )}
                          {selectedCocktail.alcohol_metrics.standard_drinks !=
                            null && (
                            <div className="flex justify-between">
                              <span className="text-orange-700">標準飲酒量</span>
                              <span className="font-semibold text-orange-900">
                                {
                                  selectedCocktail.alcohol_metrics.standard_drinks
                                }
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
                </section>
              )}

              {/* 6. 建議杯具 */}
              <section>
                <h3 className="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 mb-2">
                  建議杯具
                </h3>
                <div className="rounded-2xl bg-white px-4 py-3 border border-slate-100 shadow-sm text-sm flex items-center gap-3">
                  <Wine className="w-5 h-5 text-slate-400" />
                  <div>
                    {langZh && selectedCocktail.glass_zh && (
                      <div className="text-slate-900">{selectedCocktail.glass_zh}</div>
                    )}
                    <div className="text-[11px] text-slate-500">
                      {selectedCocktail.glass || '無杯具資訊'}
                    </div>
                  </div>
                </div>
              </section>

              {/* 7. 歷史與故事 */}
              {(selectedCocktail.history_zh &&
                selectedCocktail.history_zh.length > 0) ||
              (selectedCocktail.history &&
                (Array.isArray(selectedCocktail.history)
                  ? selectedCocktail.history.length > 0
                  : selectedCocktail.history.paragraphs?.length > 0)) ? (
                <section>
                  <h3 className="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 mb-2">
                    歷史與故事
                  </h3>
                  <div className="space-y-2 text-sm leading-relaxed">
                    {(langZh &&
                    selectedCocktail.history_zh &&
                    selectedCocktail.history_zh.length > 0
                      ? selectedCocktail.history_zh
                      : Array.isArray(selectedCocktail.history)
                      ? selectedCocktail.history
                      : selectedCocktail.history.paragraphs || []
                    ).map((paragraph: string, i: number) => (
                      <div
                        key={i}
                        className="rounded-2xl bg-white px-4 py-3 border border-slate-100 shadow-sm"
                      >
                        {paragraph}
                      </div>
                    ))}
                  </div>
                </section>
              ) : null}

              {/* 8. 專業評論 */}
              {(langZh &&
                selectedCocktail.review_zh &&
                selectedCocktail.review_zh.length > 0) ||
              (selectedCocktail.review && selectedCocktail.review.length > 0) ? (
                <section>
                  <h3 className="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 mb-2">
                    專業評論
                  </h3>
                  <div className="space-y-2 text-sm leading-relaxed">
                    {(langZh &&
                    selectedCocktail.review_zh &&
                    selectedCocktail.review_zh.length > 0
                      ? selectedCocktail.review_zh
                      : selectedCocktail.review || []
                    ).map((comment: string, i: number) => (
                      <div
                        key={i}
                        className="rounded-2xl bg-slate-50 px-4 py-3 border border-slate-100 shadow-sm italic text-slate-800"
                      >
                        “{comment}”
                      </div>
                    ))}
                  </div>
                </section>
              ) : null}

              {/* 9. 相關變化版本 */}
              {selectedCocktail.variants && selectedCocktail.variants.length > 0 && (
                <section>
                  <h3 className="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 mb-3 flex items-center gap-2">
                    <LinkIcon className="w-4 h-4 text-cyan-600" />
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
                        <span className="text-cyan-800 font-medium">
                          {variant.name}
                        </span>
                        <LinkIcon className="w-3 h-3 text-cyan-600 ml-auto" />
                      </a>
                    ))}
                  </div>
                </section>
              )}

              {/* 10. 過敏原警告 */}
              {allergensToShow.length > 0 && (
                <section>
                  <h3 className="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 mb-3 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    過敏原警告
                  </h3>
                  <div className="bg-red-50 border border-red-200 rounded-2xl p-4">
                    <ul className="space-y-2 text-sm">
                      {allergensToShow.map((allergen, i) => (
                        <li
                          key={i}
                          className="flex items-start gap-2 text-red-800"
                        >
                          <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                          <div>
                            <div className="font-semibold">
                              {langZh && (allergen.item_zh || allergen.item) ? (
                                <>
                                  {allergen.item_zh || allergen.item}
                                  <span className="text-xs text-red-700 ml-1">
                                    ({allergen.item})
                                  </span>
                                </>
                              ) : (
                                allergen.item
                              )}
                            </div>
                            <div className="text-[11px] text-red-700">
                              {langZh && allergen.allergen_zh ? (
                                <>
                                  {allergen.allergen_zh}
                                  <span className="ml-1">({allergen.allergen})</span>
                                </>
                              ) : (
                                allergen.allergen
                              )}
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </section>
              )}


              {/* More Categories */}
              {selectedCocktail.more_categories &&
                selectedCocktail.more_categories.length > 0 && (
                  <section className="pt-4 border-t border-gray-200">
                    <h4 className="text-[11px] font-semibold tracking-[0.18em] uppercase text-slate-500 mb-3">
                      More Categories
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedCocktail.more_categories.map((category) => (
                        <CategoryBadge key={category} categoryName={category} />
                      ))}
                    </div>
                  </section>
                )}

              {/* 來源連結 */}
              {selectedCocktail.detail_url && (
                <section className="pt-4 border-t border-gray-200">
                  <a
                    href={selectedCocktail.detail_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium text-sm"
                  >
                    <LinkIcon className="w-4 h-4" />
                    查看原始配方
                  </a>
                </section>
              )}
            </div>
          </div>
        </div>
      )}


    </div>
  );
};

export default CocktailsPage;
