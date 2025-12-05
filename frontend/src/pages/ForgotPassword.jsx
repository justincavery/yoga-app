import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowRight, CheckCircle } from 'lucide-react';
import { Button, Input, Form } from '../components/ui';
import { Container } from '../components/layout';
import apiClient from '../lib/api';
import { validateForgotPasswordForm } from '../lib/validation';

export default function ForgotPassword() {
  const [formData, setFormData] = useState({
    email: '',
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submittedEmail, setSubmittedEmail] = useState('');

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
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Clear previous errors
    setFieldErrors({});
    setError('');

    // Validate form
    const { isValid, errors } = validateForgotPasswordForm(formData);
    if (!isValid) {
      setFieldErrors(errors);
      return;
    }

    // Submit request
    setIsLoading(true);
    try {
      await apiClient.forgotPassword(formData);
      setSubmittedEmail(formData.email);
      setIsSubmitted(true);
    } catch (err) {
      setError(err.message || 'Failed to send reset email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setIsLoading(true);
    setError('');

    try {
      await apiClient.forgotPassword({ email: submittedEmail });
    } catch (err) {
      setError(err.message || 'Failed to resend email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Container size="sm">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {!isSubmitted ? (
            <>
              {/* Header */}
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-neutral-900 mb-2">
                  Forgot Your Password?
                </h1>
                <p className="text-neutral-600">
                  Enter your email address and we'll send you a link to reset your password.
                </p>
              </div>

              {/* Error Alert */}
              {error && (
                <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg text-error-700">
                  {error}
                </div>
              )}

              {/* Forgot Password Form */}
              <Form onSubmit={handleSubmit}>
                {/* Email */}
                <Input
                  label="Email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  icon={<Mail size={20} />}
                  placeholder="your.email@example.com"
                  error={fieldErrors.email}
                  fullWidth
                  disabled={isLoading}
                />

                {/* Submit Button */}
                <Button
                  type="submit"
                  variant="primary"
                  fullWidth
                  loading={isLoading}
                  size="lg"
                  icon={<ArrowRight size={20} />}
                >
                  {isLoading ? 'Sending...' : 'Send Reset Link'}
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
            </>
          ) : (
            <>
              {/* Success State */}
              <div className="text-center">
                <div className="mb-6 flex justify-center">
                  <div className="rounded-full bg-success-100 p-4">
                    <CheckCircle size={48} className="text-success-600" />
                  </div>
                </div>

                <h1 className="text-3xl font-bold text-neutral-900 mb-2">
                  Check Your Email
                </h1>
                <p className="text-neutral-600 mb-6">
                  We've sent a password reset link to:
                </p>
                <p className="text-lg font-medium text-neutral-900 mb-8">
                  {submittedEmail}
                </p>

                <div className="space-y-4">
                  <p className="text-sm text-neutral-600">
                    The link will expire in 1 hour for security reasons.
                  </p>

                  {error && (
                    <div className="p-4 bg-error-50 border border-error-200 rounded-lg text-error-700">
                      {error}
                    </div>
                  )}

                  <Button
                    variant="outline"
                    fullWidth
                    onClick={handleResend}
                    loading={isLoading}
                    disabled={isLoading}
                  >
                    Resend Email
                  </Button>

                  <Link to="/login">
                    <Button variant="ghost" fullWidth>
                      Back to Login
                    </Button>
                  </Link>
                </div>
              </div>
            </>
          )}

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
