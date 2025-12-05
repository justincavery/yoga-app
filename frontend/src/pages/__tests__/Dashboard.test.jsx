import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithRouter, mockAuthUser, clearAuthUser, userEvent } from '../../test/utils';
import Dashboard from '../Dashboard';
import apiClient from '../../lib/api';

// Mock the API client
vi.mock('../../lib/api', () => ({
  default: {
    getStats: vi.fn(),
    getHistory: vi.fn(),
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

describe('Dashboard Page', () => {
  const mockStats = {
    total_sessions: 15,
    total_practice_time_seconds: 18000,
    total_practice_time_hours: 5.0,
    average_session_duration_minutes: 20,
    current_streak_days: 3,
    completion_rate_percentage: 93.3,
    sessions_last_30_days: 12,
    most_practiced_sequences: [
      {
        sequence_id: 1,
        sequence_name: 'Morning Energy Flow',
        practice_count: 5,
      },
      {
        sequence_id: 2,
        sequence_name: 'Deep Stretch & Relaxation',
        practice_count: 4,
      },
    ],
  };

  const mockHistory = {
    sessions: [
      {
        session_id: 1,
        sequence_name: 'Morning Energy Flow',
        started_at: '2025-12-05T08:00:00Z',
        duration_seconds: 1200,
        completion_status: 'completed',
        sequence_difficulty: 'beginner',
      },
      {
        session_id: 2,
        sequence_name: 'Deep Stretch & Relaxation',
        started_at: '2025-12-04T19:00:00Z',
        duration_seconds: 1800,
        completion_status: 'completed',
        sequence_difficulty: 'beginner',
      },
      {
        session_id: 3,
        sequence_name: 'Core Strength Builder',
        started_at: '2025-12-03T17:00:00Z',
        duration_seconds: 1500,
        completion_status: 'completed',
        sequence_difficulty: 'intermediate',
      },
    ],
    total: 15,
    page: 1,
    page_size: 5,
    total_pages: 3,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthUser({
      user_id: 1,
      email: 'test@example.com',
      name: 'Test User',
      experience_level: 'beginner',
    });
    apiClient.getStats.mockResolvedValue(mockStats);
    apiClient.getHistory.mockResolvedValue(mockHistory);
  });

  afterEach(() => {
    clearAuthUser();
  });

  describe('Initial Rendering', () => {
    it('should render the dashboard header', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('YogaFlow')).toBeInTheDocument();
      });
    });

    it('should display welcome message with user name', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Welcome back, Test User!/i)).toBeInTheDocument();
      });
    });

    it('should show navigation links', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /Dashboard/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /Poses/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /Sequences/i })).toBeInTheDocument();
      });
    });

    it('should display user email in header', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('test@example.com')).toBeInTheDocument();
      });
    });

    it('should show logout button', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Logout/i })).toBeInTheDocument();
      });
    });
  });

  describe('Statistics Display', () => {
    it('should fetch and display practice statistics', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(apiClient.getStats).toHaveBeenCalled();
      });
    });

    it('should display total sessions count', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('15')).toBeInTheDocument();
        expect(screen.getByText(/Total Sessions/i)).toBeInTheDocument();
      });
    });

    it('should display total practice time in hours', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('5.0')).toBeInTheDocument();
        expect(screen.getByText(/Total Time/i)).toBeInTheDocument();
      });
    });

    it('should display current streak in days', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('3')).toBeInTheDocument();
        expect(screen.getByText(/Current Streak/i)).toBeInTheDocument();
      });
    });

    it('should show loading state while fetching stats', async () => {
      apiClient.getStats.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve(mockStats), 1000)));

      renderWithRouter(<Dashboard />);

      expect(screen.getByText(/Loading/i)).toBeInTheDocument();
    });

    it('should handle stats API error gracefully', async () => {
      apiClient.getStats.mockRejectedValue(new Error('Failed to fetch stats'));

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Unable to load statistics/i)).toBeInTheDocument();
      });
    });
  });

  describe('Recent Sessions Display', () => {
    it('should fetch recent practice sessions', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(apiClient.getHistory).toHaveBeenCalledWith(expect.anything(), {
          page: 1,
          page_size: 5,
        });
      });
    });

    it('should display recent sessions section', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Recent Sessions/i)).toBeInTheDocument();
      });
    });

    it('should show last 5 sessions', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
        expect(screen.getByText('Deep Stretch & Relaxation')).toBeInTheDocument();
        expect(screen.getByText('Core Strength Builder')).toBeInTheDocument();
      });
    });

    it('should display session duration for each session', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/20 min/i)).toBeInTheDocument(); // 1200 seconds
        expect(screen.getByText(/30 min/i)).toBeInTheDocument(); // 1800 seconds
        expect(screen.getByText(/25 min/i)).toBeInTheDocument(); // 1500 seconds
      });
    });

    it('should display difficulty level for each session', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getAllByText(/beginner/i).length).toBeGreaterThan(0);
        expect(screen.getByText(/intermediate/i)).toBeInTheDocument();
      });
    });

    it('should show empty state when no sessions exist', async () => {
      apiClient.getHistory.mockResolvedValue({
        sessions: [],
        total: 0,
        page: 1,
        page_size: 5,
        total_pages: 0,
      });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/No practice sessions yet/i)).toBeInTheDocument();
      });
    });

    it('should handle history API error gracefully', async () => {
      apiClient.getHistory.mockRejectedValue(new Error('Failed to fetch history'));

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Unable to load recent sessions/i)).toBeInTheDocument();
      });
    });
  });

  describe('Quick Action Buttons', () => {
    it('should display Start Practice button', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Start Practice/i })).toBeInTheDocument();
      });
    });

    it('should display View History button', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /View History/i })).toBeInTheDocument();
      });
    });

    it('should navigate to sequences when Start Practice clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Start Practice/i })).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /Start Practice/i }));

      expect(mockNavigate).toHaveBeenCalledWith('/sequences');
    });

    it('should navigate to history page when View History clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /View History/i })).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /View History/i }));

      expect(mockNavigate).toHaveBeenCalledWith('/history');
    });
  });

  describe('Practice Streak Calendar Preview', () => {
    it('should display streak calendar preview section', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Practice Streak/i)).toBeInTheDocument();
      });
    });

    it('should show current streak with fire emoji for active streaks', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/3 day streak/i)).toBeInTheDocument();
        expect(screen.getByText(/🔥/)).toBeInTheDocument();
      });
    });

    it('should show encouragement message for zero streak', async () => {
      apiClient.getStats.mockResolvedValue({
        ...mockStats,
        current_streak_days: 0,
      });

      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByText(/Start your practice streak today!/i)).toBeInTheDocument();
      });
    });
  });

  describe('Mobile Responsive Layout', () => {
    it('should use card-based layout', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        const cards = screen.getAllByRole('article');
        expect(cards.length).toBeGreaterThan(0);
      });
    });

    it('should apply responsive grid classes', async () => {
      const { container } = renderWithRouter(<Dashboard />);

      await waitFor(() => {
        const grid = container.querySelector('.grid');
        expect(grid).toBeInTheDocument();
        expect(grid).toHaveClass('grid-cols-1');
      });
    });
  });

  describe('Logout Functionality', () => {
    it('should logout and navigate to login when logout clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Logout/i })).toBeInTheDocument();
      });

      await user.click(screen.getByRole('button', { name: /Logout/i }));

      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  describe('Navigation Integration', () => {
    it('should navigate to poses page when Poses link clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /Poses/i })).toBeInTheDocument();
      });

      const posesLink = screen.getByRole('link', { name: /Poses/i });
      expect(posesLink).toHaveAttribute('href', '/poses');
    });

    it('should navigate to sequences page when Sequences link clicked', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /Sequences/i })).toBeInTheDocument();
      });

      const sequencesLink = screen.getByRole('link', { name: /Sequences/i });
      expect(sequencesLink).toHaveAttribute('href', '/sequences');
    });

    it('should have active Dashboard link', async () => {
      renderWithRouter(<Dashboard />);

      await waitFor(() => {
        const dashboardLink = screen.getByRole('link', { name: /Dashboard/i });
        expect(dashboardLink).toHaveAttribute('href', '/dashboard');
      });
    });
  });
});
