#!/bin/bash
# Apply database migrations and populate sequences
# Run this on the Hetzner server in /opt/yogaflow directory

set -e

echo "=== Applying Database Schema Changes ==="

# Add pose instruction fields (replaces alembic migration)
docker exec yogaflow-postgres psql -U yogaflow -d yogaflow_prod << 'EOF'
-- Add pose instruction fields
ALTER TABLE poses ADD COLUMN IF NOT EXISTS entry_instructions TEXT[];
ALTER TABLE poses ADD COLUMN IF NOT EXISTS exit_instructions TEXT[];
ALTER TABLE poses ADD COLUMN IF NOT EXISTS holding_cues TEXT;
ALTER TABLE poses ADD COLUMN IF NOT EXISTS breathing_pattern TEXT;
ALTER TABLE poses ADD COLUMN IF NOT EXISTS has_side_variation BOOLEAN DEFAULT false;

SELECT 'Schema updated successfully' as status;
EOF

echo ""
echo "=== Populating Pose Instructions ==="

# Populate pose instructions (4 batches)
docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow_prod < backend/scripts/populate_pose_instructions_batch1.sql
echo "✓ Batch 1 complete"

docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow_prod < backend/scripts/populate_pose_instructions_batch2.sql
echo "✓ Batch 2 complete"

docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow_prod < backend/scripts/populate_pose_instructions_batch3.sql
echo "✓ Batch 3 complete"

docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow_prod < backend/scripts/populate_pose_instructions_batch4.sql
echo "✓ Batch 4 complete"

echo ""
echo "=== Populating Sequences ==="

# Populate sequences
docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow_prod < backend/scripts/populate_sequences.sql

echo ""
echo "=== Verification ==="

# Check sequence count
SEQUENCE_COUNT=$(docker exec yogaflow-postgres psql -U yogaflow -d yogaflow_prod -t -c "SELECT COUNT(*) FROM sequences WHERE is_preset = true;" | xargs)

echo "✅ Found $SEQUENCE_COUNT preset sequences in database"

if [[ "$SEQUENCE_COUNT" -eq 15 ]]; then
    echo "✅ All 15 sequences successfully populated!"
else
    echo "⚠️  Expected 15 sequences but found $SEQUENCE_COUNT"
fi

echo ""
echo "Test the API:"
echo "curl https://app.laurayoga.co.uk/api/v1/sequences | jq '.total'"
