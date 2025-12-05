// 用戶類型
export interface User {
  id: string;
  username: string;
  email: string;
  preferences: UserPreferences;
}

export interface UserPreferences {
  favorite_spirits: string[];
  skill_level: 'beginner' | 'intermediate' | 'expert';
  personality?: string;  // 酒保性格 ID（新增）
}

// 性格類型（新增）
export interface Personality {
  personality_id: string;
  name: string;
  description: string;
  icon: string;
  type: 'system' | 'custom';
  is_public?: boolean;
}

export interface PersonalitiesResponse {
  system: Personality[];
  custom: Personality[];
}

// 調酒類型（完整 Difford's Guide schema）
export interface Cocktail {
  _id: string;
  name: string;
  slug?: string;
  category: string;
  original_url?: string;
  detail_url?: string;
  image_url?: string;

  // 材料資訊
  ingredients: string[];  // 簡單列表
  ingredients_detail?: IngredientDetail[];  // 詳細配方

  // 製作方法
  method: string[];  // 簡單步驟列表
  method_sections?: MethodSection[];  // 結構化步驟
  garnish: string[];

  // 評分系統
  ratings?: Ratings;

  // 風味檔案
  taste_profile?: TasteProfile;

  // 營養資訊
  nutrition?: Nutrition;

  // 酒精指標
  alcohol_metrics?: AlcoholMetrics;

  // 杯具資訊
  glass?: string;

  // 歷史與故事
  history?: string[];

  // 專業評論
  review?: string[];

  // 相關變化版本
  variants?: Variant[];

  // 過敏原資訊
  allergens?: Allergen[];

  // COTD (Cocktail of the Day) 資訊
  cotd?: COTD;

  // 分類與標籤
  difficulty?: 'easy' | 'medium' | 'hard';
  tags?: string[];
  tags_categorized?: TagsCategorized;  // 分類化的 tags
  more_categories?: string[];  // Difford's Guide 更多分類

  // 推薦系統欄位
  recommendation_reason?: string;  // 推薦理由
  recommendation_type?: 'safe' | 'adventure' | 'hidden_gem' | 'popular' | 'newbie' | 'general';  // 推薦類型
  similarity_score?: number;  // 相似度分數

  // ===== 中文欄位（翻譯產生） =====
  name_zh?: string;
  ingredients_zh?: string[];
  review_zh?: string[];
  history_zh?: string[];
  method_sections_zh?: {
    title_zh?: string;
    steps_zh?: string[];
  }[];
  more_categories_zh?: string[];
  glass_zh?: string;
  category_zh?:string;

  // 元數據
  scraped_at?: string;
  created_at?: string;
}


// 詳細配方材料
export interface IngredientDetail {
  amount: string;
  ingredient: string;
  ingredient_url?: string;
  ingredient_zh?: string;   // 新增：材料名稱的中文
}

// 製作步驟區塊
export interface MethodSection {
  title: string;
  steps: string[];
}

// 評分
export interface Ratings {
  professional?: number;  // 0-5
  public?: number;  // 0-5
  public_count?: number;
}

// 風味檔案
export interface TasteProfile {
  strength?: number;  // 0-10 (酒精強度)
  sweetness?: number;  // 0-10 (甜度)
}

// 營養資訊
export interface Nutrition {
  calories?: number;
}

// 酒精指標
export interface AlcoholMetrics {
  abv?: number;  // 酒精濃度百分比
  standard_drinks?: number;  // 標準飲酒量
  proof?: number;  // 酒精度數（美式）
  pure_alcohol_grams?: number;  // 純酒精克數
}

// 調酒變化版本
export interface Variant {
  name: string;
  url: string;
}

// 過敏原
export interface Allergen {
  item: string;
  allergen: string;
  allergen_url?: string; 

  item_zh?: string;
  allergen_zh?: string;
}

export interface AllergenZh {
  item_zh?: string;
  allergen_zh?: string;
  allergen_url?: string;
}




// COTD (Cocktail of the Day)
export interface COTD {
  title?: string | null;
  text?: string | null;
  links?: any[];
}

// Tag 系統
export interface TagsCategorized {
  base_spirits: string[];
  flavors: string[];
  ingredients: string[];
  styles: string[];
}

export interface TagsResponse {
  tags: TagsCategorized;
  counts: {
    base_spirits: { [key: string]: number };
    flavors: { [key: string]: number };
    ingredients: { [key: string]: number };
    styles: { [key: string]: number };
  };
}

// 對話類型
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sentiment?: number;
  timestamp?: string;
}

export interface Conversation {
  _id: string;
  user_id: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

// API 回應類型
export interface AuthResponse {
  access_token: string;
  user?: User;
  message?: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  sentiment: number;
  warning_issued?: boolean;
}

export interface CocktailsResponse {
  cocktails: Cocktail[];
  page?: number;
  limit?: number;
  total?: number;
  total_pages?: number;
}

// 飲用紀錄類型
export type PreferenceLevel = 'loved' | 'liked' | 'neutral' | 'disliked';

export interface CocktailSnapshot {
  name: string;
  image_url?: string;
  category: string;
  taste_profile?: TasteProfile;
  tags_categorized: TagsCategorized;
}

export interface DrinkingRecord {
  _id: string;
  user_id: string;
  cocktail_id: string;
  cocktail_snapshot: CocktailSnapshot;
  preference: PreferenceLevel;
  notes: string;
  drunk_at: string;  // ISO datetime string
  location?: string;
  mood_tags: string[];
  created_at: string;
  updated_at: string;
}

export interface DrinkingRecordsResponse {
  records: DrinkingRecord[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface CreateRecordData {
  cocktail_id: string;
  preference: PreferenceLevel;
  notes: string;
  drunk_at?: string | Date;
  location?: string;
  mood_tags?: string[];
}

export interface UpdateRecordData {
  preference?: PreferenceLevel;
  notes?: string;
  drunk_at?: string | Date;
  location?: string;
  mood_tags?: string[];
}

// 飲用統計類型
export interface PreferenceDistribution {
  loved: number;
  liked: number;
  neutral: number;
  disliked: number;
}

export interface CocktailSummary {
  _id: string;
  cocktail_name: string;
  cocktail_image?: string;
  count?: number;  // for most drunk
  preference?: PreferenceLevel;  // for favorites
  last_drunk?: string;
}

export interface DrinkingStats {
  total_drinks: number;
  preference_distribution: PreferenceDistribution;
  most_drunk_cocktails: CocktailSummary[];
  favorite_cocktails: CocktailSummary[];
}

// 偏好分析類型
export interface TagPreference {
  tag: string;
  count: number;
}

export interface TasteRange {
  min: number;
  max: number;
  avg: number;
}

export interface TimeDistribution {
  _id: number;  // hour of day (0-23)
  count: number;
}

export interface MoodDistribution {
  _id: string;  // mood tag name
  count: number;
}

export interface UserPreferencesAnalysis {
  favorite_tags: {
    base_spirits: TagPreference[];
    flavors: TagPreference[];
    styles: TagPreference[];
  };
  taste_range: {
    strength: TasteRange;
    sweetness: TasteRange;
  };
  time_distribution: TimeDistribution[];
  mood_distribution: MoodDistribution[];
}

export interface RecommendationsResponse {
  recommendations: Cocktail[];
  count: number;
}
