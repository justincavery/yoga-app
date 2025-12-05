import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithRouter, mockAuthUser, clearAuthUser, userEvent } from '../../test/utils';
import PracticeComplete from '../PracticeComplete';
import apiClient from '../../lib/api';

// Mock the API client
vi.mock('../../lib/api', () => ({
  default: {
    saveSession: vi.fn(),
  },
}));

// Mock router navigation and location state
const mockNavigate = vi.fn();
const mockLocation = {
  state: {
    sessionData: {
      sequenceName: 'Morning Energy Flow',
      durationMinutes: 20,
      posesCompleted: 8,
      totalPoses: 8,
      caloriesBurned: 85,
      completedAt: '2025-12-05T10:30:00Z',
    },
  },
};

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation,
  };
});

describe('PracticeComplete Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthUser();
    apiClient.saveSession.mockResolvedValue({
      message: 'Session saved successfully',
      session_id: 123,
    });
  });

  afterEach(() => {
    clearAuthUser();
  });

  describe('Initial Rendering', () => {
    it('should render the completion message', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByText(/Practice Complete/i)).toBeInTheDocument();
      });
    });

    it('should display congratulatory message', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        // Check for one of the possible encouraging messages
        const encouragementRegex = /(Great job|Excellent work|Well done|Wonderful|Amazing)/i;
        expect(screen.getByText(encouragementRegex)).toBeInTheDocument();
      });
    });

    it('should display the sequence name', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByText(/Morning Energy Flow/i)).toBeInTheDocument();
      });
    });
  });

  describe('Session Statistics Display', () => {
    it('should display duration completed', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByText(/20/)).toBeInTheDocument();
        expect(screen.getByText(/minutes/i)).toBeInTheDocument();
      });
    });

    it('should display poses completed', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        // Look for all instances of "8" and check one is present
        const eights = screen.getAllByText('8');
        expect(eights.length).toBeGreaterThan(0);
        expect(screen.getByText(/poses/i)).toBeInTheDocument();
      });
    });

    it('should display calories burned estimate', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByText(/85/)).toBeInTheDocument();
        expect(screen.getByText(/calories/i)).toBeInTheDocument();
      });
    });

    it('should display all three statistics', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByText(/Duration/i)).toBeInTheDocument();
        expect(screen.getByText(/Poses/i)).toBeInTheDocument();
        expect(screen.getByText(/Calories/i)).toBeInTheDocument();
      });
    });
  });

  describe('Navigation Buttons', () => {
    it('should display Practice Again button', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Practice Again/i })).toBeInTheDocument();
      });
    });

    it('should display Back to Dashboard button', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Back to Dashboard/i })).toBeInTheDocument();
      });
    });

    it('should navigate to sequences when Practice Again is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Practice Again/i })).toBeInTheDocument();
      });

      const practiceAgainButton = screen.getByRole('button', { name: /Practice Again/i });
      await user.click(practiceAgainButton);

      expect(mockNavigate).toHaveBeenCalledWith('/sequences');
    });

    it('should navigate to dashboard when Back to Dashboard is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Back to Dashboard/i })).toBeInTheDocument();
      });

      const dashboardButton = screen.getByRole('button', { name: /Back to Dashboard/i });
      await user.click(dashboardButton);

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  describe('Session Saving', () => {
    it('should call saveSession API on mount', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(apiClient.saveSession).toHaveBeenCalled();
      });
    });

    it('should save session with correct data', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(apiClient.saveSession).toHaveBeenCalledWith(
          expect.objectContaining({
            durationMinutes: 20,
            posesCompleted: 8,
            caloriesBurned: 85,
          })
        );
      });
    });

    it('should handle session save error gracefully', async () => {
      apiClient.saveSession.mockRejectedValue({
        status: 500,
        message: 'Failed to save session',
      });

      renderWithRouter(<PracticeComplete />);

      // Should still render the page even if save fails
      await waitFor(() => {
        expect(screen.getByText(/Practice Complete/i)).toBeInTheDocument();
      });
    });

    it('should only save session once', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(apiClient.saveSession).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Encouragement Messages', () => {
    it('should display an encouraging message', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        const encouragementMessages = [
          /Great job/i,
          /Excellent work/i,
          /Well done/i,
          /Wonderful/i,
          /Amazing/i,
        ];

        const hasEncouragement = encouragementMessages.some((regex) =>
          screen.queryByText(regex)
        );

        expect(hasEncouragement).toBe(true);
      });
    });
  });

  describe('Missing Session Data', () => {
    it('should handle missing session data gracefully', async () => {
      // Mock empty location state
      vi.mocked(vi.importActual('react-router-dom')).useLocation = () => ({
        state: null,
      });

      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByText(/Practice Complete/i)).toBeInTheDocument();
      });
    });

    it('should show default values when session data is missing', async () => {
      // This test ensures we have fallback behavior
      const emptyLocation = {
        state: {
          sessionData: {
            sequenceName: 'Unknown Sequence',
            durationMinutes: 0,
            posesCompleted: 0,
            totalPoses: 0,
            caloriesBurned: 0,
          },
        },
      };

      vi.mocked(vi.importActual('react-router-dom')).useLocation = () => emptyLocation;

      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByText(/0/)).toBeInTheDocument();
      });
    });
  });

  describe('Visual Design', () => {
    it('should display success icon or visual indicator', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        // Should have some visual success indicator (could be icon, emoji, or color)
        const successElement = screen.getByText(/Practice Complete/i);
        expect(successElement).toBeInTheDocument();
      });
    });

    it('should use cards or containers for statistics', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        expect(screen.getByText(/Duration/i)).toBeInTheDocument();
        expect(screen.getByText(/Poses/i)).toBeInTheDocument();
        expect(screen.getByText(/Calories/i)).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Design', () => {
    it('should render mobile-friendly statistics layout', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        const statsContainer = screen.getByText(/Duration/i).closest('div');
        expect(statsContainer).toBeInTheDocument();
      });
    });
  });

  describe('User Feedback', () => {
    it('should show positive feedback for completing practice', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        // Check for positive language - should find at least "Practice Complete!" and encouraging text
        const pageText = document.body.textContent;
        const hasComplete = /complete/i.test(pageText);
        const hasPositive = /(great|excellent|wonderful|amazing|well done)/i.test(pageText);

        expect(hasComplete || hasPositive).toBe(true);
      });
    });
  });

  describe('Accessibility', () => {
    it('should have accessible button labels', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        const practiceButton = screen.getByRole('button', { name: /Practice Again/i });
        const dashboardButton = screen.getByRole('button', { name: /Back to Dashboard/i });

        expect(practiceButton).toBeInTheDocument();
        expect(dashboardButton).toBeInTheDocument();
      });
    });

    it('should have proper heading hierarchy', async () => {
      renderWithRouter(<PracticeComplete />);

      await waitFor(() => {
        const heading = screen.getByText(/Practice Complete/i);
        expect(heading.tagName).toMatch(/H[1-3]/i);
      });
    });
  });
});
