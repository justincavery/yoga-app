# Deploy Sequences to Production

Run these commands on your Hetzner server to populate the sequences.

## Step 1: Navigate to the app directory

```bash
cd /opt/yogaflow
```

## Step 2: Apply database schema changes

```bash
docker exec yogaflow-postgres psql -U yogaflow -d yogaflow << 'EOF'
ALTER TABLE poses ADD COLUMN IF NOT EXISTS entry_instructions TEXT[];
ALTER TABLE poses ADD COLUMN IF NOT EXISTS exit_instructions TEXT[];
ALTER TABLE poses ADD COLUMN IF NOT EXISTS holding_cues TEXT;
ALTER TABLE poses ADD COLUMN IF NOT EXISTS breathing_pattern TEXT;
ALTER TABLE poses ADD COLUMN IF NOT EXISTS has_side_variation BOOLEAN DEFAULT false;
EOF
```

## Step 3: Populate pose instructions (batch 1)

```bash
docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_pose_instructions_batch1.sql
```

## Step 4: Populate pose instructions (batch 2)

```bash
docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_pose_instructions_batch2.sql
```

## Step 5: Populate pose instructions (batch 3)

```bash
docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_pose_instructions_batch3.sql
```

## Step 6: Populate pose instructions (batch 4)

```bash
docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_pose_instructions_batch4.sql
```

## Step 7: Populate sequences

```bash
docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_sequences.sql
```

## Step 8: Verify sequences were created

```bash
docker exec yogaflow-postgres psql -U yogaflow -d yogaflow -c "SELECT COUNT(*) FROM sequences WHERE is_preset = true;"
```

Expected output: `15`

## Step 9: Test the API

```bash
curl https://app.laurayoga.co.uk/api/v1/sequences | jq '.total'
```

Expected output: `15`

---

## All commands in one block (copy this entire block):

```bash
cd /opt/yogaflow

docker exec yogaflow-postgres psql -U yogaflow -d yogaflow << 'EOF'
ALTER TABLE poses ADD COLUMN IF NOT EXISTS entry_instructions TEXT[];
ALTER TABLE poses ADD COLUMN IF NOT EXISTS exit_instructions TEXT[];
ALTER TABLE poses ADD COLUMN IF NOT EXISTS holding_cues TEXT;
ALTER TABLE poses ADD COLUMN IF NOT EXISTS breathing_pattern TEXT;
ALTER TABLE poses ADD COLUMN IF NOT EXISTS has_side_variation BOOLEAN DEFAULT false;
EOF

docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_pose_instructions_batch1.sql

docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_pose_instructions_batch2.sql

docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_pose_instructions_batch3.sql

docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_pose_instructions_batch4.sql

docker exec -i yogaflow-postgres psql -U yogaflow -d yogaflow < backend/scripts/populate_sequences.sql

docker exec yogaflow-postgres psql -U yogaflow -d yogaflow -c "SELECT COUNT(*) FROM sequences WHERE is_preset = true;"

curl https://app.laurayoga.co.uk/api/v1/sequences | jq '.total'
```
