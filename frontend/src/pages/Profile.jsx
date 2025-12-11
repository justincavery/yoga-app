import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Lock, Calendar, Mail, Award } from 'lucide-react';
import { Button, Card, Input } from '../components/ui';
import { Container } from '../components/layout';
import useAuthStore from '../store/authStore';
import apiClient from '../lib/api';
import toast from 'react-hot-toast';

export default function Profile() {
  const navigate = useNavigate();
  const { accessToken: token, setUser } = useAuthStore();

  // Profile state
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Profile form state
  const [profileForm, setProfileForm] = useState({
    name: '',
    experience_level: 'beginner',
  });
  const [profileErrors, setProfileErrors] = useState({});
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);

  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [passwordErrors, setPasswordErrors] = useState({});
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // Load profile on mount
  useEffect(() => {
    const loadProfile = async () => {
      if (!token) {
        navigate('/login');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const data = await apiClient.getProfile(token);
        setProfile(data);
        setProfileForm({
          name: data.name || '',
          experience_level: data.experience_level || 'beginner',
        });
      } catch (err) {
        console.error('Error loading profile:', err);
        if (err.status === 401) {
          navigate('/login');
        } else {
          setError('Failed to load profile. Please try again.');
          toast.error('Failed to load profile');
        }
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [token, navigate]);

  // Handle profile form changes
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileForm(prev => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (profileErrors[name]) {
      setProfileErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  // Handle profile update
  const handleProfileUpdate = async (e) => {
    e.preventDefault();

    // Validate profile form
    const errors = {};
    if (!profileForm.name || profileForm.name.trim() === '') {
      errors.name = 'Name is required';
    }

    if (Object.keys(errors).length > 0) {
      setProfileErrors(errors);
      return;
    }

    setIsUpdatingProfile(true);
    setProfileErrors({});

    try {
      const updatedProfile = await apiClient.updateProfile(token, {
        name: profileForm.name.trim(),
        experience_level: profileForm.experience_level,
      });

      setProfile(updatedProfile);
      setUser(updatedProfile); // Update auth store
      toast.success('Profile updated successfully!');
    } catch (err) {
      console.error('Error updating profile:', err);
      setProfileErrors({ general: err.message || 'Failed to update profile' });
      toast.error(err.message || 'Failed to update profile');
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  // Handle password form changes
  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordForm(prev => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (passwordErrors[name]) {
      setPasswordErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  // Validate password
  const validatePassword = (password) => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters long';
    }
    if (!/[A-Z]/.test(password)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!/[a-z]/.test(password)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!/\d/.test(password)) {
      return 'Password must contain at least one number';
    }
    return null;
  };

  // Handle password change
  const handlePasswordChangeSubmit = async (e) => {
    e.preventDefault();

    // Validate password form
    const errors = {};

    if (!passwordForm.current_password) {
      errors.current_password = 'Current password is required';
    }

    if (!passwordForm.new_password) {
      errors.new_password = 'New password is required';
    } else {
      const passwordError = validatePassword(passwordForm.new_password);
      if (passwordError) {
        errors.new_password = passwordError;
      }
    }

    if (!passwordForm.confirm_password) {
      errors.confirm_password = 'Please confirm your new password';
    } else if (passwordForm.new_password !== passwordForm.confirm_password) {
      errors.confirm_password = 'Passwords do not match';
    }

    if (Object.keys(errors).length > 0) {
      setPasswordErrors(errors);
      return;
    }

    setIsChangingPassword(true);
    setPasswordErrors({});

    try {
      await apiClient.changePassword(token, {
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });

      // Clear form on success
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });

      toast.success('Password changed successfully!');
    } catch (err) {
      console.error('Error changing password:', err);
      setPasswordErrors({ general: err.message || 'Failed to change password' });
      toast.error(err.message || 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <Container>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading profile...</p>
          </div>
        </div>
      </Container>
    );
  }

  if (error && !profile) {
    return (
      <Container>
        <div className="max-w-2xl mx-auto mt-8">
          <Card className="p-8 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
          </Card>
        </div>
      </Container>
    );
  }

  return (
    <Container>
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
          <p className="mt-2 text-sm text-gray-600">Manage your account settings and preferences</p>
        </div>

        <div className="space-y-6">
          {/* User Information Card */}
          <Card className="p-6">
            <div className="flex items-center space-x-4 mb-6">
              <div className="h-16 w-16 rounded-full bg-indigo-100 flex items-center justify-center">
                <User className="h-8 w-8 text-indigo-600" />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-gray-900">{profile?.name}</h2>
                <p className="text-sm text-gray-500">{profile?.email}</p>
              </div>
              <div className="flex flex-col items-end">
                {profile?.email_verified && (
                  <div className="flex items-center text-sm text-green-600 mb-1">
                    <Award className="h-4 w-4 mr-1" />
                    Verified
                  </div>
                )}
                <div className="flex items-center text-sm text-gray-500">
                  <Calendar className="h-4 w-4 mr-1" />
                  Member since {formatDate(profile?.created_at)}
                </div>
              </div>
            </div>
          </Card>

          {/* Update Profile Card */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Profile Information
            </h3>

            <form onSubmit={handleProfileUpdate} className="space-y-4">
              {profileErrors.general && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <p className="text-sm text-red-600">{profileErrors.general}</p>
                </div>
              )}

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    value={profile?.email || ''}
                    disabled
                    className="pl-10 bg-gray-50"
                  />
                </div>
                <p className="mt-1 text-xs text-gray-500">Email cannot be changed</p>
              </div>

              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                  Name *
                </label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  value={profileForm.name}
                  onChange={handleProfileChange}
                  placeholder="Your full name"
                  className={profileErrors.name ? 'border-red-300' : ''}
                />
                {profileErrors.name && (
                  <p className="mt-1 text-sm text-red-600">{profileErrors.name}</p>
                )}
              </div>

              <div>
                <label htmlFor="experience_level" className="block text-sm font-medium text-gray-700 mb-1">
                  Experience Level
                </label>
                <select
                  id="experience_level"
                  name="experience_level"
                  value={profileForm.experience_level}
                  onChange={handleProfileChange}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div className="flex justify-end">
                <Button
                  type="submit"
                  disabled={isUpdatingProfile}
                  className="min-w-[140px]"
                >
                  {isUpdatingProfile ? 'Updating...' : 'Update Profile'}
                </Button>
              </div>
            </form>
          </Card>

          {/* Change Password Card */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Lock className="h-5 w-5 mr-2" />
              Change Password
            </h3>

            <form onSubmit={handlePasswordChangeSubmit} className="space-y-4">
              {passwordErrors.general && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <p className="text-sm text-red-600">{passwordErrors.general}</p>
                </div>
              )}

              <div>
                <label htmlFor="current_password" className="block text-sm font-medium text-gray-700 mb-1">
                  Current Password *
                </label>
                <Input
                  id="current_password"
                  name="current_password"
                  type="password"
                  value={passwordForm.current_password}
                  onChange={handlePasswordChange}
                  placeholder="Enter current password"
                  className={passwordErrors.current_password ? 'border-red-300' : ''}
                />
                {passwordErrors.current_password && (
                  <p className="mt-1 text-sm text-red-600">{passwordErrors.current_password}</p>
                )}
              </div>

              <div>
                <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-1">
                  New Password *
                </label>
                <Input
                  id="new_password"
                  name="new_password"
                  type="password"
                  value={passwordForm.new_password}
                  onChange={handlePasswordChange}
                  placeholder="Enter new password"
                  className={passwordErrors.new_password ? 'border-red-300' : ''}
                />
                {passwordErrors.new_password && (
                  <p className="mt-1 text-sm text-red-600">{passwordErrors.new_password}</p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  Password must be at least 8 characters with uppercase, lowercase, and numbers
                </p>
              </div>

              <div>
                <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password *
                </label>
                <Input
                  id="confirm_password"
                  name="confirm_password"
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={handlePasswordChange}
                  placeholder="Confirm new password"
                  className={passwordErrors.confirm_password ? 'border-red-300' : ''}
                />
                {passwordErrors.confirm_password && (
                  <p className="mt-1 text-sm text-red-600">{passwordErrors.confirm_password}</p>
                )}
              </div>

              <div className="flex justify-end">
                <Button
                  type="submit"
                  disabled={isChangingPassword}
                  className="min-w-[160px]"
                >
                  {isChangingPassword ? 'Changing Password...' : 'Change Password'}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </Container>
  );
}
