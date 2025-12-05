import React from 'react';

const Form = React.forwardRef(
  (
    {
      children,
      onSubmit,
      className = '',
      ...props
    },
    ref
  ) => {
    const handleSubmit = (event) => {
      event.preventDefault();
      if (onSubmit) {
        onSubmit(event);
      }
    };

    return (
      <form
        ref={ref}
        onSubmit={handleSubmit}
        className={`space-y-6 ${className}`}
        {...props}
      >
        {children}
      </form>
    );
  }
);

Form.displayName = 'Form';

const FormField = ({ children, className = '', ...props }) => (
  <div className={`space-y-2 ${className}`} {...props}>
    {children}
  </div>
);

const FormLabel = ({ children, required, className = '', htmlFor, ...props }) => (
  <label
    htmlFor={htmlFor}
    className={`block text-sm font-medium text-neutral-700 ${className}`}
    {...props}
  >
    {children}
    {required && <span className="text-red-500 ml-1">*</span>}
  </label>
);

const FormError = ({ children, className = '', ...props }) => {
  if (!children) return null;

  return (
    <p className={`text-sm text-red-600 ${className}`} {...props}>
      {children}
    </p>
  );
};

const FormHelperText = ({ children, className = '', ...props }) => {
  if (!children) return null;

  return (
    <p className={`text-sm text-neutral-500 ${className}`} {...props}>
      {children}
    </p>
  );
};

Form.Field = FormField;
Form.Label = FormLabel;
Form.Error = FormError;
Form.HelperText = FormHelperText;

export default Form;
