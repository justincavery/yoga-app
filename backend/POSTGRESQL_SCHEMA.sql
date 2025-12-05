-- PostgreSQL Database Schema for YogaFlow
-- Compatible with requirements.md specifications
-- Generated: 2025-12-05

-- Enable UUID extension (optional, currently using INTEGER for IDs)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- USERS TABLE
-- Stores user account information and authentication
-- ==============================================

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    experience_level VARCHAR(50) DEFAULT 'beginner' CHECK (experience_level IN ('beginner', 'intermediate', 'advanced')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE NOT NULL,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- POSES TABLE
-- Stores yoga poses/asanas with detailed information
-- ==============================================

CREATE TABLE poses (
    pose_id SERIAL PRIMARY KEY,
    name_english VARCHAR(255) NOT NULL,
    name_sanskrit VARCHAR(255),
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'standing', 'seated', 'balancing', 'backbends',
        'forward_bends', 'twists', 'inversions', 'arm_balances', 'restorative'
    )),
    difficulty_level VARCHAR(50) NOT NULL CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    description TEXT NOT NULL,
    instructions JSONB NOT NULL,  -- Array of step-by-step instructions
    benefits TEXT,
    contraindications TEXT,
    target_areas JSONB,  -- Array of target muscle groups
    image_urls JSONB NOT NULL,  -- Array of image URLs (minimum 1)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_poses_name_english ON poses(name_english);
CREATE INDEX idx_poses_name_sanskrit ON poses(name_sanskrit);
CREATE INDEX idx_poses_category ON poses(category);
CREATE INDEX idx_poses_difficulty ON poses(difficulty_level);
CREATE INDEX idx_poses_created_at ON poses(created_at);

-- GIN indexes for JSONB columns (for searching within JSON)
CREATE INDEX idx_poses_instructions_gin ON poses USING GIN (instructions);
CREATE INDEX idx_poses_target_areas_gin ON poses USING GIN (target_areas);

-- Trigger to auto-update updated_at
CREATE TRIGGER update_poses_updated_at BEFORE UPDATE ON poses
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- SEQUENCES TABLE
-- Stores ordered collections of poses for practice
-- ==============================================

CREATE TABLE sequences (
    sequence_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty_level VARCHAR(50) NOT NULL CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    duration_minutes INTEGER NOT NULL,
    focus_area VARCHAR(50) NOT NULL CHECK (focus_area IN ('flexibility', 'strength', 'relaxation', 'balance', 'core', 'energy')),
    style VARCHAR(50) NOT NULL CHECK (style IN ('vinyasa', 'yin', 'restorative', 'hatha', 'power', 'gentle')),
    is_preset BOOLEAN DEFAULT FALSE NOT NULL,
    created_by INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_sequences_name ON sequences(name);
CREATE INDEX idx_sequences_difficulty ON sequences(difficulty_level);
CREATE INDEX idx_sequences_focus_area ON sequences(focus_area);
CREATE INDEX idx_sequences_style ON sequences(style);
CREATE INDEX idx_sequences_is_preset ON sequences(is_preset);
CREATE INDEX idx_sequences_created_by ON sequences(created_by);
CREATE INDEX idx_sequences_created_at ON sequences(created_at);

-- Trigger to auto-update updated_at
CREATE TRIGGER update_sequences_updated_at BEFORE UPDATE ON sequences
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- SEQUENCE_POSES TABLE
-- Junction table for sequence-pose many-to-many relationship
-- ==============================================

CREATE TABLE sequence_poses (
    sequence_pose_id SERIAL PRIMARY KEY,
    sequence_id INTEGER NOT NULL REFERENCES sequences(sequence_id) ON DELETE CASCADE,
    pose_id INTEGER NOT NULL REFERENCES poses(pose_id) ON DELETE CASCADE,
    position_order INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL DEFAULT 60,
    UNIQUE(sequence_id, position_order)
);

-- Indexes for performance
CREATE INDEX idx_sequence_poses_sequence ON sequence_poses(sequence_id);
CREATE INDEX idx_sequence_poses_pose ON sequence_poses(pose_id);
CREATE INDEX idx_sequence_poses_order ON sequence_poses(sequence_id, position_order);

-- ==============================================
-- PRACTICE_SESSIONS TABLE
-- Tracks user practice history and statistics
-- ==============================================

CREATE TABLE practice_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    sequence_id INTEGER REFERENCES sequences(sequence_id) ON DELETE SET NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds INTEGER NOT NULL DEFAULT 0,
    completion_status VARCHAR(50) NOT NULL DEFAULT 'abandoned' CHECK (completion_status IN ('completed', 'partial', 'abandoned'))
);

-- Indexes for performance (critical for statistics queries)
CREATE INDEX idx_practice_sessions_user ON practice_sessions(user_id);
CREATE INDEX idx_practice_sessions_sequence ON practice_sessions(sequence_id);
CREATE INDEX idx_practice_sessions_started_at ON practice_sessions(started_at);
CREATE INDEX idx_practice_sessions_user_started ON practice_sessions(user_id, started_at);
CREATE INDEX idx_practice_sessions_status ON practice_sessions(completion_status);

-- ==============================================
-- USER_FAVORITES TABLE
-- Tracks user-saved sequences
-- ==============================================

CREATE TABLE user_favorites (
    favorite_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    sequence_id INTEGER NOT NULL REFERENCES sequences(sequence_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, sequence_id)
);

