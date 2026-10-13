import { FeatureAnalysis } from '../types';
import './RiskBreakdown.css';

interface RiskBreakdownProps {
  features: FeatureAnalysis[];
  /** Sum of the weights of available features (1 when nothing is missing). */
  totalWeightUsed?: number;
}

export default function RiskBreakdown({ features, totalWeightUsed }: RiskBreakdownProps) {
  const partial = totalWeightUsed !== undefined && totalWeightUsed > 0 && totalWeightUsed < 0.9999;
  const weightedSum = features.reduce((sum, f) => sum + (f.available ? f.weighted_contribution : 0), 0);

  return (
    <div className="risk-breakdown">
      <h3>Feature Risk Breakdown</h3>
      {partial && (
        <p className="breakdown-note">
          Some features could not be calculated, so only {Math.round(totalWeightUsed * 100)}% of the
          weight is available. The score is the weighted sum divided by that share:{' '}
          {weightedSum.toFixed(2)} ÷ {totalWeightUsed.toFixed(2)} ={' '}
          {(weightedSum / totalWeightUsed).toFixed(1)}.
        </p>
      )}
      <div className="breakdown-list">
        {features.map((feature) => (
          <div key={feature.feature} className="breakdown-item">
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
                
                <div
                  className="progress-bar"
                  role="progressbar"
                  aria-label={`${feature.feature} risk`}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={Math.round(feature.risk_score)}
                >
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