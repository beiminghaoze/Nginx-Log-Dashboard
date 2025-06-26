# 部署指南

本文档提供了详细的部署说明，包括不同环境下的部署方法和最佳实践。

## 📋 目录

- [环境准备](#环境准备)
- [Docker部署](#docker部署)
- [本地部署](#本地部署)
- [生产环境部署](#生产环境部署)
- [监控和维护](#监控和维护)
- [故障排除](#故障排除)

## 🛠️ 环境准备

### 系统要求

#### 最低配置
- **CPU**: 1核心
- **内存**: 2GB RAM
- **存储**: 1GB可用空间
- **网络**: 100Mbps

#### 推荐配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 10GB可用空间（SSD）
- **网络**: 1Gbps

### 软件依赖

#### Docker部署
- Docker 20.10+
- Docker Compose 2.0+

#### 本地部署
- Python 3.8+
- pip 20.0+
- 虚拟环境工具（推荐）

## 🐳 Docker部署

### 快速部署

1. **下载项目**
```bash
git clone <repository-url>
cd nginx-log-dashboard
```

2. **配置日志目录**
```bash
# 创建日志目录
mkdir -p logs/nas logs/nasqb

# 复制nginx日志文件
cp /var/log/nginx/nas/*.log logs/nas/
cp /var/log/nginx/nasqb/*.log logs/nasqb/
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **验证部署**
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 访问应用
curl http://localhost:5000
```

### 自定义配置

#### 修改端口
编辑 `docker-compose.yml`：
```yaml
ports:
  - "8080:5000"  # 修改为8080端口
```

#### 修改日志目录
编辑 `docker-compose.yml`：
```yaml
volumes:
  - /your/nas/logs:/var/log/nginx/nas:ro
  - /your/nasqb/logs:/var/log/nginx/nasqb:ro
```

#### 添加环境变量
编辑 `docker-compose.yml`：
```yaml
environment:
  - TZ=Asia/Shanghai
  - FLASK_ENV=production
  - FLASK_DEBUG=0
```

### 生产环境Docker部署

#### 1. 构建生产镜像
```bash
# 构建优化镜像
docker build -t nginx-log-dashboard:prod .

# 标记镜像
docker tag nginx-log-dashboard:prod your-registry/nginx-log-dashboard:latest
```

#### 2. 推送到镜像仓库
```bash
# 推送到Docker Hub
docker push your-registry/nginx-log-dashboard:latest

# 或推送到私有仓库
docker push your-private-registry/nginx-log-dashboard:latest
```

#### 3. 生产环境运行
```bash
# 使用生产镜像
docker run -d \
  --name nginx-log-dashboard \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /var/log/nginx/nas:/var/log/nginx/nas:ro \
  -v /var/log/nginx/nasqb:/var/log/nginx/nasqb:ro \
  -e TZ=Asia/Shanghai \
  your-registry/nginx-log-dashboard:latest
```

## 💻 本地部署

### Python环境部署

#### 1. 环境准备
```bash
# 安装Python 3.8+
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 或使用pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

#### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

#### 3. 安装依赖
```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
python -c "import flask; print(flask.__version__)"
```

#### 4. 配置应用
```bash
# 复制配置文件
cp parser.py.example parser.py

# 编辑配置
vim parser.py
```

#### 5. 运行应用
```bash
# 开发模式
python app.py

# 生产模式
export FLASK_ENV=production
export FLASK_DEBUG=0
python app.py
```

### 使用Gunicorn（推荐生产环境）

#### 1. 安装Gunicorn
```bash
pip install gunicorn
```

#### 2. 创建Gunicorn配置
创建 `gunicorn.conf.py`：
```python
# Gunicorn配置文件
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 3. 启动服务
```bash
# 使用配置文件启动
gunicorn -c gunicorn.conf.py app:app

# 或直接启动
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🚀 生产环境部署

### 使用Systemd服务

#### 1. 创建服务文件
创建 `/etc/systemd/system/nginx-log-dashboard.service`：
```ini
[Unit]
Description=Nginx Log Dashboard
After=network.target

[Service]
Type=simple
User=nginx-dashboard
Group=nginx-dashboard
WorkingDirectory=/opt/nginx-log-dashboard
Environment=PATH=/opt/nginx-log-dashboard/venv/bin
ExecStart=/opt/nginx-log-dashboard/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 创建用户
```bash
# 创建用户和组
sudo useradd -r -s /bin/false nginx-dashboard

# 创建应用目录
sudo mkdir -p /opt/nginx-log-dashboard
sudo chown nginx-dashboard:nginx-dashboard /opt/nginx-log-dashboard
```

#### 3. 部署应用
```bash
# 复制应用文件
sudo cp -r . /opt/nginx-log-dashboard/
sudo chown -R nginx-dashboard:nginx-dashboard /opt/nginx-log-dashboard

# 安装依赖
cd /opt/nginx-log-dashboard
sudo -u nginx-dashboard python3 -m venv venv
sudo -u nginx-dashboard venv/bin/pip install -r requirements.txt
sudo -u nginx-dashboard venv/bin/pip install gunicorn
```

#### 4. 启动服务
```bash
# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable nginx-log-dashboard

# 启动服务
sudo systemctl start nginx-log-dashboard

# 检查状态
sudo systemctl status nginx-log-dashboard
```

### 使用Nginx反向代理

#### 1. 安装Nginx
```bash
sudo apt install nginx
```

#### 2. 配置Nginx
创建 `/etc/nginx/sites-available/nginx-log-dashboard`：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件缓存
    location /static/ {
        alias /opt/nginx-log-dashboard/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 3. 启用站点
```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/nginx-log-dashboard /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### SSL/HTTPS配置

#### 使用Let's Encrypt
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 监控和维护

### 日志监控

#### 应用日志
```bash
# 查看应用日志
sudo journalctl -u nginx-log-dashboard -f

# 查看Docker日志
docker logs -f nginx-log-dashboard
```

#### 系统监控
```bash
# 监控系统资源
htop
iotop
nethogs

# 监控磁盘使用
df -h
du -sh /var/log/nginx/
```

### 性能优化

#### 1. 数据库优化（如果使用）
```sql
-- 定期清理旧数据
DELETE FROM log_entries WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

#### 2. 日志轮转
配置 `/etc/logrotate.d/nginx-log-dashboard`：
```
/var/log/nginx-log-dashboard/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 nginx-dashboard nginx-dashboard
    postrotate
        systemctl reload nginx-log-dashboard
    endscript
}
```

#### 3. 内存优化
```bash
# 调整Gunicorn配置
workers = 2  # 减少worker数量
max_requests = 500  # 减少最大请求数
```

### 备份策略

#### 1. 配置文件备份
```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/nginx-log-dashboard"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    app.py parser.py requirements.txt \
    templates/ static/ docker-compose.yml

# 备份日志文件（可选）
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz \
    /var/log/nginx/nas /var/log/nginx/nasqb

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh
```

#### 2. 定时备份
```bash
# 添加到crontab
crontab -e
# 添加以下行
0 2 * * * /path/to/backup.sh
```

## 🔧 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
sudo netstat -tulpn | grep 5000

# 杀死占用进程
sudo kill -9 <PID>

# 或修改端口
export FLASK_RUN_PORT=8080
```

#### 2. 权限问题
```bash
# 检查文件权限
ls -la /var/log/nginx/

# 修改权限
sudo chmod 644 /var/log/nginx/*.log
sudo chown nginx:nginx /var/log/nginx/*.log
```

#### 3. 内存不足
```bash
# 检查内存使用
free -h

# 增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 调试技巧

#### 1. 启用调试模式
```bash
export FLASK_DEBUG=1
export FLASK_ENV=development
```

#### 2. 查看详细日志
```bash
# 增加日志级别
export LOG_LEVEL=DEBUG

# 查看系统日志
sudo journalctl -u nginx-log-dashboard -f --no-pager
```

#### 3. 性能分析
```bash
# 使用cProfile分析性能
python -m cProfile -o profile.stats app.py

# 查看分析结果
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```

### 联系支持

如果遇到无法解决的问题，请：

1. 查看 [故障排除](#故障排除) 部分
2. 收集错误日志和系统信息
3. 在GitHub上创建Issue
4. 提供详细的错误描述和复现步骤

---

**注意**：在生产环境中部署时，请确保：
- 修改默认的用户名和密码
- 启用HTTPS
- 配置防火墙规则
- 定期更新系统和依赖
- 监控系统资源使用情况 