import { FeatureAnalysis } from '../types';
import './RiskBreakdown.css';

interface RiskBreakdownProps {
  features: FeatureAnalysis[];
}

export default function RiskBreakdown({ features }: RiskBreakdownProps) {
  return (
    <div className="risk-breakdown">
      <h3>Feature Risk Breakdown</h3>
      <div className="breakdown-list">
        {features.map((feature, index) => (
          <div key={index} className="breakdown-item">
            <div className="breakdown-header">
              <span className="feature-name">{feature.feature}</span>
              {!feature.available && (
                <span className="unavailable-badge">Unavailable</span>
              )}
            </div>
            
            {feature.available ? (
              <>
                <div className="breakdown-scores">
                  <span className="feature-score">
                    Risk: {Math.round(feature.risk_score)}/100
                  </span>
                  <span className="weighted-score">
                    Weighted: {feature.weighted_contribution.toFixed(2)}
                  </span>
                </div>
                
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${feature.risk_score}%`,
                      background: getRiskColor(feature.risk_score),
                    }}
                  />
                </div>
                
                {feature.details && (
                  <div className="feature-details">{feature.details}</div>
                )}
              </>
            ) : (
              <div className="feature-unavailable">
                {feature.details || 'Cannot calculate (missing data)'}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function getRiskColor(score: number): string {
  if (score < 30) return 'var(--color-low)';
  if (score < 60) return 'var(--color-medium)';
  if (score < 80) return 'var(--color-high)';
  return 'var(--color-critical)';
}