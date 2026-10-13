import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import AuthProvider from '../auth/AuthProvider';
import RequireAuth from '../auth/RequireAuth';
import { SESSION_KEY, readSession, writeSession } from '../auth/authContext';
import Login from '../pages/Login';
import { ApiError, api, setAuthToken, setUnauthorizedHandler } from '../services/api';

const future = () => Math.floor(Date.now() / 1000) + 3600;

function renderApp(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <h1>Protected dashboard</h1>
              </RequireAuth>
            }
          />
          <Route
            path="/accounts"
            element={
              <RequireAuth>
                <h1>Protected accounts</h1>
              </RequireAuth>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('authentication flow', () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    setAuthToken(null);
    setUnauthorizedHandler(null);
  });

  it('redirects to the login page and back after signing in', async () => {
    vi.spyOn(api, 'authStatus').mockResolvedValue({ auth_required: true, auth_configured: true });
    const login = vi.spyOn(api, 'login').mockResolvedValue({
      access_token: 'tok',
      token_type: 'bearer',
      expires_at: future(),
      username: 'reviewer',
    });

    renderApp('/accounts');
    expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument();

    const user = userEvent.setup();
    await user.type(screen.getByLabelText('Username'), ' reviewer ');
    await user.type(screen.getByLabelText('Password'), 'correct horse battery');
    await user.click(screen.getByRole('button', { name: 'Sign in' }));

    expect(login).toHaveBeenCalledWith('reviewer', 'correct horse battery');
    // Returned to the page originally requested.
    expect(await screen.findByRole('heading', { name: 'Protected accounts' })).toBeInTheDocument();
    expect(readSession()?.token).toBe('tok');
  });

  it('shows login errors and clears the password', async () => {
    vi.spyOn(api, 'authStatus').mockResolvedValue({ auth_required: true, auth_configured: true });
    vi.spyOn(api, 'login').mockRejectedValue(new ApiError('Incorrect username or password', 401));

    renderApp('/login');
    const user = userEvent.setup();
    await user.type(await screen.findByLabelText('Username'), 'reviewer');
    await user.type(screen.getByLabelText('Password'), 'wrong password');
    await user.click(screen.getByRole('button', { name: 'Sign in' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Incorrect username or password');
    expect(screen.getByLabelText('Password')).toHaveValue('');
  });

  it('warns when the server has no authentication configured', async () => {
    vi.spyOn(api, 'authStatus').mockResolvedValue({ auth_required: true, auth_configured: false });
    renderApp('/login');
    expect(await screen.findByRole('alert')).toHaveTextContent(/not configured on the server/);
  });

  it('skips the login screen when the server disables auth', async () => {
    vi.spyOn(api, 'authStatus').mockResolvedValue({ auth_required: false, auth_configured: false });
    renderApp('/dashboard');
    expect(await screen.findByRole('heading', { name: 'Protected dashboard' })).toBeInTheDocument();
  });

  it('restores a stored session after validating it', async () => {
    writeSession({ token: 'stored', username: 'reviewer', expiresAt: future() });
    vi.spyOn(api, 'authStatus').mockResolvedValue({ auth_required: true, auth_configured: true });
    const me = vi.spyOn(api, 'me').mockResolvedValue({ username: 'reviewer' });

    renderApp('/dashboard');
    expect(await screen.findByRole('heading', { name: 'Protected dashboard' })).toBeInTheDocument();
    expect(me).toHaveBeenCalled();
  });

  it('drops a stored session the server rejects', async () => {
    writeSession({ token: 'revoked', username: 'reviewer', expiresAt: future() });
    vi.spyOn(api, 'authStatus').mockResolvedValue({ auth_required: true, auth_configured: true });
    vi.spyOn(api, 'me').mockRejectedValue(new ApiError('Invalid or expired token', 401));

    renderApp('/dashboard');
    expect(await screen.findByRole('heading', { name: 'Sign in' })).toBeInTheDocument();
    expect(sessionStorage.getItem(SESSION_KEY)).toBeNull();
  });

  it('shows a retryable error when the server is unreachable', async () => {
    vi.spyOn(api, 'authStatus').mockRejectedValue(new ApiError('Unable to reach the FakeGuard API.', 0));
    renderApp('/dashboard');
    expect(await screen.findByRole('alert')).toHaveTextContent('Unable to reach the FakeGuard API.');
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
  });
});

describe('session storage', () => {
  beforeEach(() => sessionStorage.clear());

  it('ignores expired or malformed sessions', () => {
    writeSession({ token: 't', username: 'u', expiresAt: Math.floor(Date.now() / 1000) - 1 });
    expect(readSession()).toBeNull();
    expect(sessionStorage.getItem(SESSION_KEY)).toBeNull();

    sessionStorage.setItem(SESSION_KEY, '{not json');
    expect(readSession()).toBeNull();
  });
});

describe('API client authorization', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    setAuthToken(null);
    setUnauthorizedHandler(null);
  });

  it('sends the bearer token and reports rejected tokens', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify({ detail: 'Invalid or expired token' }), { status: 401 }));
    vi.stubGlobal('fetch', fetchMock);
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);
    setAuthToken('abc');

    await expect(api.getDashboardSummary()).rejects.toThrow('Invalid or expired token');
    const headers = fetchMock.mock.calls[0][1].headers as Headers;
    expect(headers.get('Authorization')).toBe('Bearer abc');
    expect(onUnauthorized).toHaveBeenCalledTimes(1);
  });

  it('does not treat a failed login as a session expiry', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'Incorrect' }), { status: 401 })),
    );
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);

    await expect(api.login('a', 'b')).rejects.toThrow('Incorrect');
    expect(onUnauthorized).not.toHaveBeenCalled();
  });

  it('includes Retry-After in rate-limit errors', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Too many requests.' }), {
          status: 429,
          headers: { 'Retry-After': '42' },
        }),
      ),
    );
    await waitFor(() => expect(api.health()).rejects.toThrow('Too many requests. (retry in 42s)'));
  });
});
