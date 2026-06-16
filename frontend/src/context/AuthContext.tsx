/* eslint-disable react-refresh/only-export-components */
import { createContext, useState, useCallback, useEffect } from 'react';
import type { ReactNode } from 'react';
import api from '../lib/api';
import { tokenStorage } from '../lib/tokenStorage';

interface User {
  id: number;
  email: string;
  display_name: string | null;
  role_id: number;
  is_active: boolean;
}

interface Role {
  id: number;
  name: string;
  description: string | null;
  is_system: boolean;
}

interface AuthState {
  token: string | null;
  user: User | null;
  role: Role | null;
  permissions: string[];
}

export interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasPermission: (code: string) => boolean;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    token: null,
    user: null,
    role: null,
    permissions: [],
  });

  // Clear auth state (used by both manual logout and interceptor-triggered logout)
  const clearAuthState = useCallback(() => {
    setState({ token: null, user: null, role: null, permissions: [] });
    tokenStorage.setToken(null);
  }, []);

  // Register the logout callback with tokenStorage so interceptors can trigger logout
  useEffect(() => {
    tokenStorage.setLogoutCallback(clearAuthState);
  }, [clearAuthState]);

  const login = useCallback(async (email: string, password: string) => {
    // POST /auth/login
    const loginRes = await api.post('/auth/login', { email, password });
    const token = loginRes.data.data.access_token;

    // Store token in tokenStorage for interceptor access
    tokenStorage.setToken(token);

    // GET /auth/me (interceptor will now attach the token automatically)
    const meRes = await api.get('/auth/me');
    const { user, role, permissions } = meRes.data.data;

    setState({ token, user, role, permissions });
  }, []);

  const logout = useCallback(() => {
    clearAuthState();
  }, [clearAuthState]);

  const hasPermission = useCallback(
    (code: string) => {
      return state.permissions.includes(code);
    },
    [state.permissions]
  );

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        logout,
        hasPermission,
        isAuthenticated: !!state.token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
