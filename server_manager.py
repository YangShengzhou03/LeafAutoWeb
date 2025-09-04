import subprocess
import time
import socket
import webbrowser
import os


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
            print('Vue开发服务器已经在运行')
            return

        print('正在启动Vue开发服务器...')

        cmd = ['npm', 'run', 'serve']
        process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )

        print('Vue开发服务器已启动')
        time.sleep(3)
        return process
    except Exception as e:
        print(f'启动Vue开发服务器失败: {e}')


def open_browser():
    try:
        print('正在打开浏览器...')
        webbrowser.open('http://localhost:8080')
    except Exception as e:
        print(f'打开浏览器失败: {e}')
