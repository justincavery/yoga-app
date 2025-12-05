import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithRouter, userEvent } from '../../test/utils';
import Profile from '../Profile';
import apiClient from '../../lib/api';

// Mock the API client
vi.mock('../../lib/api', () => ({
  default: {
    getProfile: vi.fn(),
    updateProfile: vi.fn(),
    changePassword: vi.fn(),
  },
}));

// Mock toast notifications
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock router navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock localStorage for auth token
const mockToken = 'test-token-123';
Storage.prototype.getItem = vi.fn((key) => {
  if (key === 'token') return mockToken;
  return null;
});

describe('Profile Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default successful profile fetch
    apiClient.getProfile.mockResolvedValue({
      user_id: 1,
      email: 'test@example.com',
      name: 'Test User',
      experience_level: 'beginner',
      email_verified: true,
      created_at: '2025-01-15T10:30:00Z',
      last_login: '2025-12-05T08:00:00Z',
    });
  });

  describe('Initial Rendering', () => {
    it('should render the page header', async () => {
      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByText('Profile')).toBeInTheDocument();
      });
    });

    it('should load and display user information', async () => {
      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByText('test@example.com')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
      });
    });

    it('should display user email as read-only', async () => {
      renderWithRouter(<Profile />);

      await waitFor(() => {
        const emailField = screen.getByDisplayValue('test@example.com');
        expect(emailField).toBeDisabled();
      });
    });

    it('should display join date', async () => {
      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByText(/member since/i)).toBeInTheDocument();
      });
    });

    it('should have profile edit form', async () => {
      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/experience level/i)).toBeInTheDocument();
      });
    });

    it('should have change password form', async () => {
      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/confirm new password/i)).toBeInTheDocument();
      });
    });

    it('should have save buttons', async () => {
      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /update profile/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /change password/i })).toBeInTheDocument();
      });
    });
  });

  describe('Profile Update', () => {
    it('should update name successfully', async () => {
      const user = userEvent.setup();
      apiClient.updateProfile.mockResolvedValue({
        user_id: 1,
        email: 'test@example.com',
        name: 'Updated Name',
        experience_level: 'beginner',
        email_verified: true,
        created_at: '2025-01-15T10:30:00Z',
      });

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/name/i);
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Name');

      const updateButton = screen.getByRole('button', { name: /update profile/i });
      await user.click(updateButton);

      await waitFor(() => {
        expect(apiClient.updateProfile).toHaveBeenCalledWith(mockToken, {
          name: 'Updated Name',
          experience_level: 'beginner',
        });
      });
    });

    it('should update experience level successfully', async () => {
      const user = userEvent.setup();
      apiClient.updateProfile.mockResolvedValue({
        user_id: 1,
        email: 'test@example.com',
        name: 'Test User',
        experience_level: 'intermediate',
        email_verified: true,
        created_at: '2025-01-15T10:30:00Z',
      });

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByLabelText(/experience level/i)).toBeInTheDocument();
      });

      const levelSelect = screen.getByLabelText(/experience level/i);
      await user.selectOptions(levelSelect, 'intermediate');

      const updateButton = screen.getByRole('button', { name: /update profile/i });
      await user.click(updateButton);

      await waitFor(() => {
        expect(apiClient.updateProfile).toHaveBeenCalledWith(mockToken, {
          name: 'Test User',
          experience_level: 'intermediate',
        });
      });
    });

    it('should show error when profile update fails', async () => {
      const user = userEvent.setup();
      apiClient.updateProfile.mockRejectedValue({
        status: 500,
        message: 'Update failed',
      });

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/name/i);
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Name');

      const updateButton = screen.getByRole('button', { name: /update profile/i });
      await user.click(updateButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to update profile/i)).toBeInTheDocument();
      });
    });

    it('should show loading state during update', async () => {
      const user = userEvent.setup();
      apiClient.updateProfile.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
      });

      const updateButton = screen.getByRole('button', { name: /update profile/i });
      await user.click(updateButton);

      expect(screen.getByText(/updating/i)).toBeInTheDocument();
    });

    it('should validate name is not empty', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
      });

      const nameInput = screen.getByLabelText(/name/i);
      await user.clear(nameInput);

      const updateButton = screen.getByRole('button', { name: /update profile/i });
      await user.click(updateButton);

      await waitFor(() => {
        expect(screen.getByText(/name is required/i)).toBeInTheDocument();
      });

      expect(apiClient.updateProfile).not.toHaveBeenCalled();
    });
  });

  describe('Password Change', () => {
    it('should change password successfully', async () => {
      const user = userEvent.setup();
      apiClient.changePassword.mockResolvedValue({
        message: 'Password changed successfully',
        email: 'test@example.com',
      });

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
      });

      await user.type(screen.getByLabelText(/current password/i), 'OldPassword123');
      await user.type(screen.getByLabelText(/^new password$/i), 'NewPassword456');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword456');

      const changeButton = screen.getByRole('button', { name: /change password/i });
      await user.click(changeButton);

      await waitFor(() => {
        expect(apiClient.changePassword).toHaveBeenCalledWith(mockToken, {
          current_password: 'OldPassword123',
          new_password: 'NewPassword456',
        });
      });
    });

    it('should show error when current password is wrong', async () => {
      const user = userEvent.setup();
      apiClient.changePassword.mockRejectedValue({
        status: 401,
        message: 'Current password is incorrect',
      });

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
      });

      await user.type(screen.getByLabelText(/current password/i), 'WrongPassword123');
      await user.type(screen.getByLabelText(/^new password$/i), 'NewPassword456');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword456');

      const changeButton = screen.getByRole('button', { name: /change password/i });
      await user.click(changeButton);

      await waitFor(() => {
        expect(screen.getByText(/current password is incorrect/i)).toBeInTheDocument();
      });
    });

    it('should validate password confirmation matches', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
      });

      await user.type(screen.getByLabelText(/current password/i), 'OldPassword123');
      await user.type(screen.getByLabelText(/^new password$/i), 'NewPassword456');
      await user.type(screen.getByLabelText(/confirm new password/i), 'DifferentPassword789');

      const changeButton = screen.getByRole('button', { name: /change password/i });
      await user.click(changeButton);

      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
      });

      expect(apiClient.changePassword).not.toHaveBeenCalled();
    });

    it('should validate new password length', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
      });

      await user.type(screen.getByLabelText(/current password/i), 'OldPassword123');
      await user.type(screen.getByLabelText(/^new password$/i), 'Short1');
      await user.type(screen.getByLabelText(/confirm new password/i), 'Short1');

      const changeButton = screen.getByRole('button', { name: /change password/i });
      await user.click(changeButton);

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      });

      expect(apiClient.changePassword).not.toHaveBeenCalled();
    });

    it('should clear password fields after successful change', async () => {
      const user = userEvent.setup();
      apiClient.changePassword.mockResolvedValue({
        message: 'Password changed successfully',
        email: 'test@example.com',
      });

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
      });

      const currentPwdInput = screen.getByLabelText(/current password/i);
      const newPwdInput = screen.getByLabelText(/^new password$/i);
      const confirmPwdInput = screen.getByLabelText(/confirm new password/i);

      await user.type(currentPwdInput, 'OldPassword123');
      await user.type(newPwdInput, 'NewPassword456');
      await user.type(confirmPwdInput, 'NewPassword456');

      const changeButton = screen.getByRole('button', { name: /change password/i });
      await user.click(changeButton);

      await waitFor(() => {
        expect(currentPwdInput.value).toBe('');
        expect(newPwdInput.value).toBe('');
        expect(confirmPwdInput.value).toBe('');
      });
    });

    it('should show loading state during password change', async () => {
      const user = userEvent.setup();
      apiClient.changePassword.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByLabelText(/current password/i)).toBeInTheDocument();
      });

      await user.type(screen.getByLabelText(/current password/i), 'OldPassword123');
      await user.type(screen.getByLabelText(/^new password$/i), 'NewPassword456');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword456');

      const changeButton = screen.getByRole('button', { name: /change password/i });
      await user.click(changeButton);

      expect(screen.getByText(/changing password/i)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should show error when profile load fails', async () => {
      apiClient.getProfile.mockRejectedValue({
        status: 500,
        message: 'Failed to load profile',
      });

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load profile/i)).toBeInTheDocument();
      });
    });

    it('should handle unauthorized access', async () => {
      apiClient.getProfile.mockRejectedValue({
        status: 401,
        message: 'Unauthorized',
      });

      renderWithRouter(<Profile />);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      });
    });
  });
});
