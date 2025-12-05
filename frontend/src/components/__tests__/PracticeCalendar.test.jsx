import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import { renderWithRouter, userEvent } from '../../test/utils';
import PracticeCalendar from '../PracticeCalendar';

describe('PracticeCalendar Component', () => {
  const mockOnDayClick = vi.fn();
  const mockOnMonthChange = vi.fn();

  const defaultProps = {
    month: 11, // December (0-indexed)
    year: 2025,
    practiceData: {},
    onDayClick: mockOnDayClick,
    onMonthChange: mockOnMonthChange,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Calendar Rendering', () => {
    it('should render calendar with month and year header', () => {
      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      expect(screen.getByText('December 2025')).toBeInTheDocument();
    });

    it('should render all day headers', () => {
      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      dayHeaders.forEach((day) => {
        expect(screen.getByText(day)).toBeInTheDocument();
      });
    });

    it('should render correct number of days for the month', () => {
      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      // December 2025 has 31 days
      for (let day = 1; day <= 31; day++) {
        expect(screen.getByText(String(day))).toBeInTheDocument();
      }
    });

    it('should render previous month navigation button', () => {
      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      const prevButton = screen.getByLabelText('Previous month');
      expect(prevButton).toBeInTheDocument();
    });

    it('should render next month navigation button', () => {
      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      const nextButton = screen.getByLabelText('Next month');
      expect(nextButton).toBeInTheDocument();
    });
  });

  describe('Practice Data Display', () => {
    it('should highlight days with practice sessions', () => {
      const practiceDataWithSessions = {
        '2025-12-05': { sessionCount: 2, totalDuration: 3600 },
        '2025-12-10': { sessionCount: 1, totalDuration: 1800 },
        '2025-12-15': { sessionCount: 3, totalDuration: 5400 },
      };

      renderWithRouter(
        <PracticeCalendar {...defaultProps} practiceData={practiceDataWithSessions} />
      );

      // Days with sessions should have practice indicator
      const day5 = screen.getByText('5').closest('button');
      const day10 = screen.getByText('10').closest('button');
      const day15 = screen.getByText('15').closest('button');

      expect(day5).toHaveClass('has-practice');
      expect(day10).toHaveClass('has-practice');
      expect(day15).toHaveClass('has-practice');
    });

    it('should show session count on days with multiple sessions', () => {
      const practiceDataWithSessions = {
        '2025-12-05': { sessionCount: 3, totalDuration: 5400 },
      };

      renderWithRouter(
        <PracticeCalendar {...defaultProps} practiceData={practiceDataWithSessions} />
      );

      const day5Button = screen.getByText('5').closest('button');
      expect(within(day5Button).getByText('3')).toBeInTheDocument();
    });

    it('should apply different color intensity based on session count', () => {
      const practiceDataWithSessions = {
        '2025-12-01': { sessionCount: 1, totalDuration: 1800 },
        '2025-12-05': { sessionCount: 2, totalDuration: 3600 },
        '2025-12-10': { sessionCount: 3, totalDuration: 5400 },
        '2025-12-15': { sessionCount: 5, totalDuration: 9000 },
      };

      renderWithRouter(
        <PracticeCalendar {...defaultProps} practiceData={practiceDataWithSessions} />
      );

      const day1 = screen.getByText('1').closest('button');
      const day5 = screen.getByText('5').closest('button');
      const day10 = screen.getByText('10').closest('button');
      const day15 = screen.getByText('15').closest('button');

      expect(day1).toHaveClass('intensity-low');
      expect(day5).toHaveClass('intensity-medium');
      expect(day10).toHaveClass('intensity-high');
      expect(day15).toHaveClass('intensity-very-high');
    });

    it('should highlight current day', () => {
      const today = new Date();
      const currentMonth = today.getMonth();
      const currentYear = today.getFullYear();
      const currentDay = today.getDate();

      renderWithRouter(
        <PracticeCalendar
          {...defaultProps}
          month={currentMonth}
          year={currentYear}
        />
      );

      const currentDayButton = screen.getByText(String(currentDay)).closest('button');
      expect(currentDayButton).toHaveClass('current-day');
    });
  });

  describe('User Interactions', () => {
    it('should call onDayClick when clicking a day with practice', async () => {
      const user = userEvent.setup();
      const practiceDataWithSessions = {
        '2025-12-05': { sessionCount: 2, totalDuration: 3600 },
      };

      renderWithRouter(
        <PracticeCalendar {...defaultProps} practiceData={practiceDataWithSessions} />
      );

      const day5Button = screen.getByText('5').closest('button');
      await user.click(day5Button);

      expect(mockOnDayClick).toHaveBeenCalledWith(new Date(2025, 11, 5));
    });

    it('should not call onDayClick when clicking a day without practice', async () => {
      const user = userEvent.setup();

      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      const day7Button = screen.getByText('7').closest('button');
      await user.click(day7Button);

      expect(mockOnDayClick).not.toHaveBeenCalled();
    });

    it('should navigate to previous month when clicking prev button', async () => {
      const user = userEvent.setup();

      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      const prevButton = screen.getByLabelText('Previous month');
      await user.click(prevButton);

      expect(mockOnMonthChange).toHaveBeenCalledWith(10, 2025); // November 2025
    });

    it('should navigate to next month when clicking next button', async () => {
      const user = userEvent.setup();

      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      const nextButton = screen.getByLabelText('Next month');
      await user.click(nextButton);

      expect(mockOnMonthChange).toHaveBeenCalledWith(0, 2026); // January 2026
    });

    it('should handle year transition when navigating from December to January', async () => {
      const user = userEvent.setup();

      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      const nextButton = screen.getByLabelText('Next month');
      await user.click(nextButton);

      expect(mockOnMonthChange).toHaveBeenCalledWith(0, 2026);
    });

    it('should handle year transition when navigating from January to December', async () => {
      const user = userEvent.setup();

      renderWithRouter(
        <PracticeCalendar {...defaultProps} month={0} year={2026} />
      );

      const prevButton = screen.getByLabelText('Previous month');
      await user.click(prevButton);

      expect(mockOnMonthChange).toHaveBeenCalledWith(11, 2025);
    });
  });

  describe('Edge Cases', () => {
    it('should handle months with different number of days', () => {
      // February 2025 (not a leap year) has 28 days
      renderWithRouter(
        <PracticeCalendar {...defaultProps} month={1} year={2025} />
      );

      expect(screen.getByText('28')).toBeInTheDocument();
      expect(screen.queryByText('29')).not.toBeInTheDocument();
    });

    it('should handle leap year February', () => {
      // February 2024 (leap year) has 29 days
      renderWithRouter(
        <PracticeCalendar {...defaultProps} month={1} year={2024} />
      );

      expect(screen.getByText('29')).toBeInTheDocument();
    });

    it('should handle empty practice data gracefully', () => {
      renderWithRouter(<PracticeCalendar {...defaultProps} practiceData={{}} />);

      // Should not crash and should render calendar
      expect(screen.getByText('December 2025')).toBeInTheDocument();
    });

    it('should handle undefined practice data gracefully', () => {
      renderWithRouter(
        <PracticeCalendar {...defaultProps} practiceData={undefined} />
      );

      // Should not crash and should render calendar
      expect(screen.getByText('December 2025')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have accessible navigation buttons', () => {
      renderWithRouter(<PracticeCalendar {...defaultProps} />);

      const prevButton = screen.getByLabelText('Previous month');
      const nextButton = screen.getByLabelText('Next month');

      expect(prevButton).toHaveAttribute('type', 'button');
      expect(nextButton).toHaveAttribute('type', 'button');
    });

    it('should have accessible day buttons', () => {
      const practiceDataWithSessions = {
        '2025-12-05': { sessionCount: 2, totalDuration: 3600 },
      };

      renderWithRouter(
        <PracticeCalendar {...defaultProps} practiceData={practiceDataWithSessions} />
      );

      const day5Button = screen.getByText('5').closest('button');
      expect(day5Button).toHaveAttribute('aria-label');
      expect(day5Button.getAttribute('aria-label')).toContain('December 5');
    });

    it('should indicate practice sessions in aria-label', () => {
      const practiceDataWithSessions = {
        '2025-12-05': { sessionCount: 2, totalDuration: 3600 },
      };

      renderWithRouter(
        <PracticeCalendar {...defaultProps} practiceData={practiceDataWithSessions} />
      );

      const day5Button = screen.getByText('5').closest('button');
      expect(day5Button.getAttribute('aria-label')).toContain('2 sessions');
    });
  });

  describe('Mobile Responsiveness', () => {
    it('should render with mobile-friendly classes', () => {
      const { container } = renderWithRouter(<PracticeCalendar {...defaultProps} />);

      const calendar = container.querySelector('.practice-calendar');
      expect(calendar).toHaveClass('mobile-responsive');
    });

    it('should have touch-friendly button sizes', () => {
      const practiceDataWithSessions = {
        '2025-12-05': { sessionCount: 2, totalDuration: 3600 },
      };

      renderWithRouter(
        <PracticeCalendar {...defaultProps} practiceData={practiceDataWithSessions} />
      );

      const day5Button = screen.getByText('5').closest('button');
      const buttonStyle = window.getComputedStyle(day5Button);

      // Minimum touch target size should be defined
      expect(day5Button).toHaveClass('touch-target');
    });
  });
});
