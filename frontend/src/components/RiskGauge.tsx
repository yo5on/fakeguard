import './RiskGauge.css';

interface RiskGaugeProps {
  score: number;
  category: string;
}

export default function RiskGauge({ score, category }: RiskGaugeProps) {
  const displayScore = Math.round(score);
  const rotation = (score / 100) * 180;
  
  const getCategoryColor = () => {
    switch (category) {
      case 'LOW': return 'var(--color-low)';
      case 'MEDIUM': return 'var(--color-medium)';
      case 'HIGH': return 'var(--color-high)';
      case 'CRITICAL': return 'var(--color-critical)';
      default: return 'var(--color-text-secondary)';
    }
  };

  return (
    <div className="risk-gauge">
      <div className="gauge-container">
        <svg viewBox="0 0 200 120" className="gauge-svg">
          {/* Background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="20"
            strokeLinecap="round"
          />
          
          {/* Colored arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke={getCategoryColor()}
            strokeWidth="20"
            strokeLinecap="round"
            strokeDasharray={`${(score / 100) * 251} 251`}
          />
          
          {/* Needle */}
          <g transform={`rotate(${rotation - 90} 100 100)`}>
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="30"
              stroke={getCategoryColor()}
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="100" cy="100" r="6" fill={getCategoryColor()} />
          </g>
        </svg>
        
        <div className="gauge-score">
          <div className="score-value">{displayScore}</div>
          <div className="score-max">/ 100</div>
        </div>
      </div>
      
      <div className="gauge-labels">
        <span className="label-low">0</span>
        <span className="label-mid">50</span>
        <span className="label-high">100</span>
      </div>
    </div>
  );
}