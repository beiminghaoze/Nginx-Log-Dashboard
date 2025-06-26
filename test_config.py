#!/usr/bin/env python3
"""
测试脚本 - 验证日志目录配置
"""

import os
from parser import LOG_DIRS, list_log_prefixes, get_logs_by_prefix

def test_log_directories():
    """测试日志目录配置"""
    print("=== 日志目录配置测试 ===\n")
    
    print("配置的日志目录:")
    for prefix, log_dir in LOG_DIRS.items():
        print(f"  {prefix}: {log_dir}")
        if os.path.exists(log_dir):
            print(f"    ✓ 目录存在")
            files = os.listdir(log_dir)
            print(f"    文件列表: {files}")
        else:
            print(f"    ✗ 目录不存在")
    print()
    
    print("=== 前缀列表测试 ===")
    prefixes = list_log_prefixes()
    print(f"发现的前缀: {prefixes}")
    print()
    
    print("=== 文件获取测试 ===")
    for prefix in prefixes:
        files = get_logs_by_prefix(prefix)
        print(f"{prefix}: {files}")
    print()

if __name__ == "__main__":
    test_log_directories() 