-- Indexes for performance
CREATE INDEX idx_user_favorites_user ON user_favorites(user_id);
CREATE INDEX idx_user_favorites_sequence ON user_favorites(sequence_id);
CREATE INDEX idx_user_favorites_created_at ON user_favorites(created_at);

-- ==============================================
-- ACHIEVEMENTS TABLE
-- Defines available badges and milestones
-- ==============================================

CREATE TABLE achievements (
    achievement_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(500) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('streak', 'sessions', 'time', 'mastery')),
    threshold_value INTEGER NOT NULL,
    icon_url VARCHAR(500)
);

-- Indexes for performance
CREATE INDEX idx_achievements_type ON achievements(type);

-- ==============================================
-- USER_ACHIEVEMENTS TABLE
-- Tracks earned user achievements
-- ==============================================

CREATE TABLE user_achievements (
    user_achievement_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    achievement_id INTEGER NOT NULL REFERENCES achievements(achievement_id) ON DELETE CASCADE,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, achievement_id)
);

-- Indexes for performance
CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_achievement ON user_achievements(achievement_id);
CREATE INDEX idx_user_achievements_earned_at ON user_achievements(earned_at);

-- ==============================================
-- SAMPLE DATA (Optional - for development)
-- ==============================================

-- Insert sample achievements
INSERT INTO achievements (name, description, type, threshold_value) VALUES
    ('First Step', 'Complete your first practice session', 'sessions', 1),
    ('Getting Started', 'Complete 10 practice sessions', 'sessions', 10),
    ('Dedicated Practitioner', 'Complete 50 practice sessions', 'sessions', 50),
    ('Yoga Enthusiast', 'Complete 100 practice sessions', 'sessions', 100),
    ('7-Day Streak', 'Practice 7 consecutive days', 'streak', 7),
    ('30-Day Streak', 'Practice 30 consecutive days', 'streak', 30),
    ('100-Day Streak', 'Practice 100 consecutive days', 'streak', 100),
    ('10 Hours', 'Accumulate 10 hours of practice time', 'time', 600),
    ('50 Hours', 'Accumulate 50 hours of practice time', 'time', 3000),
    ('100 Hours', 'Accumulate 100 hours of practice time', 'time', 6000);

-- ==============================================
-- VIEWS (Optional - for analytics)
-- ==============================================

-- User Statistics View
CREATE OR REPLACE VIEW user_statistics AS
SELECT
    u.user_id,
    u.email,
    u.name,
    COUNT(ps.session_id) as total_sessions,
    SUM(ps.duration_seconds) as total_practice_seconds,
    AVG(ps.duration_seconds) as avg_session_seconds,
    MAX(ps.started_at) as last_practice_date,
    COUNT(DISTINCT DATE(ps.started_at)) as total_practice_days
FROM users u
LEFT JOIN practice_sessions ps ON u.user_id = ps.user_id
    AND ps.completion_status = 'completed'
GROUP BY u.user_id, u.email, u.name;

-- Popular Poses View
CREATE OR REPLACE VIEW popular_poses AS
SELECT
    p.pose_id,
    p.name_english,
    p.name_sanskrit,
    p.category,
    p.difficulty_level,
    COUNT(DISTINCT sp.sequence_id) as times_in_sequences,
    COUNT(DISTINCT ps.session_id) as times_practiced
FROM poses p
LEFT JOIN sequence_poses sp ON p.pose_id = sp.pose_id
LEFT JOIN practice_sessions ps ON sp.sequence_id = ps.sequence_id
    AND ps.completion_status = 'completed'
GROUP BY p.pose_id, p.name_english, p.name_sanskrit, p.category, p.difficulty_level
ORDER BY times_practiced DESC;

-- ==============================================
-- COMMENTS AND DOCUMENTATION
-- ==============================================

COMMENT ON TABLE users IS 'User accounts and authentication information';
COMMENT ON TABLE poses IS 'Yoga poses/asanas with detailed instructions';
COMMENT ON TABLE sequences IS 'Ordered collections of poses for practice sessions';
COMMENT ON TABLE sequence_poses IS 'Junction table linking sequences to poses with order and duration';
COMMENT ON TABLE practice_sessions IS 'User practice history and session tracking';
COMMENT ON TABLE user_favorites IS 'User-saved favorite sequences';
COMMENT ON TABLE achievements IS 'Available badges and milestones';
COMMENT ON TABLE user_achievements IS 'User-earned achievements';

-- ==============================================
-- SECURITY
-- ==============================================

-- Revoke public access
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;

-- Grant appropriate permissions (adjust for your user)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO yogaflow_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO yogaflow_app;

-- ==============================================
-- MAINTENANCE
-- ==============================================

-- Enable auto-vacuum
ALTER TABLE users SET (autovacuum_enabled = true);
ALTER TABLE poses SET (autovacuum_enabled = true);
ALTER TABLE sequences SET (autovacuum_enabled = true);
ALTER TABLE practice_sessions SET (autovacuum_enabled = true);

-- ==============================================
-- BACKUP RECOMMENDATIONS
-- ==============================================

-- Daily backups recommended
-- pg_dump yogaflow_db > backup_$(date +%Y%m%d).sql

-- Point-in-time recovery (PITR) for production
-- Configure in postgresql.conf:
-- wal_level = replica
-- archive_mode = on
-- archive_command = 'cp %p /path/to/archive/%f'
