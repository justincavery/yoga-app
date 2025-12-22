import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Clock, Users, Play } from 'lucide-react';
import { Button, Card, Badge, Spinner } from '../components/ui';
import { Container } from '../components/layout';
import apiClient from '../lib/api';

export default function PracticePrep() {
  const navigate = useNavigate();
  const { sequenceId } = useParams();

  // State
  const [sequence, setSequence] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch sequence details
  useEffect(() => {
    const fetchSequence = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await apiClient.getSequenceById(sequenceId);
        setSequence(data);
      } catch (err) {
        setError(err.message || 'Failed to load sequence');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSequence();
  }, [sequenceId]);

  const handleStartPractice = () => {
    navigate(`/practice/${sequenceId}`);
  };

  const handleBackToSequences = () => {
    navigate('/sequences');
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':
        return 'success';
      case 'intermediate':
        return 'warning';
      case 'advanced':
        return 'error';
      default:
        return 'default';
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <Spinner size="lg" role="status" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Container>
          <div className="py-16 text-center">
            <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg text-error-700 max-w-md mx-auto">
              {error}
            </div>
            <Button variant="outline" onClick={handleBackToSequences} icon={<ArrowLeft size={20} />}>
              Back to Sequences
            </Button>
          </div>
        </Container>
      </div>
    );
  }

  // No sequence found
  if (!sequence) {
    return (
      <div className="min-h-screen bg-neutral-50">
        <Container>
          <div className="py-16 text-center">
            <p className="text-neutral-600 mb-4">Sequence not found</p>
            <Button variant="outline" onClick={handleBackToSequences} icon={<ArrowLeft size={20} />}>
              Back to Sequences
            </Button>
          </div>
        </Container>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 pb-24">
      <Container>
        <div className="py-8">
          {/* Page Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-neutral-900 mb-2">Get Ready to Practice</h1>
            <p className="text-neutral-600">Review the sequence before you begin</p>
          </div>

          {/* Sequence Details Card */}
          <Card className="mb-8">
            {/* Sequence Image */}
            <div className="aspect-video bg-neutral-100 overflow-hidden">
              <img
                src={sequence.image_url}
                alt={sequence.name}
                className="w-full h-full object-cover"
              />
            </div>

            <Card.Content padding="lg">
              {/* Sequence Name */}
              <h2 className="text-2xl font-bold text-neutral-900 mb-4">{sequence.name}</h2>

              {/* Badges */}
              <div className="flex items-center gap-2 mb-4">
                <Badge variant={getDifficultyColor(sequence.difficulty)}>
                  {sequence.difficulty}
                </Badge>
                <Badge variant="secondary">{sequence.category}</Badge>
              </div>

              {/* Metadata */}
              <div className="flex items-center gap-6 text-neutral-600 mb-4">
                <div className="flex items-center gap-2">
                  <Clock size={20} />
                  <span className="font-medium">{sequence.duration} minutes</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users size={20} />
                  <span className="font-medium">{sequence.pose_count} poses</span>
                </div>
              </div>

              {/* Description */}
              <p className="text-neutral-700 leading-relaxed">{sequence.description}</p>
            </Card.Content>
          </Card>

          {/* Poses List */}
          {sequence.poses && sequence.poses.length > 0 && (
            <Card className="mb-8">
              <Card.Content padding="lg">
                <h3 className="text-xl font-bold text-neutral-900 mb-6">
                  Poses in this Sequence ({sequence.poses.length})
                </h3>

                <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                  {sequence.poses.map((pose, index) => (
                    <div
                      key={pose.id}
                      className="flex items-start gap-4 p-4 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors"
                    >
                      {/* Order Number */}
                      <div className="flex-shrink-0 w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center font-semibold text-sm">
                        {index + 1}.
                      </div>

                      {/* Pose Info */}
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-neutral-900">{pose.name}</h4>
                        <p className="text-sm text-neutral-600">{pose.sanskrit_name}</p>
                      </div>

                      {/* Duration */}
                      <div className="flex-shrink-0 text-sm text-neutral-600 font-medium">
                        {pose.duration}s
                      </div>
                    </div>
                  ))}
                </div>
              </Card.Content>
            </Card>
          )}

        </div>
      </Container>

      {/* Sticky Action Buttons */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-neutral-200 shadow-lg z-10">
        <Container>
          <div className="py-4 flex flex-col sm:flex-row gap-4">
            <Button
              onClick={handleStartPractice}
              icon={<Play size={20} />}
              size="lg"
              fullWidth
              className="sm:flex-1"
            >
              Start Practice
            </Button>
            <Button
              variant="outline"
              onClick={handleBackToSequences}
              icon={<ArrowLeft size={20} />}
              size="lg"
              fullWidth
              className="sm:flex-1"
            >
              Back to Sequences
            </Button>
          </div>
        </Container>
      </div>
    </div>
  );
}
