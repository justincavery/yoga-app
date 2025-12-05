import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import useAuthStore from '../store/authStore';

// Custom render function that includes router
export function renderWithRouter(ui, { route = '/', ...renderOptions } = {}) {
  window.history.pushState({}, 'Test page', route);

  return render(ui, {
    wrapper: ({ children }) => <BrowserRouter>{children}</BrowserRouter>,
    ...renderOptions,
  });
}

// Mock authenticated user
export function mockAuthUser(user = {
  user_id: 1,
  email: 'test@example.com',
  name: 'Test User',
  experience_level: 'beginner',
}) {
  useAuthStore.setState({
    isAuthenticated: true,
    user: user,
    token: 'mock-token',
  });
}

// Clear auth state
export function clearAuthUser() {
  useAuthStore.setState({
    isAuthenticated: false,
    user: null,
    token: null,
  });
}

// Export everything from testing library
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
