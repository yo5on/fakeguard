import { FormEvent, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/authContext';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import './Login.css';

export default function Login() {
  const auth = useAuth();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = (location.state as { from?: string } | null)?.from;
  const destination = from && from.startsWith('/') && !from.startsWith('//') ? from : '/dashboard';

  if (auth.status === 'loading') return <LoadingState />;
  if (auth.status === 'error') {
    return <ErrorState message={auth.error ?? 'Unable to reach the server'} onRetry={auth.retry} />;
  }
  if (!auth.authRequired || auth.username) return <Navigate to={destination} replace />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await auth.login(username.trim(), password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign-in failed');
      setPassword('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login">
      <div className="container">
        <div className="login-card card">
          <h1>Sign in</h1>
          <p className="login-intro">Sign in to review account data and run analyses.</p>

          {!auth.authConfigured && (
            <div className="login-warning" role="alert">
              Authentication is not configured on the server. Ask the administrator to set
              AUTH_USERNAME, AUTH_PASSWORD_HASH and AUTH_SECRET_KEY.
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label htmlFor="login-username">Username</label>
              <input
                id="login-username"
                name="username"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                maxLength={255}
                autoFocus
              />
            </div>
            <div className="input-group">
              <label htmlFor="login-password">Password</label>
              <input
                id="login-password"
                name="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                maxLength={1024}
              />
            </div>

            {error && (
              <div className="error-message" role="alert">
                {error}
              </div>
            )}

            <button type="submit" className="btn btn-primary login-submit" disabled={submitting}>
              {submitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
