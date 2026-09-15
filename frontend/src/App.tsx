import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Analyzer from './pages/Analyzer';
import Accounts from './pages/Accounts';
import AccountDetails from './pages/AccountDetails';
import ScoringMethodology from './pages/ScoringMethodology';
import './styles/global.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analyzer" element={<Analyzer />} />
            <Route path="/accounts" element={<Accounts />} />
            <Route path="/accounts/:id" element={<AccountDetails />} />
            <Route path="/scoring" element={<ScoringMethodology />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;