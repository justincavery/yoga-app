import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import { renderWithRouter, mockAuthUser, clearAuthUser, userEvent } from '../../test/utils';
import PracticeSession from '../PracticeSession';
import apiClient from '../../lib/api';

// Mock the API client
vi.mock('../../lib/api', () => ({
  default: {
    getSequenceById: vi.fn(),
  },
}));

// Mock router navigation and params
const mockNavigate = vi.fn();
const mockParams = { sequenceId: '1' };

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => mockParams,
  };
});

// Mock audio using a class constructor
global.Audio = class {
  play() {
    return Promise.resolve();
  }
  pause() {}
  addEventListener() {}
  removeEventListener() {}
};

describe('PracticeSession Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    mockAuthUser();

    // Default mock response - sequence with 3 poses
    apiClient.getSequenceById.mockResolvedValue({
      id: 1,
      name: 'Morning Energy Flow',
      description: 'Start your day with this energizing sequence',
      category: 'Vinyasa',
      difficulty: 'Beginner',
      duration: 20,
      pose_count: 3,
      image_url: 'https://example.com/sequence1.jpg',
      poses: [
        {
          id: 1,
          name: 'Mountain Pose',
          sanskrit_name: 'Tadasana',
          duration: 60,
          order: 1,
          instructions: 'Stand tall with feet together',
          image_url: 'https://example.com/pose1.jpg',
        },
        {
          id: 2,
          name: 'Downward Dog',
          sanskrit_name: 'Adho Mukha Svanasana',
          duration: 90,
          order: 2,
          instructions: 'Form an inverted V shape with your body',
          image_url: 'https://example.com/pose2.jpg',
        },
        {
          id: 3,
          name: 'Warrior I',
          sanskrit_name: 'Virabhadrasana I',
          duration: 120,
          order: 3,
          instructions: 'Step back and raise arms overhead',
          image_url: 'https://example.com/pose3.jpg',
        },
      ],
    });
  });

  afterEach(() => {
    clearAuthUser();
    vi.useRealTimers();
  });

  describe('Initial Loading and Display', () => {
    it('should render loading state while fetching sequence', async () => {
      apiClient.getSequenceById.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      );

      renderWithRouter(<PracticeSession />);

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should display sequence name and details', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Morning Energy Flow')).toBeInTheDocument();
      });
    });

    it('should display overall progress indicator', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText(/pose 1 of 3/i)).toBeInTheDocument();
      });
    });

    it('should display estimated total time', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        // Total duration is 60+90+120 = 270 seconds = 4 min 30 sec
        expect(screen.getByText(/4:30/i)).toBeInTheDocument();
      });
    });

    it('should fetch sequence using sequenceId from params', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(apiClient.getSequenceById).toHaveBeenCalledWith('1');
      });
    });
  });

  describe('Current Pose Display', () => {
    it('should display current pose name', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });
    });

    it('should display current pose Sanskrit name', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Tadasana')).toBeInTheDocument();
      });
    });

    it('should display current pose image', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        const image = screen.getByAltText('Mountain Pose');
        expect(image).toBeInTheDocument();
        expect(image).toHaveAttribute('src', 'https://example.com/pose1.jpg');
      });
    });

    it('should display current pose instructions', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText(/stand tall with feet together/i)).toBeInTheDocument();
      });
    });

    it('should update pose display when transitioning to next pose', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Skip to next pose
      const skipButton = screen.getByRole('button', { name: /next pose/i });
      await userEvent.setup().click(skipButton);

      await waitFor(() => {
        expect(screen.getByText('Downward Dog')).toBeInTheDocument();
        expect(screen.getByText('Adho Mukha Svanasana')).toBeInTheDocument();
      });
    });
  });

  describe('Timer Functionality', () => {
    it('should display countdown timer for current pose', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        // 60 seconds = 1:00
        expect(screen.getByText(/1:00/)).toBeInTheDocument();
      });
    });

    it('should count down timer every second', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText(/1:00/)).toBeInTheDocument();
      });

      // Advance timer by 1 second
      vi.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(screen.getByText(/0:59/)).toBeInTheDocument();
      });

      // Advance by another second
      vi.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(screen.getByText(/0:58/)).toBeInTheDocument();
      });
    });

    it('should automatically transition to next pose when timer reaches 0', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Fast-forward through entire first pose (60 seconds)
      vi.advanceTimersByTime(60000);

      await waitFor(() => {
        expect(screen.getByText('Downward Dog')).toBeInTheDocument();
        expect(screen.getByText(/pose 2 of 3/i)).toBeInTheDocument();
      });
    });

    it('should display completion screen when all poses are finished', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Fast-forward through all poses (60 + 90 + 120 = 270 seconds)
      vi.advanceTimersByTime(270000);

      await waitFor(() => {
        expect(screen.getByText(/practice complete/i)).toBeInTheDocument();
      });
    });
  });

  describe('Pause and Resume Controls', () => {
    it('should have a pause button', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
      });
    });

    it('should pause the timer when pause button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText(/1:00/)).toBeInTheDocument();
      });

      const pauseButton = screen.getByRole('button', { name: /pause/i });
      await user.click(pauseButton);

      // Advance time - timer should not change
      vi.advanceTimersByTime(5000);

      await waitFor(() => {
        expect(screen.getByText(/1:00/)).toBeInTheDocument();
      });
    });

    it('should change pause button to resume when paused', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
      });

      const pauseButton = screen.getByRole('button', { name: /pause/i });
      await user.click(pauseButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /resume/i })).toBeInTheDocument();
      });
    });

    it('should resume timer when resume button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText(/1:00/)).toBeInTheDocument();
      });

      // Pause
      const pauseButton = screen.getByRole('button', { name: /pause/i });
      await user.click(pauseButton);

      // Resume
      const resumeButton = screen.getByRole('button', { name: /resume/i });
      await user.click(resumeButton);

      // Timer should continue counting down
      vi.advanceTimersByTime(1000);

      await waitFor(() => {
        expect(screen.getByText(/0:59/)).toBeInTheDocument();
      });
    });
  });

  describe('Skip to Next Pose', () => {
    it('should have a skip/next pose button', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /next pose/i })).toBeInTheDocument();
      });
    });

    it('should skip to next pose immediately when clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      const skipButton = screen.getByRole('button', { name: /next pose/i });
      await user.click(skipButton);

      await waitFor(() => {
        expect(screen.getByText('Downward Dog')).toBeInTheDocument();
      });
    });

    it('should disable skip button on last pose', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      const skipButton = screen.getByRole('button', { name: /next pose/i });

      // Skip to pose 2
      await user.click(skipButton);
      await waitFor(() => {
        expect(screen.getByText('Downward Dog')).toBeInTheDocument();
      });

      // Skip to pose 3 (last pose)
      await user.click(skipButton);
      await waitFor(() => {
        expect(screen.getByText('Warrior I')).toBeInTheDocument();
      });

      // Skip button should be disabled on last pose
      expect(skipButton).toBeDisabled();
    });
  });

  describe('Exit Session', () => {
    it('should have an exit button', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /exit/i })).toBeInTheDocument();
      });
    });

    it('should show confirmation dialog when exit is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /exit/i })).toBeInTheDocument();
      });

      const exitButton = screen.getByRole('button', { name: /exit/i });
      await user.click(exitButton);

      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
      });
    });

    it('should cancel exit when user clicks cancel in confirmation', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /exit/i })).toBeInTheDocument();
      });

      const exitButton = screen.getByRole('button', { name: /exit/i });
      await user.click(exitButton);

      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
      });

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText(/are you sure/i)).not.toBeInTheDocument();
      });

      // Should still be on practice session
      expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
    });

    it('should navigate to sequences when user confirms exit', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /exit/i })).toBeInTheDocument();
      });

      const exitButton = screen.getByRole('button', { name: /exit/i });
      await user.click(exitButton);

      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
      });

      const confirmButton = screen.getByRole('button', { name: /^exit$/i });
      await user.click(confirmButton);

      expect(mockNavigate).toHaveBeenCalledWith('/sequences');
    });
  });

  describe('Transition Audio Cues', () => {
    it('should play audio cue 5 seconds before transition', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Advance to 55 seconds (5 seconds before end)
      vi.advanceTimersByTime(55000);

      await waitFor(() => {
        expect(global.Audio).toHaveBeenCalled();
      });
    });

    it('should have audio mute/unmute toggle button', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /mute|unmute|sound/i })).toBeInTheDocument();
      });
    });

    it('should not play audio when muted', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Mute audio
      const muteButton = screen.getByRole('button', { name: /mute|unmute|sound/i });
      await user.click(muteButton);

      const audioCallsBefore = global.Audio.mock.calls.length;

      // Advance to warning time
      vi.advanceTimersByTime(55000);

      // No new audio calls should be made when muted
      expect(global.Audio.mock.calls.length).toBe(audioCallsBefore);
    });

    it('should play audio on pose transition', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      const audioCallsBefore = global.Audio.mock.calls.length;

      // Advance to pose transition
      vi.advanceTimersByTime(60000);

      await waitFor(() => {
        expect(global.Audio.mock.calls.length).toBeGreaterThan(audioCallsBefore);
      });
    });
  });

  describe('Progress Indicator', () => {
    it('should show visual progress bar', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('progressbar')).toBeInTheDocument();
      });
    });

    it('should update progress bar as poses complete', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        const progressBar = screen.getByRole('progressbar');
        // First pose: 1/3 = 33.33%
        expect(progressBar).toHaveAttribute('aria-valuenow', '1');
        expect(progressBar).toHaveAttribute('aria-valuemax', '3');
      });

      // Skip to second pose
      const skipButton = screen.getByRole('button', { name: /next pose/i });
      await userEvent.setup().click(skipButton);

      await waitFor(() => {
        const progressBar = screen.getByRole('progressbar');
        // Second pose: 2/3 = 66.67%
        expect(progressBar).toHaveAttribute('aria-valuenow', '2');
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when sequence fails to load', async () => {
      apiClient.getSequenceById.mockRejectedValue({
        status: 404,
        message: 'Sequence not found',
      });

      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText(/sequence not found/i)).toBeInTheDocument();
      });
    });

    it('should show option to return to sequences on error', async () => {
      apiClient.getSequenceById.mockRejectedValue({
        status: 404,
        message: 'Sequence not found',
      });

      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /back to sequences/i })).toBeInTheDocument();
      });
    });
  });

  describe('Completion Screen', () => {
    it('should display completion message when practice is finished', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Complete all poses
      vi.advanceTimersByTime(270000);

      await waitFor(() => {
        expect(screen.getByText(/great work/i)).toBeInTheDocument();
        expect(screen.getByText(/practice complete/i)).toBeInTheDocument();
      });
    });

    it('should show session summary on completion', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Complete all poses
      vi.advanceTimersByTime(270000);

      await waitFor(() => {
        expect(screen.getByText(/3 poses completed/i)).toBeInTheDocument();
        expect(screen.getByText(/4 minutes/i)).toBeInTheDocument();
      });
    });

    it('should have button to return to sequences on completion', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Complete all poses
      vi.advanceTimersByTime(270000);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /finish/i })).toBeInTheDocument();
      });
    });
  });

  describe('Transition Animations and Next Pose Preview', () => {
    it('should show "Next: [Pose Name]" 5 seconds before transition', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Advance to 55 seconds (5 seconds before end of 60-second pose)
      vi.advanceTimersByTime(55000);

      await waitFor(() => {
        expect(screen.getByText(/next.*downward dog/i)).toBeInTheDocument();
      });
    });

    it('should have fade-in animation class on pose transition', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Transition to next pose
      vi.advanceTimersByTime(60000);

      await waitFor(() => {
        const poseContainer = screen.getByText('Downward Dog').closest('[data-testid="pose-container"]');
        expect(poseContainer).toHaveClass(/fade|animate/);
      });
    });

    it('should NOT show next pose preview on last pose', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Skip to last pose
      const skipButton = screen.getByRole('button', { name: /next pose/i });
      await user.click(skipButton);
      await user.click(skipButton);

      await waitFor(() => {
        expect(screen.getByText('Warrior I')).toBeInTheDocument();
      });

      // Advance near end of last pose
      vi.advanceTimersByTime(115000);

      // Should not show "Next:" preview
      expect(screen.queryByText(/next:/i)).not.toBeInTheDocument();
    });
  });

  describe('Keyboard Shortcuts', () => {
    it('should pause/resume when Space key is pressed', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Press Space to pause
      fireEvent.keyDown(document, { key: ' ', code: 'Space' });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /resume/i })).toBeInTheDocument();
      });

      // Press Space again to resume
      fireEvent.keyDown(document, { key: ' ', code: 'Space' });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
      });
    });

    it('should skip to next pose when Right Arrow is pressed', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Press Right Arrow
      fireEvent.keyDown(document, { key: 'ArrowRight', code: 'ArrowRight' });

      await waitFor(() => {
        expect(screen.getByText('Downward Dog')).toBeInTheDocument();
      });
    });

    it('should skip to previous pose when Left Arrow is pressed', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Skip forward first
      fireEvent.keyDown(document, { key: 'ArrowRight', code: 'ArrowRight' });

      await waitFor(() => {
        expect(screen.getByText('Downward Dog')).toBeInTheDocument();
      });

      // Press Left Arrow to go back
      fireEvent.keyDown(document, { key: 'ArrowLeft', code: 'ArrowLeft' });

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });
    });

    it('should not skip backward when on first pose', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Try to go backward on first pose
      fireEvent.keyDown(document, { key: 'ArrowLeft', code: 'ArrowLeft' });

      // Should still be on first pose
      expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      expect(screen.getByText(/pose 1 of 3/i)).toBeInTheDocument();
    });

    it('should not skip forward when on last pose', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Skip to last pose
      const skipButton = screen.getByRole('button', { name: /next pose/i });
      await user.click(skipButton);
      await user.click(skipButton);

      await waitFor(() => {
        expect(screen.getByText('Warrior I')).toBeInTheDocument();
      });

      // Try to skip forward on last pose
      fireEvent.keyDown(document, { key: 'ArrowRight', code: 'ArrowRight' });

      // Should still be on last pose
      expect(screen.getByText('Warrior I')).toBeInTheDocument();
      expect(screen.getByText(/pose 3 of 3/i)).toBeInTheDocument();
    });
  });

  describe('Practice Settings', () => {
    it('should have settings button', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
      });
    });

    it('should open settings modal when settings button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
      });

      const settingsButton = screen.getByRole('button', { name: /settings/i });
      await user.click(settingsButton);

      await waitFor(() => {
        expect(screen.getByText(/practice settings/i)).toBeInTheDocument();
      });
    });

    it('should have preparation time setting (5-30 seconds)', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
      });

      const settingsButton = screen.getByRole('button', { name: /settings/i });
      await user.click(settingsButton);

      await waitFor(() => {
        const prepTimeInput = screen.getByLabelText(/preparation time|prep time/i);
        expect(prepTimeInput).toBeInTheDocument();
        expect(prepTimeInput).toHaveAttribute('min', '5');
        expect(prepTimeInput).toHaveAttribute('max', '30');
      });
    });

    it('should have transition warning time setting (3-10 seconds)', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
      });

      const settingsButton = screen.getByRole('button', { name: /settings/i });
      await user.click(settingsButton);

      await waitFor(() => {
        const warningTimeInput = screen.getByLabelText(/warning time|transition warning/i);
        expect(warningTimeInput).toBeInTheDocument();
        expect(warningTimeInput).toHaveAttribute('min', '3');
        expect(warningTimeInput).toHaveAttribute('max', '10');
      });
    });

    it('should have audio volume control (0-1)', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
      });

      const settingsButton = screen.getByRole('button', { name: /settings/i });
      await user.click(settingsButton);

      await waitFor(() => {
        const volumeInput = screen.getByLabelText(/volume/i);
        expect(volumeInput).toBeInTheDocument();
        expect(volumeInput).toHaveAttribute('type', 'range');
        expect(volumeInput).toHaveAttribute('min', '0');
        expect(volumeInput).toHaveAttribute('max', '1');
      });
    });

    it('should close settings modal when close button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
      });

      const settingsButton = screen.getByRole('button', { name: /settings/i });
      await user.click(settingsButton);

      await waitFor(() => {
        expect(screen.getByText(/practice settings/i)).toBeInTheDocument();
      });

      const closeButton = screen.getByRole('button', { name: /close|save/i });
      await user.click(closeButton);

      await waitFor(() => {
        expect(screen.queryByText(/practice settings/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Skip Backward Functionality', () => {
    it('should have skip backward button', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /previous|back/i })).toBeInTheDocument();
      });
    });

    it('should skip to previous pose when clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Skip forward first
      const nextButton = screen.getByRole('button', { name: /next pose/i });
      await user.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText('Downward Dog')).toBeInTheDocument();
      });

      // Now skip backward
      const backButton = screen.getByRole('button', { name: /previous|back/i });
      await user.click(backButton);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });
    });

    it('should disable skip backward button on first pose', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        const backButton = screen.getByRole('button', { name: /previous|back/i });
        expect(backButton).toBeDisabled();
      });
    });

    it('should enable skip backward button after first pose', async () => {
      const user = userEvent.setup();
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        expect(screen.getByText('Mountain Pose')).toBeInTheDocument();
      });

      // Skip forward
      const nextButton = screen.getByRole('button', { name: /next pose/i });
      await user.click(nextButton);

      await waitFor(() => {
        const backButton = screen.getByRole('button', { name: /previous|back/i });
        expect(backButton).not.toBeDisabled();
      });
    });
  });

  describe('Responsive Design and Fullscreen', () => {
    it('should have fullscreen-friendly layout classes', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        const mainContainer = screen.getByText('Mountain Pose').closest('div[class*="min-h-screen"]');
        expect(mainContainer).toBeInTheDocument();
      });
    });

    it('should be mobile responsive', async () => {
      renderWithRouter(<PracticeSession />);

      await waitFor(() => {
        // Check for responsive classes (could be more specific based on implementation)
        const content = screen.getByText('Mountain Pose').closest('div');
        expect(content).toBeInTheDocument();
      });
    });
  });
});
