"""
应用启动模块
负责启动Flask后端服务器和Vue前端服务器，并自动打开浏览器
"""

import os
import subprocess
import sys
import time

from server_manager import open_browser, start_vue_server

flask_process = subprocess.Popen(
    ["python", "app.py"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True,
)


for i in range(5):
    time.sleep(1)


start_vue_server()


open_browser()


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    flask_process.kill()

    sys.exit(0)
