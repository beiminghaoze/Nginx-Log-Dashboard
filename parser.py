import re
from collections import Counter
from datetime import datetime, timedelta
from glob import glob
import os

# 定义日志目录映射
LOG_DIRS = {
    'nas': '/var/log/nginx/nas',
    'nasqb': '/var/log/nginx/nasqb'
}
# # 本地开发环境使用
# LOG_DIRS = {
#     'nas': 'C:/Users/beiming/PycharmProjects/nginx-log-dashboard/nginx/nas',
#     # 'nasqb': 'C:/Users/beiming/PycharmProjects/nginx-log-dashboard/nginx'
# }

# 定义日志格式的正则表达式，支持IPv4和IPv6
LOG_PATTERN = r'([0-9a-fA-F:.]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'

def parse_file(filepath):
    """解析单个日志文件"""
    ip_counts = Counter()
    url_counts = Counter()
    status_counts = Counter()
    
    try:
        print(f"Reading file: {filepath}")
        file_size = os.path.getsize(filepath)
        print(f"File size: {file_size} bytes")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            line_count = 0
            match_count = 0
            for line in f:
                line_count += 1
                match = re.match(LOG_PATTERN, line)
                if match:
                    match_count += 1
                    ip, timestamp, request, status, size, referer, user_agent = match.groups()
                    parts = request.split(' ', 2)
                    if len(parts) >= 2:
                        method, url = parts[0], parts[1]
                        if ':' in ip:
                            ip = ip.lower()
                        ip_counts[ip] += 1
                        url_counts[url] += 1
                        status_counts[status] += 1
            print(f"Processed {line_count} lines, matched {match_count} lines")
    except Exception as e:
        print(f"Error reading file {filepath}: {str(e)}")
    
    return ip_counts, url_counts, status_counts

def parse_logs(filepaths):
    """解析多个日志文件并返回统计结果"""
    total_ip_counts = Counter()
    total_url_counts = Counter()
    total_status_counts = Counter()
    
    for filepath in filepaths:
        ip_counts, url_counts, status_counts = parse_file(filepath)
        total_ip_counts.update(ip_counts)
        total_url_counts.update(url_counts)
        total_status_counts.update(status_counts)
    
    return {
        'ip': total_ip_counts.most_common(10),
        'url': total_url_counts.most_common(10),
        'status': dict(total_status_counts)
    }

def list_log_prefixes():
    """列出日志文件的前缀"""
    prefixes = set()
    for prefix, log_dir in LOG_DIRS.items():
        if os.path.exists(log_dir):
            files = glob(os.path.join(log_dir, '*_access.log*'))
            for file in files:
                # 从文件名中提取前缀（例如：nasqb_access.log -> nasqb）
                base = os.path.basename(file)
                if '_access.log' in base:
                    file_prefix = base.split('_access.log')[0]
                    prefixes.add(file_prefix)
            print(f"Found prefixes in {log_dir}:", sorted(list(prefixes)))  # 添加调试信息
    return sorted(list(prefixes))

def get_logs_by_prefix(prefix, days=None):
    """根据前缀获取日志文件"""
    all_files = []
    
    # 遍历所有日志目录
    for log_dir in LOG_DIRS.values():
        if os.path.exists(log_dir):
            files = glob(os.path.join(log_dir, '*_access.log*'))
            all_files.extend(files)
    
    print(f"All files found: {all_files}")
    
    # 筛选出匹配前缀的文件
    files = [f for f in all_files if os.path.basename(f).startswith(prefix + '_access.log')]
    print(f"Matched files for prefix {prefix}: {files}")
    
    if not files:
        print(f"No files found for prefix: {prefix}")
        return []
    
    # 按修改时间排序，返回最新的文件
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # 只返回最新的access.log文件（不包含轮转文件）
    latest_files = [f for f in files if os.path.basename(f) == f'{prefix}_access.log']
    
    if latest_files:
        print(f"Latest file for prefix {prefix}: {latest_files[0]}")
        return [latest_files[0]]
    else:
        print(f"No latest access.log file found for prefix: {prefix}")
        return []
