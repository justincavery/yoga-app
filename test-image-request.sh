#!/bin/bash
# Test image request and check nginx logs

SERVER="23.88.127.14"
USER="root"

echo "Testing image request..."
echo "========================"
echo ""

ssh ${USER}@${SERVER} << 'ENDSSH'
set -e

cd /opt/yogaflow

echo "1. Clear nginx access log:"
docker exec yogaflow-nginx sh -c "echo '' > /var/log/nginx/access.log"

echo ""
echo "2. Make test request from backend container:"
docker exec yogaflow-backend curl -I http://nginx/images/poses/mountain-pose.jpg

echo ""
echo "3. Check nginx access log:"
docker exec yogaflow-nginx tail -20 /var/log/nginx/access.log

echo ""
echo "4. Check nginx error log:"
docker exec yogaflow-nginx tail -20 /var/log/nginx/error.log

ENDSSH

echo ""
echo "Test complete!"
