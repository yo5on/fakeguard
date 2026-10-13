import { useState } from 'react';
import { api } from '../services/api';
import { AnalysisResponse } from '../types';
import { AnalyzerFormValues, initialFormData, toAccountPayload } from '../utils/accountForm';
import RiskGauge from '../components/RiskGauge';
import RiskBadge from '../components/RiskBadge';
import RiskBreakdown from '../components/RiskBreakdown';
import ReasonList from '../components/ReasonList';
import './Analyzer.css';

export default function Analyzer() {
  const [formData, setFormData] = useState<AnalyzerFormValues>(initialFormData);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const payload = toAccountPayload(formData);
    if (typeof payload === 'string') {
      setError(payload);
      return;
    }

    setLoading(true);
    try {
      const response = await api.analyzeAccount(payload);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData(initialFormData);
    setResult(null);
    setError(null);
  };

  return (
    <div className="analyzer">
      <div className="container">
        <h1>Account Risk Analyzer</h1>
        <p className="analyzer-description">
          Analyze social media account data to assess potential risk indicators.
          This tool provides decision support for manual review prioritization.
        </p>

        <div className="analyzer-content">
          <div className="analyzer-form card">
            <h2>Account Information</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="input-group">
                  <label htmlFor="username">Username *</label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    maxLength={255}
                    autoComplete="off"
                    onChange={handleChange}
                    required
                    placeholder="e.g., john_doe"
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="age_days">Account Age (days) *</label>
                  <input
                    type="number"
                    id="age_days"
                    name="age_days"
                    value={formData.age_days}
                    inputMode="numeric"
                    step="1"
                    onChange={handleChange}
                    required
                    min="0"
                    placeholder="e.g., 365"
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="followers">Followers *</label>
                  <input
                    type="number"
                    id="followers"
                    name="followers"
                    value={formData.followers}
                    inputMode="numeric"
                    step="1"
                    onChange={handleChange}
                    required
                    min="0"
                    placeholder="e.g., 1000"
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="following">Following *</label>
                  <input
                    type="number"
                    id="following"
                    name="following"
                    value={formData.following}
                    inputMode="numeric"
                    step="1"
                    onChange={handleChange}
                    required
                    min="0"
                    placeholder="e.g., 500"
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="posts_per_day">Posts Per Day *</label>
                  <input
                    type="number"
                    id="posts_per_day"
                    name="posts_per_day"
                    value={formData.posts_per_day}
                    onChange={handleChange}
                    required
                    min="0"
                    step="any"
                    placeholder="e.g., 3.5"
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="profile_completeness">Profile Completeness (%) *</label>
                  <input
                    type="number"
                    id="profile_completeness"
                    name="profile_completeness"
                    value={formData.profile_completeness}
                    onChange={handleChange}
                    required
                    min="0"
                    max="100"
                    step="any"
                    placeholder="e.g., 85"
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="avg_likes">Avg Likes Per Post *</label>
                  <input
                    type="number"
                    id="avg_likes"
                    name="avg_likes"
                    value={formData.avg_likes}
                    onChange={handleChange}
                    required
                    min="0"
                    step="any"
                    placeholder="e.g., 50"
                  />
                </div>

                <div className="input-group">
                  <label htmlFor="avg_comments">Avg Comments Per Post *</label>
                  <input
                    type="number"
                    id="avg_comments"
                    name="avg_comments"
                    value={formData.avg_comments}
                    onChange={handleChange}
                    required
                    min="0"
                    step="any"
                    placeholder="e.g., 5"
                  />
                </div>
              </div>

              {error && (
                <div className="error-message" role="alert">
                  {error}
                </div>
              )}

              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Analyzing...' : 'Analyze Account'}
                </button>
                <button type="button" className="btn btn-secondary" onClick={handleReset}>
                  Reset
                </button>
              </div>
            </form>
          </div>

          {result && (
            <div className="analyzer-results" aria-live="polite">
              <div className="card">
                <h2>Analysis Results</h2>
                
                <div className="result-summary">
                  <RiskGauge
                    score={result.analysis.risk_score}
                    category={result.analysis.category}
                  />
                  
                  <div className="result-info">
                    <div className="result-row">
                      <span className="result-label">Category:</span>
                      <RiskBadge category={result.analysis.category} size="lg" />
                    </div>
                    <div className="result-row">
                      <span className="result-label">Recommended Action:</span>
                      <span className="result-value">{result.analysis.recommended_action}</span>
                    </div>
                    <div className="result-row">
                      <span className="result-label">Username:</span>
                      <span className="result-value">{result.account.username}</span>
                    </div>
                  </div>
                </div>

                <RiskBreakdown
                  features={result.analysis.features}
                  totalWeightUsed={result.analysis.total_weight_used}
                />
                <ReasonList reasons={result.analysis.reason_codes} />

                <div className="disclaimer">
                  <strong>Disclaimer:</strong> The scoring weights and thresholds are prototype heuristics 
                  intended for demonstration and evaluation. They are not official government, 
                  law-enforcement, or social-media-platform standards. This analysis provides decision 
                  support only — human review is required.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}