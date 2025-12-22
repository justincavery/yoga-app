import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, Filter } from 'lucide-react';
import { Button, Card, Badge, Input, Select, Spinner } from '../components/ui';
import { Container } from '../components/layout';
import PageHeader from '../components/PageHeader';
import apiClient from '../lib/api';

export default function Poses() {
  const navigate = useNavigate();

  // State
  const [poses, setPoses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Debounced search
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search query (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch poses when filters change
  useEffect(() => {
    fetchPoses();
  }, [debouncedSearch, difficultyFilter, categoryFilter]);

  const fetchPoses = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const filters = {};
      if (debouncedSearch) filters.search = debouncedSearch;
      if (difficultyFilter) filters.difficulty = difficultyFilter;
      if (categoryFilter) filters.category = categoryFilter;

      const response = await apiClient.getPoses(filters);
      setPoses(response.poses);
    } catch (err) {
      setError(err.message || 'Failed to load poses');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setDifficultyFilter('');
    setCategoryFilter('');
  };

  // Count active filters
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (searchQuery) count++;
    if (difficultyFilter) count++;
    if (categoryFilter) count++;
    return count;
  }, [searchQuery, difficultyFilter, categoryFilter]);

  const difficultyOptions = [
    { value: '', label: 'All Difficulties' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' },
  ];

  const categoryOptions = [
    { value: '', label: 'All Categories' },
    { value: 'standing', label: 'Standing' },
    { value: 'seated', label: 'Seated' },
    { value: 'backbend', label: 'Backbend' },
    { value: 'inversion', label: 'Inversion' },
    { value: 'balance', label: 'Balance' },
    { value: 'core', label: 'Core' },
    { value: 'restorative', label: 'Restorative' },
  ];

  const getDifficultyColor = (difficulty) => {
    switch (difficulty.toLowerCase()) {
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
      <PageHeader />

      {/* Main Content */}
      <Container>
        <div className="py-8">
          {/* Page Header */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-neutral-900 mb-2">Pose Library</h2>
            <p className="text-neutral-600">Explore and discover yoga poses for your practice</p>
          </div>

          {/* Search and Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Search */}
              <div className="md:col-span-3">
                <Input
                  type="text"
                  placeholder="Search poses by name, Sanskrit name, or description..."
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  icon={<Search size={20} />}
                  fullWidth
                />
              </div>

              {/* Difficulty Filter */}
              <Select
                name="difficulty"
                placeholder="All difficulties"
                value={difficultyFilter}
                onChange={(event) => setDifficultyFilter(event.target.value)}
                options={difficultyOptions}
                fullWidth
              />

              {/* Category Filter */}
              <Select
                name="category"
                placeholder="All categories"
                value={categoryFilter}
                onChange={(event) => setCategoryFilter(event.target.value)}
                options={categoryOptions}
                fullWidth
              />

              {/* Clear Filters Button */}
              <div className="flex items-end">
                <Button
                  variant="outline"
                  fullWidth
                  onClick={handleClearFilters}
                  icon={<X size={20} />}
                  disabled={activeFilterCount === 0}
                >
                  Clear {activeFilterCount > 0 && `(${activeFilterCount})`}
                </Button>
              </div>
            </div>

            {/* Active Filter Count */}
            {activeFilterCount > 0 && (
              <div className="mt-4 flex items-center gap-2 text-sm text-neutral-600">
                <Filter size={16} />
                <span>
                  {activeFilterCount} active filter{activeFilterCount !== 1 ? 's' : ''}
                </span>
              </div>
            )}
          </div>

          {/* Error State */}
          {error && (
            <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg text-error-700">
              {error}
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="flex justify-center items-center py-16">
              <Spinner size="lg" />
            </div>
          )}

          {/* Empty State */}
          {!isLoading && poses.length === 0 && (
            <div className="text-center py-16">
              <p className="text-neutral-600 mb-4">No poses found matching your criteria</p>
              <Button variant="outline" onClick={handleClearFilters}>
                Clear Filters
              </Button>
            </div>
          )}

          {/* Pose Grid */}
          {!isLoading && poses.length > 0 && (
            <>
              {/* Results Count */}
              <div className="mb-4 text-sm text-neutral-600">
                Showing {poses.length} pose{poses.length !== 1 ? 's' : ''}
              </div>

              {/* Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {poses.map((pose) => (
                  <Card key={pose.id} hoverable>
                    {/* Pose Image */}
                    <div className="aspect-square bg-neutral-100 overflow-hidden">
                      <img
                        src={pose.image_url}
                        alt={pose.name}
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                    </div>

                    {/* Pose Info */}
                    <Card.Content padding="md">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h3 className="font-semibold text-neutral-900 line-clamp-1">{pose.name}</h3>
                        <Badge variant={getDifficultyColor(pose.difficulty)} size="sm">
                          {pose.difficulty}
                        </Badge>
                      </div>
                      <p className="text-sm text-neutral-600 mb-2 line-clamp-1">{pose.sanskrit_name}</p>
                      <p className="text-sm text-neutral-700 line-clamp-2 mb-3">{pose.description}</p>
                      <Badge variant="secondary" size="sm">
                        {pose.category}
                      </Badge>
                    </Card.Content>

                    {/* Card Footer */}
                    <Card.Footer>
                      <Button
                        variant="outline"
                        size="sm"
                        fullWidth
                        onClick={() => navigate(`/poses/${pose.id}`)}
                      >
                        View Details
                      </Button>
                    </Card.Footer>
                  </Card>
                ))}
              </div>
            </>
          )}
        </div>
      </Container>
    </div>
  );
}
