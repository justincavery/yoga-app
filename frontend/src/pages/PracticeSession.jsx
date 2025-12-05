import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Play,
  Pause,
  SkipForward,
  SkipBack,
  X,
  CheckCircle,
  Volume2,
  VolumeX,
  Settings as SettingsIcon
} from 'lucide-react';
import { Button, Spinner } from '../components/ui';
import apiClient from '../lib/api';

export default function PracticeSession() {
  const { sequenceId } = useParams();
  const navigate = useNavigate();

  // State
  const [sequence, setSequence] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPoseIndex, setCurrentPoseIndex] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [showExitDialog, setShowExitDialog] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [showNextPosePreview, setShowNextPosePreview] = useState(false);

  // Settings state
  const [settings, setSettings] = useState({
    preparationTime: 5, // seconds (5-30)
    transitionWarningTime: 5, // seconds (3-10)
    volume: 0.5, // 0-1
  });

  // Refs
  const timerRef = useRef(null);
  const warningAudioRef = useRef(null);
  const transitionAudioRef = useRef(null);

  // Fetch sequence on mount
  useEffect(() => {
    fetchSequence();
  }, [sequenceId]);

  // Initialize audio
  useEffect(() => {
    // Create audio elements for warning and transition sounds
    warningAudioRef.current = new Audio();
    transitionAudioRef.current = new Audio();

    // Set initial volume
    if (warningAudioRef.current) {
      warningAudioRef.current.volume = settings.volume;
    }
    if (transitionAudioRef.current) {
      transitionAudioRef.current.volume = settings.volume;
    }

    return () => {
      if (warningAudioRef.current) {
        warningAudioRef.current.pause();
      }
      if (transitionAudioRef.current) {
        transitionAudioRef.current.pause();
      }
    };
  }, []);

  // Update audio volume when settings change
  useEffect(() => {
    if (warningAudioRef.current) {
      warningAudioRef.current.volume = settings.volume;
    }
    if (transitionAudioRef.current) {
      transitionAudioRef.current.volume = settings.volume;
    }
  }, [settings.volume]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Ignore if typing in an input field or settings modal is open
      if (
        event.target.tagName === 'INPUT' ||
        event.target.tagName === 'TEXTAREA' ||
        showSettingsModal ||
        isCompleted
      ) {
        return;
      }

      switch (event.key) {
        case ' ': // Space - pause/resume
          event.preventDefault();
          handlePauseResume();
          break;
        case 'ArrowRight': // Right arrow - next pose
          event.preventDefault();
          if (currentPoseIndex < (sequence?.poses?.length || 0) - 1) {
            handleNextPose();
          }
          break;
        case 'ArrowLeft': // Left arrow - previous pose
          event.preventDefault();
          if (currentPoseIndex > 0) {
            handlePreviousPose();
          }
          break;
        default:
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [currentPoseIndex, sequence, showSettingsModal, isCompleted, isPaused]);

  // Timer effect
  useEffect(() => {
    if (!sequence || isPaused || isCompleted) return;

    const currentPose = sequence.poses[currentPoseIndex];
    if (!currentPose) return;

    // Initialize time remaining if not set
    if (timeRemaining === 0 && currentPoseIndex >= 0) {
      setTimeRemaining(currentPose.duration);
    }

    // Start timer
    timerRef.current = setInterval(() => {
      setTimeRemaining((prev) => {
        const warningTime = settings.transitionWarningTime;

        // Show next pose preview at warning time (if not on last pose)
        if (prev === warningTime && currentPoseIndex < sequence.poses.length - 1) {
          setShowNextPosePreview(true);
          playWarningSound();
        }

        // Transition to next pose when timer reaches 0
        if (prev <= 1) {
          setShowNextPosePreview(false);
          playTransitionSound();
          handleNextPose();
          return 0;
        }

        return prev - 1;
      });
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [sequence, currentPoseIndex, isPaused, isCompleted, timeRemaining, settings.transitionWarningTime]);

  const fetchSequence = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.getSequenceById(sequenceId);
      setSequence(response);
      if (response.poses && response.poses.length > 0) {
        setTimeRemaining(response.poses[0].duration);
      }
    } catch (err) {
      setError(err.message || 'Failed to load sequence');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextPose = () => {
    if (!sequence) return;

    const nextIndex = currentPoseIndex + 1;

    if (nextIndex >= sequence.poses.length) {
      // Practice complete
      setIsCompleted(true);
      setShowNextPosePreview(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    } else {
      // Move to next pose
      setCurrentPoseIndex(nextIndex);
      setTimeRemaining(sequence.poses[nextIndex].duration);
      setShowNextPosePreview(false);
    }
  };

  const handlePreviousPose = () => {
    if (!sequence || currentPoseIndex === 0) return;

    const prevIndex = currentPoseIndex - 1;
    setCurrentPoseIndex(prevIndex);
    setTimeRemaining(sequence.poses[prevIndex].duration);
    setShowNextPosePreview(false);
  };

  const handlePauseResume = () => {
    setIsPaused(!isPaused);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const handleExit = () => {
    setShowExitDialog(true);
  };

  const confirmExit = () => {
    navigate('/sequences');
  };

  const cancelExit = () => {
    setShowExitDialog(false);
  };

  const handleFinish = () => {
    navigate('/sequences');
  };

  const toggleSettings = () => {
    setShowSettingsModal(!showSettingsModal);
  };

  const updateSettings = (key, value) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const playWarningSound = () => {
    if (isMuted) return;

    try {
      if (warningAudioRef.current) {
        // In a real implementation, this would play a warning sound file
        // For testing purposes, we just trigger play
        warningAudioRef.current.play().catch(() => {
          // Silently fail if audio playback is blocked
        });
      }
    } catch (error) {
      // Ignore audio errors
    }
  };

  const playTransitionSound = () => {
    if (isMuted) return;

    try {
      if (transitionAudioRef.current) {
        // In a real implementation, this would play a transition sound file
        // For testing purposes, we just trigger play
        transitionAudioRef.current.play().catch(() => {
          // Silently fail if audio playback is blocked
        });
      }
    } catch (error) {
      // Ignore audio errors
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const calculateTotalDuration = () => {
    if (!sequence || !sequence.poses) return 0;
    return sequence.poses.reduce((total, pose) => total + pose.duration, 0);
  };

  const currentPose = sequence?.poses?.[currentPoseIndex];

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-900 flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-neutral-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-neutral-800 rounded-lg p-8 text-center">
          <div className="text-error-400 mb-4">
            <X size={48} className="mx-auto" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Error</h2>
          <p className="text-neutral-300 mb-6">{error}</p>
          <Button onClick={() => navigate('/sequences')} fullWidth>
            Back to Sequences
          </Button>
        </div>
      </div>
    );
  }

  // Completion screen
  if (isCompleted) {
    const totalDuration = Math.ceil(calculateTotalDuration() / 60);

    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg p-8 text-center">
          <div className="text-success-600 mb-4">
            <CheckCircle size={64} className="mx-auto" />
          </div>
          <h2 className="text-3xl font-bold text-neutral-900 mb-2">Great Work!</h2>
          <p className="text-xl text-neutral-700 mb-6">Practice Complete</p>

          <div className="bg-neutral-50 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4">Session Summary</h3>
            <div className="space-y-2">
              <div className="flex justify-between text-neutral-700">
                <span>Sequence:</span>
                <span className="font-medium">{sequence.name}</span>
              </div>
              <div className="flex justify-between text-neutral-700">
                <span>Poses Completed:</span>
                <span className="font-medium">{sequence.poses.length} poses</span>
              </div>
              <div className="flex justify-between text-neutral-700">
                <span>Duration:</span>
                <span className="font-medium">{totalDuration} minutes</span>
              </div>
            </div>
          </div>

          <Button onClick={handleFinish} fullWidth size="lg">
            Finish
          </Button>
        </div>
      </div>
    );
  }

  // Main practice interface
  return (
    <div className="min-h-screen bg-neutral-900 flex flex-col">
      {/* Header */}
      <header className="bg-neutral-800 border-b border-neutral-700 px-4 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex-1">
            <h1 className="text-lg font-semibold text-white">{sequence.name}</h1>
            <p className="text-sm text-neutral-400">
              Pose {currentPoseIndex + 1} of {sequence.poses.length}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleMute}
              className="p-2 text-neutral-400 hover:text-white transition-colors"
              aria-label={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
            </button>
            <button
              onClick={toggleSettings}
              className="p-2 text-neutral-400 hover:text-white transition-colors"
              aria-label="Settings"
            >
              <SettingsIcon size={20} />
            </button>
            <div className="text-right">
              <p className="text-sm text-neutral-400">Total Time</p>
              <p className="text-lg font-semibold text-white">
                {formatTime(calculateTotalDuration())}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="bg-neutral-800 px-4 py-2">
        <div className="max-w-6xl mx-auto">
          <div
            className="w-full bg-neutral-700 rounded-full h-2"
            role="progressbar"
            aria-valuenow={currentPoseIndex + 1}
            aria-valuemin="0"
            aria-valuemax={sequence.poses.length}
          >
            <div
              className="bg-primary-500 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${((currentPoseIndex + 1) / sequence.poses.length) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          {/* Pose Image */}
          <div className="mb-6">
            <div
              className="aspect-video bg-neutral-800 rounded-lg overflow-hidden mb-4 transition-opacity duration-300"
              data-testid="pose-container"
            >
              <img
                src={currentPose.image_url}
                alt={currentPose.name}
                className="w-full h-full object-cover animate-fade-in"
              />
            </div>
          </div>

          {/* Pose Info */}
          <div className="text-center mb-6">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-2">
              {currentPose.name}
            </h2>
            <p className="text-xl text-neutral-400 mb-4">{currentPose.sanskrit_name}</p>
            {currentPose.instructions && (
              <p className="text-neutral-300 max-w-2xl mx-auto">{currentPose.instructions}</p>
            )}
          </div>

          {/* Timer */}
          <div className="text-center mb-8">
            <div className="text-7xl md:text-8xl font-bold text-primary-400 mb-2">
              {formatTime(timeRemaining)}
            </div>
            <p className="text-neutral-500">Remaining</p>

            {/* Next Pose Preview */}
            {showNextPosePreview && currentPoseIndex < sequence.poses.length - 1 && (
              <div className="mt-4 text-neutral-300 text-lg animate-fade-in">
                Next: {sequence.poses[currentPoseIndex + 1].name}
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Button
              variant="outline"
              size="lg"
              onClick={handleExit}
              icon={<X size={20} />}
              className="bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700"
            >
              Exit
            </Button>

            <Button
              variant="outline"
              size="lg"
              onClick={handlePreviousPose}
              icon={<SkipBack size={20} />}
              disabled={currentPoseIndex === 0}
              className="bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Previous Pose"
            >
              Back
            </Button>

            <Button
              size="lg"
              onClick={handlePauseResume}
              icon={isPaused ? <Play size={24} /> : <Pause size={24} />}
              className="px-8"
            >
              {isPaused ? 'Resume' : 'Pause'}
            </Button>

            <Button
              variant="outline"
              size="lg"
              onClick={handleNextPose}
              icon={<SkipForward size={20} />}
              disabled={currentPoseIndex >= sequence.poses.length - 1}
              className="bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next Pose
            </Button>
          </div>
        </div>
      </main>

      {/* Exit Confirmation Dialog */}
      {showExitDialog && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50"
          onClick={cancelExit}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="bg-neutral-800 rounded-lg p-6 max-w-md w-full"
            onClick={(event) => event.stopPropagation()}
          >
            <h3 className="text-xl font-bold text-white mb-2">Exit Practice?</h3>
            <p className="text-neutral-300 mb-6">
              Are you sure you want to exit? Your progress will not be saved.
            </p>
            <div className="flex gap-3">
              <Button variant="outline" onClick={cancelExit} fullWidth>
                Cancel
              </Button>
              <Button onClick={confirmExit} fullWidth>
                Exit
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Settings Modal */}
      {showSettingsModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50"
          onClick={toggleSettings}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="bg-neutral-800 rounded-lg p-6 max-w-md w-full"
            onClick={(event) => event.stopPropagation()}
          >
            <h3 className="text-2xl font-bold text-white mb-6">Practice Settings</h3>

            <div className="space-y-6">
              {/* Preparation Time */}
              <div>
                <label
                  htmlFor="prep-time"
                  className="block text-sm font-medium text-neutral-300 mb-2"
                >
                  Preparation Time (seconds)
                </label>
                <input
                  id="prep-time"
                  type="number"
                  min="5"
                  max="30"
                  value={settings.preparationTime}
                  onChange={(event) =>
                    updateSettings('preparationTime', Number(event.target.value))
                  }
                  className="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <p className="mt-1 text-xs text-neutral-400">Time to prepare before each pose (5-30s)</p>
              </div>

              {/* Transition Warning Time */}
              <div>
                <label
                  htmlFor="warning-time"
                  className="block text-sm font-medium text-neutral-300 mb-2"
                >
                  Transition Warning Time (seconds)
                </label>
                <input
                  id="warning-time"
                  type="number"
                  min="3"
                  max="10"
                  value={settings.transitionWarningTime}
                  onChange={(event) =>
                    updateSettings('transitionWarningTime', Number(event.target.value))
                  }
                  className="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <p className="mt-1 text-xs text-neutral-400">
                  When to show next pose preview (3-10s before transition)
                </p>
              </div>

              {/* Volume Control */}
              <div>
                <label
                  htmlFor="volume"
                  className="block text-sm font-medium text-neutral-300 mb-2"
                >
                  Audio Volume
                </label>
                <input
                  id="volume"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.volume}
                  onChange={(event) => updateSettings('volume', Number(event.target.value))}
                  className="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
                />
                <div className="flex justify-between text-xs text-neutral-400 mt-1">
                  <span>0%</span>
                  <span>{Math.round(settings.volume * 100)}%</span>
                  <span>100%</span>
                </div>
              </div>
            </div>

            <div className="mt-8 flex gap-3">
              <Button variant="outline" onClick={toggleSettings} fullWidth>
                Close
              </Button>
              <Button onClick={toggleSettings} fullWidth>
                Save
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
