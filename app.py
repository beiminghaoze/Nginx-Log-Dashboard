from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
from parser import parse_logs, list_log_prefixes, get_logs_by_prefix
import os
from file_read_backwards import FileReadBackwards
import ssl

app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = '6A737944E841BF3BDEB34F8CF9CD561E559'  # 改成你自己的密钥

# 性能优化配置
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 静态文件缓存1年
app.config['TEMPLATES_AUTO_RELOAD'] = False  # 生产环境关闭模板自动重载

@app.before_request
def before_request():
    """全局请求处理器：强制HTTPS"""
    if SSL_ENABLED:
        # 跳过静态文件，避免影响性能
        if request.path.startswith('/static/') or request.path.startswith('/favicon.ico'):
            return None
            
        # 调试信息
        print(f"Request URL: {request.url}")
        print(f"Request scheme: {request.environ.get('wsgi.url_scheme')}")
        print(f"X-Forwarded-Proto: {request.headers.get('X-Forwarded-Proto')}")
        print(f"X-Forwarded-Ssl: {request.headers.get('X-Forwarded-Ssl')}")
        print(f"X-Forwarded-Scheme: {request.headers.get('X-Forwarded-Scheme')}")
        
        # 检查是否为HTTP请求 - 更直接的检测方法
        is_http = False
        
        # 方法1: 检查代理头
        if (request.headers.get('X-Forwarded-Proto') == 'http' or
            request.headers.get('X-Forwarded-Ssl') == 'off' or
            request.headers.get('X-Forwarded-Scheme') == 'http'):
            is_http = True
            print("HTTP detected via proxy headers")
        
        # 方法2: 检查wsgi环境变量
        elif request.environ.get('wsgi.url_scheme') == 'http':
            is_http = True
            print("HTTP detected via wsgi.url_scheme")
        
        # 方法3: 检查请求URL本身
        elif request.url.startswith('http://'):
            is_http = True
            print("HTTP detected via request URL")
        
        # 方法4: 检查Host头中的协议（如果有的话）
        elif request.headers.get('Host') and 'http://' in request.headers.get('Host', ''):
            is_http = True
            print("HTTP detected via Host header")
        
        if is_http:
            # 构建HTTPS URL
            https_url = request.url.replace('http://', 'https://', 1)
            if https_url == request.url:  # 如果没有替换，说明URL中没有协议
                https_url = f"https://{request.host}{request.full_path}"
            print(f"Redirecting HTTP to HTTPS: {request.url} -> {https_url}")
            return redirect(https_url, code=301)
        else:
            print("No HTTP detection, continuing with request")

USERNAME = 'admin'
PASSWORD = 'password'
REQUIRE_LOGIN = False  # 是否需要登录的开关，True=需要，False=不需要

# SSL证书配置
SSL_CERT_PATH = '/app/certs/cert.pem'
SSL_KEY_PATH = '/app/certs/key.pem'
SSL_ENABLED = os.path.exists(SSL_CERT_PATH) and os.path.exists(SSL_KEY_PATH)

# 调试SSL配置
print(f"SSL Certificate exists: {os.path.exists(SSL_CERT_PATH)}")
print(f"SSL Key exists: {os.path.exists(SSL_KEY_PATH)}")
print(f"SSL Enabled: {SSL_ENABLED}")
if os.path.exists(SSL_CERT_PATH):
    print(f"SSL Certificate size: {os.path.getsize(SSL_CERT_PATH)} bytes")
if os.path.exists(SSL_KEY_PATH):
    print(f"SSL Key size: {os.path.getsize(SSL_KEY_PATH)} bytes")



@app.route('/login', methods=['GET', 'POST'])
def login():
    if not REQUIRE_LOGIN:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['user'] = USERNAME
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if not REQUIRE_LOGIN:
        return redirect(url_for('index'))
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if REQUIRE_LOGIN and 'user' not in session:
        return redirect(url_for('login'))
    prefixes = list_log_prefixes()
    return render_template('index.html', prefixes=prefixes)



@app.route('/api/stats')
def stats():
    if REQUIRE_LOGIN and 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    prefix = request.args.get('file')
    if not prefix:
        return jsonify({'error': 'Missing file parameter'}), 400
    files = get_logs_by_prefix(prefix)
    result = parse_logs(files)
    return jsonify(result)

def tail_log_file(filepath, lines=20):
    """返回日志文件最后 N 行内容"""
    try:
        with open(filepath, 'rb') as f:
            f.seek(0, os.SEEK_END)
            end = f.tell()
            buffer = bytearray()
            pointer = end
            count = 0
            while pointer > 0 and count < lines:
                pointer -= 1
                f.seek(pointer)
                byte = f.read(1)
                if byte == b'\n' and buffer:
                    count += 1
                    if count == lines:
                        break
                buffer.extend(byte)
            buffer.reverse()
            content = buffer.decode(errors='replace')
            return content.splitlines()[-lines:]
    except Exception as e:
        return [f'Error reading file: {e}']

def tail_log_file_since(filepath, since_hours=24):
    """返回日志文件中最近 since_hours 小时内的所有内容（按时间过滤，倒序读取）"""
    import re
    from datetime import datetime, timedelta
    LOG_PATTERN = r'([^ ]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'
    now = datetime.now().astimezone()
    threshold = now - timedelta(hours=since_hours)
    result = []
    try:
        with FileReadBackwards(filepath, encoding='utf-8') as frb:
            for line in frb:
                match = re.match(LOG_PATTERN, line)
                if not match:
                    continue
                ts = match.group(2)
                try:
                    dt = datetime.strptime(ts, '%d/%b/%Y:%H:%M:%S %z')
                except Exception:
                    continue
                if dt >= threshold:
                    result.append(line.rstrip('\n'))
                else:
                    break  # 前面的都更早，无需再查
        return result[::-1][-10000:]  # 结果倒序，需反转
    except Exception as e:
        return [f'Error reading file: {e}']

@app.route('/api/tail')
def api_tail():
    if REQUIRE_LOGIN and 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    prefix = request.args.get('file')
    lines = int(request.args.get('lines', 10))
    since_hours = request.args.get('since_hours')
    from parser import get_logs_by_prefix
    files = get_logs_by_prefix(prefix)
    if not files:
        return jsonify({'lines': []})
    filepath = files[0]
    if since_hours:
        log_lines = tail_log_file_since(filepath, int(since_hours))
    else:
        log_lines = tail_log_file(filepath, lines)
    return jsonify({'lines': log_lines})

if __name__ == '__main__':
    if SSL_ENABLED:
        print(f"Starting with HTTPS on port 5000")
        print(f"SSL Certificate: {SSL_CERT_PATH}")
        print(f"SSL Key: {SSL_KEY_PATH}")
        try:
            # 验证证书文件并优化SSL配置
            import ssl
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(SSL_CERT_PATH, SSL_KEY_PATH)
            
            # 优化SSL性能配置
            context.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384')
            context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            
            print("SSL certificate validation successful")
            print("SSL performance optimizations applied")
            
            # 使用优化的SSL上下文启动
            app.run(host='0.0.0.0', port=5000, ssl_context=context, threaded=True)
        except Exception as e:
            print(f"SSL certificate validation failed: {e}")
            print("Falling back to HTTP mode")
            app.run(host='0.0.0.0', port=5000, threaded=True)
    else:
        print("Starting with HTTP on port 5000 (SSL certificates not found)")
        app.run(host='0.0.0.0', port=5000, threaded=True)
