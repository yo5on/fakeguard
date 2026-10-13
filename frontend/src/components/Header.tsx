import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../auth/authContext';
import './Header.css';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/analyzer', label: 'Analyzer' },
  { to: '/accounts', label: 'Accounts' },
  { to: '/scoring', label: 'Methodology' },
];

export default function Header() {
  const auth = useAuth();
  const signedIn = auth.authRequired && auth.username;

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo" aria-label="FakeGuard home">
            <span className="logo-icon" aria-hidden="true">🛡️</span>
            <span className="logo-text">FakeGuard</span>
          </Link>

          <nav className="nav" aria-label="Main">
            {/* NavLink also marks nested routes (e.g. /accounts/42) active and sets aria-current. */}
            {NAV_ITEMS.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
              >
                {label}
              </NavLink>
            ))}
            {signedIn && (
              <div className="session">
                <span className="session-user" title="Signed in user">
                  {auth.username}
                </span>
                <button type="button" className="btn btn-secondary btn-small" onClick={auth.logout}>
                  Sign out
                </button>
              </div>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
