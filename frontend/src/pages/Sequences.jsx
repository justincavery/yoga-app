import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, Filter, Clock, Users, Layers } from 'lucide-react';
import { Button, Card, Badge, Input, Select, Spinner } from '../components/ui';
import { Container } from '../components/layout';
import PageHeader from '../components/PageHeader';
import apiClient from '../lib/api';

export default function Sequences() {
  const navigate = useNavigate();

  // State
  const [sequences, setSequences] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSequence, setSelectedSequence] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [durationFilter, setDurationFilter] = useState('');

  // Debounced search
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search query (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch sequences when filters change
  useEffect(() => {
    fetchSequences();
  }, [debouncedSearch, difficultyFilter, categoryFilter, durationFilter]);

  const fetchSequences = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const filters = {};
      if (debouncedSearch) filters.search = debouncedSearch;
      if (difficultyFilter) filters.difficulty = difficultyFilter;
      if (categoryFilter) filters.category = categoryFilter;
      if (durationFilter) filters.duration = durationFilter;

      const response = await apiClient.getSequences(filters);
      setSequences(response.sequences);
    } catch (err) {
      setError(err.message || 'Failed to load sequences');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setDifficultyFilter('');
    setCategoryFilter('');
    setDurationFilter('');
  };

  const handleSequenceClick = (sequence) => {
    setSelectedSequence(sequence);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedSequence(null);
  };

  const handleStartPractice = () => {
    navigate(`/practice/prep/${selectedSequence.id}`);
    handleCloseModal();
  };

  // Count active filters
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (searchQuery) count++;
    if (difficultyFilter) count++;
    if (categoryFilter) count++;
    if (durationFilter) count++;
    return count;
  }, [searchQuery, difficultyFilter, categoryFilter, durationFilter]);

  const difficultyOptions = [
    { value: '', label: 'All Difficulties' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' },
  ];

  const categoryOptions = [
    { value: '', label: 'All Categories' },
    { value: 'vinyasa', label: 'Vinyasa' },
    { value: 'hatha', label: 'Hatha' },
    { value: 'restorative', label: 'Restorative' },
    { value: 'power', label: 'Power' },
    { value: 'yin', label: 'Yin' },
    { value: 'ashtanga', label: 'Ashtanga' },
  ];

  const durationOptions = [
    { value: '', label: 'All Durations' },
    { value: 'short', label: 'Short (< 20 min)' },
    { value: 'medium', label: 'Medium (20-35 min)' },
    { value: 'long', label: 'Long (> 35 min)' },
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
            <h2 className="text-3xl font-bold text-neutral-900 mb-2">Sequence Library</h2>
            <p className="text-neutral-600">Browse and discover yoga sequences for your practice</p>
          </div>

          {/* Search and Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="md:col-span-4">
                <Input
                  type="text"
                  placeholder="Search sequences by name, description, or category..."
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
                aria-label="Difficulty filter"
              />

              {/* Category Filter */}
              <Select
                name="category"
                placeholder="All categories"
                value={categoryFilter}
                onChange={(event) => setCategoryFilter(event.target.value)}
                options={categoryOptions}
                fullWidth
                aria-label="Category filter"
              />

              {/* Duration Filter */}
              <Select
                name="duration"
                placeholder="All durations"
                value={durationFilter}
                onChange={(event) => setDurationFilter(event.target.value)}
                options={durationOptions}
                fullWidth
                aria-label="Duration filter"
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
          {!isLoading && sequences.length === 0 && (
            <div className="text-center py-16">
              {activeFilterCount > 0 ? (
                <>
                  <p className="text-neutral-600 mb-4">No sequences found matching your criteria</p>
                  <Button variant="outline" onClick={handleClearFilters}>
                    Clear Filters
                  </Button>
                </>
              ) : (
                <div className="max-w-md mx-auto">
                  <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Layers className="text-neutral-400" size={32} />
                  </div>
                  <h3 className="text-xl font-semibold text-neutral-900 mb-2">No Sequences Available Yet</h3>
                  <p className="text-neutral-600 mb-6">
                    Sequences are curated collections of poses designed for specific goals and skill levels.
                    While we prepare our sequence library, you can explore individual poses.
                  </p>
                  <Button onClick={() => navigate('/poses')}>
                    Browse Poses
                  </Button>
                </div>
              )}
            </div>
          )}

          {/* Sequence Grid */}
          {!isLoading && sequences.length > 0 && (
            <>
              {/* Results Count */}
              <div className="mb-4 text-sm text-neutral-600">
                Showing {sequences.length} sequence{sequences.length !== 1 ? 's' : ''}
              </div>

              {/* Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {sequences.map((sequence) => (
                  <Card
                    key={sequence.id}
                    hoverable
                    onClick={() => handleSequenceClick(sequence)}
                    role="button"
                    tabIndex={0}
                    onKeyPress={(event) => {
                      if (event.key === 'Enter') {
                        handleSequenceClick(sequence);
                      }
                    }}
                  >
                    {/* Sequence Image */}
                    <div className="aspect-video bg-neutral-100 overflow-hidden">
                      <img
                        src={sequence.image_url}
                        alt={sequence.name}
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                    </div>

                    {/* Sequence Info */}
                    <Card.Content padding="md">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h3 className="font-semibold text-neutral-900 line-clamp-1">{sequence.name}</h3>
                        <Badge variant={getDifficultyColor(sequence.difficulty)} size="sm">
                          {sequence.difficulty}
                        </Badge>
                      </div>
                      <p className="text-sm text-neutral-700 line-clamp-2 mb-3">{sequence.description}</p>

                      {/* Metadata */}
                      <div className="flex items-center gap-4 text-xs text-neutral-600 mb-3">
                        <div className="flex items-center gap-1">
                          <Clock size={14} />
                          <span>{sequence.duration} min</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Users size={14} />
                          <span>{sequence.pose_count} poses</span>
                        </div>
                      </div>

                      <Badge variant="secondary" size="sm">
                        {sequence.category}
                      </Badge>
                    </Card.Content>
                  </Card>
                ))}
              </div>
            </>
          )}
        </div>
      </Container>

      {/* Preview Modal */}
      {showModal && selectedSequence && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={handleCloseModal}
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
        >
          <div
            className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(event) => event.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-neutral-200 p-6 flex items-center justify-between">
              <h3 id="modal-title" className="text-2xl font-bold text-neutral-900">
                {selectedSequence.name}
              </h3>
              <Button variant="outline" size="sm" onClick={handleCloseModal} aria-label="Close">
                <X size={20} />
              </Button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {/* Image */}
              <div className="aspect-video bg-neutral-100 overflow-hidden rounded-lg mb-6">
                <img
                  src={selectedSequence.image_url}
                  alt={selectedSequence.name}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Badges */}
              <div className="flex items-center gap-2 mb-4">
                <Badge variant={getDifficultyColor(selectedSequence.difficulty)}>
                  {selectedSequence.difficulty}
                </Badge>
                <Badge variant="secondary">{selectedSequence.category}</Badge>
              </div>

              {/* Metadata */}
              <div className="flex items-center gap-6 text-sm text-neutral-600 mb-4">
                <div className="flex items-center gap-2">
                  <Clock size={16} />
                  <span>{selectedSequence.duration} minutes</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users size={16} />
                  <span>{selectedSequence.pose_count} poses</span>
                </div>
              </div>

              {/* Description */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-neutral-900 mb-2">Description</h4>
                <p className="text-neutral-700">{selectedSequence.description}</p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Button onClick={handleStartPractice} fullWidth>
                  Start Practice
                </Button>
                <Button variant="outline" onClick={handleCloseModal}>
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
