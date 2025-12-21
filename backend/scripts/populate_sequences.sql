-- Populate 15 curated yoga sequences
-- This script creates preset sequences with appropriate poses, durations, and flow
-- Run after pose instructions have been populated

-- First, let's create a helper to get pose IDs by name
-- We'll use subqueries to reference poses by their English names

-- RELAXATION SEQUENCES (3 sequences)

-- Sequence 1: Gentle Evening Unwind (Easy, 15 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Gentle Evening Unwind',
  'A calming 15-minute sequence perfect for evening practice. Release the tension of your day with gentle stretches and restorative poses that prepare your body and mind for restful sleep.',
  'beginner',
  15,
  'RELAXATION',
  'GENTLE',
  true,
  NULL, NOW(), NOW()
);

-- Get the sequence_id for Gentle Evening Unwind
DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Gentle Evening Unwind';

  -- Insert poses for Gentle Evening Unwind
  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Easy Pose'), 1, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 3, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Forward Bend'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Spinal Twist'), 5, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bound Angle Pose'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 7, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Knees to Chest Pose'), 8, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Happy Baby Pose'), 9, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 10, 300);
END $$;

-- Sequence 2: Deep Relaxation Flow (Medium, 25 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Deep Relaxation Flow',
  'A comprehensive 25-minute restorative sequence that systematically releases tension from every part of your body. Perfect for stress relief and deep relaxation.',
  'intermediate',
  25,
  'RELAXATION',
  'RESTORATIVE',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Deep Relaxation Flow';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Easy Pose'), 1, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 2, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 3, 120),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Standing Forward Bend'), 5, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Forward Bend'), 6, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bound Angle Pose'), 7, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Reclined Bound Angle Pose'), 8, 120),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 9, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Happy Baby Pose'), 10, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Legs Up the Wall'), 11, 180),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 12, 300);
END $$;

-- Sequence 3: Restorative Stress Relief (Easy, 30 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Restorative Stress Relief',
  'An extended 30-minute restorative practice focused on releasing deep-seated tension and anxiety. Use props for maximum comfort and surrender into each pose.',
  'beginner',
  30,
  'RELAXATION',
  'RESTORATIVE',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Restorative Stress Relief';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Easy Pose'), 1, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 2, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 3, 180),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Sphinx Pose'), 4, 120),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 5, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Forward Bend'), 6, 150),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bound Angle Pose'), 7, 120),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Reclined Bound Angle Pose'), 8, 180),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Knees to Chest Pose'), 9, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 10, 120),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Legs Up the Wall'), 11, 300),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 12, 300);
END $$;

-- MORNING/ENERGIZING SEQUENCES (3 sequences)

-- Sequence 4: Morning Wake-Up (Easy, 10 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Morning Wake-Up',
  'A quick 10-minute energizing sequence to awaken your body and mind. Perfect for busy mornings when you need a gentle boost of energy.',
  'beginner',
  10,
  'ENERGY',
  'GENTLE',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Morning Wake-Up';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Mountain Pose'), 1, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Standing Forward Bend'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 3, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Low Lunge'), 5, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior I'), 6, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Mountain Pose'), 7, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 8, 120);
END $$;

-- Sequence 5: Energizing Flow (Medium, 20 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Energizing Flow',
  'A dynamic 20-minute vinyasa flow that builds heat and energy. Move with your breath through standing poses and gentle backbends to invigorate your entire being.',
  'intermediate',
  20,
  'ENERGY',
  'VINYASA',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Energizing Flow';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Mountain Pose'), 1, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 3, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior I'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior II'), 5, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Triangle Pose'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Extended Side Angle Pose'), 7, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 8, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cobra Pose'), 9, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bridge Pose'), 10, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Spinal Twist'), 11, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 12, 180);
END $$;

