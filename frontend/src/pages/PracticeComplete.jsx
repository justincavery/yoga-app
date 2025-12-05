import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { CheckCircle, Clock, Activity, Zap, Home, Repeat } from 'lucide-react';
import { Button, Card } from '../components/ui';
import { Container } from '../components/layout';
import apiClient from '../lib/api';

export default function PracticeComplete() {
  const navigate = useNavigate();
  const location = useLocation();
  const sessionData = location.state?.sessionData || {};

  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  // Extract session data with defaults
  const {
    sequenceName = 'Unknown Sequence',
    durationMinutes = 0,
    posesCompleted = 0,
    totalPoses = 0,
    caloriesBurned = 0,
    completedAt = new Date().toISOString(),
  } = sessionData;

  // Save session to history on mount
  useEffect(() => {
    const saveSession = async () => {
      setIsSaving(true);
      setSaveError(null);

      try {
        await apiClient.saveSession({
          durationMinutes,
          posesCompleted,
          caloriesBurned,
          completedAt,
        });
      } catch (err) {
        setSaveError(err.message || 'Failed to save session');
        console.error('Failed to save session:', err);
      } finally {
        setIsSaving(false);
      }
    };

    // Only save if we have valid session data
    if (durationMinutes > 0 || posesCompleted > 0) {
      saveSession();
    }
  }, []); // Empty dependency array - only run once on mount

  const handlePracticeAgain = () => {
    navigate('/sequences');
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  // Get encouraging message based on completion
  const getEncouragementMessage = () => {
    const messages = [
      'Great job on completing your practice!',
      'Excellent work! Keep up the great practice.',
      'Well done! You are building a strong yoga practice.',
      'Wonderful! Your dedication is inspiring.',
      'Amazing effort! Every practice brings you closer to your goals.',
    ];

    // Randomly select or pick based on some criteria
    return messages[Math.floor(Math.random() * messages.length)];
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <Container>
        <div className="py-8 max-w-3xl mx-auto">
          {/* Success Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-success-100 text-success-600 rounded-full mb-4">
              <CheckCircle size={48} />
            </div>
            <h1 className="text-4xl font-bold text-neutral-900 mb-2">Practice Complete!</h1>
            <p className="text-lg text-neutral-600">{getEncouragementMessage()}</p>
          </div>

          {/* Sequence Name */}
          {sequenceName && sequenceName !== 'Unknown Sequence' && (
            <div className="text-center mb-8">
              <p className="text-neutral-600">You completed</p>
              <h2 className="text-2xl font-semibold text-neutral-900">{sequenceName}</h2>
            </div>
          )}

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
            {/* Duration */}
            <Card>
              <Card.Content padding="lg" className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 text-primary-600 rounded-full mb-3">
                  <Clock size={24} />
                </div>
                <div className="text-3xl font-bold text-neutral-900 mb-1">{durationMinutes}</div>
                <div className="text-sm text-neutral-600 font-medium">Minutes</div>
                <div className="text-xs text-neutral-500 mt-1">Duration</div>
              </Card.Content>
            </Card>

            {/* Poses Completed */}
            <Card>
              <Card.Content padding="lg" className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-secondary-100 text-secondary-600 rounded-full mb-3">
                  <Activity size={24} />
                </div>
                <div className="text-3xl font-bold text-neutral-900 mb-1">
                  {posesCompleted}
                  {totalPoses > 0 && (
                    <span className="text-xl text-neutral-500">/{totalPoses}</span>
                  )}
                </div>
                <div className="text-sm text-neutral-600 font-medium">Poses</div>
                <div className="text-xs text-neutral-500 mt-1">Completed</div>
              </Card.Content>
            </Card>

            {/* Calories Burned */}
            <Card>
              <Card.Content padding="lg" className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-warning-100 text-warning-600 rounded-full mb-3">
                  <Zap size={24} />
                </div>
                <div className="text-3xl font-bold text-neutral-900 mb-1">{caloriesBurned}</div>
                <div className="text-sm text-neutral-600 font-medium">Calories</div>
                <div className="text-xs text-neutral-500 mt-1">Burned (est.)</div>
              </Card.Content>
            </Card>
          </div>

          {/* Save Status */}
          {saveError && (
            <div className="mb-6 p-4 bg-warning-50 border border-warning-200 rounded-lg text-warning-700 text-sm">
              Note: Session statistics could not be saved to your history. ({saveError})
            </div>
          )}

          {/* Additional Encouragement */}
          <Card className="mb-8">
            <Card.Content padding="lg">
              <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                Keep Building Your Practice
              </h3>
              <p className="text-neutral-600 mb-4">
                Consistency is key to progress in yoga. Try to practice regularly to build
                strength, flexibility, and mindfulness. Every session brings you closer to your
                wellness goals.
              </p>
              <div className="flex items-start gap-3 p-3 bg-primary-50 rounded-lg">
                <div className="flex-shrink-0 mt-0.5">
                  <CheckCircle size={20} className="text-primary-600" />
                </div>
                <div className="text-sm text-primary-900">
                  <strong>Pro Tip:</strong> Regular practice helps develop muscle memory and
                  deepens your mind-body connection. Aim for at least 3 sessions per week for
                  best results.
                </div>
              </div>
            </Card.Content>
          </Card>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Button
              onClick={handlePracticeAgain}
              icon={<Repeat size={20} />}
              size="lg"
              fullWidth
              className="sm:flex-1"
            >
              Practice Again
            </Button>
            <Button
              variant="outline"
              onClick={handleBackToDashboard}
              icon={<Home size={20} />}
              size="lg"
              fullWidth
              className="sm:flex-1"
            >
              Back to Dashboard
            </Button>
          </div>
        </div>
      </Container>
    </div>
  );
}
