from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
from parser import parse_logs, list_log_prefixes, get_logs_by_prefix
import os
from file_read_backwards import FileReadBackwards
import ssl

app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = '6A737944E841BF3BDEB34F8CF9CD561E559'  # 改成你自己的密钥

USERNAME = 'admin'
PASSWORD = 'password'
REQUIRE_LOGIN = False  # 是否需要登录的开关，True=需要，False=不需要

# SSL证书配置
SSL_CERT_PATH = '/app/certs/cert.pem'
SSL_KEY_PATH = '/app/certs/key.pem'
SSL_ENABLED = os.path.exists(SSL_CERT_PATH) and os.path.exists(SSL_KEY_PATH)

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

@app.route('/http_redirect')
def http_redirect():
    """HTTP到HTTPS的自动跳转"""
    if SSL_ENABLED and request.headers.get('X-Forwarded-Proto') == 'http':
        return redirect(request.url.replace('http://', 'https://', 1), code=301)
    return redirect(url_for('index'))

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
        app.run(host='0.0.0.0', port=5000, ssl_context=(SSL_CERT_PATH, SSL_KEY_PATH))
    else:
        print("Starting with HTTP on port 5000 (SSL certificates not found)")
        app.run(host='0.0.0.0', port=5000)
