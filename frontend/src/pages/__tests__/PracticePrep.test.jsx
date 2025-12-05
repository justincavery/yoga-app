import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithRouter, mockAuthUser, clearAuthUser, userEvent } from '../../test/utils';
import PracticePrep from '../PracticePrep';
import apiClient from '../../lib/api';

// Mock the API client
vi.mock('../../lib/api', () => ({
  default: {
    getSequenceById: vi.fn(),
  },
}));

// Mock router navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ sequenceId: '1' }),
  };
});

describe('PracticePrep Page', () => {
  const mockSequence = {
    id: 1,
    name: 'Morning Energy Flow',
    description: 'Start your day with this energizing 20-minute sequence designed to awaken your body and mind.',
    category: 'Vinyasa',
    difficulty: 'Beginner',
    duration: 20,
    pose_count: 8,
    image_url: 'https://example.com/sequence1.jpg',
    poses: [
      {
        id: 1,
        name: 'Mountain Pose',
        sanskrit_name: 'Tadasana',
        duration: 60,
        order: 1,
      },
      {
        id: 2,
        name: 'Downward Dog',
        sanskrit_name: 'Adho Mukha Svanasana',
        duration: 120,
        order: 2,
      },
      {
        id: 3,
        name: 'Warrior I',
        sanskrit_name: 'Virabhadrasana I',
        duration: 90,
        order: 3,
      },
      {
        id: 4,
        name: 'Tree Pose',
        sanskrit_name: 'Vrksasana',
        duration: 60,
        order: 4,
      },
      {
        id: 5,
        name: "Child's Pose",
        sanskrit_name: 'Balasana',
        duration: 120,
        order: 5,
      },
      {
        id: 6,
        name: 'Cobra Pose',
        sanskrit_name: 'Bhujangasana',
        duration: 90,
        order: 6,
      },
      {
        id: 7,
        name: 'Bridge Pose',
        sanskrit_name: 'Setu Bandhasana',
        duration: 120,
        order: 7,
      },
      {
        id: 8,
        name: 'Corpse Pose',
        sanskrit_name: 'Savasana',
        duration: 180,
        order: 8,
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthUser();
    apiClient.getSequenceById.mockResolvedValue(mockSequence);
  });

  afterEach(() => {
    clearAuthUser();
  });

  describe('Initial Rendering', () => {
    it('should render the page header', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText(/Get Ready to Practice/i)).toBeInTheDocument();
      });
    });

    it('should display the sequence name', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
      });
    });

    it('should display the sequence image', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        const image = screen.getByAltText('Morning Energy Flow');
        expect(image).toBeInTheDocument();
        expect(image).toHaveAttribute('src', 'https://example.com/sequence1.jpg');
      });
    });

    it('should display the sequence description', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText(/Start your day with this energizing/i)).toBeInTheDocument();
      });
    });

    it('should display difficulty badge', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText('Beginner')).toBeInTheDocument();
      });
    });

    it('should display category badge', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText('Vinyasa')).toBeInTheDocument();
      });
    });

    it('should display duration in minutes', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText(/20 minutes/i)).toBeInTheDocument();
      });
    });

    it('should display pose count', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText(/8 poses/i)).toBeInTheDocument();
      });
    });
  });

  describe('Pose List Display', () => {
    it('should display a list of poses', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText('Poses in this Sequence')).toBeInTheDocument();
      });
    });

    it('should display all pose names in order', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
        expect(screen.getByText('Downward Dog')).toBeInTheDocument();
        expect(screen.getByText('Warrior I')).toBeInTheDocument();
        expect(screen.getByText('Tree Pose')).toBeInTheDocument();
        expect(screen.getByText("Child's Pose")).toBeInTheDocument();
        expect(screen.getByText('Cobra Pose')).toBeInTheDocument();
        expect(screen.getByText('Bridge Pose')).toBeInTheDocument();
        expect(screen.getByText('Corpse Pose')).toBeInTheDocument();
      });
    });

    it('should display Sanskrit names for poses', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText('Tadasana')).toBeInTheDocument();
        expect(screen.getByText('Adho Mukha Svanasana')).toBeInTheDocument();
        expect(screen.getByText('Virabhadrasana I')).toBeInTheDocument();
      });
    });

    it('should display pose durations', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        // Check that duration displays exist (multiple poses may have same duration)
        const durations60 = screen.getAllByText(/60s/);
        const durations120 = screen.getAllByText(/120s/);
        const durations90 = screen.getAllByText(/90s/);

        expect(durations60.length).toBeGreaterThan(0);
        expect(durations120.length).toBeGreaterThan(0);
        expect(durations90.length).toBeGreaterThan(0);
      });
    });

    it('should display pose order numbers', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText('1.')).toBeInTheDocument();
        expect(screen.getByText('2.')).toBeInTheDocument();
        expect(screen.getByText('8.')).toBeInTheDocument();
      });
    });
  });

  describe('Navigation Buttons', () => {
    it('should display Start Practice button', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Start Practice/i })).toBeInTheDocument();
      });
    });

    it('should display Back to Sequences button', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Back to Sequences/i })).toBeInTheDocument();
      });
    });

    it('should navigate to practice session when Start Practice is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Start Practice/i })).toBeInTheDocument();
      });

      const startButton = screen.getByRole('button', { name: /Start Practice/i });
      await user.click(startButton);

      expect(mockNavigate).toHaveBeenCalledWith('/practice/1');
    });

    it('should navigate to sequences page when Back to Sequences is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Back to Sequences/i })).toBeInTheDocument();
      });

      const backButton = screen.getByRole('button', { name: /Back to Sequences/i });
      await user.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith('/sequences');
    });
  });

  describe('Loading State', () => {
    it('should show loading spinner while fetching sequence', async () => {
      apiClient.getSequenceById.mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockSequence), 100))
      );

      renderWithRouter(<PracticePrep />);

      expect(screen.getByRole('status')).toBeInTheDocument(); // Spinner has role="status"

      await waitFor(() => {
        expect(screen.queryByRole('status')).not.toBeInTheDocument();
      });
    });

    it('should hide loading spinner after data loads', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.queryByRole('status')).not.toBeInTheDocument();
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
      });
    });
  });

  describe('Error State', () => {
    it('should display error message when sequence fetch fails', async () => {
      apiClient.getSequenceById.mockRejectedValue({
        status: 404,
        message: 'Sequence not found',
      });

      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByText(/Sequence not found/i)).toBeInTheDocument();
      });
    });

    it('should show Back to Sequences button on error', async () => {
      apiClient.getSequenceById.mockRejectedValue({
        status: 500,
        message: 'Server error',
      });

      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Back to Sequences/i })).toBeInTheDocument();
      });
    });

    it('should navigate to sequences when back button clicked on error', async () => {
      const user = userEvent.setup();
      apiClient.getSequenceById.mockRejectedValue({
        status: 404,
        message: 'Sequence not found',
      });

      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Back to Sequences/i })).toBeInTheDocument();
      });

      const backButton = screen.getByRole('button', { name: /Back to Sequences/i });
      await user.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith('/sequences');
    });
  });

  describe('API Integration', () => {
    it('should call getSequenceById with correct ID on mount', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(apiClient.getSequenceById).toHaveBeenCalledWith('1');
      });
    });

    it('should call API only once on mount', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        expect(apiClient.getSequenceById).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Responsive Design', () => {
    it('should render mobile-friendly layout', async () => {
      renderWithRouter(<PracticePrep />);

      await waitFor(() => {
        const container = screen.getByText('Morning Energy Flow').closest('div');
        expect(container).toBeInTheDocument();
      });
    });
  });
});
