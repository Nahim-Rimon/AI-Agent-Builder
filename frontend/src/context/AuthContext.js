import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { API_BASE } from '../config';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      setIsAuthenticated(true);
      // Set default authorization header for axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      const res = await axios.post(`${API_BASE}/auth/login`, formData);
      const newToken = res.data.access_token;
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setIsAuthenticated(true);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Login failed'
      };
    }
  };

  const register = async (username, email, password) => {
    try {
      await axios.post(`${API_BASE}/auth/register`, { username, email, password });
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Registration failed'
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsAuthenticated(false);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{
      isAuthenticated,
      loading,
      token,
      login,
      register,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
};

