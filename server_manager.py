"""
服务器管理模块
负责Vue前端服务器的启动、状态检查和浏览器打开功能
"""

import os
import socket
import subprocess
import time
import webbrowser

from logging_config import get_logger

# 初始化日志器
logger = get_logger(__name__)


def is_vue_server_running():
    """
    检查Vue开发服务器是否正在运行
    
    Returns:
        bool: True表示服务器正在运行，False表示未运行
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", 8080))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_vue_server():
    """
    启动Vue开发服务器
    
    Returns:
        subprocess.Popen: Vue服务器进程对象，如果启动失败则返回None
    """
    try:
        if is_vue_server_running():
            return

        cmd = ["npm", "run", "serve"]
        process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )

        time.sleep(3)
        return process
    except Exception as e:
        logger.error(f"启动Vue服务器失败: {e}")


def open_browser():
    """
    在默认浏览器中打开Vue应用
    """
    try:
        webbrowser.open("http://localhost:8080")
    except Exception as e:
        logger.error(f"打开浏览器失败: {e}")
