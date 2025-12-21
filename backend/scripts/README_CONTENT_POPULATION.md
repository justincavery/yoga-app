# Content Population Scripts

This directory contains SQL scripts for populating pose instructions and creating curated sequences for the YogaFlow application.

## Prerequisites

1. Database must be running (PostgreSQL)
2. Alembic migration `add_pose_instruction_fields` must be applied
3. Poses must already exist in the database (from poses.yaml seed data)

## Execution Order

Run the scripts in this order:

### 1. Apply Database Migration

```bash
cd /Users/justinavery/claude/yoga-app/backend
alembic upgrade head
```

This adds the following fields to the `poses` table:
- `entry_instructions` (TEXT ARRAY)
- `exit_instructions` (TEXT ARRAY)
- `holding_cues` (TEXT)
- `breathing_pattern` (TEXT)
- `has_side_variation` (BOOLEAN)

### 2. Populate Pose Instructions

Run all four batches to add instructions for all 80 poses:

```bash
# Batch 1: Poses 1-20
psql postgresql://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev -f populate_pose_instructions_batch1.sql

# Batch 2: Poses 21-40
psql postgresql://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev -f populate_pose_instructions_batch2.sql

# Batch 3: Poses 41-60
psql postgresql://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev -f populate_pose_instructions_batch3.sql

# Batch 4: Poses 61-80
psql postgresql://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev -f populate_pose_instructions_batch4.sql
```

Or run all at once:

```bash
psql postgresql://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev \
  -f populate_pose_instructions_batch1.sql \
  -f populate_pose_instructions_batch2.sql \
  -f populate_pose_instructions_batch3.sql \
  -f populate_pose_instructions_batch4.sql
```

### 3. Create Sequences

```bash
psql postgresql://yogaflow:yogaflow_dev_password@localhost:5432/yogaflow_dev -f populate_sequences.sql
```

This creates 15 curated sequences:

**Relaxation (3):**
1. Gentle Evening Unwind (Easy, 15 min)
2. Deep Relaxation Flow (Medium, 25 min)
3. Restorative Stress Relief (Easy, 30 min)

**Morning/Energizing (3):**
4. Morning Wake-Up (Easy, 10 min)
5. Energizing Flow (Medium, 20 min)
6. Invigorating Power Sequence (Hard, 30 min)

**Body-Specific Focus (5):**
7. Gentle Back Care (Easy, 15 min)
8. Back Strengthening (Medium, 25 min)
9. Advanced Backbend Practice (Hard, 30 min)
10. Leg & Hip Opening (Easy, 20 min)
11. Strong Legs & Balance (Medium, 25 min)

**Specialized (4):**
12. Core Foundations (Medium, 20 min)
13. Flexibility Builder (Medium, 25 min)
14. Arm Balance Progression (Hard, 30 min)
15. Full Body Integration (Hard, 35 min)

## Verification

After running all scripts, verify the data:

```sql
-- Check pose instructions are populated
SELECT
  name_english,
  ARRAY_LENGTH(entry_instructions, 1) as entry_steps,
  ARRAY_LENGTH(exit_instructions, 1) as exit_steps,
  has_side_variation
FROM poses
WHERE entry_instructions IS NOT NULL
LIMIT 10;

-- Check sequences were created
SELECT
  s.name,
  s.difficulty_level,
  s.duration_minutes,
  s.focus_area,
  COUNT(sp.pose_id) as pose_count
FROM sequences s
LEFT JOIN sequence_poses sp ON s.sequence_id = sp.sequence_id
WHERE s.is_preset = true
GROUP BY s.sequence_id, s.name, s.difficulty_level, s.duration_minutes, s.focus_area
ORDER BY s.sequence_id;

-- Check poses with side variations
SELECT name_english
FROM poses
WHERE has_side_variation = true
ORDER BY name_english;
```

Expected results:
- 80 poses with complete instructions
- 15 preset sequences
- ~20 poses marked with `has_side_variation = true`

## Content Guidelines

### Pose Instructions
- **Entry Instructions**: 3-5 steps with breathing cues
- **Exit Instructions**: 2-3 steps for safe transitions
- **Holding Cues**: 1-2 sentences on alignment and safety
- **Breathing Pattern**: Specific guidance (e.g., "Breathe deeply for 5-8 counts")
- **Side Variations**: Marked for poses like Warrior II, Triangle, Tree Pose, etc.

### Sequence Design Principles
- Start with gentle warm-up poses
- Build to main practice poses
- End with cool-down and relaxation
- Never jarring transitions (e.g., standing→floor→standing)
- Include variety: forward bends, backbends, twists, lateral bends
- Duration per pose:
  - Easy poses: 30-45 seconds
  - Medium poses: 45-60 seconds
  - Advanced poses: 60-90 seconds
  - Savasana: 3-5 minutes

## Troubleshooting

### Common Issues

**Error: column "entry_instructions" does not exist**
- Solution: Run Alembic migration first: `alembic upgrade head`

**Error: relation "poses" does not exist**
- Solution: Ensure database is seeded with poses from poses.yaml

**Error: null value in column "pose_id"**
- Solution: Check that pose names in SQL match exactly with database entries

**Sequences have 0 poses**
- Solution: Verify pose names match exactly (check for typos, special characters)

## Development Notes

- All sequences use `is_preset = true` and `created_by = NULL`
- Pose durations are in seconds
- Position order is 1-indexed
- Some advanced sequences include rest periods (Child's Pose)
- TTS pacing target: 120-140 words per minute

## Next Steps

After populating content:
1. Test sequence playback via API endpoints
2. Verify TTS integration reads instructions correctly
3. Test pose detail pages display instructions
4. Create user acceptance tests for sequence flow
5. Consider adding more sequences based on user feedback
