"""
应用启动模块
负责启动Flask后端服务器和Vue前端服务器，并自动打开浏览器
"""

import os
import subprocess
import sys
import time

from server_manager import open_browser, start_vue_server

# 启动后端Flask服务器（生产环境端口5000）
flask_process = subprocess.Popen(
    ["python", "app.py", "--port", "5000"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True,
)

# 等待后端服务器启动
for i in range(5):
    time.sleep(1)

# 启动前端Vue服务器（生产环境端口8080）
vue_process = start_vue_server(8080)

# 等待前端服务器启动
time.sleep(3)

# 延迟3秒后自动打开浏览器
time.sleep(3)
open_browser(8080)


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    flask_process.kill()

    sys.exit(0)
