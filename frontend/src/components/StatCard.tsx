import './StatCard.css';

interface StatCardProps {
  title: string;
  value: number | string;
  color?: string;
  icon?: string;
}

export default function StatCard({ title, value, color, icon }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-header">
        {icon && <span className="stat-icon">{icon}</span>}
        <span className="stat-title">{title}</span>
      </div>
      <div className="stat-value" style={{ color }}>
        {value}
      </div>
    </div>
  );
}