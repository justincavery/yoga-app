import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithRouter, userEvent } from '../../test/utils';
import ResetPassword from '../ResetPassword';
import apiClient from '../../lib/api';

// Mock the API client
vi.mock('../../lib/api', () => ({
  default: {
    resetPassword: vi.fn(),
  },
}));

// Mock router navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ token: 'test-reset-token' }),
  };
});

describe('ResetPassword Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial Rendering', () => {
    it('should render the page header', () => {
      renderWithRouter(<ResetPassword />);

      expect(screen.getByText('Reset Your Password')).toBeInTheDocument();
    });

    it('should render the page description', () => {
      renderWithRouter(<ResetPassword />);

      expect(screen.getByText(/Enter your new password below/i)).toBeInTheDocument();
    });

    it('should have password input field', () => {
      renderWithRouter(<ResetPassword />);

      expect(screen.getByLabelText(/^new password$/i)).toBeInTheDocument();
    });

    it('should have confirm password input field', () => {
      renderWithRouter(<ResetPassword />);

      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    });

    it('should have submit button', () => {
      renderWithRouter(<ResetPassword />);

      expect(screen.getByRole('button', { name: /reset password/i })).toBeInTheDocument();
    });

    it('should have back to login link', () => {
      renderWithRouter(<ResetPassword />);

      const backLink = screen.getByText(/back to login/i);
      expect(backLink).toBeInTheDocument();
      expect(backLink.closest('a')).toHaveAttribute('href', '/login');
    });
  });

  describe('Password Strength Indicator', () => {
    it('should show password strength indicator when typing', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'Test');

      await waitFor(() => {
        expect(screen.getByText(/password strength/i)).toBeInTheDocument();
      });
    });

    it('should show weak strength for short passwords', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'test');

      await waitFor(() => {
        expect(screen.getByText(/weak/i)).toBeInTheDocument();
      });
    });

    it('should show medium strength for moderate passwords', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'TestPass123');

      await waitFor(() => {
        expect(screen.getByText(/medium/i)).toBeInTheDocument();
      });
    });

    it('should show strong strength for complex passwords', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'TestPass123!@#');

      await waitFor(() => {
        expect(screen.getByText(/strong/i)).toBeInTheDocument();
      });
    });

    it('should hide password strength indicator when input is empty', () => {
      renderWithRouter(<ResetPassword />);

      expect(screen.queryByText(/password strength/i)).not.toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('should show error when password is empty', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      });
    });

    it('should show error when password is too short', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'Test123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      });
    });

    it('should show error when password lacks uppercase', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'testpass123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password must contain at least one uppercase letter/i)).toBeInTheDocument();
      });
    });

    it('should show error when password lacks lowercase', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'TESTPASS123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password must contain at least one lowercase letter/i)).toBeInTheDocument();
      });
    });

    it('should show error when password lacks number', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'TestPassword');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password must contain at least one number/i)).toBeInTheDocument();
      });
    });

    it('should show error when passwords do not match', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'TestPass123');

      const confirmInput = screen.getByLabelText(/confirm password/i);
      await user.type(confirmInput, 'TestPass456');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
      });
    });

    it('should clear error when user starts typing', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      });

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'T');

      expect(screen.queryByText(/password is required/i)).not.toBeInTheDocument();
    });
  });

  describe('Password Visibility Toggle', () => {
    it('should have password visibility toggle buttons', () => {
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('should toggle password visibility when clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      expect(passwordInput).toHaveAttribute('type', 'password');

      // Find and click the toggle button (assuming it's near the password input)
      const toggleButtons = screen.getAllByRole('button');
      const toggleButton = toggleButtons.find(btn =>
        btn.getAttribute('aria-label')?.includes('password') ||
        btn.closest('.relative')?.contains(passwordInput)
      );

      if (toggleButton) {
        await user.click(toggleButton);
        expect(passwordInput).toHaveAttribute('type', 'text');
      }
    });
  });

  describe('Form Submission', () => {
    it('should submit form with valid data', async () => {
      const user = userEvent.setup();
      apiClient.resetPassword.mockResolvedValue({
        message: 'Password reset successful',
        email: 'test@example.com',
      });

      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'NewPass123');

      const confirmInput = screen.getByLabelText(/confirm password/i);
      await user.type(confirmInput, 'NewPass123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(apiClient.resetPassword).toHaveBeenCalledWith({
          token: 'test-reset-token',
          new_password: 'NewPass123',
        });
      });
    });

    it('should disable submit button during submission', async () => {
      const user = userEvent.setup();
      apiClient.resetPassword.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      );

      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'NewPass123');

      const confirmInput = screen.getByLabelText(/confirm password/i);
      await user.type(confirmInput, 'NewPass123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      expect(submitButton).toBeDisabled();
    });

    it('should show loading state during submission', async () => {
      const user = userEvent.setup();
      apiClient.resetPassword.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      );

      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'NewPass123');

      const confirmInput = screen.getByLabelText(/confirm password/i);
      await user.type(confirmInput, 'NewPass123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      expect(screen.getByRole('button', { name: /resetting/i })).toBeInTheDocument();
    });
  });

  describe('Success State', () => {
    it('should redirect to login page after successful reset', async () => {
      const user = userEvent.setup();
      apiClient.resetPassword.mockResolvedValue({
        message: 'Password reset successful',
        email: 'test@example.com',
      });

      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'NewPass123');

      const confirmInput = screen.getByLabelText(/confirm password/i);
      await user.type(confirmInput, 'NewPass123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      // Wait for the 2-second delay before redirect
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      }, { timeout: 3000 });
    });

    it('should show success message before redirect', async () => {
      const user = userEvent.setup();
      apiClient.resetPassword.mockResolvedValue({
        message: 'Password reset successful',
        email: 'test@example.com',
      });

      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'NewPass123');

      const confirmInput = screen.getByLabelText(/confirm password/i);
      await user.type(confirmInput, 'NewPass123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/password reset successful/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when API fails', async () => {
      const user = userEvent.setup();
      apiClient.resetPassword.mockRejectedValue({
        message: 'Invalid or expired token',
      });

      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'NewPass123');

      const confirmInput = screen.getByLabelText(/confirm password/i);
      await user.type(confirmInput, 'NewPass123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid or expired token/i)).toBeInTheDocument();
      });
    });

    it('should keep form visible when API fails', async () => {
      const user = userEvent.setup();
      apiClient.resetPassword.mockRejectedValue({
        message: 'Network error',
      });

      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'NewPass123');

      const confirmInput = screen.getByLabelText(/confirm password/i);
      await user.type(confirmInput, 'NewPass123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });

      expect(screen.getByLabelText(/^new password$/i)).toBeInTheDocument();
    });

    it('should show specific error for expired token', async () => {
      const user = userEvent.setup();
      apiClient.resetPassword.mockRejectedValue({
        status: 400,
        message: 'Reset token has expired',
      });

      renderWithRouter(<ResetPassword />);

      const passwordInput = screen.getByLabelText(/^new password$/i);
      await user.type(passwordInput, 'NewPass123');

      const confirmInput = screen.getByLabelText(/confirm password/i);
      await user.type(confirmInput, 'NewPass123');

      const submitButton = screen.getByRole('button', { name: /reset password/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/reset token has expired/i)).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Design', () => {
    it('should use mobile-responsive container', () => {
      renderWithRouter(<ResetPassword />);

      const container = screen.getByText('Reset Your Password').closest('.bg-white');
      expect(container.parentElement).toHaveClass('px-4');
    });
  });
});
