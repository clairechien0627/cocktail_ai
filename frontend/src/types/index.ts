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
  more_categories?: string[];  // Difford's Guide 更多分類

  // 元數據
  scraped_at?: string;
  created_at?: string;
}

// 詳細配方材料
export interface IngredientDetail {
  amount: string;
  ingredient: string;
  ingredient_url?: string;
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
}

// COTD (Cocktail of the Day)
export interface COTD {
  title?: string | null;
  text?: string | null;
  links?: any[];
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
