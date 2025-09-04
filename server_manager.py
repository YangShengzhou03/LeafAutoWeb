import subprocess
import time
import socket
import webbrowser
import os
from logging_config import get_logger

# 初始化日志器
logger = get_logger(__name__)


def is_vue_server_running():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8080))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_vue_server():
    try:
        if is_vue_server_running():
        
            return

    

        cmd = ['npm', 'run', 'serve']
        process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )

    
        time.sleep(3)
        return process
    except Exception as e:
        logger.error(f'启动Vue服务器失败: {e}')
    


def open_browser():
    try:
        webbrowser.open('http://localhost:8080')
    except Exception as e:
        logger.error(f'打开浏览器失败: {e}')
