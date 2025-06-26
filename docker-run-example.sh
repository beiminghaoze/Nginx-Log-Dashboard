#!/bin/bash

# Docker运行示例 - 将nas和nasqb的日志分别映射到不同目录

# 构建镜像
docker build -t nginx-log-dashboard .

# 运行容器，映射日志目录
docker run -d \
  --name nginx-log-dashboard \
  -p 5000:5000 \
  -v /path/to/your/nas/logs:/var/log/nginx/nas:ro \
  -v /path/to/your/nasqb/logs:/var/log/nginx/nasqb:ro \
  nginx-log-dashboard

echo "容器已启动，访问 http://localhost:5000 查看日志面板"
echo ""
echo "注意：请将 /path/to/your/nas/logs 和 /path/to/your/nasqb/logs 替换为实际的日志目录路径"
echo ""
echo "应用会自动分析每个目录下的最新 *_access.log 文件"
echo ""
echo "例如："
echo "  -v /home/user/nas/logs:/var/log/nginx/nas:ro \\"
echo "  -v /home/user/nasqb/logs:/var/log/nginx/nasqb:ro \\" 