import { ReactNode } from 'react';
import { vi } from 'vitest';
import { AuthContext, AuthState } from '../auth/authContext';

export function authState(overrides: Partial<AuthState> = {}): AuthState {
  return {
    status: 'ready',
    authRequired: true,
    authConfigured: true,
    username: 'reviewer',
    error: null,
    login: vi.fn().mockResolvedValue(undefined),
    logout: vi.fn(),
    retry: vi.fn(),
    ...overrides,
  };
}

export function WithAuth({ value, children }: { value: AuthState; children: ReactNode }) {
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
