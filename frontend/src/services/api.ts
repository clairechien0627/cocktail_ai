import axios from 'axios';
import type {
  AuthResponse,
  User,
  ChatResponse,
  Cocktail,
  CocktailsResponse,
  Conversation,
  UserPreferences,
  TagsResponse,
  DrinkingRecord,
  DrinkingRecordsResponse,
  CreateRecordData,
  UpdateRecordData,
  DrinkingStats,
  UserPreferencesAnalysis,
  RecommendationsResponse,
  PersonalitiesResponse,
  Personality,
} from '../types';

// API 基礎 URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// 建立 Axios 實例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器：自動加入 JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 回應攔截器：處理 401 未授權錯誤
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 過期或無效，清除並重新導向到登入頁
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==================== 認證 API ====================

export const authAPI = {
  // 註冊
  register: async (username: string, email: string, password: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  },

  // 登入
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  // 取得當前用戶資訊
  getCurrentUser: async (): Promise<{ user: User }> => {
    const response = await api.get<{ user: User }>('/api/auth/me');
    return response.data;
  },

  // 更新用戶偏好
  updatePreferences: async (preferences: UserPreferences): Promise<{ message: string }> => {
    const response = await api.put<{ message: string }>('/api/auth/preferences', {
      preferences,
    });
    return response.data;
  },
};

// ==================== 聊天 API ====================

export const chatAPI = {
  // 發送訊息
  sendMessage: async (message: string, conversationId?: string, personality?: string): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/api/chat/message', {
      message,
      conversation_id: conversationId,
      personality,  // 新增：性格參數
    });
    return response.data;
  },

  // 建立新對話
  createConversation: async (): Promise<{ conversation_id: string; message: string }> => {
    const response = await api.post<{ conversation_id: string; message: string }>(
      '/api/chat/conversations'
    );
    return response.data;
  },

  // 取得所有對話
  getConversations: async (): Promise<{ conversations: Conversation[] }> => {
    const response = await api.get<{ conversations: Conversation[] }>('/api/chat/conversations');
    return response.data;
  },

  // 取得特定對話
  getConversation: async (conversationId: string): Promise<{ conversation: Conversation }> => {
    const response = await api.get<{ conversation: Conversation }>(
      `/api/chat/conversations/${conversationId}`
    );
    return response.data;
  },

  // 刪除對話
  deleteConversation: async (conversationId: string): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(
      `/api/chat/conversations/${conversationId}`
    );
    return response.data;
  },
};

// ==================== 調酒 API ====================

export const cocktailAPI = {
  // 取得所有調酒（分頁）
  getAll: async (page: number = 1, limit: number = 20): Promise<CocktailsResponse> => {
    const response = await api.get<CocktailsResponse>('/api/cocktails/', {
      params: { page, limit },
    });
    return response.data;
  },

  // 取得特定調酒
  getById: async (cocktailId: string): Promise<{ cocktail: Cocktail }> => {
    const response = await api.get<{ cocktail: Cocktail }>(`/api/cocktails/${cocktailId}`);
    return response.data;
  },

  // 搜尋調酒
  search: async (query: string): Promise<{ cocktails: Cocktail[]; count: number }> => {
    const response = await api.get<{ cocktails: Cocktail[]; count: number }>(
      '/api/cocktails/search',
      {
        params: { q: query },
      }
    );
    return response.data;
  },

  // 根據分類取得調酒
  getByCategory: async (
    category: string
  ): Promise<{ cocktails: Cocktail[]; category: string; count: number }> => {
    const response = await api.get<{ cocktails: Cocktail[]; category: string; count: number }>(
      `/api/cocktails/category/${category}`
    );
    return response.data;
  },

  // 取得所有分類
  getCategories: async (): Promise<{ categories: string[] }> => {
    const response = await api.get<{ categories: string[] }>('/api/cocktails/categories');
    return response.data;
  },

  // 取得所有 More Categories
  getMoreCategories: async (): Promise<{ more_categories: string[] }> => {
    const response = await api.get<{ more_categories: string[] }>('/api/cocktails/more-categories');
    return response.data;
  },

  // 取得所有 Tags（分類顯示）
  getTags: async (): Promise<TagsResponse> => {
    const response = await api.get<TagsResponse>('/api/cocktails/tags');
    return response.data;
  },

  // 隨機取得一個調酒
  getRandom: async (): Promise<{ cocktail: Cocktail }> => {
    const response = await api.get<{ cocktail: Cocktail }>('/api/cocktails/random');
    return response.data;
  },
};

// ==================== 飲用紀錄 API ====================

