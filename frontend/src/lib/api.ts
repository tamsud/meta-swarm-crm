import axios from 'axios';
import { tokenStorage } from './tokenStorage';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor - attach Authorization header when token is available.
 */
api.interceptors.request.use(
  (config) => {
    const token = tokenStorage.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - handle 401 Unauthorized errors.
 * Clears auth state and redirects to login, EXCEPT for the login endpoint itself
 * (login form should show inline error, not redirect).
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginEndpoint = error.config?.url?.includes('/auth/login');
    const isUnauthorized = error.response?.status === 401;

    // On 401 from any endpoint EXCEPT the login endpoint, clear auth and redirect
    if (isUnauthorized && !isLoginEndpoint) {
      tokenStorage.logout();
      // Use window.location for hard redirect to ensure clean state
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

export default api;
