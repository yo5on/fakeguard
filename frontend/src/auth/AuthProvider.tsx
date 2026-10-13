import { ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import { ApiError, api, setAuthToken, setUnauthorizedHandler } from '../services/api';
import { AuthContext, AuthState, StoredSession, readSession, writeSession } from './authContext';

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthState['status']>('loading');
  const [authRequired, setAuthRequired] = useState(true);
  const [authConfigured, setAuthConfigured] = useState(true);
  const [session, setSession] = useState<StoredSession | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  const applySession = useCallback((next: StoredSession | null) => {
    setAuthToken(next?.token ?? null);
    writeSession(next);
    setSession(next);
  }, []);

  const logout = useCallback(() => applySession(null), [applySession]);

  // Any request rejected with 401 means the token expired or was revoked.
  useEffect(() => {
    setUnauthorizedHandler(logout);
    return () => setUnauthorizedHandler(null);
  }, [logout]);

  useEffect(() => {
    let cancelled = false;
    const stored = readSession();
    setAuthToken(stored?.token ?? null);

    (async () => {
      try {
        const serverStatus = await api.authStatus();
        if (cancelled) return;
        setAuthRequired(serverStatus.auth_required);
        setAuthConfigured(serverStatus.auth_configured);

        if (serverStatus.auth_required && stored) {
          try {
            await api.me();
            if (!cancelled) applySession(stored);
          } catch {
            if (!cancelled) applySession(null);
          }
        }
        if (!cancelled) {
          setError(null);
          setStatus('ready');
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Unable to reach the server');
        setStatus('error');
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [applySession, attempt]);

  // Sign out when the token's lifetime ends.
  useEffect(() => {
    if (!session) return;
    const remaining = session.expiresAt * 1000 - Date.now();
    const timer = setTimeout(logout, Math.max(0, remaining));
    return () => clearTimeout(timer);
  }, [session, logout]);

  const login = useCallback(
    async (username: string, password: string) => {
      try {
        const result = await api.login(username, password);
        applySession({ token: result.access_token, username: result.username, expiresAt: result.expires_at });
      } catch (err) {
        if (err instanceof ApiError && err.status === 503) setAuthConfigured(false);
        throw err;
      }
    },
    [applySession],
  );

  const retry = useCallback(() => {
    setStatus('loading');
    setAttempt((n) => n + 1);
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      status,
      authRequired,
      authConfigured,
      username: authRequired ? session?.username ?? null : 'anonymous',
      error,
      login,
      logout,
      retry,
    }),
    [status, authRequired, authConfigured, session, error, login, logout, retry],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
