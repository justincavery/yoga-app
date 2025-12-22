import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, Clock, Flame, Play, History, BookOpen, Activity } from 'lucide-react';
import { Button, Card, Badge } from '../components/ui';
import { Container } from '../components/layout';
import PageHeader from '../components/PageHeader';
import useAuthStore from '../store/authStore';
import apiClient from '../lib/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, accessToken: token, logout } = useAuthStore();
  const [stats, setStats] = useState(null);
  const [recentSessions, setRecentSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statsError, setStatsError] = useState(false);
  const [historyError, setHistoryError] = useState(false);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setStatsError(false);
      setHistoryError(false);

      try {
        // Fetch stats and recent history in parallel
        const [statsResponse, historyResponse] = await Promise.allSettled([
          apiClient.getStats(token),
          apiClient.getHistory(token, { page: 1, page_size: 5 }),
        ]);

        if (statsResponse.status === 'fulfilled') {
          setStats(statsResponse.value);
        } else {
          setStatsError(true);
        }

        if (historyResponse.status === 'fulfilled') {
          setRecentSessions(historyResponse.value.sessions);
        } else {
          setHistoryError(true);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchDashboardData();
    }
  }, [token]);

  const handleStartPractice = () => {
    navigate('/sequences');
  };

  const handleViewHistory = () => {
    navigate('/history');
  };

  const formatDuration = (seconds) => {
    const minutes = Math.round(seconds / 60);
    return `${minutes} min`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
          <p className="text-neutral-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      <PageHeader />

      {/* Main Content */}
      <Container>
        <div className="py-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-neutral-900 mb-2">
              Welcome back, {user?.name}!
            </h2>
            <p className="text-neutral-600">Here's an overview of your yoga practice journey</p>
          </div>

          {/* Stats Cards */}
          {statsError && stats === null ? (
            <div className="mb-8 p-4 bg-primary-50 border border-primary-200 rounded-lg">
              <p className="text-primary-900 font-medium">Welcome to YogaFlow!</p>
              <p className="text-primary-700 text-sm mt-1">
                Start your first practice session to begin tracking your progress.
              </p>
            </div>
          ) : null}
          {(stats || statsError) && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {/* Total Sessions */}
              <Card role="article">
                <Card.Content padding="lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-neutral-600 mb-1">Total Sessions</p>
                      <p className="text-3xl font-bold text-neutral-900">
                        {stats?.total_sessions || 0}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                      <Activity className="text-primary-600" size={24} />
                    </div>
                  </div>
                </Card.Content>
              </Card>

              {/* Total Time */}
              <Card role="article">
                <Card.Content padding="lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-neutral-600 mb-1">Total Time</p>
                      <p className="text-3xl font-bold text-neutral-900">
                        {stats?.total_practice_time_hours?.toFixed(1) || '0.0'}
                      </p>
                      <p className="text-xs text-neutral-500">hours</p>
                    </div>
                    <div className="w-12 h-12 bg-secondary-100 rounded-full flex items-center justify-center">
                      <Clock className="text-secondary-600" size={24} />
                    </div>
                  </div>
                </Card.Content>
              </Card>

              {/* Current Streak */}
              <Card role="article">
                <Card.Content padding="lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-neutral-600 mb-1">Current Streak</p>
                      <p className="text-3xl font-bold text-neutral-900">
                        {stats?.current_streak_days || 0}
                      </p>
                      <p className="text-xs text-neutral-500">
                        {stats?.current_streak_days === 1 ? 'day' : 'days'}
                      </p>
                    </div>
                    <div className="w-12 h-12 bg-accent-100 rounded-full flex items-center justify-center">
                      <Flame className="text-accent-600" size={24} />
                    </div>
                  </div>
                </Card.Content>
              </Card>
            </div>
          )}

          {/* Practice Streak Section */}
          {!statsError && (
            <Card className="mb-8" role="article">
              <Card.Content padding="lg">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-neutral-900">Practice Streak</h3>
                  <Flame className="text-accent-600" size={24} />
                </div>
                {stats?.current_streak_days > 0 ? (
                  <div>
                    <p className="text-2xl font-bold text-accent-600 mb-2">
                      {stats.current_streak_days} day streak! 🔥
                    </p>
                    <p className="text-neutral-600">
                      Keep it going! You've practiced {stats.sessions_last_30_days} times in the last 30 days.
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-neutral-700 font-medium mb-2">
                      Start your practice streak today!
                    </p>
                    <p className="text-neutral-600">
                      Practice today to begin building your streak and establish a consistent routine.
                    </p>
                  </div>
                )}
              </Card.Content>
            </Card>
          )}

          {/* Recent Sessions */}
          <Card className="mb-8" role="article">
            <Card.Content padding="lg">
              <h3 className="text-xl font-semibold text-neutral-900 mb-4">Recent Sessions</h3>

              {historyError ? (
                <div className="p-4 bg-error-50 border border-error-200 rounded-lg">
                  <p className="text-error-900 font-medium">Unable to load recent sessions</p>
                  <p className="text-error-700 text-sm mt-1">
                    Please refresh the page or try again later.
                  </p>
                </div>
              ) : recentSessions.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <History className="text-neutral-400" size={32} />
                  </div>
                  <p className="text-neutral-600 mb-2">No practice sessions yet</p>
                  <p className="text-neutral-500 text-sm">
                    Start a practice to see your history here!
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentSessions.map((session) => (
                    <div
                      key={session.session_id}
                      className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors"
                    >
                      <div className="flex-1">
                        <h4 className="font-medium text-neutral-900 mb-1">
                          {session.sequence_name}
                        </h4>
                        <div className="flex items-center gap-3 text-sm text-neutral-600">
                          <span>{formatDate(session.started_at)}</span>
                          <span className="w-1 h-1 bg-neutral-400 rounded-full"></span>
                          <span>{formatDuration(session.duration_seconds)}</span>
                          <span className="w-1 h-1 bg-neutral-400 rounded-full"></span>
                          <Badge variant="secondary" size="sm">
                            {session.sequence_difficulty}
                          </Badge>
                        </div>
                      </div>
                      <div className="text-success-600">
                        <svg
                          className="w-6 h-6"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card.Content>
          </Card>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card hoverable role="article">
              <Card.Content padding="lg">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Play className="text-primary-600" size={24} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-neutral-900 mb-2">
                      Start Practice
                    </h3>
                    <p className="text-neutral-600 mb-4">
                      Choose from our collection of guided sequences and begin your practice.
                    </p>
                    <Button
                      variant="primary"
                      onClick={handleStartPractice}
                      icon={<Play size={20} />}
                      fullWidth
                    >
                      Start Practice
                    </Button>
                  </div>
                </div>
              </Card.Content>
            </Card>

            <Card hoverable role="article">
              <Card.Content padding="lg">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-secondary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <History className="text-secondary-600" size={24} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-neutral-900 mb-2">
                      View History
                    </h3>
                    <p className="text-neutral-600 mb-4">
                      Review your past sessions and track your progress over time.
                    </p>
                    <Button
                      variant="secondary"
                      onClick={handleViewHistory}
                      icon={<History size={20} />}
                      fullWidth
                    >
                      View History
                    </Button>
                  </div>
                </div>
              </Card.Content>
            </Card>
          </div>
        </div>
      </Container>
    </div>
  );
}
