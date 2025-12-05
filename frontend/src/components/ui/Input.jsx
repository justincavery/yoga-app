import React from 'react';
import { AlertCircle, Eye, EyeOff } from 'lucide-react';

const Input = React.forwardRef(
  (
    {
      label,
      error,
      helperText,
      icon,
      iconPosition = 'left',
      type = 'text',
      fullWidth = false,
      className = '',
      containerClassName = '',
      showPasswordToggle = false,
      onTogglePassword,
      ...props
    },
    ref
  ) => {
    const [internalShowPassword, setInternalShowPassword] = React.useState(false);
    const isPassword = type === 'password' || (showPasswordToggle && !internalShowPassword);
    const showPassword = showPasswordToggle ? internalShowPassword : false;
    const inputType = (type === 'password' || showPasswordToggle) && showPassword ? 'text' : type;

    const inputId = props.id || `input-${Math.random().toString(36).substr(2, 9)}`;

    const baseInputStyles = `
      block w-full px-4 py-3 text-neutral-900 bg-white border rounded-lg
      transition-colors duration-200 ease-yoga
      focus:outline-none focus:ring-2 focus:ring-offset-0
      disabled:bg-neutral-100 disabled:cursor-not-allowed
      placeholder:text-neutral-400
    `;

    const borderStyles = error
      ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
      : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-200';

    const iconStyles = icon || isPassword ? (iconPosition === 'left' ? 'pl-11' : 'pr-11') : '';

    const combinedInputClassName = `
      ${baseInputStyles}
      ${borderStyles}
      ${iconStyles}
      ${className}
    `.replace(/\s+/g, ' ').trim();

    return (
      <div className={`${fullWidth ? 'w-full' : ''} ${containerClassName}`}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-neutral-700 mb-2"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {icon && iconPosition === 'left' && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
              {React.cloneElement(icon, { size: 20 })}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            type={inputType}
            className={combinedInputClassName}
            {...props}
          />
          {(isPassword || showPasswordToggle) && (
            <button
              type="button"
              onClick={() => {
                const newValue = !internalShowPassword;
                setInternalShowPassword(newValue);
                if (onTogglePassword) {
                  onTogglePassword(newValue);
                }
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 focus:outline-none"
              tabIndex={-1}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          )}
          {icon && iconPosition === 'right' && !isPassword && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400">
              {React.cloneElement(icon, { size: 20 })}
            </div>
          )}
        </div>
        {error && (
          <div className="flex items-center gap-1 mt-1.5 text-sm text-red-600">
            <AlertCircle size={14} />
            <span>{error}</span>
          </div>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-sm text-neutral-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
