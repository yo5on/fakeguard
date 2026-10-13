import { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import { useAuth } from './authContext';

/** Renders children only for signed-in users (or when the server disables auth). */
export default function RequireAuth({ children }: { children: ReactNode }) {
  const auth = useAuth();
  const location = useLocation();

  if (auth.status === 'loading') return <LoadingState />;
  if (auth.status === 'error') {
    return <ErrorState message={auth.error ?? 'Unable to reach the server'} onRetry={auth.retry} />;
  }
  if (auth.authRequired && !auth.username) {
    return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  }
  return <>{children}</>;
}
