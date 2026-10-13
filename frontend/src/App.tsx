import { ReactNode } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthProvider from './auth/AuthProvider';
import RequireAuth from './auth/RequireAuth';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Analyzer from './pages/Analyzer';
import Accounts from './pages/Accounts';
import AccountDetails from './pages/AccountDetails';
import ScoringMethodology from './pages/ScoringMethodology';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import './styles/global.css';

const protect = (page: ReactNode) => <RequireAuth>{page}</RequireAuth>;

export function AppRoutes() {
  return (
    <div className="app">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={protect(<Dashboard />)} />
          <Route path="/analyzer" element={protect(<Analyzer />)} />
          <Route path="/accounts" element={protect(<Accounts />)} />
          <Route path="/accounts/:id" element={protect(<AccountDetails />)} />
          {/* The methodology is public, like its API endpoint. */}
          <Route path="/scoring" element={<ScoringMethodology />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
