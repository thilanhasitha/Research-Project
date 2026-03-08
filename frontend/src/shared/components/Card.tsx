import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  title?: string;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
  hover?: boolean;
}

const Card = ({ 
  children, 
  title, 
  className = '', 
  padding = 'md',
  hover = false 
}: CardProps) => {
  const paddings = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  const hoverClass = hover ? 'hover:shadow-lg transition-shadow duration-200' : '';

  return (
    <div className={`bg-white rounded-lg shadow-md ${paddings[padding]} ${hoverClass} ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-3 border-b pb-2">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};

export default Card;
