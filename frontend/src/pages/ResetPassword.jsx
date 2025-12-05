import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Lock, ArrowRight } from 'lucide-react';
import { Button, Input, Form } from '../components/ui';
import { Container } from '../components/layout';
import apiClient from '../lib/api';
import { validateResetPasswordForm, getPasswordStrength } from '../lib/validation';

export default function ResetPassword() {
  const navigate = useNavigate();
  const { token } = useParams();

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState({ strength: 0, label: '', color: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: null }));
    }
    // Clear general error
    if (error) {
      setError('');
    }

    // Update password strength in real-time
    if (name === 'password') {
      setPasswordStrength(getPasswordStrength(value));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Clear previous errors
    setFieldErrors({});
    setError('');
    setSuccessMessage('');

    // Validate form
    const { isValid, errors } = validateResetPasswordForm(formData);
    if (!isValid) {
      setFieldErrors(errors);
      return;
    }

    // Submit reset
    setIsLoading(true);
    try {
      const response = await apiClient.resetPassword({
        token,
        new_password: formData.password,
      });
      setSuccessMessage(response.message || 'Password reset successful!');

      // Redirect to login after a short delay
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to reset password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Container size="sm">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">
              Reset Your Password
            </h1>
            <p className="text-neutral-600">
              Enter your new password below.
            </p>
          </div>

          {/* Success Alert */}
          {successMessage && (
            <div className="mb-6 p-4 bg-success-50 border border-success-200 rounded-lg text-success-700">
              {successMessage}
            </div>
          )}

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg text-error-700">
              {error}
            </div>
          )}

          {/* Reset Password Form */}
          <Form onSubmit={handleSubmit}>
            {/* New Password */}
            <div className="space-y-2">
              <Input
                label="New Password"
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                icon={<Lock size={20} />}
                placeholder="Create a strong password"
                error={fieldErrors.password}
                fullWidth
                disabled={isLoading}
                showPasswordToggle
                onTogglePassword={() => setShowPassword(!showPassword)}
              />

              {/* Password Strength Indicator */}
              {formData.password && (
                <div className="space-y-1">
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5, 6].map((level) => (
                      <div
                        key={level}
                        className={`h-1 flex-1 rounded-full transition-colors ${
                          level <= passwordStrength.strength
                            ? passwordStrength.color === 'red'
                              ? 'bg-error-500'
                              : passwordStrength.color === 'yellow'
                              ? 'bg-warning-500'
                              : 'bg-success-500'
                            : 'bg-neutral-200'
                        }`}
                      />
                    ))}
                  </div>
                  <p
                    className={`text-xs ${
                      passwordStrength.color === 'red'
                        ? 'text-error-600'
                        : passwordStrength.color === 'yellow'
                        ? 'text-warning-600'
                        : 'text-success-600'
                    }`}
                  >
                    Password strength: {passwordStrength.label}
                  </p>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <Input
              label="Confirm Password"
              type={showConfirmPassword ? 'text' : 'password'}
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              icon={<Lock size={20} />}
              placeholder="Re-enter your password"
              error={fieldErrors.confirmPassword}
              fullWidth
              disabled={isLoading}
              showPasswordToggle
              onTogglePassword={() => setShowConfirmPassword(!showConfirmPassword)}
            />

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              fullWidth
              loading={isLoading}
              size="lg"
              icon={<ArrowRight size={20} />}
              disabled={isLoading || !!successMessage}
            >
              {isLoading ? 'Resetting...' : 'Reset Password'}
            </Button>
          </Form>

          {/* Back to Login Link */}
          <div className="mt-6 text-center">
            <Link
              to="/login"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Back to Login
            </Link>
          </div>

          {/* Divider */}
          <div className="mt-6 border-t border-neutral-200 pt-6">
            <p className="text-xs text-neutral-500 text-center">
              Protected by industry-standard security protocols
            </p>
          </div>
        </div>
      </Container>
    </div>
  );
}
