import { LoadingState } from '../types/common';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
}

const LoadingSpinner = ({ size = 'md' }: LoadingSpinnerProps) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex justify-center items-center">
      <div className={`${sizes[size]} border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin`}></div>
    </div>
  );
};

interface LoadingWrapperProps {
  loadingState: LoadingState;
  error?: string;
  children: React.ReactNode;
}

export const LoadingWrapper = ({ loadingState, error, children }: LoadingWrapperProps) => {
  if (loadingState === 'loading') {
    return (
      <div className="flex justify-center items-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (loadingState === 'error') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <p className="font-medium">Error</p>
        <p className="text-sm">{error || 'Something went wrong. Please try again.'}</p>
      </div>
    );
  }

  return <>{children}</>;
};

export default LoadingSpinner;
