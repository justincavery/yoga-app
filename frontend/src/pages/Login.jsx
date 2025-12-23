import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, ArrowRight } from 'lucide-react';
import { Button, Input, Form } from '../components/ui';
import { Container } from '../components/layout';
import useAuthStore from '../store/authStore';
import apiClient from '../lib/api';
import { validateLoginForm } from '../lib/validation';

export default function Login() {
  const navigate = useNavigate();
  const { setAuth, setLoading, setError, isLoading, error } = useAuthStore();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    remember_me: false,
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Clear previous errors
    setFieldErrors({});
    useAuthStore.getState().clearError();

    // Validate form
    const { isValid, errors } = validateLoginForm(formData);
    if (!isValid) {
      setFieldErrors(errors);
      return;
    }

    // Submit login
    setLoading(true);
    try {
      const response = await apiClient.login(formData);
      setAuth(response.user, response.tokens);

      // Small delay to ensure localStorage is updated before navigation
      // This prevents race condition where Dashboard loads before token is persisted
      await new Promise(resolve => setTimeout(resolve, 100));

      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Container size="sm">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">Welcome Back</h1>
            <p className="text-neutral-600">Sign in to continue your practice</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg text-error-700">
              {error}
            </div>
          )}

          {/* Mock Login Hint (for testing) */}
          <div className="mb-6 p-4 bg-info-50 border border-info-200 rounded-lg text-info-700 text-sm">
            <p className="font-medium mb-1">Demo Credentials (Mock API):</p>
            <p>Email: test@example.com</p>
            <p>Password: TestPass123</p>
          </div>

          {/* Login Form */}
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
              required
            />

            {/* Password */}
            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              name="password"
              value={formData.password}
              onChange={handleChange}
              icon={<Lock size={20} />}
              placeholder="Enter your password"
              error={fieldErrors.password}
              fullWidth
              disabled={isLoading}
              required
              showPasswordToggle
              onTogglePassword={() => setShowPassword(!showPassword)}
            />

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  name="remember_me"
                  checked={formData.remember_me}
                  onChange={handleChange}
                  disabled={isLoading}
                  className="w-4 h-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500 focus:ring-2 cursor-pointer disabled:cursor-not-allowed"
                />
                <span className="text-sm text-neutral-700">Remember me</span>
              </label>

              <Link
                to="/forgot-password"
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Forgot password?
              </Link>
            </div>

            {/* Submit Button */}
            <Button type="submit" variant="primary" fullWidth loading={isLoading} size="lg" icon={<ArrowRight size={20} />}>
              Sign In
            </Button>
          </Form>

          {/* Registration Link */}
          <div className="mt-6 text-center">
            <p className="text-neutral-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
                Create one now
              </Link>
            </p>
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
