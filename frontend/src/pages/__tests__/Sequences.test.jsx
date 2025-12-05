import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import { renderWithRouter, mockAuthUser, clearAuthUser, userEvent } from '../../test/utils';
import Sequences from '../Sequences';
import apiClient from '../../lib/api';

// Mock the API client
vi.mock('../../lib/api', () => ({
  default: {
    getSequences: vi.fn(),
  },
}));

// Mock router navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Sequences Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthUser();

    // Default mock response
    apiClient.getSequences.mockResolvedValue({
      sequences: [
        {
          id: 1,
          name: 'Morning Energy Flow',
          description: 'Start your day with this energizing 20-minute sequence',
          category: 'Vinyasa',
          difficulty: 'Beginner',
          duration: 20,
          pose_count: 8,
          image_url: 'https://example.com/image1.jpg',
        },
        {
          id: 2,
          name: 'Deep Stretch & Relaxation',
          description: 'Wind down with this gentle stretching sequence',
          category: 'Restorative',
          difficulty: 'Beginner',
          duration: 30,
          pose_count: 10,
          image_url: 'https://example.com/image2.jpg',
        },
        {
          id: 3,
          name: 'Core Strength Builder',
          description: 'Build core strength with this challenging sequence',
          category: 'Power',
          difficulty: 'Intermediate',
          duration: 25,
          pose_count: 12,
          image_url: 'https://example.com/image3.jpg',
        },
      ],
      total: 3,
    });
  });

  afterEach(() => {
    clearAuthUser();
  });

  describe('Initial Rendering', () => {
    it('should render the page header', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('Sequence Library')).toBeInTheDocument();
      });
    });

    it('should render the page description', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText(/Browse and discover yoga sequences/i)).toBeInTheDocument();
      });
    });

    it('should display YogaFlow branding in header', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('YogaFlow')).toBeInTheDocument();
      });
    });

    it('should display user information in header', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument();
        expect(screen.getByText('test@example.com')).toBeInTheDocument();
      });
    });

    it('should have navigation links to Dashboard and Poses', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByRole('link', { name: /dashboard/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /poses/i })).toBeInTheDocument();
      });
    });
  });

  describe('Loading State', () => {
    it('should display loading spinner while fetching sequences', async () => {
      apiClient.getSequences.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      );

      renderWithRouter(<Sequences />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should hide loading spinner after sequences load', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.queryByRole('status')).not.toBeInTheDocument();
      });
    });
  });

  describe('Sequence Grid Display', () => {
    it('should display all sequences in a grid', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
        expect(screen.getByText('Deep Stretch & Relaxation')).toBeInTheDocument();
        expect(screen.getByText('Core Strength Builder')).toBeInTheDocument();
      });
    });

    it('should display sequence difficulty badges', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const beginnerBadges = screen.getAllByText('Beginner');
        expect(beginnerBadges.length).toBeGreaterThan(0);
        expect(screen.getByText('Intermediate')).toBeInTheDocument();
      });
    });

    it('should display sequence category badges', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('Vinyasa')).toBeInTheDocument();
        expect(screen.getByText('Restorative')).toBeInTheDocument();
        expect(screen.getByText('Power')).toBeInTheDocument();
      });
    });

    it('should display sequence duration and pose count', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const durationTexts = screen.getAllByText(/20 min/i);
        expect(durationTexts.length).toBeGreaterThan(0);
        const poseCountTexts = screen.getAllByText(/8 poses/i);
        expect(poseCountTexts.length).toBeGreaterThan(0);
      });
    });

    it('should display sequence images', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const images = screen.getAllByRole('img');
        expect(images.length).toBeGreaterThan(0);
        expect(images[0]).toHaveAttribute('alt', 'Morning Energy Flow');
      });
    });

    it('should display results count', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText(/showing 3 sequences/i)).toBeInTheDocument();
      });
    });
  });

  describe('Search Functionality', () => {
    it('should have a search input field', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search sequences/i)).toBeInTheDocument();
      });
    });

    it('should filter sequences by search query', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search sequences/i);
      await user.type(searchInput, 'Morning');

      await waitFor(() => {
        expect(apiClient.getSequences).toHaveBeenCalledWith(
          expect.objectContaining({ search: 'Morning' })
        );
      });
    });

    it('should debounce search input', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search sequences/i)).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search sequences/i);

      // Type multiple characters quickly
      await user.type(searchInput, 'Mor');

      // Should not call API for each keystroke
      expect(apiClient.getSequences).toHaveBeenCalledTimes(1); // Initial load only

      // Wait for debounce
      await waitFor(() => {
        expect(apiClient.getSequences).toHaveBeenCalledWith(
          expect.objectContaining({ search: 'Mor' })
        );
      }, { timeout: 500 });
    });
  });

  describe('Difficulty Filter', () => {
    it('should have a difficulty filter dropdown', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const difficultySelect = screen.getByLabelText(/difficulty/i);
        expect(difficultySelect).toBeInTheDocument();
      });
    });

    it('should filter sequences by difficulty', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByLabelText(/difficulty/i)).toBeInTheDocument();
      });

      const difficultySelect = screen.getByLabelText(/difficulty/i);
      await user.selectOptions(difficultySelect, 'intermediate');

      await waitFor(() => {
        expect(apiClient.getSequences).toHaveBeenCalledWith(
          expect.objectContaining({ difficulty: 'intermediate' })
        );
      });
    });

    it('should have all difficulty options', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const difficultySelect = screen.getByLabelText(/difficulty/i);
        expect(within(difficultySelect).getByText(/all difficulties/i)).toBeInTheDocument();
        expect(within(difficultySelect).getByText('Beginner')).toBeInTheDocument();
        expect(within(difficultySelect).getByText('Intermediate')).toBeInTheDocument();
        expect(within(difficultySelect).getByText('Advanced')).toBeInTheDocument();
      });
    });
  });

  describe('Category Filter', () => {
    it('should have a category filter dropdown', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const categorySelect = screen.getByLabelText(/category/i);
        expect(categorySelect).toBeInTheDocument();
      });
    });

    it('should filter sequences by category', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
      });

      const categorySelect = screen.getByLabelText(/category/i);
      await user.selectOptions(categorySelect, 'vinyasa');

      await waitFor(() => {
        expect(apiClient.getSequences).toHaveBeenCalledWith(
          expect.objectContaining({ category: 'vinyasa' })
        );
      });
    });

    it('should have all category options', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const categorySelect = screen.getByLabelText(/category/i);
        expect(within(categorySelect).getByText(/all categories/i)).toBeInTheDocument();
        expect(within(categorySelect).getByText('Vinyasa')).toBeInTheDocument();
        expect(within(categorySelect).getByText('Hatha')).toBeInTheDocument();
        expect(within(categorySelect).getByText('Restorative')).toBeInTheDocument();
      });
    });
  });

  describe('Clear Filters', () => {
    it('should have a clear filters button', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
      });
    });

    it('should clear all filters when clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByLabelText(/difficulty/i)).toBeInTheDocument();
      });

      // Set some filters
      const difficultySelect = screen.getByLabelText(/difficulty/i);
      await user.selectOptions(difficultySelect, 'intermediate');

      const categorySelect = screen.getByLabelText(/category/i);
      await user.selectOptions(categorySelect, 'vinyasa');

      const searchInput = screen.getByPlaceholderText(/search sequences/i);
      await user.type(searchInput, 'Test');

      // Click clear filters
      const clearButton = screen.getByRole('button', { name: /clear/i });
      await user.click(clearButton);

      // Check that filters are cleared
      expect(difficultySelect.value).toBe('');
      expect(categorySelect.value).toBe('');
      expect(searchInput.value).toBe('');
    });

    it('should disable clear button when no filters are active', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const clearButton = screen.getByRole('button', { name: /clear/i });
        expect(clearButton).toBeDisabled();
      });
    });

    it('should show active filter count', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByLabelText(/difficulty/i)).toBeInTheDocument();
      });

      const difficultySelect = screen.getByLabelText(/difficulty/i);
      await user.selectOptions(difficultySelect, 'intermediate');

      await waitFor(() => {
        expect(screen.getByText(/1 active filter/i)).toBeInTheDocument();
      });
    });
  });

  describe('Preview Modal', () => {
    it('should open preview modal when clicking on a sequence card', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
      });

      const sequenceCard = screen.getByText('Morning Energy Flow').closest('div[role="button"]');
      await user.click(sequenceCard);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });
    });

    it('should display sequence details in modal', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
      });

      const sequenceCard = screen.getByText('Morning Energy Flow').closest('div[role="button"]');
      await user.click(sequenceCard);

      await waitFor(() => {
        const modal = screen.getByRole('dialog');
        expect(within(modal).getByText('Morning Energy Flow')).toBeInTheDocument();
        expect(within(modal).getByText(/start your day/i)).toBeInTheDocument();
      });
    });

    it('should close modal when clicking close button', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
      });

      const sequenceCard = screen.getByText('Morning Energy Flow').closest('div[role="button"]');
      await user.click(sequenceCard);

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      const modal = screen.getByRole('dialog');
      const closeButtons = within(modal).getAllByRole('button', { name: /close/i });
      await user.click(closeButtons[0]); // Click the first close button in the modal

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });
    });

    it('should have a start practice button in modal', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
      });

      const sequenceCard = screen.getByText('Morning Energy Flow').closest('div[role="button"]');
      await user.click(sequenceCard);

      await waitFor(() => {
        const modal = screen.getByRole('dialog');
        expect(within(modal).getByRole('button', { name: /start practice/i })).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when API fails', async () => {
      apiClient.getSequences.mockRejectedValue({
        message: 'Failed to load sequences',
      });

      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load sequences/i)).toBeInTheDocument();
      });
    });

    it('should still display error if API returns non-200 status', async () => {
      apiClient.getSequences.mockRejectedValue({
        status: 500,
        message: 'Server error',
      });

      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText(/server error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Empty State', () => {
    it('should display empty state when no sequences match filters', async () => {
      apiClient.getSequences.mockResolvedValue({
        sequences: [],
        total: 0,
      });

      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByText(/no sequences found/i)).toBeInTheDocument();
      });
    });

    it('should show clear filters button in empty state', async () => {
      apiClient.getSequences.mockResolvedValue({
        sequences: [],
        total: 0,
      });

      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const emptyState = screen.getByText(/no sequences found/i).closest('div');
        expect(within(emptyState).getByRole('button', { name: /clear filters/i })).toBeInTheDocument();
      });
    });
  });

  describe('Logout Functionality', () => {
    it('should have a logout button', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
      });
    });

    it('should navigate to login page when logout is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
      });

      const logoutButton = screen.getByRole('button', { name: /logout/i });
      await user.click(logoutButton);

      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  describe('Responsive Design', () => {
    it('should have responsive grid classes', async () => {
      renderWithRouter(<Sequences />);

      await waitFor(() => {
        const grid = screen.getByText('Morning Energy Flow').closest('.grid');
        expect(grid).toHaveClass('grid-cols-1');
        expect(grid).toHaveClass('sm:grid-cols-2');
        expect(grid).toHaveClass('lg:grid-cols-3');
      });
    });
  });
});
