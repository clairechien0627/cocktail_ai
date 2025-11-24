import axios from 'axios';
import type {
  AuthResponse,
  User,
  ChatResponse,
  Cocktail,
  CocktailsResponse,
  Conversation,
  UserPreferences,
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
  sendMessage: async (message: string, conversationId?: string): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/api/chat/message', {
      message,
      conversation_id: conversationId,
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

  // 隨機取得一個調酒
  getRandom: async (): Promise<{ cocktail: Cocktail }> => {
    const response = await api.get<{ cocktail: Cocktail }>('/api/cocktails/random');
    return response.data;
  },
};

export default api;
