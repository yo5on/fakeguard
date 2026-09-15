import { Link, useLocation } from 'react-router-dom';
import './Header.css';

export default function Header() {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo">
            <span className="logo-icon">🛡️</span>
            <span className="logo-text">FakeGuard</span>
          </Link>
          
          <nav className="nav">
            <Link to="/dashboard" className={`nav-link ${isActive('/dashboard')}`}>
              Dashboard
            </Link>
            <Link to="/analyzer" className={`nav-link ${isActive('/analyzer')}`}>
              Analyzer
            </Link>
            <Link to="/accounts" className={`nav-link ${isActive('/accounts')}`}>
              Accounts
            </Link>
            <Link to="/scoring" className={`nav-link ${isActive('/scoring')}`}>
              Methodology
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}