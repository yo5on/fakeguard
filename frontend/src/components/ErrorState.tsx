interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="error-state">
      <p>{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-primary" style={{ marginTop: 'var(--spacing-md)' }}>
          Retry
        </button>
      )}
    </div>
  );
}