-- Sequence 6: Invigorating Power Sequence (Hard, 30 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Invigorating Power Sequence',
  'An intense 30-minute power yoga sequence that challenges your strength, balance, and endurance. Build heat with dynamic movements and powerful standing poses.',
  'advanced',
  30,
  'STRENGTH',
  'POWER',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Invigorating Power Sequence';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Mountain Pose'), 1, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 3, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior I'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior II'), 5, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Reverse Warrior'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Extended Side Angle Pose'), 7, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Half Moon Pose'), 8, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior III'), 9, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Tree Pose'), 10, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Crow Pose'), 11, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Boat Pose'), 12, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bridge Pose'), 13, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 14, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 15, 300);
END $$;

-- BODY-SPECIFIC FOCUS SEQUENCES (5 sequences)

-- Sequence 7: Gentle Back Care (Easy, 15 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Gentle Back Care',
  'A therapeutic 15-minute sequence designed to relieve back tension and improve spinal mobility. Perfect for those with mild back discomfort or looking to maintain back health.',
  'beginner',
  15,
  'FLEXIBILITY',
  'GENTLE',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Gentle Back Care';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 1, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 2, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Sphinx Pose'), 3, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Extended Puppy Pose'), 4, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 5, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Knees to Chest Pose'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bridge Pose'), 7, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Happy Baby Pose'), 8, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 9, 180);
END $$;

-- Sequence 8: Back Strengthening (Medium, 25 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Back Strengthening',
  'A 25-minute sequence focused on building back strength and improving posture. Combines gentle backbends with core engagement to create a healthy, resilient spine.',
  'intermediate',
  25,
  'STRENGTH',
  'HATHA',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Back Strengthening';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 1, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Sphinx Pose'), 3, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cobra Pose'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 5, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Locust Pose'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bow Pose'), 7, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 8, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bridge Pose'), 9, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Boat Pose'), 10, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Spinal Twist'), 11, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 12, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 13, 240);
END $$;

-- Sequence 9: Advanced Backbend Practice (Hard, 30 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Advanced Backbend Practice',
  'An intensive 30-minute sequence exploring deep backbends. Build heat with preparatory poses before moving into advanced heart-opening backbends.',
  'advanced',
  30,
  'FLEXIBILITY',
  'VINYASA',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Advanced Backbend Practice';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 1, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Low Lunge'), 3, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cobra Pose'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Locust Pose'), 5, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bow Pose'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Camel Pose'), 7, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 8, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bridge Pose'), 9, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Wheel Pose'), 10, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Full Wheel Pose'), 11, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Knees to Chest Pose'), 12, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 13, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 14, 300);
END $$;

-- Sequence 10: Leg & Hip Opening (Easy, 20 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Leg & Hip Opening',
  'A 20-minute sequence focused on releasing tight hips and hamstrings. Perfect for those who sit for long periods or want to improve lower body flexibility.',
  'beginner',
  20,
  'FLEXIBILITY',
  'YIN',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Leg & Hip Opening';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Easy Pose'), 1, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 3, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Low Lunge'), 4, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Lizard Pose'), 5, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Pigeon Pose'), 6, 120),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Garland Pose'), 7, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bound Angle Pose'), 8, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Wide-Legged Forward Bend'), 9, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 10, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 11, 180);
END $$;

-- Sequence 11: Strong Legs & Balance (Medium, 25 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Strong Legs & Balance',
  'A 25-minute strength and balance sequence focused on building powerful legs and improving stability. Challenge yourself with standing poses and balancing postures.',
  'intermediate',
  25,
  'STRENGTH',
  'HATHA',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Strong Legs & Balance';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Mountain Pose'), 1, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior I'), 3, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior II'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Triangle Pose'), 5, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Extended Side Angle Pose'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Half Moon Pose'), 7, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior III'), 8, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Tree Pose'), 9, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Eagle Pose'), 10, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Chair Pose' OR name_english = 'Garland Pose'), 11, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Standing Split'), 12, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Forward Bend'), 13, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 14, 240);
END $$;

-- SPECIALIZED SEQUENCES (4 sequences)

