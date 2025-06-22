import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { apiRequest, API_ENDPOINTS } from '../config/api.js';

const SubscriptionContext = createContext();

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
};

export const SubscriptionProvider = ({ children }) => {
  const { user, token } = useAuth();
  const [subscriptions, setSubscriptions] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user && token) {
      fetchUserSubscriptions();
    }
  }, [user, token]);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchUserSubscriptions = async () => {
    if (!user || !token) return;

    setLoading(true);
    try {
      const data = await apiRequest(`${API_ENDPOINTS.SUBSCRIPTIONS}?user_id=${user.user_id}`);
      setSubscriptions(data.subscriptions || []);
    } catch (error) {
      console.error('Error fetching subscriptions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const data = await apiRequest(`${API_ENDPOINTS.PRODUCTS}?subscription_only=true`);
      setProducts(data.products || []);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const createSubscription = async (subscriptionData) => {
    if (!token) return { success: false, error: 'Not authenticated' };

    try {
      const response = await fetch('http://localhost:5000/api/subscriptions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(subscriptionData),
      });

      const data = await response.json();

      if (response.ok) {
        await fetchUserSubscriptions(); // Refresh subscriptions
        return { success: true, subscription: data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const updateSubscription = async (subscriptionId, updateData) => {
    if (!token) return { success: false, error: 'Not authenticated' };

    try {
      const response = await fetch(`http://localhost:5000/api/subscriptions/${subscriptionId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      const data = await response.json();

      if (response.ok) {
        await fetchUserSubscriptions(); // Refresh subscriptions
        return { success: true, subscription: data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const pauseSubscription = async (subscriptionId) => {
    if (!token) return { success: false, error: 'Not authenticated' };

    try {
      const response = await fetch(`http://localhost:5000/api/subscriptions/${subscriptionId}/pause`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        await fetchUserSubscriptions(); // Refresh subscriptions
        return { success: true, subscription: data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const resumeSubscription = async (subscriptionId) => {
    if (!token) return { success: false, error: 'Not authenticated' };

    try {
      const response = await fetch(`http://localhost:5000/api/subscriptions/${subscriptionId}/resume`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        await fetchUserSubscriptions(); // Refresh subscriptions
        return { success: true, subscription: data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const cancelSubscription = async (subscriptionId) => {
    if (!token) return { success: false, error: 'Not authenticated' };

    try {
      const response = await fetch(`http://localhost:5000/api/subscriptions/${subscriptionId}/cancel`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        await fetchUserSubscriptions(); // Refresh subscriptions
        return { success: true, subscription: data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const skipNextDelivery = async (subscriptionId) => {
    if (!token) return { success: false, error: 'Not authenticated' };

    try {
      const response = await fetch(`http://localhost:5000/api/subscriptions/${subscriptionId}/skip`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        await fetchUserSubscriptions(); // Refresh subscriptions
        return { success: true, subscription: data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const value = {
    subscriptions,
    products,
    loading,
    createSubscription,
    updateSubscription,
    pauseSubscription,
    resumeSubscription,
    cancelSubscription,
    skipNextDelivery,
    fetchUserSubscriptions,
    fetchProducts,
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
};

