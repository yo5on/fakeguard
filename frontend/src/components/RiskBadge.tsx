interface RiskBadgeProps {
  category: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function RiskBadge({ category, size = 'md' }: RiskBadgeProps) {
  const badgeClass = `badge badge-${category.toLowerCase()} badge-${size}`;
  
  return (
    <span className={badgeClass}>
      {category}
    </span>
  );
}