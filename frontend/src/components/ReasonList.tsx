import { ReasonCode } from '../types';
import './ReasonList.css';

interface ReasonListProps {
  reasons: ReasonCode[];
}

export default function ReasonList({ reasons }: ReasonListProps) {
  if (reasons.length === 0) {
    return (
      <div className="reason-list">
        <h3>Risk Indicators</h3>
        <p className="no-reasons">No significant risk indicators detected.</p>
      </div>
    );
  }

  return (
    <div className="reason-list">
      <h3>Risk Indicators</h3>
      <div className="reasons">
        {reasons.map((reason, index) => (
          <div key={index} className="reason-item">
            <div className="reason-header">
              <span className="reason-code">{reason.code}</span>
              <span className="reason-weight">
                Weight: {reason.weighted_contribution.toFixed(2)}
              </span>
            </div>
            <p className="reason-description">{reason.description}</p>
            <p className="reason-details">
              Feature: {reason.feature} (Risk: {Math.round(reason.feature_score)}/100)
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}