import React from 'react';
import { Loader2 } from 'lucide-react';

const Button = React.forwardRef(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      fullWidth = false,
      icon,
      iconPosition = 'left',
      className = '',
      ...props
    },
    ref
  ) => {
    const baseStyles = `
      inline-flex items-center justify-center font-medium
      transition-all duration-200 ease-yoga
      focus:outline-none focus:ring-2 focus:ring-offset-2
      disabled:opacity-50 disabled:cursor-not-allowed
      rounded-lg
    `;

    const variants = {
      primary: `
        bg-primary-500 text-white hover:bg-primary-600
        focus:ring-primary-500 shadow-sm hover:shadow-md
      `,
      secondary: `
        bg-secondary-500 text-white hover:bg-secondary-600
        focus:ring-secondary-500 shadow-sm hover:shadow-md
      `,
      accent: `
        bg-accent-500 text-white hover:bg-accent-600
        focus:ring-accent-500 shadow-sm hover:shadow-md
      `,
      outline: `
        border-2 border-primary-500 text-primary-500
        hover:bg-primary-50 focus:ring-primary-500
      `,
      ghost: `
        text-primary-500 hover:bg-primary-50
        focus:ring-primary-500
      `,
      danger: `
        bg-red-500 text-white hover:bg-red-600
        focus:ring-red-500 shadow-sm hover:shadow-md
      `,
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-6 py-3 text-base gap-2',
      lg: 'px-8 py-4 text-lg gap-2.5',
    };

    const widthClass = fullWidth ? 'w-full' : '';

    const combinedClassName = `
      ${baseStyles}
      ${variants[variant] || variants.primary}
      ${sizes[size] || sizes.md}
      ${widthClass}
      ${className}
    `.replace(/\s+/g, ' ').trim();

    const renderIcon = () => {
      if (loading) {
        return <Loader2 className="animate-spin" size={size === 'sm' ? 16 : size === 'lg' ? 24 : 20} />;
      }
      if (icon) {
        return React.cloneElement(icon, {
          size: size === 'sm' ? 16 : size === 'lg' ? 24 : 20,
        });
      }
      return null;
    };

    return (
      <button
        ref={ref}
        className={combinedClassName}
        disabled={disabled || loading}
        {...props}
      >
        {iconPosition === 'left' && renderIcon()}
        {children}
        {iconPosition === 'right' && renderIcon()}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
