import { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './ui';

/**
 * PracticeCalendar Component
 *
 * Displays a monthly calendar view with practice session indicators.
 *
 * @param {Object} props
 * @param {number} props.month - Current month (0-11, 0 = January)
 * @param {number} props.year - Current year
 * @param {Object} props.practiceData - Practice data object with dates as keys
 *   Format: { 'YYYY-MM-DD': { sessionCount: number, totalDuration: number } }
 * @param {Function} props.onDayClick - Callback when clicking a day with practice
 * @param {Function} props.onMonthChange - Callback when changing months
 */
function PracticeCalendar({ month, year, practiceData = {}, onDayClick, onMonthChange }) {
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  // Calculate calendar grid
  const calendarDays = useMemo(() => {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];

    // Add empty cells for days before the first of the month
    for (let index = 0; index < startingDayOfWeek; index++) {
      days.push({ date: null, isEmpty: true });
    }

    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const dateString = formatDateKey(date);
      const practice = practiceData[dateString];

      days.push({
        date,
        day,
        dateString,
        isEmpty: false,
        hasPractice: !!practice,
        sessionCount: practice?.sessionCount || 0,
        totalDuration: practice?.totalDuration || 0,
      });
    }

    return days;
  }, [month, year, practiceData]);

  // Format date as YYYY-MM-DD
  function formatDateKey(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // Check if date is today
  function isToday(date) {
    if (!date) return false;
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  }

  // Get intensity class based on session count
  function getIntensityClass(sessionCount) {
    if (sessionCount === 0) return '';
    if (sessionCount === 1) return 'intensity-low';
    if (sessionCount === 2) return 'intensity-medium';
    if (sessionCount <= 4) return 'intensity-high';
    return 'intensity-very-high';
  }

  // Handle previous month navigation
  function handlePrevMonth() {
    if (month === 0) {
      onMonthChange(11, year - 1);
    } else {
      onMonthChange(month - 1, year);
    }
  }

  // Handle next month navigation
  function handleNextMonth() {
    if (month === 11) {
      onMonthChange(0, year + 1);
    } else {
      onMonthChange(month + 1, year);
    }
  }

  // Handle day click
  function handleDayClick(dayData) {
    if (dayData.hasPractice && onDayClick) {
      onDayClick(dayData.date);
    }
  }

  // Format duration for display (minutes)
  function formatDuration(seconds) {
    const minutes = Math.round(seconds / 60);
    return `${minutes} min`;
  }

  return (
    <div className="practice-calendar mobile-responsive">
      {/* Calendar Header */}
      <div className="calendar-header">
        <Button
          variant="ghost"
          size="sm"
          onClick={handlePrevMonth}
          aria-label="Previous month"
          type="button"
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>

        <h2 className="calendar-title">
          {monthNames[month]} {year}
        </h2>

        <Button
          variant="ghost"
          size="sm"
          onClick={handleNextMonth}
          aria-label="Next month"
          type="button"
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
      </div>

      {/* Day Headers */}
      <div className="calendar-grid">
        <div className="day-headers">
          {dayNames.map((dayName) => (
            <div key={dayName} className="day-header">
              {dayName}
            </div>
          ))}
        </div>

        {/* Calendar Days */}
        <div className="calendar-days">
          {calendarDays.map((dayData, index) => {
            if (dayData.isEmpty) {
              return <div key={`empty-${index}`} className="calendar-day empty" />;
            }

            const today = isToday(dayData.date);
            const intensityClass = getIntensityClass(dayData.sessionCount);
            const dayClasses = [
              'calendar-day',
              'touch-target',
              dayData.hasPractice && 'has-practice',
              today && 'current-day',
              intensityClass,
            ]
              .filter(Boolean)
              .join(' ');

            const ariaLabel = dayData.hasPractice
              ? `${monthNames[month]} ${dayData.day}, ${dayData.sessionCount} sessions`
              : `${monthNames[month]} ${dayData.day}`;

            return (
              <button
                key={dayData.dateString}
                type="button"
                className={dayClasses}
                onClick={() => handleDayClick(dayData)}
                disabled={!dayData.hasPractice}
                aria-label={ariaLabel}
              >
                <span className="day-number">{dayData.day}</span>
                {dayData.hasPractice && (
                  <span className="session-indicator">
                    {dayData.sessionCount > 1 && (
                      <span className="session-count">{dayData.sessionCount}</span>
                    )}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="calendar-legend">
        <div className="legend-item">
          <div className="legend-dot intensity-low" />
          <span>1 session</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot intensity-medium" />
          <span>2 sessions</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot intensity-high" />
          <span>3-4 sessions</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot intensity-very-high" />
          <span>5+ sessions</span>
        </div>
      </div>

      <style>{`
        .practice-calendar {
          width: 100%;
          padding: 1rem;
        }

        .calendar-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }

        .calendar-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
        }

        .calendar-grid {
          background: white;
          border-radius: 0.5rem;
          overflow: hidden;
          box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        }

        .day-headers {
          display: grid;
          grid-template-columns: repeat(7, 1fr);
          background: #f9fafb;
          border-bottom: 1px solid #e5e7eb;
        }

        .day-header {
          padding: 0.75rem;
          text-align: center;
          font-size: 0.875rem;
          font-weight: 600;
          color: #6b7280;
          text-transform: uppercase;
        }

        .calendar-days {
          display: grid;
          grid-template-columns: repeat(7, 1fr);
          gap: 1px;
          background: #e5e7eb;
        }

        .calendar-day {
          aspect-ratio: 1;
          background: white;
          border: none;
          padding: 0.5rem;
          position: relative;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: flex-start;
          cursor: default;
          transition: all 0.2s;
          min-height: 3rem;
        }

        .calendar-day.touch-target {
          min-height: 44px;
        }

        .calendar-day.empty {
          background: #f9fafb;
        }

        .calendar-day.has-practice {
          cursor: pointer;
          background: #dbeafe;
        }

        .calendar-day.has-practice:hover:not(:disabled) {
          background: #bfdbfe;
          transform: scale(1.05);
        }

        .calendar-day.current-day {
          border: 2px solid #3b82f6;
        }

        .calendar-day.intensity-low {
          background: #dbeafe;
        }

        .calendar-day.intensity-medium {
          background: #93c5fd;
        }

        .calendar-day.intensity-high {
          background: #60a5fa;
        }

        .calendar-day.intensity-very-high {
          background: #3b82f6;
          color: white;
        }

        .calendar-day.intensity-very-high .day-number {
          color: white;
        }

        .calendar-day:disabled {
          cursor: default;
        }

        .day-number {
          font-size: 0.875rem;
          font-weight: 500;
          color: #1f2937;
          margin-bottom: 0.25rem;
        }

        .session-indicator {
          position: absolute;
          bottom: 0.25rem;
          right: 0.25rem;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .session-count {
          font-size: 0.75rem;
          font-weight: 600;
          background: #1f2937;
          color: white;
          border-radius: 9999px;
          width: 1.25rem;
          height: 1.25rem;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .intensity-very-high .session-count {
          background: white;
          color: #3b82f6;
        }

        .calendar-legend {
          display: flex;
          justify-content: center;
          gap: 1.5rem;
          margin-top: 1.5rem;
          flex-wrap: wrap;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .legend-dot {
          width: 1rem;
          height: 1rem;
          border-radius: 0.25rem;
        }

        /* Mobile Responsive Styles */
        @media (max-width: 640px) {
          .practice-calendar {
            padding: 0.5rem;
          }

          .calendar-title {
            font-size: 1rem;
          }

          .day-header {
            padding: 0.5rem;
            font-size: 0.75rem;
          }

          .calendar-day {
            padding: 0.25rem;
            min-height: 2.5rem;
          }

          .day-number {
            font-size: 0.75rem;
          }

          .session-count {
            font-size: 0.625rem;
            width: 1rem;
            height: 1rem;
          }

          .calendar-legend {
            gap: 0.75rem;
            font-size: 0.75rem;
          }

          .legend-dot {
            width: 0.75rem;
            height: 0.75rem;
          }
        }
      `}</style>
    </div>
  );
}

export default PracticeCalendar;
