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


def is_vue_server_running(port=8080):
    """
    检查Vue开发服务器是否正在运行
    
    Args:
        port: 服务器端口号，默认为8080
    
    Returns:
        bool: True表示服务器正在运行，False表示未运行
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_vue_server(port=8080):
    """
    启动Vue开发服务器
    
    Args:
        port: 服务器端口号，默认为8080
    
    Returns:
        subprocess.Popen: Vue服务器进程对象，如果启动失败则返回None
    """
    try:
        if is_vue_server_running(port):
            return

        cmd = ["npm", "run", "serve", "--port", str(port)]
        process = subprocess.Popen(
            cmd,
            cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )

        time.sleep(3)
        return process
    except Exception as e:
        logger.error(f"启动Vue服务器失败: {e}")


def open_browser(port=8080):
    """
    在默认浏览器中打开Vue应用
    
    Args:
        port: 服务器端口号，默认为8080
    """
    try:
        webbrowser.open(f"http://localhost:{port}")
    except Exception as e:
        logger.error(f"打开浏览器失败: {e}")
