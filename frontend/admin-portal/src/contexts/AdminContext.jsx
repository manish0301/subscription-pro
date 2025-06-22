import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const AdminContext = createContext();

export const useAdmin = () => {
  const context = useContext(AdminContext);
  if (!context) {
    throw new Error('useAdmin must be used within an AdminProvider');
  }
  return context;
};

export const AdminProvider = ({ children }) => {
  const { admin, token } = useAuth();
  const [dashboardStats, setDashboardStats] = useState({});
  const [users, setUsers] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [products, setProducts] = useState([]);
  const [payments, setPayments] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (admin && token) {
      fetchDashboardStats();
    }
  }, [admin, token]);

  const fetchDashboardStats = async () => {
    if (!token) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/admin/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardStats(data);
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async (page = 1, search = '', role = '') => {
    if (!token) return { success: false, error: 'Not authenticated' };

    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '20',
        ...(search && { search }),
        ...(role && { role })
      });

      const response = await fetch(`http://localhost:5000/api/admin/users?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
        return { success: true, data };
      } else {
        const error = await response.json();
        return { success: false, error: error.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  const fetchSubscriptions = async (page = 1, status = '', userEmail = '') => {
    if (!token) return { success: false, error: 'Not authenticated' };

    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '20',
        ...(status && { status }),
        ...(userEmail && { user_email: userEmail })
      });

      const response = await fetch(`http://localhost:5000/api/admin/subscriptions?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSubscriptions(data.subscriptions);
        return { success: true, data };
      } else {
        const error = await response.json();
        return { success: false, error: error.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  const modifySubscription = async (subscriptionId, updateData) => {
    if (!token) return { success: false, error: 'Not authenticated' };

    try {
      const response = await fetch(`http://localhost:5000/api/admin/subscriptions/${subscriptionId}/modify`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Admin-User-ID': admin.user_id
        },
        body: JSON.stringify(updateData),
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, subscription: data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const extendSubscription = async (subscriptionId, extendDays) => {
    if (!token) return { success: false, error: 'Not authenticated' };

    try {
      const response = await fetch(`http://localhost:5000/api/admin/subscriptions/${subscriptionId}/extend`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Admin-User-ID': admin.user_id
        },
        body: JSON.stringify({ extend_days: extendDays }),
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, subscription: data };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const fetchAuditLogs = async (page = 1, actionType = '', entityType = '', userId = '') => {
    if (!token) return { success: false, error: 'Not authenticated' };

    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '50',
        ...(actionType && { action_type: actionType }),
        ...(entityType && { entity_type: entityType }),
        ...(userId && { user_id: userId })
      });

      const response = await fetch(`http://localhost:5000/api/admin/audit-logs?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAuditLogs(data.logs);
        return { success: true, data };
      } else {
        const error = await response.json();
        return { success: false, error: error.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  const fetchRevenueReport = async (startDate, endDate) => {
    if (!token) return { success: false, error: 'Not authenticated' };

    try {
      const params = new URLSearchParams({
        ...(startDate && { start_date: startDate }),
        ...(endDate && { end_date: endDate })
      });

      const response = await fetch(`http://localhost:5000/api/admin/reports/revenue?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        return { success: true, data };
      } else {
        const error = await response.json();
        return { success: false, error: error.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const value = {
    dashboardStats,
    users,
    subscriptions,
    products,
    payments,
    auditLogs,
    loading,
    fetchDashboardStats,
    fetchUsers,
    fetchSubscriptions,
    modifySubscription,
    extendSubscription,
    fetchAuditLogs,
    fetchRevenueReport,
  };

  return (
    <AdminContext.Provider value={value}>
      {children}
    </AdminContext.Provider>
  );
};

