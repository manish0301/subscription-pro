import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('admin_token'));

  useEffect(() => {
    if (token) {
      // Verify token and get admin data
      fetchAdminData();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchAdminData = async () => {
    try {
      // In a real implementation, you would verify the token with the backend
      // For now, we'll simulate admin data based on the token
      const adminData = JSON.parse(localStorage.getItem('admin_user') || 'null');
      if (adminData) {
        setAdmin(adminData);
      }
    } catch (error) {
      console.error('Error fetching admin data:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok && data.user.user_role === 'admin') {
        setAdmin(data.user);
        setToken(data.token);
        localStorage.setItem('admin_token', data.token);
        localStorage.setItem('admin_user', JSON.stringify(data.user));
        return { success: true };
      } else if (response.ok && data.user.user_role !== 'admin') {
        return { success: false, error: 'Access denied. Admin privileges required.' };
      } else {
        return { success: false, error: data.error };
      }
    } catch (error) {
      return { success: false, error: 'Network error. Please try again.' };
    }
  };

  const logout = () => {
    setAdmin(null);
    setToken(null);
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
  };

  const updateAdmin = (updatedAdmin) => {
    setAdmin(updatedAdmin);
    localStorage.setItem('admin_user', JSON.stringify(updatedAdmin));
  };

  const value = {
    admin,
    token,
    loading,
    login,
    logout,
    updateAdmin,
    isAuthenticated: !!admin,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

