import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Account } from '../types';
import RiskGauge from '../components/RiskGauge';
import RiskBadge from '../components/RiskBadge';
import RiskBreakdown from '../components/RiskBreakdown';
import ReasonList from '../components/ReasonList';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import './AccountDetails.css';

export default function AccountDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [account, setAccount] = useState<Account | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAccount = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      setError(null);
      const data = await api.getAccount(parseInt(id));
      setAccount(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load account');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccount();
  }, [id]);

  const handleAnalyze = async () => {
    if (!id) return;

    try {
      setAnalyzing(true);
      await api.analyzeExistingAccount(parseInt(id));
      await loadAccount();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={loadAccount} />;
  if (!account) return <ErrorState message="Account not found" />;

  return (
    <div className="account-details">
      <div className="container">
        <button onClick={() => navigate('/accounts')} className="back-button">
          ← Back to Accounts
        </button>

        <div className="details-header">
          <h1>{account.username}</h1>
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="btn btn-primary"
          >
            {analyzing ? 'Analyzing...' : 'Re-analyze Account'}
          </button>
        </div>

        <div className="details-content">
          <div className="account-info card">
            <h2>Account Information</h2>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Username</span>
                <span className="info-value">{account.username}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Age</span>
                <span className="info-value">{account.age_days} days</span>
              </div>
              <div className="info-item">
                <span className="info-label">Followers</span>
                <span className="info-value">{account.followers.toLocaleString()}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Following</span>
                <span className="info-value">{account.following.toLocaleString()}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Posts Per Day</span>
                <span className="info-value">{account.posts_per_day.toFixed(1)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Profile Completeness</span>
                <span className="info-value">{account.profile_completeness.toFixed(0)}%</span>
              </div>
              <div className="info-item">
                <span className="info-label">Avg Likes</span>
                <span className="info-value">{account.avg_likes.toFixed(1)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Avg Comments</span>
                <span className="info-value">{account.avg_comments.toFixed(1)}</span>
              </div>
            </div>
          </div>

          {account.latest_analysis && account.latest_analysis.details ? (
            <div className="analysis-section">
              <div className="card">
                <div className="analysis-header">
                  <h2>Latest Analysis</h2>
                  <span className="analysis-date">
                    {new Date(account.latest_analysis.created_at).toLocaleString()}
                  </span>
                </div>

                <div className="result-summary">
                  <RiskGauge
                    score={account.latest_analysis.details.risk_score}
                    category={account.latest_analysis.details.category}
                  />
                  
                  <div className="result-info">
                    <div className="result-row">
                      <span className="result-label">Category:</span>
                      <RiskBadge category={account.latest_analysis.details.category} size="lg" />
                    </div>
                    <div className="result-row">
                      <span className="result-label">Recommended Action:</span>
                      <span className="result-value">
                        {account.latest_analysis.details.recommended_action}
                      </span>
                    </div>
                    <div className="result-row">
                      <span className="result-label">Risk Score:</span>
                      <span className="result-value">
                        {Math.round(account.latest_analysis.details.risk_score)} / 100
                      </span>
                    </div>
                  </div>
                </div>

                <RiskBreakdown features={account.latest_analysis.details.features} />
                <ReasonList reasons={account.latest_analysis.details.reason_codes} />
              </div>
            </div>
          ) : (
            <div className="card">
              <p className="no-analysis">
                This account has not been analyzed yet. Click "Re-analyze Account" to perform an analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}