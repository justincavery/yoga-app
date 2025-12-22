// API client for YogaFlow backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Flag to toggle between mock and real API
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API !== 'false';

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE_URL;
    this.useMock = USE_MOCK_API;
  }

  // Helper method to make requests
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      // Handle non-OK responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
          status: response.status,
          message: errorData.detail || errorData.error || 'Request failed',
          data: errorData,
        };
      }

      return await response.json();
    } catch (error) {
      // Re-throw if it's already our error format
      if (error.status) throw error;

      // Network error or other failure
      throw {
        status: 0,
        message: error.message || 'Network error',
        data: {},
      };
    }
  }

  // Auth endpoints
  async register(data) {
    if (this.useMock) {
      return this.mockRegister(data);
    }
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data) {
    if (this.useMock) {
      return this.mockLogin(data);
    }
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async logout(token) {
    if (this.useMock) {
      return this.mockLogout();
    }
    return this.request('/auth/logout', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async getCurrentUser(token) {
    if (this.useMock) {
      return this.mockGetCurrentUser();
    }
    return this.request('/auth/me', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async refreshToken(refreshToken) {
    if (this.useMock) {
      return this.mockRefreshToken();
    }
    return this.request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  async forgotPassword(data) {
    if (this.useMock) {
      return this.mockForgotPassword(data);
    }
    return this.request('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async resetPassword(data) {
    if (this.useMock) {
      return this.mockResetPassword(data);
    }
    return this.request('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Profile endpoints
  async getProfile(token) {
    if (this.useMock) {
      return this.mockGetProfile();
    }
    return this.request('/profile', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async updateProfile(token, data) {
    if (this.useMock) {
      return this.mockUpdateProfile(data);
    }
    return this.request('/profile', {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
  }

  async changePassword(token, data) {
    if (this.useMock) {
      return this.mockChangePassword(data);
    }
    return this.request('/profile/password', {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
  }

  // Helper to transform pose data from API format to frontend format
  transformPose(pose) {
    // Split benefits and contraindications if they're strings
    const benefits = typeof pose.benefits === 'string'
      ? pose.benefits.split('\n').filter(b => b.trim()).map(b => b.replace(/^[•\-\*]\s*/, '').trim())
      : pose.benefits || [];

    const contraindications = typeof pose.contraindications === 'string'
      ? pose.contraindications.split('\n').filter(c => c.trim()).map(c => c.replace(/^[•\-\*]\s*/, '').trim())
      : pose.contraindications || [];

    return {
      id: pose.pose_id,
      name: pose.name_english,
      sanskrit_name: pose.name_sanskrit,
      difficulty: pose.difficulty_level,
      category: pose.category,
      description: pose.description,
      image_url: pose.image_urls?.[0] || 'https://placeholder.com/300',
      benefits,
      contraindications,
      instructions: pose.instructions,
      target_areas: pose.target_areas,
    };
  }

  // Pose endpoints
  async getPoses(filters = {}) {
    if (this.useMock) {
      return this.mockGetPoses(filters);
    }
    const params = new URLSearchParams(filters);
    const response = await this.request(`/poses?${params}`);

    // Transform poses to match frontend expectations
    if (response.poses && Array.isArray(response.poses)) {
      response.poses = response.poses.map(pose => this.transformPose(pose));
    }

    return response;
  }

  async getPoseById(poseId) {
    if (this.useMock) {
      return this.mockGetPoseById(poseId);
    }
    const pose = await this.request(`/poses/${poseId}`);
    return this.transformPose(pose);
  }

  // Transform sequence data from API format to frontend format
  transformSequence(sequence) {
    return {
      id: sequence.sequence_id,
      name: sequence.name,
      description: sequence.description,
      difficulty: sequence.difficulty_level,
      duration: sequence.duration_minutes,
      category: sequence.style,
      pose_count: sequence.pose_count,
      focus_area: sequence.focus_area,
      is_preset: sequence.is_preset,
      image_url: sequence.image_url || 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&h=600&fit=crop',
      created_at: sequence.created_at,
    };
  }

  // Sequence endpoints
  async getSequences(filters = {}) {
    if (this.useMock) {
      return this.mockGetSequences(filters);
    }
    const params = new URLSearchParams(filters);
    const response = await this.request(`/sequences?${params}`);

    // Transform sequences array if present
    if (response.sequences && Array.isArray(response.sequences)) {
      response.sequences = response.sequences.map(seq => this.transformSequence(seq));
    }

    return response;
  }

  async getSequenceById(sequenceId) {
    if (this.useMock) {
      return this.mockGetSequenceById(sequenceId);
    }
    const sequence = await this.request(`/sequences/${sequenceId}`);
    return this.transformSequence(sequence);
  }

  // Practice session endpoints
  async saveSession(data) {
    if (this.useMock) {
      return this.mockSaveSession(data);
    }
    return this.request('/sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Practice history and statistics endpoints
  async getStats(token) {
    if (this.useMock) {
      return this.mockGetStats();
    }
    return this.request('/stats', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async getHistory(params = {}) {
    if (this.useMock) {
      return this.mockGetHistory(params);
    }
    const queryParams = new URLSearchParams(params);
    return this.request(`/history?${queryParams}`, {
      method: 'GET',
    });
  }

  async getCalendar(params = {}) {
    if (this.useMock) {
      return this.mockGetCalendar(params);
    }
    const queryParams = new URLSearchParams(params);
    return this.request(`/calendar?${queryParams}`, {
      method: 'GET',
    });
  }

  // Mock implementations
  mockRegister(data) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          user: {
            user_id: 1,
            email: data.email,
            name: data.name,
            experience_level: data.experience_level,
            email_verified: false,
            created_at: new Date().toISOString(),
            last_login: new Date().toISOString(),
          },
          tokens: {
            access_token: 'mock-access-token-' + Date.now(),
            refresh_token: null,
            token_type: 'bearer',
            expires_in: 86400,
          },
        });
      }, 500);
    });
  }

  mockLogin(data) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Mock validation
        if (data.email === 'test@example.com' && data.password === 'TestPass123') {
          resolve({
            user: {
              user_id: 1,
              email: data.email,
              name: 'Test User',
              experience_level: 'beginner',
              email_verified: true,
              created_at: '2025-01-15T10:30:00Z',
              last_login: new Date().toISOString(),
            },
            tokens: {
              access_token: 'mock-access-token-' + Date.now(),
              refresh_token: data.remember_me ? 'mock-refresh-token-' + Date.now() : null,
              token_type: 'bearer',
              expires_in: data.remember_me ? 604800 : 86400,
            },
          });
        } else {
          reject({
            status: 401,
            message: 'Invalid credentials',
            data: {},
          });
        }
      }, 500);
    });
  }

  mockLogout() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          message: 'Successfully logged out',
          detail: 'Please discard your access and refresh tokens',
        });
      }, 300);
    });
  }

  mockGetCurrentUser() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          user_id: 1,
          email: 'test@example.com',
          name: 'Test User',
          experience_level: 'beginner',
          email_verified: true,
          created_at: '2025-01-15T10:30:00Z',
          last_login: new Date().toISOString(),
        });
      }, 300);
    });
  }

  mockRefreshToken() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          access_token: 'mock-access-token-' + Date.now(),
          refresh_token: 'mock-refresh-token-' + Date.now(),
          token_type: 'bearer',
          expires_in: 86400,
        });
      }, 300);
    });
  }

  mockGetPoses(filters) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const allPoses = [
          {
            id: 1,
            name: 'Mountain Pose',
            sanskrit_name: 'Tadasana',
            difficulty: 'Beginner',
            category: 'Standing',
            description: 'A foundational standing pose that improves posture and balance.',
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
          },
          {
            id: 2,
            name: 'Downward Dog',
            sanskrit_name: 'Adho Mukha Svanasana',
            difficulty: 'Beginner',
            category: 'Inversion',
            description: 'An energizing pose that stretches the entire body.',
            image_url: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400',
          },
          {
            id: 3,
            name: 'Warrior I',
            sanskrit_name: 'Virabhadrasana I',
            difficulty: 'Intermediate',
            category: 'Standing',
            description: 'A powerful standing pose that builds strength and stability.',
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
          },
          {
            id: 4,
            name: 'Tree Pose',
            sanskrit_name: 'Vrksasana',
            difficulty: 'Beginner',
            category: 'Balance',
            description: 'A balancing pose that improves focus and stability.',
            image_url: 'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400',
          },
          {
            id: 5,
            name: 'Child\'s Pose',
            sanskrit_name: 'Balasana',
            difficulty: 'Beginner',
            category: 'Restorative',
            description: 'A gentle resting pose that calms the mind and body.',
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
          },
          {
            id: 6,
            name: 'Cobra Pose',
            sanskrit_name: 'Bhujangasana',
            difficulty: 'Intermediate',
            category: 'Backbend',
            description: 'A gentle backbend that strengthens the spine.',
            image_url: 'https://images.unsplash.com/photo-1588286840104-8957b019727f?w=400',
          },
          {
            id: 7,
            name: 'Triangle Pose',
            sanskrit_name: 'Trikonasana',
            difficulty: 'Intermediate',
            category: 'Standing',
            description: 'A standing pose that stretches the sides of the body.',
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
          },
          {
            id: 8,
            name: 'Seated Forward Bend',
            sanskrit_name: 'Paschimottanasana',
            difficulty: 'Intermediate',
            category: 'Seated',
            description: 'A calming forward bend that stretches the back body.',
            image_url: 'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400',
          },
          {
            id: 9,
            name: 'Bridge Pose',
            sanskrit_name: 'Setu Bandhasana',
            difficulty: 'Beginner',
            category: 'Backbend',
            description: 'A gentle backbend that strengthens the back and legs.',
            image_url: 'https://images.unsplash.com/photo-1588286840104-8957b019727f?w=400',
          },
          {
            id: 10,
            name: 'Warrior II',
            sanskrit_name: 'Virabhadrasana II',
            difficulty: 'Intermediate',
            category: 'Standing',
            description: 'A powerful standing pose that opens the hips.',
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
          },
          {
            id: 11,
            name: 'Corpse Pose',
            sanskrit_name: 'Savasana',
            difficulty: 'Beginner',
            category: 'Restorative',
            description: 'A final relaxation pose for deep rest.',
            image_url: 'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400',
          },
          {
            id: 12,
            name: 'Plank Pose',
            sanskrit_name: 'Phalakasana',
            difficulty: 'Intermediate',
            category: 'Core',
            description: 'A core strengthening pose that builds endurance.',
            image_url: 'https://images.unsplash.com/photo-1588286840104-8957b019727f?w=400',
          },
        ];

        // Apply filters
        let filteredPoses = [...allPoses];

        if (filters.search) {
          const searchLower = filters.search.toLowerCase();
          filteredPoses = filteredPoses.filter(
            (pose) =>
              pose.name.toLowerCase().includes(searchLower) ||
              pose.sanskrit_name.toLowerCase().includes(searchLower) ||
              pose.description.toLowerCase().includes(searchLower)
          );
        }

        if (filters.difficulty) {
          filteredPoses = filteredPoses.filter(
            (pose) => pose.difficulty.toLowerCase() === filters.difficulty.toLowerCase()
          );
        }

        if (filters.category) {
          filteredPoses = filteredPoses.filter(
            (pose) => pose.category.toLowerCase() === filters.category.toLowerCase()
          );
        }

        resolve({
          poses: filteredPoses,
          total: filteredPoses.length,
          page: 1,
          pageSize: filteredPoses.length,
        });
      }, 500);
    });
  }

  mockGetPoseById(poseId) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const poses = {
          '1': {
            id: 1,
            name: 'Mountain Pose',
            sanskrit_name: 'Tadasana',
            difficulty: 'Beginner',
            category: 'Standing',
            description: 'A foundational standing pose that improves posture and balance. Mountain Pose is the basis for all standing poses and helps develop a sense of grounding and stability.',
            benefits: [
              'Improves posture and body awareness',
              'Builds strength in legs and core',
              'Calms the mind and reduces stress',
              'Improves balance and stability',
            ],
            steps: [
              'Stand with feet together, toes touching and heels slightly apart',
              'Distribute weight evenly across both feet',
              'Engage leg muscles and lift kneecaps',
              'Lengthen spine and lift chest',
              'Relax shoulders down and back',
              'Let arms hang naturally by your sides with palms facing forward',
              'Breathe deeply for 5-10 breaths',
            ],
            target_areas: ['Legs', 'Core', 'Posture'],
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
          },
          '2': {
            id: 2,
            name: 'Downward Dog',
            sanskrit_name: 'Adho Mukha Svanasana',
            difficulty: 'Beginner',
            category: 'Inversion',
            description: 'An energizing pose that stretches the entire body while building strength. This pose is one of the most recognized yoga poses and is part of the traditional Sun Salutation sequence.',
            benefits: [
              'Stretches hamstrings, calves, and shoulders',
              'Strengthens arms, legs, and core',
              'Energizes the body and calms the mind',
              'Relieves back pain and headaches',
            ],
            steps: [
              'Start on hands and knees in a tabletop position',
              'Spread fingers wide and press firmly into the mat',
              'Tuck toes under and lift hips up and back',
              'Straighten legs while keeping knees slightly bent if needed',
              'Press heels toward the floor',
              'Lengthen spine and relax neck',
              'Hold for 5-10 breaths',
            ],
            target_areas: ['Hamstrings', 'Shoulders', 'Back', 'Calves'],
            image_url: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400',
          },
          '3': {
            id: 3,
            name: 'Warrior I',
            sanskrit_name: 'Virabhadrasana I',
            difficulty: 'Intermediate',
            category: 'Standing',
            description: 'A powerful standing pose that builds strength and stability while opening the chest and hips. Warrior I cultivates focus, strength, and determination.',
            benefits: [
              'Strengthens legs, core, and arms',
              'Opens hips and chest',
              'Improves balance and concentration',
              'Builds stamina and endurance',
            ],
            steps: [
              'Start in Mountain Pose',
              'Step left foot back about 3-4 feet',
              'Turn left foot out 45 degrees',
              'Bend right knee to 90 degrees',
              'Square hips forward',
              'Raise arms overhead with palms facing each other',
              'Hold for 5-10 breaths, then switch sides',
            ],
            target_areas: ['Legs', 'Hips', 'Core', 'Shoulders'],
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
          },
        };

        const pose = poses[String(poseId)];

        if (pose) {
          resolve(pose);
        } else {
          reject({
            status: 404,
            message: 'Pose not found',
            data: {},
          });
        }
      }, 300);
    });
  }

  mockGetSequences(filters) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const allSequences = [
          {
            id: 1,
            name: 'Morning Energy Flow',
            description: 'Start your day with this energizing 20-minute sequence',
            category: 'Vinyasa',
            difficulty: 'Beginner',
            duration: 20,
            pose_count: 8,
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
          {
            id: 2,
            name: 'Deep Stretch & Relaxation',
            description: 'Wind down with this gentle stretching sequence',
            category: 'Restorative',
            difficulty: 'Beginner',
            duration: 30,
            pose_count: 10,
            image_url: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
          {
            id: 3,
            name: 'Core Strength Builder',
            description: 'Build core strength with this challenging sequence',
            category: 'Power',
            difficulty: 'Intermediate',
            duration: 25,
            pose_count: 12,
            image_url: 'https://images.unsplash.com/photo-1588286840104-8957b019727f?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
          {
            id: 4,
            name: 'Balance & Focus',
            description: 'Improve balance and mental focus with standing poses',
            category: 'Hatha',
            difficulty: 'Intermediate',
            duration: 30,
            pose_count: 9,
            image_url: 'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
          {
            id: 5,
            name: 'Advanced Warrior Flow',
            description: 'Dynamic warrior sequence for experienced practitioners',
            category: 'Vinyasa',
            difficulty: 'Advanced',
            duration: 40,
            pose_count: 15,
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
          {
            id: 6,
            name: 'Hip Opener Sequence',
            description: 'Release tension and increase hip flexibility',
            category: 'Yin',
            difficulty: 'Beginner',
            duration: 35,
            pose_count: 8,
            image_url: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
          {
            id: 7,
            name: 'Sun Salutation Flow',
            description: 'Classic sun salutation sequence to energize your practice',
            category: 'Vinyasa',
            difficulty: 'Beginner',
            duration: 15,
            pose_count: 12,
            image_url: 'https://images.unsplash.com/photo-1588286840104-8957b019727f?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
          {
            id: 8,
            name: 'Backbend Progression',
            description: 'Safely build up to deeper backbends',
            category: 'Hatha',
            difficulty: 'Advanced',
            duration: 35,
            pose_count: 10,
            image_url: 'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
          {
            id: 9,
            name: 'Evening Wind Down',
            description: 'Gentle sequence to prepare for restful sleep',
            category: 'Restorative',
            difficulty: 'Beginner',
            duration: 20,
            pose_count: 7,
            image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
          {
            id: 10,
            name: 'Power Vinyasa',
            description: 'Intense flowing sequence for strength and endurance',
            category: 'Power',
            difficulty: 'Advanced',
            duration: 45,
            pose_count: 18,
            image_url: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400',
            created_at: '2025-01-10T08:00:00Z',
          },
        ];

        // Apply filters
        let filteredSequences = [...allSequences];

        if (filters.search) {
          const searchLower = filters.search.toLowerCase();
          filteredSequences = filteredSequences.filter(
            (sequence) =>
              sequence.name.toLowerCase().includes(searchLower) ||
              sequence.description.toLowerCase().includes(searchLower) ||
              sequence.category.toLowerCase().includes(searchLower)
          );
        }

        if (filters.difficulty) {
          filteredSequences = filteredSequences.filter(
            (sequence) => sequence.difficulty.toLowerCase() === filters.difficulty.toLowerCase()
          );
        }

        if (filters.category) {
          filteredSequences = filteredSequences.filter(
            (sequence) => sequence.category.toLowerCase() === filters.category.toLowerCase()
          );
        }

        if (filters.duration) {
          // Filter by duration range (short: <20, medium: 20-35, long: >35)
          const duration = filters.duration.toLowerCase();
          if (duration === 'short') {
            filteredSequences = filteredSequences.filter((seq) => seq.duration < 20);
          } else if (duration === 'medium') {
            filteredSequences = filteredSequences.filter((seq) => seq.duration >= 20 && seq.duration <= 35);
          } else if (duration === 'long') {
            filteredSequences = filteredSequences.filter((seq) => seq.duration > 35);
          }
        }

        resolve({
          sequences: filteredSequences,
          total: filteredSequences.length,
          page: 1,
          pageSize: filteredSequences.length,
        });
      }, 500);
    });
  }

  mockGetSequenceById(sequenceId) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const sequence = {
          id: sequenceId,
          name: 'Morning Energy Flow',
          description: 'Start your day with this energizing 20-minute sequence',
          category: 'Vinyasa',
          difficulty: 'Beginner',
          duration: 20,
          pose_count: 8,
          image_url: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400',
          created_at: '2025-01-10T08:00:00Z',
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
          ],
        };

        if (sequenceId) {
          resolve(sequence);
        } else {
          reject({
            status: 404,
            message: 'Sequence not found',
            data: {},
          });
        }
      }, 300);
    });
  }

  mockForgotPassword(data) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          message: 'Password reset email sent',
          email: data.email,
        });
      }, 500);
    });
  }

  mockResetPassword(data) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Simulate expired token scenario
        if (data.token === 'expired-token') {
          reject({
            status: 400,
            message: 'Reset token has expired',
            data: {},
          });
        } else {
          resolve({
            message: 'Password reset successful',
            email: 'test@example.com',
          });
        }
      }, 500);
    });
  }

  mockGetProfile() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          user_id: 1,
          email: 'test@example.com',
          name: 'Test User',
          experience_level: 'beginner',
          email_verified: true,
          created_at: '2025-01-15T10:30:00Z',
          last_login: '2025-12-05T08:00:00Z',
        });
      }, 300);
    });
  }

  mockUpdateProfile(data) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          user_id: 1,
          email: 'test@example.com',
          name: data.name || 'Test User',
          experience_level: data.experience_level || 'beginner',
          email_verified: true,
          created_at: '2025-01-15T10:30:00Z',
          last_login: '2025-12-05T08:00:00Z',
        });
      }, 500);
    });
  }

  mockChangePassword(data) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // Simulate wrong current password
        if (data.current_password === 'WrongPassword123') {
          reject({
            status: 401,
            message: 'Current password is incorrect',
            data: {},
          });
        } else {
          resolve({
            message: 'Password changed successfully',
            email: 'test@example.com',
          });
        }
      }, 500);
    });
  }

  mockSaveSession(data) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          message: 'Session saved successfully',
          session_id: Math.floor(Math.random() * 1000) + 1,
          saved_at: new Date().toISOString(),
        });
      }, 300);
    });
  }

  mockGetStats() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          total_sessions: 15,
          total_practice_time_seconds: 18000,
          total_practice_time_hours: 5.0,
          average_session_duration_minutes: 20,
          current_streak_days: 3,
          completion_rate_percentage: 93.3,
          sessions_last_30_days: 12,
          most_practiced_sequences: [
            {
              sequence_id: 1,
              sequence_name: 'Morning Energy Flow',
              practice_count: 5,
            },
            {
              sequence_id: 2,
              sequence_name: 'Deep Stretch & Relaxation',
              practice_count: 4,
            },
            {
              sequence_id: 3,
              sequence_name: 'Core Strength Builder',
              practice_count: 3,
            },
          ],
        });
      }, 300);
    });
  }

  mockGetHistory(params = {}) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const allSessions = [
          {
            session_id: 1,
            user_id: 1,
            sequence_id: 1,
            started_at: '2025-12-05T08:00:00Z',
            completed_at: '2025-12-05T08:20:00Z',
            duration_seconds: 1200,
            completion_status: 'completed',
            sequence_name: 'Morning Energy Flow',
            sequence_difficulty: 'beginner',
            sequence_focus_area: 'energy',
          },
          {
            session_id: 2,
            user_id: 1,
            sequence_id: 2,
            started_at: '2025-12-04T19:00:00Z',
            completed_at: '2025-12-04T19:30:00Z',
            duration_seconds: 1800,
            completion_status: 'completed',
            sequence_name: 'Deep Stretch & Relaxation',
            sequence_difficulty: 'beginner',
            sequence_focus_area: 'flexibility',
          },
          {
            session_id: 3,
            user_id: 1,
            sequence_id: 3,
            started_at: '2025-12-03T17:00:00Z',
            completed_at: '2025-12-03T17:25:00Z',
            duration_seconds: 1500,
            completion_status: 'completed',
            sequence_name: 'Core Strength Builder',
            sequence_difficulty: 'intermediate',
            sequence_focus_area: 'strength',
          },
          {
            session_id: 4,
            user_id: 1,
            sequence_id: 1,
            started_at: '2025-12-02T08:00:00Z',
            completed_at: '2025-12-02T08:20:00Z',
            duration_seconds: 1200,
            completion_status: 'completed',
            sequence_name: 'Morning Energy Flow',
            sequence_difficulty: 'beginner',
            sequence_focus_area: 'energy',
          },
          {
            session_id: 5,
            user_id: 1,
            sequence_id: 2,
            started_at: '2025-12-01T19:30:00Z',
            completed_at: '2025-12-01T20:00:00Z',
            duration_seconds: 1800,
            completion_status: 'completed',
            sequence_name: 'Deep Stretch & Relaxation',
            sequence_difficulty: 'beginner',
            sequence_focus_area: 'flexibility',
          },
        ];

        const page = parseInt(params.page) || 1;
        const pageSize = parseInt(params.page_size) || 20;
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        const sessions = allSessions.slice(startIndex, endIndex);

        resolve({
          sessions,
          total: allSessions.length,
          page,
          page_size: pageSize,
          total_pages: Math.ceil(allSessions.length / pageSize),
        });
      }, 300);
    });
  }
}

// Export singleton instance
const apiClient = new ApiClient();
export default apiClient;