-- Sequence 12: Core Foundations (Medium, 20 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Core Foundations',
  'A 20-minute sequence dedicated to building core strength and stability. Develop a strong foundation for all your yoga poses with targeted abdominal and back work.',
  'intermediate',
  20,
  'CORE',
  'POWER',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Core Foundations';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 1, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Boat Pose'), 3, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Side Plank'), 4, 45),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Dolphin Pose'), 5, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Locust Pose'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bow Pose'), 7, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bridge Pose'), 8, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Boat Pose'), 9, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Spinal Twist'), 10, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 11, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 12, 180);
END $$;

-- Sequence 13: Flexibility Builder (Medium, 25 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Flexibility Builder',
  'A 25-minute sequence designed to systematically improve flexibility throughout your entire body. Hold poses longer to deepen stretches and increase range of motion.',
  'intermediate',
  25,
  'FLEXIBILITY',
  'YIN',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Flexibility Builder';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 1, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 2, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Low Lunge'), 3, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Lizard Pose'), 4, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Pigeon Pose'), 5, 120),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Wide-Legged Forward Bend'), 6, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Forward Bend'), 7, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Wide-Legged Forward Bend'), 8, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bound Angle Pose'), 9, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Reclining Hand to Big Toe Pose'), 10, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 11, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 12, 240);
END $$;

-- Sequence 14: Arm Balance Progression (Hard, 30 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Arm Balance Progression',
  'An advanced 30-minute sequence building toward challenging arm balances. Develop the strength, technique, and confidence needed for inversions and arm-supported poses.',
  'advanced',
  30,
  'STRENGTH',
  'POWER',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Arm Balance Progression';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 1, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 2, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Dolphin Pose'), 3, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Side Plank'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Crow Pose'), 5, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Side Crow Pose'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 7, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Forearm Stand'), 8, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Headstand'), 9, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 10, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Flying Pigeon Pose'), 11, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Shoulder Pressing Pose'), 12, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 13, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Legs Up the Wall'), 14, 180),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 15, 300);
END $$;

-- Sequence 15: Full Body Integration (Hard, 35 min)
INSERT INTO sequences (name, description, difficulty_level, duration_minutes, focus_area, style, is_preset, created_by, created_at, updated_at)
VALUES (
  'Full Body Integration',
  'A comprehensive 35-minute advanced sequence that integrates all aspects of yoga practice. Flow through standing poses, backbends, twists, and inversions for a complete full-body workout.',
  'advanced',
  35,
  'STRENGTH',
  'VINYASA',
  true,
  NULL, NOW(), NOW()
);

DO $$
DECLARE
  seq_id INTEGER;
BEGIN
  SELECT sequence_id INTO seq_id FROM sequences WHERE name = 'Full Body Integration';

  INSERT INTO sequence_poses (sequence_id, pose_id, position_order, duration_seconds) VALUES
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Mountain Pose'), 1, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Cat-Cow Pose'), 2, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Downward Facing Dog'), 3, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior I'), 4, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior II'), 5, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Extended Side Angle Pose'), 6, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Half Moon Pose'), 7, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Warrior III'), 8, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Tree Pose'), 9, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Crow Pose'), 10, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Boat Pose'), 11, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Bow Pose'), 12, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Camel Pose'), 13, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Wheel Pose'), 14, 75),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Headstand'), 15, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Child''s Pose'), 16, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Seated Spinal Twist'), 17, 60),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Supine Spinal Twist'), 18, 90),
  (seq_id, (SELECT pose_id FROM poses WHERE name_english = 'Corpse Pose'), 19, 300);
END $$;

-- Verification query to see all sequences
SELECT
  s.sequence_id,
  s.name,
  s.difficulty_level,
  s.duration_minutes,
  s.focus_area,
  s.style,
  COUNT(sp.pose_id) as pose_count
FROM sequences s
LEFT JOIN sequence_poses sp ON s.sequence_id = sp.sequence_id
WHERE s.is_preset = true
GROUP BY s.sequence_id, s.name, s.difficulty_level, s.duration_minutes, s.focus_area, s.style
ORDER BY s.sequence_id;
