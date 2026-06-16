/**
 * Module-level token storage for sharing between AuthContext and Axios interceptors.
 * This allows interceptors (which run outside React context) to access the current token.
 */

let accessToken: string | null = null;
let onLogout: (() => void) | null = null;

export const tokenStorage = {
  /**
   * Get the current access token.
   */
  getToken: (): string | null => accessToken,

  /**
   * Set the access token (called by AuthContext when user logs in).
   */
  setToken: (token: string | null): void => {
    accessToken = token;
  },

  /**
   * Register a logout callback (called by AuthContext on mount).
   * This callback should clear AuthContext state and redirect to login.
   */
  setLogoutCallback: (callback: () => void): void => {
    onLogout = callback;
  },

  /**
   * Clear the token and invoke the logout callback.
   * Called by the response interceptor on 401 errors.
   */
  logout: (): void => {
    accessToken = null;
    onLogout?.();
  },

  /**
   * Check if a token is currently set.
   */
  hasToken: (): boolean => accessToken !== null,
};
