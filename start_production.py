"""
生产环境启动脚本

专门用于生产环境的启动脚本，使用标准端口配置：
- 后端Flask服务器：5000端口
- 前端Vue服务器：8080端口
- 禁用调试模式
"""

import os
import subprocess
import sys
import time

from server_manager import open_browser, start_vue_server


def start_production():
    """启动生产环境服务"""
    print("正在启动LeafAuto生产环境...")
    
    # 启动后端Flask服务器（生产环境端口5000，禁用调试）
    flask_process = subprocess.Popen(
        ["python", "app.py", "--port", "5000", "--host", "0.0.0.0"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    
    print("后端服务器启动中...")
    
    # 等待后端服务器启动
    for i in range(5):
        time.sleep(1)
        print(f"等待后端启动... {i+1}/5")
    
    # 启动前端Vue服务器（生产环境端口8080）
    print("启动前端服务器...")
    vue_process = start_vue_server(8080)
    
    # 等待前端服务器启动
    time.sleep(5)
    print("前端服务器启动完成")
    
    # 自动打开浏览器
    print("正在打开浏览器...")
    open_browser(8080)
    
    print("\n✅ LeafAuto生产环境启动完成!")
    print("后端API: http://localhost:5000")
    print("前端应用: http://localhost:8080")
    print("按 Ctrl+C 停止服务")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        flask_process.kill()
        if vue_process:
            vue_process.kill()
        print("服务已停止")
        sys.exit(0)


if __name__ == "__main__":
    start_production()