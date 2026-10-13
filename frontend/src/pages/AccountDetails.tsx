import { useState, useEffect, useCallback } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../services/api';
import { Account, AnalysisHistoryEntry } from '../types';
import RiskGauge from '../components/RiskGauge';
import RiskBadge from '../components/RiskBadge';
import RiskBreakdown from '../components/RiskBreakdown';
import ReasonList from '../components/ReasonList';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import './AccountDetails.css';

function parseAccountId(id: string | undefined): number | null {
  if (!id || !/^\d+$/.test(id)) return null;
  const value = Number(id);
  return Number.isSafeInteger(value) && value > 0 ? value : null;
}

export default function AccountDetails() {
  const { id } = useParams<{ id: string }>();
  const accountId = parseAccountId(id);
  const [account, setAccount] = useState<Account | null>(null);
  const [history, setHistory] = useState<AnalysisHistoryEntry[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  const loadAccount = useCallback(async () => {
    if (accountId === null) return;

    try {
      setLoading(true);
      setError(null);
      const [data, analyses] = await Promise.all([
        api.getAccount(accountId),
        api.getAccountAnalyses(accountId),
      ]);
      setAccount(data);
      setHistory(analyses.analyses);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load account');
    } finally {
      setLoading(false);
    }
  }, [accountId]);

  useEffect(() => {
    loadAccount();
  }, [loadAccount]);

  const handleAnalyze = async () => {
    if (accountId === null) return;

    try {
      setAnalyzing(true);
      setAnalyzeError(null);
      await api.analyzeExistingAccount(accountId);
      await loadAccount();
    } catch (err) {
      setAnalyzeError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  if (accountId === null) return <ErrorState message="Invalid account ID" />;
  if (loading && !account) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={loadAccount} />;
  if (!account) return <ErrorState message="Account not found" />;

  const latest = account.latest_analysis;
  const details = latest?.details;

  return (
    <div className="account-details">
      <div className="container">
        <Link to="/accounts" className="back-button">
          ← Back to Accounts
        </Link>

        <div className="details-header">
          <h1>{account.username}</h1>
          <button
            type="button"
            onClick={handleAnalyze}
            disabled={analyzing}
            className="btn btn-primary"
          >
            {analyzing ? 'Analyzing...' : latest ? 'Re-analyze Account' : 'Analyze Account'}
          </button>
        </div>
        {analyzeError && (
          <div className="error-message" role="alert">
            Analysis failed: {analyzeError}
          </div>
        )}

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

          {latest && details ? (
            <div className="analysis-section">
              <div className="card">
                <div className="analysis-header">
                  <h2>Latest Analysis</h2>
                  <span className="analysis-date">
                    {new Date(latest.created_at).toLocaleString()}
                  </span>
                </div>

                <div className="result-summary">
                  <RiskGauge
                    score={details.risk_score}
                    category={details.category}
                  />
                  
                  <div className="result-info">
                    <div className="result-row">
                      <span className="result-label">Category:</span>
                      <RiskBadge category={details.category} size="lg" />
                    </div>
                    <div className="result-row">
                      <span className="result-label">Recommended Action:</span>
                      <span className="result-value">
                        {details.recommended_action}
                      </span>
                    </div>
                    <div className="result-row">
                      <span className="result-label">Risk Score:</span>
                      <span className="result-value">
                        {Math.round(details.risk_score)} / 100
                      </span>
                    </div>
                  </div>
                </div>

                <RiskBreakdown features={details.features} />
                <ReasonList reasons={details.reason_codes} />
              </div>
            </div>
          ) : (
            <div className="card">
              <p className="no-analysis">
                This account has not been analyzed yet. Click "Analyze Account" to perform an analysis.
              </p>
            </div>
          )}

          {history.length > 1 && (
            <div className="card analysis-history">
              <h2>Analysis History</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Analyzed</th>
                      <th scope="col">Risk Score</th>
                      <th scope="col">Category</th>
                      <th scope="col">Recommended Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((entry) => (
                      <tr key={entry.id}>
                        <td>{new Date(entry.created_at).toLocaleString()}</td>
                        <td>{Math.round(entry.risk_score)}</td>
                        <td>
                          <RiskBadge category={entry.category} size="sm" />
                        </td>
                        <td>{entry.recommended_action}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}