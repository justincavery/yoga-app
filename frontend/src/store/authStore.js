import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set, get) => ({
      // Auth state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Set user and tokens after successful login/register
      setAuth: (user, tokens) => {
        set({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          isAuthenticated: true,
          error: null,
        });
      },

      // Update access token (for refresh flow)
      setAccessToken: (accessToken) => {
        set({ accessToken });
      },

      // Set loading state
      setLoading: (isLoading) => {
        set({ isLoading });
      },

      // Set error state
      setError: (error) => {
        set({ error, isLoading: false });
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },

      // Logout - clear all auth state
      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        });
      },

      // Check if token is expired (basic check)
      isTokenExpired: () => {
        const { accessToken } = get();
        if (!accessToken) return true;

        try {
          // JWT tokens have 3 parts separated by dots
          const payload = JSON.parse(atob(accessToken.split('.')[1]));
          const expirationTime = payload.exp * 1000; // Convert to milliseconds
          return Date.now() >= expirationTime;
        } catch (error) {
          console.error('Error parsing token:', error);
          return true;
        }
      },
    }),
    {
      name: 'auth-storage', // Key in localStorage
      partialize: (state) => ({
        // Only persist these fields
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