export const recordsAPI = {
  // 建立飲用紀錄
  create: async (data: CreateRecordData): Promise<{ message: string; record_id: string }> => {
    const response = await api.post<{ message: string; record_id: string }>('/api/records/', data);
    return response.data;
  },

  // 取得我的飲用紀錄（分頁、篩選）
  getAll: async (params?: {
    page?: number;
    limit?: number;
    preference?: string;
    start_date?: string;
    end_date?: string;
    mood_tags?: string;
    sort_by?: string;
  }): Promise<DrinkingRecordsResponse> => {
    const response = await api.get<DrinkingRecordsResponse>('/api/records/', { params });
    return response.data;
  },

  // 取得特定紀錄
  getById: async (recordId: string): Promise<DrinkingRecord> => {
    const response = await api.get<DrinkingRecord>(`/api/records/${recordId}`);
    return response.data;
  },

  // 更新紀錄
  update: async (recordId: string, data: UpdateRecordData): Promise<{ message: string }> => {
    const response = await api.put<{ message: string }>(`/api/records/${recordId}`, data);
    return response.data;
  },

  // 刪除紀錄
  delete: async (recordId: string): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/api/records/${recordId}`);
    return response.data;
  },

  // 取得我的統計資訊
  getStats: async (): Promise<DrinkingStats> => {
    const response = await api.get<DrinkingStats>('/api/records/stats');
    return response.data;
  },

  // 取得我的偏好分析
  getPreferences: async (): Promise<UserPreferencesAnalysis> => {
    const response = await api.get<UserPreferencesAnalysis>('/api/records/preferences');
    return response.data;
  },

  // 取得個人化推薦
  getRecommendations: async (
    limit?: number,
    excludeIds?: string[],
    explorationMode?: 'balanced' | 'adventurous'
  ): Promise<RecommendationsResponse> => {
    const params: any = { limit };

    if (excludeIds && excludeIds.length > 0) {
      params.exclude_ids = excludeIds.join(',');
    }

    if (explorationMode) {
      params.exploration_mode = explorationMode;
    }

    const response = await api.get<RecommendationsResponse>('/api/records/recommendations', {
      params,
    });
    return response.data;
  },

  // 檢查是否喝過某調酒
  checkIfDrunk: async (cocktailId: string): Promise<{ has_drunk: boolean }> => {
    const response = await api.get<{ has_drunk: boolean }>(
      `/api/records/cocktail/${cocktailId}/check`
    );
    return response.data;
  },

  // 取得對特定調酒的所有紀錄
  getCocktailRecords: async (
    cocktailId: string
  ): Promise<{ records: DrinkingRecord[]; count: number }> => {
    const response = await api.get<{ records: DrinkingRecord[]; count: number }>(
      `/api/records/cocktail/${cocktailId}`
    );
    return response.data;
  },

  // 取得預設心情標籤選項
  getMoodTags: async (): Promise<{ mood_tags: string[] }> => {
    const response = await api.get<{ mood_tags: string[] }>('/api/records/mood-tags');
    return response.data;
  },
};

// ==================== 性格 API（新增）====================

export const personalitiesAPI = {
  // 取得所有性格列表
  getPersonalities: async (): Promise<PersonalitiesResponse> => {
    const response = await api.get<PersonalitiesResponse>('/api/personalities/list');
    return response.data;
  },

  // 取得特定性格詳情
  getPersonality: async (personalityId: string): Promise<Personality> => {
    const response = await api.get<Personality>(`/api/personalities/${personalityId}`);
    return response.data;
  },

  // 創建自訂性格
  createPersonality: async (data: {
    name: string;
    description: string;
    icon: string;
    prompt: {
      tone: string;
      style: string;
      greeting: string;
      example_responses?: string[];
      custom_rules?: string[];
    };
    is_public?: boolean;
  }): Promise<{ message: string; personality_id: string }> => {
    const response = await api.post<{ message: string; personality_id: string }>(
      '/api/personalities/create',
      data
    );
    return response.data;
  },

  // 更新自訂性格
  updatePersonality: async (
    personalityId: string,
    data: Partial<{
      name: string;
      description: string;
      icon: string;
      prompt: any;
      is_public: boolean;
    }>
  ): Promise<{ message: string }> => {
    const response = await api.put<{ message: string }>(
      `/api/personalities/${personalityId}`,
      data
    );
    return response.data;
  },

  // 刪除自訂性格
  deletePersonality: async (personalityId: string): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(
      `/api/personalities/${personalityId}`
    );
    return response.data;
  },
};

export default api;
