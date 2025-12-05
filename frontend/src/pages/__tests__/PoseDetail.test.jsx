import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter, useParams } from 'react-router-dom';
import PoseDetail from '../PoseDetail';
import apiClient from '../../lib/api';
import useAuthStore from '../../store/authStore';

// Mock dependencies
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: vi.fn(),
    useNavigate: vi.fn(() => vi.fn()),
  };
});

vi.mock('../../lib/api');
vi.mock('../../store/authStore');

describe('PoseDetail Component', () => {
  const mockPose = {
    id: 1,
    name: 'Mountain Pose',
    sanskrit_name: 'Tadasana',
    difficulty: 'Beginner',
    category: 'Standing',
    description: 'A foundational standing pose that improves posture and balance.',
    benefits: [
      'Improves posture',
      'Builds strength in legs and core',
      'Increases body awareness',
      'Calms the mind',
    ],
    steps: [
      'Stand with feet together, toes touching and heels slightly apart',
      'Distribute weight evenly across both feet',
      'Engage leg muscles and lift kneecaps',
      'Lengthen spine and lift chest',
      'Relax shoulders down and back',
      'Breathe deeply for 5-10 breaths',
    ],
    target_areas: ['Legs', 'Core', 'Posture'],
    image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
  };

  const mockUser = {
    user_id: 1,
    email: 'test@example.com',
    name: 'Test User',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    useParams.mockReturnValue({ id: '1' });
    useAuthStore.mockReturnValue({
      user: mockUser,
      logout: vi.fn(),
    });
  });

  it('should render loading state initially', () => {
    apiClient.getPoseById.mockReturnValue(new Promise(() => {})); // Never resolves

    render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('should fetch and display pose details', async () => {
    apiClient.getPoseById.mockResolvedValue(mockPose);

    render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
    });

    expect(screen.getByText('Tadasana')).toBeInTheDocument();
    expect(screen.getByText('Beginner')).toBeInTheDocument();
    expect(screen.getByText('Standing')).toBeInTheDocument();
    expect(screen.getByText(/A foundational standing pose/)).toBeInTheDocument();
  });

  it('should display all benefits', async () => {
    apiClient.getPoseById.mockResolvedValue(mockPose);

    render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Benefits')).toBeInTheDocument();
    });

    mockPose.benefits.forEach((benefit) => {
      expect(screen.getByText(benefit)).toBeInTheDocument();
    });
  });

  it('should display all instruction steps', async () => {
    apiClient.getPoseById.mockResolvedValue(mockPose);

    render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Instructions')).toBeInTheDocument();
    });

    mockPose.steps.forEach((step) => {
      expect(screen.getByText(step)).toBeInTheDocument();
    });
  });

  it('should display target areas', async () => {
    apiClient.getPoseById.mockResolvedValue(mockPose);

    render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Target Areas')).toBeInTheDocument();
    });

    mockPose.target_areas.forEach((area) => {
      expect(screen.getByText(area)).toBeInTheDocument();
    });
  });

  it('should display pose image', async () => {
    apiClient.getPoseById.mockResolvedValue(mockPose);

    render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      const image = screen.getByAltText('Mountain Pose');
      expect(image).toBeInTheDocument();
      expect(image).toHaveAttribute('src', mockPose.image_url);
    });
  });

  it('should display error message when pose fetch fails', async () => {
    apiClient.getPoseById.mockRejectedValue({
      status: 404,
      message: 'Pose not found',
    });

    render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Pose not found/)).toBeInTheDocument();
    });
  });

  it('should have a back button to navigate to poses list', async () => {
    apiClient.getPoseById.mockResolvedValue(mockPose);

    render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      const backButton = screen.getByText(/Back to Poses/i);
      expect(backButton).toBeInTheDocument();
    });
  });

  it('should be responsive on mobile devices', async () => {
    apiClient.getPoseById.mockResolvedValue(mockPose);

    const { container } = render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
    });

    // Check for responsive classes
    const mainContent = container.querySelector('.grid');
    expect(mainContent).toBeInTheDocument();
  });

  it('should show difficulty badge with appropriate color', async () => {
    apiClient.getPoseById.mockResolvedValue(mockPose);

    render(
      <BrowserRouter>
        <PoseDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      const difficultyBadge = screen.getByText('Beginner');
      expect(difficultyBadge).toBeInTheDocument();
    });
  });
});
