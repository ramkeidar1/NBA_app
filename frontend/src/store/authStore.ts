import { create } from 'zustand';
import * as authService from '../services/authService';
import type { User } from '../types/auth';

type AuthStatus = 'loading' | 'authed' | 'guest';

interface AuthState {
  accessToken: string | null;
  user: User | null;
  status: AuthStatus;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  bootstrap: () => Promise<void>;
  setAccessToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  status: 'loading',

  login: async (email, password) => {
    const { access_token } = await authService.login({ email, password });
    set({ accessToken: access_token, status: 'authed' });
  },

  logout: async () => {
    await authService.logout().catch(() => undefined);
    set({ accessToken: null, user: null, status: 'guest' });
  },

  bootstrap: async () => {
    try {
      const { access_token } = await authService.refresh();
      set({ accessToken: access_token, status: 'authed' });
    } catch {
      set({ accessToken: null, user: null, status: 'guest' });
    }
  },

  setAccessToken: (token) => set({ accessToken: token }),
}));
