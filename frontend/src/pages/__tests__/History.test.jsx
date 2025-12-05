import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import { renderWithRouter, mockAuthUser, clearAuthUser, userEvent } from '../../test/utils';
import History from '../History';
import apiClient from '../../lib/api';

// Mock the API client
vi.mock('../../lib/api', () => ({
  default: {
    getCalendar: vi.fn(),
    getHistory: vi.fn(),
  },
}));

describe('History Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthUser();

    // Default mock response for calendar
    apiClient.getCalendar.mockResolvedValue({
      months: [
        {
          year: 2025,
          month: 12,
          days: [
            {
              practice_date: '2025-12-05',
              session_count: 2,
              total_duration_seconds: 3600,
            },
            {
              practice_date: '2025-12-10',
              session_count: 1,
              total_duration_seconds: 1800,
            },
          ],
        },
      ],
      total_days_practiced: 2,
    });

    // Default mock response for history
    apiClient.getHistory.mockResolvedValue({
      sessions: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 0,
    });
  });

  afterEach(() => {
    clearAuthUser();
  });

  describe('Initial Rendering', () => {
    it('should render page title', async () => {
      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText('Practice History')).toBeInTheDocument();
      });
    });

    it('should render calendar component', async () => {
      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
      });
    });

    it('should load calendar data on mount', async () => {
      renderWithRouter(<History />);

      await waitFor(() => {
        expect(apiClient.getCalendar).toHaveBeenCalled();
      });
    });

    it('should display total days practiced', async () => {
      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/2 days practiced/i)).toBeInTheDocument();
      });
    });
  });

  describe('Calendar Interaction', () => {
    it('should display practice sessions when clicking a day', async () => {
      const user = userEvent.setup();

      apiClient.getHistory.mockResolvedValue({
        sessions: [
          {
            session_id: 1,
            sequence_name: 'Morning Flow',
            sequence_difficulty: 'beginner',
            sequence_focus_area: 'flexibility',
            started_at: '2025-12-05T08:00:00Z',
            completed_at: '2025-12-05T08:30:00Z',
            duration_seconds: 1800,
            completion_status: 'completed',
          },
          {
            session_id: 2,
            sequence_name: 'Evening Stretch',
            sequence_difficulty: 'beginner',
            sequence_focus_area: 'relaxation',
            started_at: '2025-12-05T18:00:00Z',
            completed_at: '2025-12-05T18:30:00Z',
            duration_seconds: 1800,
            completion_status: 'completed',
          },
        ],
        total: 2,
        page: 1,
        page_size: 20,
        total_pages: 1,
      });

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
      });

      // Click on day 5
      const day5Button = screen.getByText('5').closest('button');
      await user.click(day5Button);

      await waitFor(() => {
        expect(apiClient.getHistory).toHaveBeenCalledWith(
          expect.objectContaining({
            start_date: expect.any(String),
            end_date: expect.any(String),
          })
        );
      });

      await waitFor(() => {
        expect(screen.getByText('Morning Flow')).toBeInTheDocument();
        expect(screen.getByText('Evening Stretch')).toBeInTheDocument();
      });
    });

    it('should navigate to different months', async () => {
      const user = userEvent.setup();

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
      });

      const nextButton = screen.getByLabelText('Next month');
      await user.click(nextButton);

      await waitFor(() => {
        expect(apiClient.getCalendar).toHaveBeenCalledWith(
          expect.objectContaining({
            start_date: expect.any(String),
            end_date: expect.any(String),
          })
        );
      });
    });

    it('should clear selected day when navigating months', async () => {
      const user = userEvent.setup();

      apiClient.getHistory.mockResolvedValue({
        sessions: [
          {
            session_id: 1,
            sequence_name: 'Morning Flow',
            sequence_difficulty: 'beginner',
            sequence_focus_area: 'flexibility',
            started_at: '2025-12-05T08:00:00Z',
            completed_at: '2025-12-05T08:30:00Z',
            duration_seconds: 1800,
            completion_status: 'completed',
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
        total_pages: 1,
      });

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
      });

      // Click on day 5
      const day5Button = screen.getByText('5').closest('button');
      await user.click(day5Button);

      await waitFor(() => {
        expect(screen.getByText('Morning Flow')).toBeInTheDocument();
      });

      // Navigate to next month
      const nextButton = screen.getByLabelText('Next month');
      await user.click(nextButton);

      // Session details should be cleared
      await waitFor(() => {
        expect(screen.queryByText('Morning Flow')).not.toBeInTheDocument();
      });
    });
  });

  describe('Session List Display', () => {
    it('should display session details correctly', async () => {
      const user = userEvent.setup();

      apiClient.getHistory.mockResolvedValue({
        sessions: [
          {
            session_id: 1,
            sequence_name: 'Morning Flow',
            sequence_difficulty: 'beginner',
            sequence_focus_area: 'flexibility',
            started_at: '2025-12-05T08:00:00Z',
            completed_at: '2025-12-05T08:30:00Z',
            duration_seconds: 1800,
            completion_status: 'completed',
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
        total_pages: 1,
      });

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
      });

      const day5Button = screen.getByText('5').closest('button');
      await user.click(day5Button);

      await waitFor(() => {
        expect(screen.getByText('Morning Flow')).toBeInTheDocument();
        expect(screen.getByText(/30 min/i)).toBeInTheDocument();
        expect(screen.getByText(/beginner/i)).toBeInTheDocument();
        expect(screen.getByText(/flexibility/i)).toBeInTheDocument();
      });
    });

    it('should show empty state when no sessions for selected day', async () => {
      const user = userEvent.setup();

      apiClient.getHistory.mockResolvedValue({
        sessions: [],
        total: 0,
        page: 1,
        page_size: 20,
        total_pages: 0,
      });

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
      });

      const day5Button = screen.getByText('5').closest('button');
      await user.click(day5Button);

      await waitFor(() => {
        expect(screen.getByText(/No sessions found/i)).toBeInTheDocument();
      });
    });

    it('should display completion status badges', async () => {
      const user = userEvent.setup();

      apiClient.getHistory.mockResolvedValue({
        sessions: [
          {
            session_id: 1,
            sequence_name: 'Morning Flow',
            sequence_difficulty: 'beginner',
            sequence_focus_area: 'flexibility',
            started_at: '2025-12-05T08:00:00Z',
            completed_at: '2025-12-05T08:30:00Z',
            duration_seconds: 1800,
            completion_status: 'completed',
          },
          {
            session_id: 2,
            sequence_name: 'Evening Flow',
            sequence_difficulty: 'intermediate',
            sequence_focus_area: 'strength',
            started_at: '2025-12-05T18:00:00Z',
            completed_at: null,
            duration_seconds: 900,
            completion_status: 'partial',
          },
        ],
        total: 2,
        page: 1,
        page_size: 20,
        total_pages: 1,
      });

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
      });

      const day5Button = screen.getByText('5').closest('button');
      await user.click(day5Button);

      await waitFor(() => {
        expect(screen.getByText('Completed')).toBeInTheDocument();
        expect(screen.getByText('Partial')).toBeInTheDocument();
      });
    });
  });

  describe('Date Range Filtering', () => {
    it('should allow selecting a date range', async () => {
      const user = userEvent.setup();

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText('Practice History')).toBeInTheDocument();
      });

      const startDateInput = screen.getByLabelText(/start date/i);
      const endDateInput = screen.getByLabelText(/end date/i);

      await user.type(startDateInput, '2025-12-01');
      await user.type(endDateInput, '2025-12-31');

      const applyButton = screen.getByRole('button', { name: /apply/i });
      await user.click(applyButton);

      await waitFor(() => {
        expect(apiClient.getCalendar).toHaveBeenCalledWith(
          expect.objectContaining({
            start_date: '2025-12-01',
            end_date: '2025-12-31',
          })
        );
      });
    });

    it('should show error for invalid date range', async () => {
      const user = userEvent.setup();

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText('Practice History')).toBeInTheDocument();
      });

      const startDateInput = screen.getByLabelText(/start date/i);
      const endDateInput = screen.getByLabelText(/end date/i);

      // End date before start date
      await user.type(startDateInput, '2025-12-31');
      await user.type(endDateInput, '2025-12-01');

      const applyButton = screen.getByRole('button', { name: /apply/i });
      await user.click(applyButton);

      await waitFor(() => {
        expect(screen.getByText(/end date must be after start date/i)).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading state while fetching calendar data', async () => {
      apiClient.getCalendar.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      );

      renderWithRouter(<History />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should show loading state while fetching session details', async () => {
      const user = userEvent.setup();

      apiClient.getHistory.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      );

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
      });

      const day5Button = screen.getByText('5').closest('button');
      await user.click(day5Button);

      expect(screen.getByText(/Loading sessions/i)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error message when calendar fetch fails', async () => {
      apiClient.getCalendar.mockRejectedValue({
        status: 500,
        message: 'Internal server error',
      });

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load calendar data/i)).toBeInTheDocument();
      });
    });

    it('should display error message when session fetch fails', async () => {
      const user = userEvent.setup();

      apiClient.getHistory.mockRejectedValue({
        status: 500,
        message: 'Internal server error',
      });

      renderWithRouter(<History />);

      await waitFor(() => {
        expect(screen.getByText(/December 2025/i)).toBeInTheDocument();
      });

      const day5Button = screen.getByText('5').closest('button');
      await user.click(day5Button);

      await waitFor(() => {
        expect(screen.getByText(/Failed to load sessions/i)).toBeInTheDocument();
      });
    });
  });

  describe('Mobile Responsiveness', () => {
    it('should render mobile-friendly layout', () => {
      const { container } = renderWithRouter(<History />);

      const historyPage = container.querySelector('.history-page');
      expect(historyPage).toHaveClass('mobile-responsive');
    });

    it('should stack calendar and session list on mobile', () => {
      // Simulate mobile viewport
      global.innerWidth = 375;
      global.dispatchEvent(new Event('resize'));

      const { container } = renderWithRouter(<History />);

      const layout = container.querySelector('.history-layout');
      expect(layout).toHaveClass('mobile-stack');
    });
  });
});
