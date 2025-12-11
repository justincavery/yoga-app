import { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, LogOut, CheckCircle } from 'lucide-react';
import { Button, Card, Badge, Spinner } from '../components/ui';
import { Container } from '../components/layout';
import MobileNav from '../components/MobileNav';
import useAuthStore from '../store/authStore';
import apiClient from '../lib/api';

export default function PoseDetail() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user, logout } = useAuthStore();

  // State
  const [pose, setPose] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch pose details
  useEffect(() => {
    fetchPoseDetails();
  }, [id]);

  const fetchPoseDetails = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const poseData = await apiClient.getPoseById(id);
      setPose(poseData);
    } catch (err) {
      setError(err.message || 'Failed to load pose details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleBack = () => {
    navigate('/poses');
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
                <Link to="/poses" className="text-primary-600 font-medium">
                  Poses
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
          {/* Back Button */}
          <div className="mb-6">
            <Button variant="outline" onClick={handleBack} icon={<ArrowLeft size={16} />}>
              Back to Poses
            </Button>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="flex justify-center items-center py-16">
              <Spinner size="lg" role="status" />
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg text-error-700">
              {error}
            </div>
          )}

          {/* Pose Details */}
          {!isLoading && !error && pose && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left Column - Image */}
              <div className="order-1">
                <Card>
                  <div className="aspect-square bg-neutral-100 overflow-hidden">
                    <img
                      src={pose.image_url}
                      alt={pose.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                </Card>
              </div>

              {/* Right Column - Details */}
              <div className="order-2 space-y-6">
                {/* Header */}
                <div>
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <h1 className="text-3xl font-bold text-neutral-900">{pose.name}</h1>
                    <Badge variant={getDifficultyColor(pose.difficulty)} size="lg">
                      {pose.difficulty}
                    </Badge>
                  </div>
                  <p className="text-xl text-neutral-600 mb-2">{pose.sanskrit_name}</p>
                  <Badge variant="secondary" size="md">
                    {pose.category}
                  </Badge>
                </div>

                {/* Description */}
                <Card>
                  <Card.Content padding="lg">
                    <h2 className="text-lg font-semibold text-neutral-900 mb-3">Description</h2>
                    <p className="text-neutral-700 leading-relaxed">{pose.description}</p>
                  </Card.Content>
                </Card>

                {/* Target Areas */}
                {pose.target_areas && pose.target_areas.length > 0 && (
                  <Card>
                    <Card.Content padding="lg">
                      <h2 className="text-lg font-semibold text-neutral-900 mb-3">Target Areas</h2>
                      <div className="flex flex-wrap gap-2">
                        {pose.target_areas.map((area, index) => (
                          <Badge key={index} variant="primary" size="md">
                            {area}
                          </Badge>
                        ))}
                      </div>
                    </Card.Content>
                  </Card>
                )}

                {/* Benefits */}
                {pose.benefits && pose.benefits.length > 0 && (
                  <Card>
                    <Card.Content padding="lg">
                      <h2 className="text-lg font-semibold text-neutral-900 mb-3">Benefits</h2>
                      <ul className="space-y-2">
                        {pose.benefits.map((benefit, index) => (
                          <li key={index} className="flex items-start gap-2 text-neutral-700">
                            <CheckCircle size={20} className="text-success-600 flex-shrink-0 mt-0.5" />
                            <span>{benefit}</span>
                          </li>
                        ))}
                      </ul>
                    </Card.Content>
                  </Card>
                )}

                {/* Instructions */}
                {pose.steps && pose.steps.length > 0 && (
                  <Card>
                    <Card.Content padding="lg">
                      <h2 className="text-lg font-semibold text-neutral-900 mb-3">Instructions</h2>
                      <ol className="space-y-3">
                        {pose.steps.map((step, index) => (
                          <li key={index} className="flex items-start gap-3 text-neutral-700">
                            <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-semibold">
                              {index + 1}
                            </span>
                            <span className="pt-0.5">{step}</span>
                          </li>
                        ))}
                      </ol>
                    </Card.Content>
                  </Card>
                )}
              </div>
            </div>
          )}
        </div>
      </Container>
    </div>
  );
}
