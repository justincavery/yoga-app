import PropTypes from 'prop-types';

/**
 * Reusable StatCard component for displaying statistics.
 * Displays a title, value, optional subtitle, and optional icon.
 */
const StatCard = ({
  title,
  value,
  subtitle,
  icon,
  variant = 'default',
  className = ''
}) => {
  const variantClasses = {
    default: 'bg-white border-gray-200',
    primary: 'bg-blue-50 border-blue-200',
    success: 'bg-green-50 border-green-200',
    info: 'bg-purple-50 border-purple-200',
  };

  const variantTextClasses = {
    default: 'text-gray-900',
    primary: 'text-blue-900',
    success: 'text-green-900',
    info: 'text-purple-900',
  };

  const variantValueClasses = {
    default: 'text-gray-700',
    primary: 'text-blue-700',
    success: 'text-green-700',
    info: 'text-purple-700',
  };

  return (
    <div
      className={`
        ${variantClasses[variant]}
        ${className}
        border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow duration-200
      `}
      data-variant={variant}
      data-testid="stat-card"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className={`text-sm font-medium ${variantTextClasses[variant]} mb-2`}>
            {title}
          </h3>
          <p className={`text-3xl font-bold ${variantValueClasses[variant]} mb-1`}>
            {value}
          </p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">
              {subtitle}
            </p>
          )}
        </div>
        {icon && (
          <div className={`ml-4 ${variantTextClasses[variant]}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
};

StatCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  subtitle: PropTypes.string,
  icon: PropTypes.node,
  variant: PropTypes.oneOf(['default', 'primary', 'success', 'info']),
  className: PropTypes.string,
};

export default StatCard;
