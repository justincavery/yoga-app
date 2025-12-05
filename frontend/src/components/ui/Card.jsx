import React from 'react';

const Card = React.forwardRef(
  (
    {
      children,
      variant = 'default',
      padding = 'md',
      hoverable = false,
      clickable = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const baseStyles = `
      bg-white rounded-xl transition-shadow duration-200
    `;

    const variants = {
      default: 'shadow-base',
      flat: 'border border-neutral-200',
      elevated: 'shadow-lg',
    };

    const paddings = {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };

    const interactionStyles = `
      ${hoverable ? 'hover:shadow-lg cursor-pointer' : ''}
      ${clickable ? 'cursor-pointer active:scale-[0.98]' : ''}
    `;

    const combinedClassName = `
      ${baseStyles}
      ${variants[variant] || variants.default}
      ${paddings[padding] || paddings.md}
      ${interactionStyles}
      ${className}
    `.replace(/\s+/g, ' ').trim();

    return (
      <div
        ref={ref}
        className={combinedClassName}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

const CardHeader = ({ children, className = '', ...props }) => (
  <div className={`mb-4 ${className}`} {...props}>
    {children}
  </div>
);

const CardTitle = ({ children, className = '', ...props }) => (
  <h3 className={`text-2xl font-semibold text-neutral-900 ${className}`} {...props}>
    {children}
  </h3>
);

const CardDescription = ({ children, className = '', ...props }) => (
  <p className={`text-sm text-neutral-600 mt-1 ${className}`} {...props}>
    {children}
  </p>
);

const CardContent = ({ children, className = '', ...props }) => (
  <div className={className} {...props}>
    {children}
  </div>
);

const CardFooter = ({ children, className = '', ...props }) => (
  <div className={`mt-6 flex items-center justify-end gap-3 ${className}`} {...props}>
    {children}
  </div>
);

Card.Header = CardHeader;
Card.Title = CardTitle;
Card.Description = CardDescription;
Card.Content = CardContent;
Card.Footer = CardFooter;

export default Card;
