#!/usr/bin/env python3
"""
启动AHA系统的两个服务：
- Flask Web UI (端口5001)
- Streamlit 分析工具 (端口5002)
"""

import subprocess
import sys
import os
import time
import threading
import signal

def start_flask_app():
    """启动Flask应用 (端口5001)"""
    print("🚀 启动Flask Web UI (端口5001)...")
    try:
        os.chdir('/mnt/f/Project/AHA_LLM-main/aha_llm/aha_UI')
        subprocess.run([sys.executable, 'run_production.py'])
    except Exception as e:
        print(f"❌ Flask应用启动失败: {e}")

def start_streamlit_app():
    """启动Streamlit应用 (端口5002)"""
    print("🚀 启动Streamlit分析工具 (端口5002)...")
    try:
        os.chdir('/mnt/f/Project/AHA_LLM-main/aha_llm')
        subprocess.run([
            sys.executable, 
            '-m', 
            'streamlit', 
            'run', 
            'aha_analyzer.py',
            '--server.port=5002',
            '--server.address=0.0.0.0'
        ])
    except Exception as e:
        print(f"❌ Streamlit应用启动失败: {e}")

def main():
    print("=" * 60)
    print("🏥 AHA系统双服务启动")
    print("=" * 60)
    print("📱 Web UI: http://0.0.0.0:5001")
    print("🔬 分析工具: http://0.0.0.0:5002")
    print("=" * 60)
    print("按 Ctrl+C 停止所有服务")
    print()

    # 创建线程启动两个服务
    flask_thread = threading.Thread(target=start_flask_app, daemon=True)
    streamlit_thread = threading.Thread(target=start_streamlit_app, daemon=True)
    
    try:
        # 启动Flask应用
        flask_thread.start()
        time.sleep(2)  # 等待Flask启动
        
        # 启动Streamlit应用
        streamlit_thread.start()
        time.sleep(2)  # 等待Streamlit启动
        
        print("✅ 两个服务都已启动")
        print("🌐 Web UI: http://localhost:5001")
        print("🔬 分析工具: http://localhost:5002")
        print("\n按 Ctrl+C 停止服务...")
        
        # 保持主线程运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
