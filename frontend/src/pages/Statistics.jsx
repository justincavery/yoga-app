import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LogOut, User } from 'lucide-react';
import apiClient from '../lib/api';
import StatCard from '../components/StatCard';
import { Container } from '../components/layout';
import { Button } from '../components/ui';
import Spinner from '../components/ui/Spinner';
import useAuthStore from '../store/authStore';

/**
 * Statistics Page - Display user practice statistics.
 * Shows total sessions, practice time, average duration, streak, completion rate, and most practiced sequences.
 */
const Statistics = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/api/v1/stats');
      setStats(response.data);
    } catch (error_obj) {
      console.error('Error fetching statistics:', error_obj);
      setError('Failed to load statistics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
  }, []);

  const formatTime = (hours) => {
    if (hours === 0) return '0 hours';
    if (hours === 1) return '1 hour';
    return `${hours} hours`;
  };

  const formatDuration = (minutes) => {
    if (minutes === 0) return '0 min';
    return `${minutes} min`;
  };

  const formatStreak = (days) => {
    if (days === 0) return '0 days';
    if (days === 1) return '1 day';
    return `${days} days`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <header className="bg-white border-b border-neutral-200 shadow-sm">
          <Container>
            <div className="py-4 flex items-center justify-between">
              <h1 className="text-2xl font-bold text-primary-600">YogaFlow</h1>
            </div>
          </Container>
        </header>
        <Container>
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center">
              <Spinner size="lg" />
              <p className="mt-4 text-gray-600">Loading your statistics...</p>
            </div>
          </div>
        </Container>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <header className="bg-white border-b border-neutral-200 shadow-sm">
          <Container>
            <div className="py-4 flex items-center justify-between">
              <h1 className="text-2xl font-bold text-primary-600">YogaFlow</h1>
            </div>
          </Container>
        </header>
        <Container>
          <div className="py-8">
            <div className="text-center py-12">
              <div className="text-red-600 mb-4">
                <svg
                  className="mx-auto h-12 w-12"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Error</h3>
              <p className="text-gray-600 mb-6">{error}</p>
              <Button onClick={fetchStatistics} variant="primary">
                Retry
              </Button>
            </div>
          </div>
        </Container>
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
                <Link to="/stats" className="text-primary-600 font-medium border-b-2 border-primary-600">
                  Statistics
                </Link>
              </nav>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/dashboard')}
              >
                <User className="w-4 h-4 mr-2" />
                {user?.name || user?.email}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </Container>
      </header>

      <Container>
        <div className="py-8">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Your Statistics</h1>
            <p className="mt-2 text-gray-600">
              Track your practice progress and achievements
            </p>
          </div>

        {/* Stats Grid */}
        <div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"
          data-testid="stats-grid"
        >
          <StatCard
            title="Total Sessions"
            value={stats.total_sessions}
            variant="primary"
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            }
          />

          <StatCard
            title="Total Practice Time"
            value={formatTime(stats.total_practice_time_hours)}
            variant="success"
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            }
          />

          <StatCard
            title="Average Duration"
            value={formatDuration(stats.average_session_duration_minutes)}
            variant="info"
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            }
          />

          <StatCard
            title="Current Streak"
            value={formatStreak(stats.current_streak_days)}
            variant="primary"
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z"
                />
              </svg>
            }
          />

          <StatCard
            title="Completion Rate"
            value={`${stats.completion_rate_percentage}%`}
            variant="success"
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            }
          />

          <StatCard
            title="Last 30 Days"
            value={stats.sessions_last_30_days}
            subtitle="Sessions"
            variant="info"
            icon={
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            }
          />
        </div>

        {/* Most Practiced Sequences */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Most Practiced Sequences
          </h2>

          {stats.most_practiced_sequences.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No sequences practiced yet. Start your first practice session!
            </p>
          ) : (
            <div className="space-y-4">
              {stats.most_practiced_sequences.map((sequence, index) => (
                <div
                  key={sequence.sequence_id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-150"
                >
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center font-semibold">
                      {index + 1}
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{sequence.name}</h3>
                      <p className="text-sm text-gray-500">
                        {sequence.practice_count} {sequence.practice_count === 1 ? 'session' : 'sessions'}
                      </p>
                    </div>
                  </div>
                  <Link
                    to={`/sequences`}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
        </div>
      </Container>
    </div>
  );
};

export default Statistics;
