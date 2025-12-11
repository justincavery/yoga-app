import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Calendar, Clock, TrendingUp, LogOut } from 'lucide-react';
import PracticeCalendar from '../components/PracticeCalendar';
import { Container } from '../components/layout';
import { Card, Badge, Button, Input, Spinner } from '../components/ui';
import MobileNav from '../components/MobileNav';
import apiClient from '../lib/api';
import useAuthStore from '../store/authStore';

function History() {
  const navigate = useNavigate();
  const { user, accessToken: token, logout } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionsError, setSessionsError] = useState(null);

  // Calendar state
  const currentDate = new Date();
  const [currentMonth, setCurrentMonth] = useState(currentDate.getMonth());
  const [currentYear, setCurrentYear] = useState(currentDate.getFullYear());
  const [calendarData, setCalendarData] = useState({});
  const [totalDaysPracticed, setTotalDaysPracticed] = useState(0);

  // Selected day and sessions
  const [selectedDate, setSelectedDate] = useState(null);
  const [sessions, setSessions] = useState([]);

  // Date range filter
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [dateRangeError, setDateRangeError] = useState('');

  // Load calendar data
  useEffect(() => {
    loadCalendarData();
  }, [currentMonth, currentYear]);

  async function loadCalendarData() {
    try {
      setLoading(true);
      setError(null);

      // Calculate date range for current month
      const start = new Date(currentYear, currentMonth, 1);
      const end = new Date(currentYear, currentMonth + 1, 0);

      // Extend range to include previous and next months for smoother navigation
      const rangeStart = new Date(currentYear, currentMonth - 1, 1);
      const rangeEnd = new Date(currentYear, currentMonth + 2, 0);

      const params = {
        start_date: rangeStart.toISOString(),
        end_date: rangeEnd.toISOString(),
      };

      const data = await apiClient.getCalendar(params);

      // Transform calendar data into a flat object for easy lookup
      const practiceDataMap = {};
      data.months.forEach((monthData) => {
        monthData.days.forEach((dayData) => {
          practiceDataMap[dayData.practice_date] = {
            sessionCount: dayData.session_count,
            totalDuration: dayData.total_duration_seconds,
          };
        });
      });

      setCalendarData(practiceDataMap);
      setTotalDaysPracticed(data.total_days_practiced);
    } catch (error) {
      console.error('Failed to load calendar data:', error);
      setError('Failed to load calendar data. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function loadSessionsForDate(date) {
    try {
      setSessionsLoading(true);
      setSessionsError(null);

      // Create date range for the selected day
      const startOfDay = new Date(date);
      startOfDay.setHours(0, 0, 0, 0);

      const endOfDay = new Date(date);
      endOfDay.setHours(23, 59, 59, 999);

      const params = {
        start_date: startOfDay.toISOString(),
        end_date: endOfDay.toISOString(),
        page: 1,
        page_size: 50,
      };

      const data = await apiClient.getHistory(params);
      setSessions(data.sessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
      setSessionsError('Failed to load sessions. Please try again.');
    } finally {
      setSessionsLoading(false);
    }
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  function handleDayClick(date) {
    setSelectedDate(date);
    loadSessionsForDate(date);
  }

  function handleMonthChange(month, year) {
    setCurrentMonth(month);
    setCurrentYear(year);
    setSelectedDate(null);
    setSessions([]);
  }

  function handleDateRangeFilter() {
    setDateRangeError('');

    if (!startDate || !endDate) {
      setDateRangeError('Please select both start and end dates');
      return;
    }

    const start = new Date(startDate);
    const end = new Date(endDate);

    if (end < start) {
      setDateRangeError('End date must be after start date');
      return;
    }

    // Load calendar data for the specified range
    loadCalendarDataForRange(start, end);
  }

  async function loadCalendarDataForRange(start, end) {
    try {
      setLoading(true);
      setError(null);

      const params = {
        start_date: start.toISOString(),
        end_date: end.toISOString(),
      };

      const data = await apiClient.getCalendar(params);

      const practiceDataMap = {};
      data.months.forEach((monthData) => {
        monthData.days.forEach((dayData) => {
          practiceDataMap[dayData.practice_date] = {
            sessionCount: dayData.session_count,
            totalDuration: dayData.total_duration_seconds,
          };
        });
      });

      setCalendarData(practiceDataMap);
      setTotalDaysPracticed(data.total_days_practiced);

      // Update current month/year to show the start of the range
      setCurrentMonth(start.getMonth());
      setCurrentYear(start.getFullYear());
    } catch (error) {
      console.error('Failed to load calendar data:', error);
      setError('Failed to load calendar data. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function formatDuration(seconds) {
    const minutes = Math.round(seconds / 60);
    return `${minutes} min`;
  }

  function getStatusBadgeVariant(status) {
    switch (status) {
      case 'completed':
        return 'success';
      case 'partial':
        return 'warning';
      case 'abandoned':
        return 'danger';
      default:
        return 'default';
    }
  }

  function getStatusText(status) {
    return status.charAt(0).toUpperCase() + status.slice(1);
  }

  if (loading && Object.keys(calendarData).length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner role="status" aria-label="Loading calendar data" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="bg-white border-b border-neutral-200 shadow-sm">
        <Container>
          <div className="py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-primary-600">YogaFlow</h1>
              <nav className="hidden sm:flex items-center gap-4 ml-8">
                <Link to="/dashboard" className="text-neutral-700 hover:text-primary-600 font-medium">
                  Dashboard
                </Link>
                <Link to="/poses" className="text-neutral-700 hover:text-primary-600 font-medium">
                  Poses
                </Link>
                <Link to="/sequences" className="text-neutral-700 hover:text-primary-600 font-medium">
                  Sequences
                </Link>
                <Link to="/history" className="text-primary-600 font-medium">
                  History
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-neutral-900">{user?.name}</p>
                <p className="text-xs text-neutral-600">{user?.email}</p>
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout} icon={<LogOut size={16} />} className="hidden sm:flex">
                Logout
              </Button>
              <MobileNav />
            </div>
          </div>
        </Container>
      </header>

      {/* Main Content */}
      <Container>
        <div className="py-8">
          {/* Page Header */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Practice History</h2>
            <p className="text-gray-600">Track your yoga practice journey</p>
          </div>

          {/* Stats Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <Card>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Calendar className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Days Practiced</p>
                  <p className="text-2xl font-bold text-gray-900">{totalDaysPracticed}</p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-green-100 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Current Month</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {new Date(currentYear, currentMonth).toLocaleString('en-US', { month: 'long' })}
                  </p>
                </div>
              </div>
            </Card>

            <Card>
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <Clock className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Selected Date</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {selectedDate
                      ? selectedDate.toLocaleString('en-US', { month: 'short', day: 'numeric' })
                      : '-'}
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Date Range Filter */}
          <Card className="mb-8">
            <h3 className="text-lg font-semibold mb-4">Filter by Date Range</h3>
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <Input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(event) => setStartDate(event.target.value)}
                />
              </div>
              <div className="flex-1">
                <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <Input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(event) => setEndDate(event.target.value)}
                />
              </div>
              <div className="flex items-end">
                <Button onClick={handleDateRangeFilter}>Apply</Button>
              </div>
            </div>
            {dateRangeError && (
              <p className="text-sm text-red-600 mt-2">{dateRangeError}</p>
            )}
          </Card>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Main Content Layout */}
          <div className="history-layout mobile-stack grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Calendar Section */}
            <div>
              <Card>
                <h2 className="text-xl font-semibold mb-4">Calendar View</h2>
                <PracticeCalendar
                  month={currentMonth}
                  year={currentYear}
                  practiceData={calendarData}
                  onDayClick={handleDayClick}
                  onMonthChange={handleMonthChange}
                />
              </Card>
            </div>

            {/* Session List Section */}
            <div>
              <Card>
                <h2 className="text-xl font-semibold mb-4">
                  {selectedDate
                    ? `Sessions for ${selectedDate.toLocaleString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric',
                      })}`
                    : 'Select a day to view sessions'}
                </h2>

                {sessionsLoading ? (
                  <div className="flex justify-center py-8">
                    <Spinner aria-label="Loading sessions" />
                  </div>
                ) : sessionsError ? (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800">{sessionsError}</p>
                  </div>
                ) : sessions.length > 0 ? (
                  <div className="space-y-4">
                    {sessions.map((session) => (
                      <div
                        key={session.session_id}
                        className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-semibold text-gray-900">
                            {session.sequence_name}
                          </h3>
                          <Badge variant={getStatusBadgeVariant(session.completion_status)}>
                            {getStatusText(session.completion_status)}
                          </Badge>
                        </div>
                        <div className="space-y-1 text-sm text-gray-600">
                          <p>
                            <Clock className="inline h-4 w-4 mr-1" />
                            {formatDuration(session.duration_seconds)}
                          </p>
                          <p>Difficulty: {session.sequence_difficulty}</p>
                          <p>Focus: {session.sequence_focus_area}</p>
                          <p className="text-xs text-gray-500">
                            {formatDate(session.started_at)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : selectedDate ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>No sessions found for this day</p>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Calendar className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                    <p>Click on a day with practice sessions to view details</p>
                  </div>
                )}
              </Card>
            </div>
          </div>
        </div>

        <style>{`
          .history-layout.mobile-stack {
            grid-template-columns: 1fr;
          }

          @media (min-width: 1024px) {
            .history-layout.mobile-stack {
              grid-template-columns: 1fr 1fr;
            }
          }

          @media (max-width: 640px) {
            .history-page {
              padding: 0;
            }
          }
        `}</style>
      </Container>
    </div>
  );
}

export default History;
