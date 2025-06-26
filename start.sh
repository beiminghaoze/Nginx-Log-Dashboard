#!/bin/bash
echo "Checking mounted nginx logs directories..."

# 检查nas日志目录
if [ -d "/var/log/nginx/nas" ]; then
    echo "✓ NAS logs directory found:"
    ls -la /var/log/nginx/nas
else
    echo "✗ NAS logs directory not found: /var/log/nginx/nas"
fi

# 检查nasqb日志目录
if [ -d "/var/log/nginx/nasqb" ]; then
    echo "✓ NASQB logs directory found:"
    ls -la /var/log/nginx/nasqb
else
    echo "✗ NASQB logs directory not found: /var/log/nginx/nasqb"
fi

echo "Current working directory:"
pwd
echo "Starting application..."
python app.py 