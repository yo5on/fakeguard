import { createContext, useContext } from 'react';

export interface AuthState {
  /** 'loading' until the server's auth status (and any stored session) is checked. */
  status: 'loading' | 'ready' | 'error';
  /** False when the backend runs with AUTH_DISABLED=true. */
  authRequired: boolean;
  /** False when the backend has authentication neither configured nor disabled. */
  authConfigured: boolean;
  username: string | null;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  retry: () => void;
}

export const AuthContext = createContext<AuthState | null>(null);

export function useAuth(): AuthState {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used inside <AuthProvider>');
  return value;
}

export interface StoredSession {
  token: string;
  username: string;
  expiresAt: number; // seconds since epoch
}

export const SESSION_KEY = 'fakeguard.session';

/**
 * The token lives in sessionStorage: it survives reloads but not closing the
 * tab, and it is never sent automatically like a cookie (so no CSRF exposure).
 * Storage access is wrapped because it can throw in private modes.
 */
export function readSession(now = Date.now()): StoredSession | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const session = JSON.parse(raw) as StoredSession;
    if (!session.token || !session.username || session.expiresAt * 1000 <= now) {
      sessionStorage.removeItem(SESSION_KEY);
      return null;
    }
    return session;
  } catch {
    return null;
  }
}

export function writeSession(session: StoredSession | null): void {
  try {
    if (session) sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
    else sessionStorage.removeItem(SESSION_KEY);
  } catch {
    // Storage unavailable: the session simply won't survive a reload.
  }
}
