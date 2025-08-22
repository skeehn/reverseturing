import React from 'react';
import { Loader2, Sparkles, Brain, Users, Trophy, BarChart3 } from 'lucide-react';

// Generic spinner component
export const Spinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; className?: string }> = ({ 
  size = 'md', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <Loader2 className={`animate-spin ${sizeClasses[size]} ${className}`} />
  );
};

// Full page loading overlay
export const LoadingOverlay: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 flex flex-col items-center">
        <Spinner size="lg" className="text-indigo-600 mb-4" />
        <p className="text-gray-700 dark:text-gray-300">{message}</p>
      </div>
    </div>
  );
};

// Game loading screen with animated elements
export const GameLoadingScreen: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
      <div className="text-center">
        <div className="relative mb-8">
          <Brain className="w-24 h-24 text-indigo-500 mx-auto animate-pulse" />
          <Sparkles className="w-8 h-8 text-yellow-400 absolute top-0 right-8 animate-bounce" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-4">Preparing Your Game</h2>
        <div className="flex items-center justify-center gap-2 text-gray-400">
          <Spinner size="sm" className="text-indigo-400" />
          <span>Loading AI models and game state...</span>
        </div>
      </div>
    </div>
  );
};

// Skeleton loader for cards
export const CardSkeleton: React.FC<{ count?: number }> = ({ count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-6 animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
          <div className="space-y-2">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-4/6"></div>
          </div>
        </div>
      ))}
    </>
  );
};

// Skeleton loader for leaderboard
export const LeaderboardSkeleton: React.FC = () => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <Trophy className="w-6 h-6 text-gray-300 animate-pulse" />
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-pulse"></div>
      </div>
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gray-200 dark:bg-gray-600 rounded-full animate-pulse"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-24 animate-pulse"></div>
            </div>
            <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-16 animate-pulse"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Skeleton loader for analytics charts
export const AnalyticsSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, index) => (
        <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <BarChart3 className="w-5 h-5 text-gray-300 animate-pulse" />
            <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-24 animate-pulse"></div>
          </div>
          <div className="h-32 bg-gray-100 dark:bg-gray-700 rounded animate-pulse"></div>
          <div className="mt-4 flex justify-between">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16 animate-pulse"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16 animate-pulse"></div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Skeleton loader for game rooms list
export const RoomListSkeleton: React.FC = () => {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-6 animate-pulse">
          <div className="flex justify-between items-start mb-4">
            <div className="space-y-2">
              <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-32"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48"></div>
            </div>
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-20"></div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-gray-300" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-12"></div>
            </div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Profile skeleton loader
export const ProfileSkeleton: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-8">
        <div className="flex items-center gap-6 mb-8">
          <div className="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse"></div>
          <div className="space-y-3">
            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-pulse"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-48 animate-pulse"></div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="h-4 bg-gray-200 dark:bg-gray-600 rounded w-20 mb-2 animate-pulse"></div>
              <div className="h-8 bg-gray-200 dark:bg-gray-600 rounded w-16 animate-pulse"></div>
            </div>
          ))}
        </div>
        
        <div className="space-y-4">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-pulse"></div>
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Inline loading for buttons
export const ButtonLoader: React.FC<{ loading: boolean; children: React.ReactNode }> = ({ 
  loading, 
  children 
}) => {
  return (
    <>
      {loading ? (
        <div className="flex items-center gap-2">
          <Spinner size="sm" />
          <span>Loading...</span>
        </div>
      ) : (
        children
      )}
    </>
  );
};

// Custom hook for loading states
export const useLoading = (initialState = false) => {
  const [isLoading, setIsLoading] = React.useState(initialState);
  
  const startLoading = () => setIsLoading(true);
  const stopLoading = () => setIsLoading(false);
  
  const withLoading = async <T,>(fn: () => Promise<T>): Promise<T> => {
    startLoading();
    try {
      const result = await fn();
      return result;
    } finally {
      stopLoading();
    }
  };
  
  return { isLoading, startLoading, stopLoading, withLoading };
};

// Animated dots for loading text
export const LoadingDots: React.FC = () => {
  return (
    <span className="inline-flex gap-1">
      <span className="animate-bounce animation-delay-0">.</span>
      <span className="animate-bounce animation-delay-200">.</span>
      <span className="animate-bounce animation-delay-400">.</span>
    </span>
  );
};

// Add CSS for animation delays (add to your global CSS)
const animationStyles = `
  @keyframes bounce {
    0%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-10px);
    }
  }
  
  .animation-delay-0 {
    animation-delay: 0ms;
  }
  
  .animation-delay-200 {
    animation-delay: 200ms;
  }
  
  .animation-delay-400 {
    animation-delay: 400ms;
  }
`;

// Export all components
export default {
  Spinner,
  LoadingOverlay,
  GameLoadingScreen,
  CardSkeleton,
  LeaderboardSkeleton,
  AnalyticsSkeleton,
  RoomListSkeleton,
  ProfileSkeleton,
  ButtonLoader,
  LoadingDots,
  useLoading,
};