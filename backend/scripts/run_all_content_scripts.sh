#!/bin/bash
# Master script to populate all pose instructions and sequences
# Run this after applying the Alembic migration: alembic upgrade head

set -e  # Exit on error

# Configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="yogaflow_dev"
DB_USER="yogaflow"
DB_PASSWORD="yogaflow_dev_password"
DB_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "================================================"
echo "YogaFlow Content Population Script"
echo "================================================"
echo ""

# Check if database is accessible
echo "Checking database connection..."
if ! psql "$DB_URL" -c "SELECT 1" > /dev/null 2>&1; then
    echo "❌ ERROR: Cannot connect to database at $DB_URL"
    echo "Please ensure:"
    echo "  1. PostgreSQL is running (docker compose up -d postgres)"
    echo "  2. Database credentials are correct"
    exit 1
fi
echo "✅ Database connection successful"
echo ""

# Check if poses table exists
echo "Checking if poses table exists..."
if ! psql "$DB_URL" -c "SELECT 1 FROM poses LIMIT 1" > /dev/null 2>&1; then
    echo "❌ ERROR: Poses table not found or empty"
    echo "Please seed the database with poses first"
    exit 1
fi

POSE_COUNT=$(psql "$DB_URL" -t -c "SELECT COUNT(*) FROM poses")
echo "✅ Found $POSE_COUNT poses in database"
echo ""

# Check if migration has been applied
echo "Checking if instruction fields exist..."
if ! psql "$DB_URL" -c "SELECT entry_instructions FROM poses LIMIT 1" > /dev/null 2>&1; then
    echo "❌ ERROR: Instruction fields not found"
    echo "Please run: alembic upgrade head"
    exit 1
fi
echo "✅ Instruction fields exist"
echo ""

# Populate pose instructions
echo "================================================"
echo "Step 1: Populating Pose Instructions (4 batches)"
echo "================================================"
echo ""

echo "Processing Batch 1 (Poses 1-20)..."
psql "$DB_URL" -f "$SCRIPT_DIR/populate_pose_instructions_batch1.sql" > /dev/null 2>&1
echo "✅ Batch 1 complete"

echo "Processing Batch 2 (Poses 21-40)..."
psql "$DB_URL" -f "$SCRIPT_DIR/populate_pose_instructions_batch2.sql" > /dev/null 2>&1
echo "✅ Batch 2 complete"

echo "Processing Batch 3 (Poses 41-60)..."
psql "$DB_URL" -f "$SCRIPT_DIR/populate_pose_instructions_batch3.sql" > /dev/null 2>&1
echo "✅ Batch 3 complete"

echo "Processing Batch 4 (Poses 61-80)..."
psql "$DB_URL" -f "$SCRIPT_DIR/populate_pose_instructions_batch4.sql" > /dev/null 2>&1
echo "✅ Batch 4 complete"
echo ""

# Create sequences
echo "================================================"
echo "Step 2: Creating Curated Sequences"
echo "================================================"
echo ""

echo "Creating 15 preset sequences..."
psql "$DB_URL" -f "$SCRIPT_DIR/populate_sequences.sql" > /dev/null 2>&1
echo "✅ Sequences created"
echo ""

# Verification
echo "================================================"
echo "Step 3: Verification"
echo "================================================"
echo ""

POSES_WITH_INSTRUCTIONS=$(psql "$DB_URL" -t -c "SELECT COUNT(*) FROM poses WHERE entry_instructions IS NOT NULL")
echo "Poses with instructions: $POSES_WITH_INSTRUCTIONS / 80"

POSES_WITH_VARIATIONS=$(psql "$DB_URL" -t -c "SELECT COUNT(*) FROM poses WHERE has_side_variation = true")
echo "Poses with side variations: $POSES_WITH_VARIATIONS"

SEQUENCE_COUNT=$(psql "$DB_URL" -t -c "SELECT COUNT(*) FROM sequences WHERE is_preset = true")
echo "Preset sequences created: $SEQUENCE_COUNT / 15"
echo ""

# Detailed verification
echo "Sequence Summary:"
echo "----------------"
psql "$DB_URL" -c "
SELECT
  s.name,
  s.difficulty_level as difficulty,
  s.duration_minutes || ' min' as duration,
  s.focus_area,
  COUNT(sp.pose_id) as poses
FROM sequences s
LEFT JOIN sequence_poses sp ON s.sequence_id = sp.sequence_id
WHERE s.is_preset = true
GROUP BY s.sequence_id, s.name, s.difficulty_level, s.duration_minutes, s.focus_area
ORDER BY s.sequence_id;
"

echo ""
echo "================================================"
echo "Content Population Complete! 🎉"
echo "================================================"
echo ""
echo "Summary:"
echo "  ✅ $POSES_WITH_INSTRUCTIONS poses with complete instructions"
echo "  ✅ $SEQUENCE_COUNT curated sequences created"
echo "  ✅ $POSES_WITH_VARIATIONS poses marked with side variations"
echo ""
echo "Next steps:"
echo "  1. Test pose detail API endpoints"
echo "  2. Test sequence list and detail endpoints"
echo "  3. Verify TTS integration with instructions"
echo "  4. Build sequence player UI"
echo ""
