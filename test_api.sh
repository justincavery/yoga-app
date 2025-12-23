#!/bin/bash
# Test API endpoints

echo "=== Testing Poses Endpoint ==="
curl -s 'http://localhost:8000/api/v1/poses?limit=1&offset=0' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Total poses: {data.get('total', 0)}\"); print(f\"Returned: {len(data.get('poses', []))}\"); pose=data.get('poses', [{}])[0]; print(f\"Pose: {pose.get('name_english')}\"); print(f\"Has entry instructions: {bool(pose.get('entry_instructions'))}\"); print(f\"Has exit instructions: {bool(pose.get('exit_instructions'))}\"); print(f\"Has holding cues: {bool(pose.get('holding_cues'))}\");"

echo ""
echo "=== Testing Sequences Endpoint ==="
curl -s 'http://localhost:8000/api/v1/sequences' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Total sequences: {len(data)}\"); seq=data[0] if data else {}; print(f\"First sequence: {seq.get('name')}\"); print(f\"Difficulty: {seq.get('difficulty_level')}\"); print(f\"Duration: {seq.get('duration_minutes')} min\");"

echo ""
echo "=== Testing Related Poses Endpoint ==="
curl -s 'http://localhost:8000/api/v1/poses/8/related' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Similar poses: {len(data.get('similar', []))}\"); print(f\"Progression poses: {len(data.get('progressions', []))}\");"

echo ""
echo "=== All Tests Complete ==="
