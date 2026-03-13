"use client";

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div className="bg-red-900/20 border border-red-800 rounded-lg p-6 text-center">
      <p className="text-red-400 mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-red-800 hover:bg-red-700 text-white rounded transition-colors"
        >
          Try again
        </button>
      )}
    </div>
  );
}
