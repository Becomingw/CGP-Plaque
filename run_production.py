#!/usr/bin/env python3
"""
生产环境运行脚本
使用 Waitress WSGI 服务器，支持多线程并发
"""

import os
import sys

try:
    from waitress import serve
except ImportError:
    print("错误: 未安装 waitress")
    print("请运行: pip install waitress")
    sys.exit(1)

from app import app, USER_DATA_PATH

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(USER_DATA_PATH, exist_ok=True)

    print("=" * 60)
    print("🏥 AHA UI 生产环境启动")
    print("=" * 60)
    print(f"📂 用户数据目录: {USER_DATA_PATH}")
    print(f"🌐 服务地址: http://0.0.0.0:5001")
    print(f"⚙️  并发线程数: 4")
    print("=" * 60)
    print("\n按 Ctrl+C 停止服务器\n")

    # 使用 Waitress 服务器
    # threads=4: 支持4个并发请求
    # channel_timeout=60: AI推理可能需要较长时间
    serve(
        app,
        host='0.0.0.0',
        port=5001,
        threads=4,
        channel_timeout=60,
        cleanup_interval=30,
        _quiet=False
    )
