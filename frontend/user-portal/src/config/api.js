// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://subscription-lhd6ksgtu-manishs-projects-e4683bf1.vercel.app/api';

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  LOGIN: `${API_BASE_URL}/auth/login`,
  REGISTER: `${API_BASE_URL}/auth/register`,
  REFRESH_TOKEN: `${API_BASE_URL}/auth/refresh`,
  
  // Users
  USERS: `${API_BASE_URL}/users`,
  USER_PROFILE: (id) => `${API_BASE_URL}/users/${id}`,
  
  // Products
  PRODUCTS: `${API_BASE_URL}/products`,
  PRODUCT_DETAIL: (id) => `${API_BASE_URL}/products/${id}`,
  
  // Subscriptions
  SUBSCRIPTIONS: `${API_BASE_URL}/subscriptions`,
  SUBSCRIPTION_DETAIL: (id) => `${API_BASE_URL}/subscriptions/${id}`,
  SUBSCRIPTION_PAUSE: (id) => `${API_BASE_URL}/subscriptions/${id}/pause`,
  SUBSCRIPTION_RESUME: (id) => `${API_BASE_URL}/subscriptions/${id}/resume`,
  SUBSCRIPTION_CANCEL: (id) => `${API_BASE_URL}/subscriptions/${id}/cancel`,
  
  // Payments
  PAYMENTS: `${API_BASE_URL}/payments`,
  CREATE_ORDER: `${API_BASE_URL}/payments/create-order`,
  VERIFY_PAYMENT: `${API_BASE_URL}/payments/verify`,
  
  // Health Check
  HEALTH: `${API_BASE_URL.replace('/api', '')}/health`,
};

// API Configuration
export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  TIMEOUT: 10000, // 10 seconds
  HEADERS: {
    'Content-Type': 'application/json',
  },
};

// Helper function to get auth headers
export const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// API request helper
export const apiRequest = async (url, options = {}) => {
  const config = {
    ...options,
    headers: {
      ...API_CONFIG.HEADERS,
      ...getAuthHeaders(),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

export default API_ENDPOINTS;
