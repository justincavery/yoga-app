#!/bin/bash
# Debug image serving on production server

SERVER="23.88.127.14"
USER="root"

echo "Debugging image serving on production..."
echo "=========================================="
echo ""

ssh ${USER}@${SERVER} << 'ENDSSH'
set -e

cd /opt/yogaflow

echo "1. Check if content/images directory exists:"
ls -la content/images/ | head -5

echo ""
echo "2. Check if content/images/poses exists:"
ls -la content/images/poses/ | head -10

echo ""
echo "3. Check nginx container volumes:"
docker inspect yogaflow-nginx --format='{{range .Mounts}}{{.Source}} -> {{.Destination}} ({{.Mode}}){{println}}{{end}}' | grep images

echo ""
echo "4. Check if files are accessible inside nginx container:"
docker exec yogaflow-nginx ls -la /var/www/images/poses/ | head -10

echo ""
echo "5. Test nginx config:"
docker exec yogaflow-nginx nginx -t

echo ""
echo "6. Check nginx access to image file:"
docker exec yogaflow-nginx cat /var/www/images/poses/mountain-pose.jpg > /dev/null && echo "✓ File accessible" || echo "✗ File not accessible"

echo ""
echo "7. Test local curl to nginx:"
docker exec yogaflow-nginx wget -O- http://localhost/images/poses/mountain-pose.jpg 2>&1 | head -5

ENDSSH

echo ""
echo "Debug complete!"
