// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  LOGIN: `${API_BASE_URL}/auth/login`,
  REGISTER: `${API_BASE_URL}/auth/register`,
  
  // Users
  USERS: `${API_BASE_URL}/users`,
  USER_PROFILE: (id) => `${API_BASE_URL}/users/${id}`,
  
  // Products
  PRODUCTS: `${API_BASE_URL}/products`,
  PRODUCT_DETAIL: (id) => `${API_BASE_URL}/products/${id}`,
  
  // Subscriptions
  SUBSCRIPTIONS: `${API_BASE_URL}/subscriptions`,
  SUBSCRIPTION_DETAIL: (id) => `${API_BASE_URL}/subscriptions/${id}`,
  
  // Payments
  PAYMENTS: `${API_BASE_URL}/payments`,
  
  // Admin
  ADMIN_DASHBOARD: `${API_BASE_URL}/admin/dashboard`,
  ADMIN_USERS: `${API_BASE_URL}/admin/users`,
  ADMIN_ANALYTICS: `${API_BASE_URL}/admin/analytics`,
  
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
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

export default API_ENDPOINTS;
