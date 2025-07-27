# Nginx Log Dashboard

一个功能强大的Nginx日志分析Web仪表板，支持多日志源、实时监控和统计分析。

## 📋 目录

- [界面](#界面)
- [功能特性](#功能特性)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细安装指南](#详细安装指南)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [API接口](#api接口)
- [故障排除](#故障排除)
- [开发指南](#开发指南)
- [更新日志](#更新日志)
- [许可证](#许可证)
- [支持](#支持)
- [致谢](#致谢)

## 📟️ 界面
![界面](https://s21.ax1x.com/2025/06/26/pVmipH1.png)

## ✨ 功能特性

- 🔍 **多日志源支持** - 同时监控多个nginx服务器的日志
- 📊 **实时统计分析** - IP地址、URL、状态码的实时统计图表
- 📝 **实时日志查看** - 实时显示最新的日志条目
- 🎨 **响应式界面** - 支持桌面和移动设备访问
- 🔐 **用户认证** - 简单的登录保护
- 🔄 **自动刷新** - 可配置的自动数据刷新
- 📱 **移动友好** - 优化的移动端体验
- 🐳 **Docker支持** - 一键部署和运行

## 🖥️ 系统要求

### 最低要求
- Python 3.8+
- 1GB RAM
- 1GB 可用磁盘空间

### 推荐配置
- Python 3.11+
- 2GB RAM
- 5GB 可用磁盘空间
- Docker 20.10+

## 🚀 快速开始

### 使用Docker Compose（推荐）

1. **克隆项目**
```bash
git clone https://github.com/beiminghaoze/Nginx-Log-Dashboard
cd nginx-log-dashboard
```

2. **准备日志目录**
```bash
在linux上nginx的默认日志路径为 /var/log/nginx
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问应用**
打开浏览器访问 https://localhost:5000

默认登录信息：
- 用户名：`admin`
- 密码：`password`

**HTTPS支持：**
如需启用HTTPS，请将SSL证书文件放置在 `./certs/` 目录下：
- `cert.pem` - SSL证书文件
- `key.pem` - SSL私钥文件

**注意：** Flask开发服务器在启用HTTPS时只监听HTTPS端口，不支持同端口HTTP到HTTPS跳转。

## 📖 详细安装指南

### 方法一：Docker部署（推荐）

#### 1. 构建Docker镜像

```bash
# 构建镜像
sudo docker build -t nginx-log-dashboard .

# 查看构建的镜像
sudo docker images | grep nginx-log-dashboard
```

#### 2. 运行容器

**基本运行命令：**
```bash
sudo docker run -d \
  --name nginx-log-dashboard \
  --restart=always \
  -p 5000:5000 \
  -v /var/log/nginx/nas:/var/log/nginx/nas:ro \
  -v /var/log/nginx/nasqb:/var/log/nginx/nasqb:ro \
  -v ./certs:/app/certs:ro \
  nginx-log-dashboard
```

**HTTPS运行命令：**
```bash
sudo docker run -d \
  --name nginx-log-dashboard \
  --restart=always \
  -p 5000:5000 \
  -v /var/log/nginx/nas:/var/log/nginx/nas:ro \
  -v /var/log/nginx/nasqb:/var/log/nginx/nasqb:ro \
  -v ./certs:/app/certs:ro \
  nginx-log-dashboard
```

**使用Docker Compose：**
```bash
# 编辑docker-compose.yml中的路径
vim docker-compose.yml

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 3. 容器管理

```bash
# 停止容器
docker stop nginx-log-dashboard

# 启动容器
docker start nginx-log-dashboard

# 重启容器
docker restart nginx-log-dashboard

# 删除容器
docker rm -f nginx-log-dashboard

# 查看容器日志
docker logs nginx-log-dashboard

# 进入容器
docker exec -it nginx-log-dashboard bash
```

### 方法二：本地Python部署

#### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置日志目录

编辑 `parser.py` 文件，修改日志目录配置：

```python
# 本地开发环境配置(实例，以实际为准。)
LOG_DIRS = {
    'nginx': './log/nginx-log/',
    'test': './log/nginx-log/test/',
}
```

#### 3. 运行应用

```bash
# 直接运行
python app.py

# 或者使用Flask开发服务器
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## ⚙️ 配置说明

### 日志目录配置

应用支持多个日志源的配置，在 `parser.py` 中定义：

```python
LOG_DIRS = {
    'nginx': '/var/log/nginx/nas',     
    'nginxtext': '/var/log/nginx/text'   
}
```

### 日志文件格式

应用支持标准的Nginx访问日志格式：

```
IP地址 - - [时间戳] "请求方法 路径 HTTP版本" 状态码 响应大小 "引用页" "用户代理"
```

示例：
```
192.168.1.100 - - [25/Dec/2023:10:30:45 +0800] "GET /api/data HTTP/1.1" 200 1234 "https://example.com" "Mozilla/5.0..."
```

### 支持的日志文件命名

- `*_access.log` - 主要访问日志文件（应用会分析此文件）
- `*_access.log.1` - 轮转的访问日志文件
- `*_error.log` - 错误日志文件
- `*_error.log.1` - 轮转的错误日志文件

**注意**：应用只会分析最新的 `*_access.log` 文件，不会分析历史轮转文件。

### 安全配置

#### 修改默认登录信息

编辑 `app.py` 文件：

```python
USERNAME = 'your_username'  # 修改用户名
PASSWORD = 'your_password'  # 修改密码
app.secret_key = 'your_secret_key'  # 修改密钥
```

#### 生产环境安全建议

1. **使用强密码**
2. **启用HTTPS**
3. **配置防火墙**
4. **定期更新依赖**
5. **监控访问日志**

## 📱 使用方法

### Web界面操作

1. **登录系统**
   - 访问 http://localhost:5000
   - 输入用户名和密码

2. **选择日志源**
   - 在左侧边栏选择要分析的日志文件
   - 支持多个日志源切换

3. **查看统计图表**
   - **Top IPs**：显示访问量最高的IP地址
   - **Top URLs**：显示访问量最高的URL路径
   - 点击图表元素可复制详细信息

4. **实时日志查看**
   - 底部显示最新的日志条目
   - 自动每5秒刷新一次

5. **手动刷新**
   - 点击"刷新"按钮手动更新数据
   - 可开启/关闭自动刷新功能

### 快捷键

- `F5` - 刷新页面
- `Ctrl+R` - 手动刷新数据
- `Ctrl+Shift+R` - 强制刷新（清除缓存）

## 🔌 API接口

### 获取统计数据

**请求：**
```
GET /api/stats?file={prefix}
```

**参数：**
- `file` (必需): 日志文件前缀，如 `nas` 或 `nasqb`

**响应：**
```json
{
  "ip": [
    ["192.168.1.100", 150],
    ["10.0.0.1", 120]
  ],
  "url": [
    ["/api/data", 200],
    ["/static/css", 180]
  ],
  "status": {
    "200": 1500,
    "404": 50,
    "500": 10
  }
}
```

### 获取最新日志

**请求：**
```
GET /api/tail?file={prefix}&lines={number}
```

**参数：**
- `file` (必需): 日志文件前缀
- `lines` (可选): 返回的日志行数，默认10行

**响应：**
```json
{
  "lines": [
    "192.168.1.100 - - [25/Dec/2023:10:30:45 +0800] \"GET /api/data HTTP/1.1\" 200 1234",
    "10.0.0.1 - - [25/Dec/2023:10:30:44 +0800] \"POST /api/update HTTP/1.1\" 201 567"
  ]
}
```

## 🔧 故障排除

### 常见问题

#### 1. 容器启动失败

**问题**：容器启动后立即退出

**解决方案**：
```bash
# 查看容器日志
docker logs nginx-log-dashboard

# 检查端口是否被占用
netstat -tulpn | grep 5000

# 检查日志目录权限
ls -la /path/to/your/logs/
```

#### 2. 日志文件无法读取

**问题**：Web界面显示"没有找到日志文件"

**解决方案**：
```bash
# 检查日志目录映射
docker exec nginx-log-dashboard ls -la /var/log/nginx/

# 检查文件权限
docker exec nginx-log-dashboard ls -la /var/log/nginx/nas/
docker exec nginx-log-dashboard ls -la /var/log/nginx/nasqb/

# 验证文件格式
docker exec nginx-log-dashboard head -5 /var/log/nginx/nas/nas_access.log
```

#### 3. 性能问题

**问题**：页面加载缓慢或响应慢

**解决方案**：
- 检查日志文件大小，过大的文件可能影响性能
- 增加容器内存限制
- 考虑使用SSD存储日志文件

#### 4. 认证问题

**问题**：无法登录或登录后立即退出

**解决方案**：
- 检查浏览器Cookie设置
- 清除浏览器缓存
- 确认用户名密码正确

### 调试模式

启用调试模式获取更多信息：

```bash
# 设置环境变量
export FLASK_DEBUG=1

# 重新启动容器
docker-compose restart
```

### 日志分析

查看应用日志：

```bash
# 查看容器日志
docker logs -f nginx-log-dashboard

# 查看系统日志
journalctl -u docker.service -f

# 查看nginx日志
tail -f /var/log/nginx/access.log
```

## 🛠️ 开发指南

### 项目结构

```
nginx-log-dashboard/
├── app.py                 # Flask应用主文件
├── parser.py              # 日志解析器
├── test_config.py         # 配置测试脚本
├── Dockerfile             # Docker镜像配置
├── docker-compose.yml     # Docker Compose配置
├── docker-run-example.sh  # Docker运行示例
├── requirements.txt       # Python依赖
├── start.sh              # 启动脚本
├── README.md             # 项目文档
├── templates/            # HTML模板
│   ├── index.html        # 主页面
│   └── login.html        # 登录页面
├── static/               # 静态文件
│   └── favicon.ico       # 网站图标
└── nginx-log/                 # 日志目录（本地开发）

```

### 开发环境设置

1. **克隆项目**
```bash
git clone <repository-url>
cd nginx-log-dashboard
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装开发依赖**
```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

4. **运行测试**
```bash
# 运行配置测试
python test_config.py

# 运行单元测试（如果有）
pytest tests/
```

### 代码规范

- 使用Python 3.8+语法
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 使用类型提示（可选）

### 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📝 更新日志
### v1.0.2 (2025-7-27)
- 🔍 添加HTTPS支持 详情请查看 HTTPS_PERFORMANCE.md

### v1.0.1 (2025-7-21)
- 🔍 添加实时日志查看功能,目前返回至15000条或近24小时
- 🚀 从此版本起取消登录页面
- 📊 优化图表显示效果

### v1.0.0 (2025-6-26)
- 🎉 初始版本发布
- ✨ 支持多日志源配置
- 🚀 移除天数限制，只分析最新access.log文件
- 🎨 简化Web界面，移除天数选择控件
- 📚 完善文档和示例
- 🐳 优化Docker配置
- 🔍 添加实时日志查看功能
- 📊 优化图表显示效果
- 🔐 添加用户认证功能
- 📱 改进移动端体验
- 📈 基础统计分析功能
- 🐳 Docker支持
- 📋 基本Web界面

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 支持

如果你遇到问题或有建议，请：

1. 查看 [故障排除](#故障排除) 部分
2. 搜索现有的 [Issues](../../issues)
3. 创建新的 Issue

## 🙏 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Bootstrap](https://getbootstrap.com/) - UI框架
- [ECharts](https://echarts.apache.org/) - 图表库
- [Docker](https://www.docker.com/) - 容器化平台

- 感谢 [chatgpt](https://chat.openai.com/)、[deepseek](https://chat.deepseek.com/)、[cursor](https://www.cursor.com/) 对本项目的大力支持！

---

**注意**：请确保在生产环境中修改默认的用户名、密码和密钥，并启用适当的安全措施。 