import os
import socket
import subprocess
import time
import webbrowser

from logging_config import get_logger

logger = get_logger(__name__)


def is_vue_server_running(port=8080):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("localhost", port))
            return result == 0
    except (OSError, OSError):
        return False


def start_vue_server(port=8080):
    try:
        if is_vue_server_running(port):
            logger.info("Vue服务器已在运行")
            return None

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
    except (OSError, subprocess.SubprocessError) as e:
        logger.error("启动Vue服务器失败: %s", e)
        return None


def open_browser(port=8080):
    try:
        webbrowser.open(f"http://localhost:{port}")
    except (OSError, webbrowser.Error) as e:
        logger.error("打开浏览器失败: %s", e)