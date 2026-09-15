import { useState, useEffect } from 'react';
import { api } from '../services/api';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import './ScoringMethodology.css';

export default function ScoringMethodology() {
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getScoringConfig();
      setConfig(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={loadConfig} />;
  if (!config) return null;

  return (
    <div className="scoring-methodology">
      <div className="container">
        <h1>Scoring Methodology</h1>
        <p className="methodology-intro">
          FakeGuard uses a rule-based scoring system to assess potential risk indicators in social media accounts.
          This page explains the methodology, feature weights, and risk categories used in the analysis.
        </p>

        <div className="methodology-content">
          <section className="card">
            <h2>Feature Weights</h2>
            <p>Each feature contributes to the final risk score based on its assigned weight:</p>
            <div className="weights-grid">
              {Object.entries(config.features).map(([key, feature]: [string, any]) => (
                <div key={key} className="weight-item">
                  <div className="weight-header">
                    <span className="feature-name">{formatFeatureName(key)}</span>
                    <span className="weight-value">{(feature.weight * 100).toFixed(0)}%</span>
                  </div>
                  {feature.thresholds && (
                    <div className="thresholds">
                      {Object.entries(feature.thresholds).map(([range, risk]: [string, any]) => (
                        <div key={range} className="threshold-item">
                          <span className="range">{range}</span>
                          <span className="risk">→ Risk: {risk}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {feature.formula && (
                    <div className="formula">
                      <strong>Formula:</strong> {feature.formula}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <h2>Risk Categories</h2>
            <p>Final risk scores are classified into four categories:</p>
            <div className="categories-grid">
              {Object.entries(config.categories).map(([category, info]: [string, any]) => (
                <div key={category} className={`category-item category-${category.toLowerCase()}`}>
                  <span className={`badge badge-${category.toLowerCase()}`}>{category}</span>
                  <span className="category-range">Score: {info.range}</span>
                  <span className="category-action">{info.action}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <h2>Reason Codes</h2>
            <p>When risk indicators are detected, the system generates reason codes:</p>
            <div className="reason-codes">
              {Object.entries(config.reason_codes).map(([code, description]: [string, any]) => (
                <div key={code} className="reason-code-item">
                  <span className="code">{code}</span>
                  <span className="description">{description}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <h2>Missing Data Handling</h2>
            <p>
              When certain metrics cannot be calculated (e.g., engagement rate when followers = 0), 
              the feature is marked as unavailable. The remaining features are renormalized to maintain 
              a valid 0-100 score range without artificially inflating the risk.
            </p>
            <div className="example">
              <strong>Example:</strong> If both follower/following ratio and engagement are unavailable 
              (45% combined weight), the remaining three features (55% weight) are scaled to represent 
              100% of the score.
            </div>
          </section>

          <section className="card methodology-disclaimer">
            <h2>⚠️ Important Disclaimer</h2>
            <p>{config.disclaimer}</p>
          </section>

          <section className="card">
            <h2>Human-in-the-Loop Review</h2>
            <p>
              FakeGuard is a decision-support tool designed to help human reviewers prioritize their work. 
              It does not make final determinations about account authenticity. All accounts flagged as 
              HIGH or CRITICAL risk should undergo manual review by trained personnel.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

function formatFeatureName(key: string): string {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}