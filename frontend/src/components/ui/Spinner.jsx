import React from 'react';
import { Loader2 } from 'lucide-react';

const Spinner = ({
  size = 'md',
  className = '',
  ...props
}) => {
  const sizes = {
    sm: 16,
    md: 24,
    lg: 32,
    xl: 48,
  };

  const sizeValue = sizes[size] || sizes.md;

  return (
    <Loader2
      size={sizeValue}
      className={`animate-spin text-primary-500 ${className}`}
      role="status"
      aria-label="Loading"
      {...props}
    />
  );
};

export default Spinner;
