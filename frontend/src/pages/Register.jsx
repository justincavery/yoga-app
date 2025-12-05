import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, User, Lock, ArrowRight } from 'lucide-react';
import { Button, Input, Select, Form } from '../components/ui';
import { Container } from '../components/layout';
import useAuthStore from '../store/authStore';
import apiClient from '../lib/api';
import { validateRegistrationForm, getPasswordStrength } from '../lib/validation';

export default function Register() {
  const navigate = useNavigate();
  const { setAuth, setLoading, setError, isLoading, error } = useAuthStore();

  const [formData, setFormData] = useState({
    email: '',
    name: '',
    password: '',
    experience_level: '',
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState({ strength: 0, label: '', color: '' });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: null }));
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
    useAuthStore.getState().clearError();

    // Validate form
    const { isValid, errors } = validateRegistrationForm(formData);
    if (!isValid) {
      setFieldErrors(errors);
      return;
    }

    // Submit registration
    setLoading(true);
    try {
      const response = await apiClient.register(formData);
      setAuth(response.user, response.tokens);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const experienceLevelOptions = [
    { value: '', label: 'Select your level', disabled: true },
    { value: 'beginner', label: 'Beginner - New to yoga' },
    { value: 'intermediate', label: 'Intermediate - Regular practice' },
    { value: 'advanced', label: 'Advanced - Experienced practitioner' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <Container size="sm">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">Create Your Account</h1>
            <p className="text-neutral-600">Start your yoga journey today</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg text-error-700">
              {error}
            </div>
          )}

          {/* Registration Form */}
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

            {/* Name */}
            <Input
              label="Full Name"
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              icon={<User size={20} />}
              placeholder="Jane Doe"
              error={fieldErrors.name}
              fullWidth
              disabled={isLoading}
              required
            />

            {/* Password */}
            <div className="space-y-2">
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                icon={<Lock size={20} />}
                placeholder="Create a strong password"
                error={fieldErrors.password}
                fullWidth
                disabled={isLoading}
                required
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

            {/* Experience Level */}
            <Select
              label="Experience Level"
              name="experience_level"
              value={formData.experience_level}
              onChange={handleChange}
              options={experienceLevelOptions}
              error={fieldErrors.experience_level}
              fullWidth
              disabled={isLoading}
              required
            />

            {/* Submit Button */}
            <Button type="submit" variant="primary" fullWidth loading={isLoading} size="lg" icon={<ArrowRight size={20} />}>
              Create Account
            </Button>
          </Form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-neutral-600">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
                Sign in
              </Link>
            </p>
          </div>

          {/* Divider */}
          <div className="mt-6 border-t border-neutral-200 pt-6">
            <p className="text-xs text-neutral-500 text-center">
              By creating an account, you agree to our{' '}
              <a href="/terms" className="text-primary-600 hover:underline">
                Terms of Service
              </a>{' '}
              and{' '}
              <a href="/privacy" className="text-primary-600 hover:underline">
                Privacy Policy
              </a>
            </p>
          </div>
        </div>
      </Container>
    </div>
  );
}
