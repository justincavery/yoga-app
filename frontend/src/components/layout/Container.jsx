import React from 'react';

const Container = ({
  children,
  size = 'lg',
  padding = true,
  className = '',
  ...props
}) => {
  const baseStyles = 'mx-auto w-full';

  const sizes = {
    sm: 'max-w-3xl',      // 768px
    md: 'max-w-5xl',      // 1024px
    lg: 'max-w-7xl',      // 1280px
    xl: 'max-w-screen-2xl', // 1536px
    full: 'max-w-full',
  };

  const paddingStyles = padding
    ? 'px-4 sm:px-6 lg:px-8'
    : '';

  const combinedClassName = `
    ${baseStyles}
    ${sizes[size] || sizes.lg}
    ${paddingStyles}
    ${className}
  `.replace(/\s+/g, ' ').trim();

  return (
    <div className={combinedClassName} {...props}>
      {children}
    </div>
  );
};

export default Container;
