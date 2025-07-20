from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_from_directory
from parser import parse_logs, list_log_prefixes, get_logs_by_prefix
import os

app = Flask(__name__, static_url_path='', static_folder='static')
app.secret_key = '6A737944E841BF3BDEB34F8CF9CD561E559'  # 改成你自己的密钥

USERNAME = 'admin'
PASSWORD = 'password'
REQUIRE_LOGIN = False  # 是否需要登录的开关，True=需要，False=不需要

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
    """返回日志文件中最近 since_hours 小时内的所有内容（按时间过滤）"""
    import re
    from datetime import datetime, timedelta
    LOG_PATTERN = r'([0-9a-fA-F:.]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'
    now = datetime.now()
    threshold = now - timedelta(hours=since_hours)
    result = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(LOG_PATTERN, line)
                if match:
                    ts = match.group(2)
                    # ts 例: 30/Jun/2025:20:36:12 +0800
                    try:
                        dt = datetime.strptime(ts.split(' ')[0], '%d/%b/%Y:%H:%M:%S')
                    except Exception:
                        continue
                    if dt >= threshold:
                        result.append(line.rstrip('\n'))
        return result[-1000:]  # 最多返回1000行，防止太多
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
    app.run(host='0.0.0.0', port=5000)
