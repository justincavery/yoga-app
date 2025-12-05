import React from 'react';
import { ChevronDown, AlertCircle } from 'lucide-react';

const Select = React.forwardRef(
  (
    {
      label,
      error,
      helperText,
      options = [],
      placeholder = 'Select an option',
      fullWidth = false,
      className = '',
      containerClassName = '',
      ...props
    },
    ref
  ) => {
    const selectId = props.id || `select-${Math.random().toString(36).substr(2, 9)}`;

    const baseSelectStyles = `
      block w-full px-4 py-3 pr-10 text-neutral-900 bg-white border rounded-lg
      transition-colors duration-200 ease-yoga appearance-none cursor-pointer
      focus:outline-none focus:ring-2 focus:ring-offset-0
      disabled:bg-neutral-100 disabled:cursor-not-allowed
    `;

    const borderStyles = error
      ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
      : 'border-neutral-300 focus:border-primary-500 focus:ring-primary-200';

    const combinedSelectClassName = `
      ${baseSelectStyles}
      ${borderStyles}
      ${className}
    `.replace(/\s+/g, ' ').trim();

    return (
      <div className={`${fullWidth ? 'w-full' : ''} ${containerClassName}`}>
        {label && (
          <label
            htmlFor={selectId}
            className="block text-sm font-medium text-neutral-700 mb-2"
          >
            {label}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            id={selectId}
            className={combinedSelectClassName}
            {...props}
          >
            <option value="" disabled>
              {placeholder}
            </option>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none">
            <ChevronDown size={20} />
          </div>
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

Select.displayName = 'Select';

export default Select;
