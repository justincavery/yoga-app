import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Statistics from '../Statistics';
import apiClient from '../../lib/api';
import useAuthStore from '../../store/authStore';

// Mock dependencies
vi.mock('../../lib/api', () => ({
  default: {
    get: vi.fn(),
  },
}));
vi.mock('../../store/authStore');
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: vi.fn(() => vi.fn()),
  };
});

describe('Statistics Page', () => {
  const mockStatsData = {
    total_sessions: 42,
    total_practice_time_seconds: 36000,
    total_practice_time_hours: 10,
    average_session_duration_minutes: 25.5,
    current_streak_days: 5,
    completion_rate_percentage: 95.5,
    sessions_last_30_days: 12,
    most_practiced_sequences: [
      { sequence_id: 1, name: 'Morning Flow', practice_count: 15 },
      { sequence_id: 2, name: 'Evening Relaxation', practice_count: 10 },
      { sequence_id: 3, name: 'Power Yoga', practice_count: 8 },
    ],
  };

  const mockUser = {
    user_id: 1,
    email: 'test@example.com',
    name: 'Test User',
  };

  beforeEach(() => {
    useAuthStore.mockReturnValue(mockUser);
    apiClient.get.mockResolvedValue({ data: mockStatsData });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    apiClient.get.mockImplementation(() => new Promise(() => {}));

    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('fetches statistics data on mount', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith('/api/v1/stats');
    });
  });

  it('displays total sessions count', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Total Sessions')).toBeInTheDocument();
      expect(screen.getByText('42')).toBeInTheDocument();
    });
  });

  it('displays total practice time in formatted hours', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Total Practice Time/i)).toBeInTheDocument();
      expect(screen.getByText('10 hours')).toBeInTheDocument();
    });
  });

  it('displays average session duration in minutes', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Average Duration/i)).toBeInTheDocument();
      expect(screen.getByText(/25\.5 min/i)).toBeInTheDocument();
    });
  });

  it('displays current streak with days', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Current Streak/i)).toBeInTheDocument();
      expect(screen.getByText(/5 days/i)).toBeInTheDocument();
    });
  });

  it('displays completion rate percentage', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Completion Rate/i)).toBeInTheDocument();
      expect(screen.getByText(/95\.5%/i)).toBeInTheDocument();
    });
  });

  it('displays sessions in last 30 days', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Last 30 Days/i)).toBeInTheDocument();
      expect(screen.getByText('12')).toBeInTheDocument();
    });
  });

  it('displays most practiced sequences', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Most Practiced Sequences/i)).toBeInTheDocument();
      expect(screen.getByText('Morning Flow')).toBeInTheDocument();
      expect(screen.getByText(/15 sessions/i)).toBeInTheDocument();
      expect(screen.getByText('Evening Relaxation')).toBeInTheDocument();
      expect(screen.getByText(/10 sessions/i)).toBeInTheDocument();
      expect(screen.getByText('Power Yoga')).toBeInTheDocument();
      expect(screen.getByText(/8 sessions/i)).toBeInTheDocument();
    });
  });

  it('handles zero sessions gracefully', async () => {
    const emptyStats = {
      ...mockStatsData,
      total_sessions: 0,
      total_practice_time_hours: 0,
      average_session_duration_minutes: 0,
      current_streak_days: 0,
      completion_rate_percentage: 0,
      sessions_last_30_days: 0,
      most_practiced_sequences: [],
    };

    apiClient.get.mockResolvedValue({ data: emptyStats });

    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Total Sessions')).toBeInTheDocument();
      // There are multiple zeros on the page which is expected
      const zeros = screen.getAllByText('0');
      expect(zeros.length).toBeGreaterThan(0);
    });
  });

  it('displays error message when API call fails', async () => {
    apiClient.get.mockRejectedValue(new Error('Failed to fetch statistics'));

    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
      expect(screen.getByText(/failed to load statistics/i)).toBeInTheDocument();
    });
  });

  it('displays retry button on error', async () => {
    apiClient.get.mockRejectedValue(new Error('Failed to fetch statistics'));

    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });
  });

  it('has responsive grid layout', async () => {
    const { container } = render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      const grid = container.querySelector('[data-testid="stats-grid"]');
      expect(grid).toBeInTheDocument();
    });
  });

  it('displays page title', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /statistics/i })).toBeInTheDocument();
    });
  });

  it('formats time with proper units (hours)', async () => {
    const statsWithHours = {
      ...mockStatsData,
      total_practice_time_hours: 10.5,
    };

    apiClient.get.mockResolvedValue({ data: statsWithHours });

    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/10\.5 hours/i)).toBeInTheDocument();
    });
  });

  it('handles singular day in streak', async () => {
    const statsWithOneDay = {
      ...mockStatsData,
      current_streak_days: 1,
    };

    apiClient.get.mockResolvedValue({ data: statsWithOneDay });

    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/1 day/i)).toBeInTheDocument();
    });
  });

  it('includes navigation back to dashboard', async () => {
    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      const backLink = screen.getByRole('link', { name: /back|dashboard/i });
      expect(backLink).toBeInTheDocument();
    });
  });

  it('uses StatCard components for displaying stats', async () => {
    const { container } = render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      // Should have multiple stat cards
      const cards = container.querySelectorAll('[data-testid="stat-card"]');
      expect(cards.length).toBeGreaterThan(0);
    });
  });

  it('shows empty state message when no sequences practiced', async () => {
    const statsNoSequences = {
      ...mockStatsData,
      most_practiced_sequences: [],
    };

    apiClient.get.mockResolvedValue({ data: statsNoSequences });

    render(
      <BrowserRouter>
        <Statistics />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/no sequences practiced yet/i)).toBeInTheDocument();
    });
  });
});
