// Form validation utilities

// Email validation
export const validateEmail = (email) => {
  if (!email) {
    return 'Email is required';
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return 'Please enter a valid email address';
  }
  return null;
};

// Password validation
export const validatePassword = (password) => {
  if (!password) {
    return 'Password is required';
  }
  if (password.length < 8) {
    return 'Password must be at least 8 characters';
  }
  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter';
  }
  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter';
  }
  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least one number';
  }
  return null;
};

// Name validation
export const validateName = (name) => {
  if (!name) {
    return 'Name is required';
  }
  if (name.trim().length < 2) {
    return 'Name must be at least 2 characters';
  }
  return null;
};

// Experience level validation
export const validateExperienceLevel = (level) => {
  if (!level) {
    return 'Experience level is required';
  }
  const validLevels = ['beginner', 'intermediate', 'advanced'];
  if (!validLevels.includes(level.toLowerCase())) {
    return 'Please select a valid experience level';
  }
  return null;
};

// Password strength indicator
export const getPasswordStrength = (password) => {
  if (!password) return { strength: 0, label: '' };

  let strength = 0;

  // Length
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;

  // Character types
  if (/[a-z]/.test(password)) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^a-zA-Z0-9]/.test(password)) strength++;

  // Map strength to label and color
  if (strength <= 2) {
    return { strength, label: 'Weak', color: 'red' };
  } else if (strength <= 4) {
    return { strength, label: 'Medium', color: 'yellow' };
  } else {
    return { strength, label: 'Strong', color: 'green' };
  }
};

// Validate entire registration form
export const validateRegistrationForm = (formData) => {
  const errors = {};

  const emailError = validateEmail(formData.email);
  if (emailError) errors.email = emailError;

  const nameError = validateName(formData.name);
  if (nameError) errors.name = nameError;

  const passwordError = validatePassword(formData.password);
  if (passwordError) errors.password = passwordError;

  const levelError = validateExperienceLevel(formData.experience_level);
  if (levelError) errors.experience_level = levelError;

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Validate entire login form
export const validateLoginForm = (formData) => {
  const errors = {};

  const emailError = validateEmail(formData.email);
  if (emailError) errors.email = emailError;

  if (!formData.password) {
    errors.password = 'Password is required';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Validate forgot password form
export const validateForgotPasswordForm = (formData) => {
  const errors = {};

  const emailError = validateEmail(formData.email);
  if (emailError) errors.email = emailError;

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

// Validate password match
export const validatePasswordMatch = (password, confirmPassword) => {
  if (password !== confirmPassword) {
    return 'Passwords do not match';
  }
  return null;
};

// Validate reset password form
export const validateResetPasswordForm = (formData) => {
  const errors = {};

  const passwordError = validatePassword(formData.password);
  if (passwordError) errors.password = passwordError;

  const matchError = validatePasswordMatch(formData.password, formData.confirmPassword);
  if (matchError) errors.confirmPassword = matchError;

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};
