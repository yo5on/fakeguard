import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { api } from '../services/api';
import { DashboardSummary, RiskDistribution, TopRiskAccount } from '../types';
import StatCard from '../components/StatCard';
import RiskBadge from '../components/RiskBadge';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import './Dashboard.css';

const COLORS = {
  LOW: '#10b981',
  MEDIUM: '#f59e0b',
  HIGH: '#f97316',
  CRITICAL: '#ef4444',
};

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [distribution, setDistribution] = useState<RiskDistribution[]>([]);
  const [topAccounts, setTopAccounts] = useState<TopRiskAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [summaryData, distData, topData] = await Promise.all([
        api.getDashboardSummary(),
        api.getRiskDistribution(),
        api.getTopRiskAccounts(10),
      ]);
      
      setSummary(summaryData);
      setDistribution(distData.distribution);
      setTopAccounts(topData.accounts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={loadDashboard} />;
  if (!summary) return null;

  return (
    <div className="dashboard">
      <div className="container">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          <Link to="/analyzer" className="btn btn-primary">
            Analyze Account
          </Link>
        </div>

        <div className="stats-grid">
          <StatCard
            title="Total Accounts"
            value={summary.total_accounts}
            icon="📊"
          />
          <StatCard
            title="Low Risk"
            value={summary.low_risk}
            color="var(--color-low)"
            icon="✅"
          />
          <StatCard
            title="Medium Risk"
            value={summary.medium_risk}
            color="var(--color-medium)"
            icon="⚠️"
          />
          <StatCard
            title="High Risk"
            value={summary.high_risk}
            color="var(--color-high)"
            icon="⚡"
          />
          <StatCard
            title="Critical Risk"
            value={summary.critical_risk}
            color="var(--color-critical)"
            icon="🚨"
          />
          <StatCard
            title="Avg Risk Score"
            value={summary.average_risk_score.toFixed(1)}
            icon="📈"
          />
        </div>

        <div className="dashboard-content">
          <div className="chart-card card">
            <h2>Risk Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={distribution}
                  dataKey="count"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ category, count }) => `${category}: ${count}`}
                >
                  {distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.category as keyof typeof COLORS]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="top-accounts-card card">
            <h2>Priority Review Accounts</h2>
            {topAccounts.length === 0 ? (
              <p className="no-data">No accounts to display</p>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Risk Score</th>
                      <th>Category</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topAccounts.map((account) => (
                      <tr key={account.id}>
                        <td>{account.username}</td>
                        <td>{Math.round(account.risk_score)}</td>
                        <td>
                          <RiskBadge category={account.category} size="sm" />
                        </td>
                        <td>
                          <Link to={`/accounts/${account.id}`} className="btn-link">
                            View Details
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}