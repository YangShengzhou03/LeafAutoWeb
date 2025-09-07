import subprocess
import time
import webbrowser
import os
import sys

# 设置编码以确保中文正常显示
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def main():
    # 获取应用程序根目录（处理打包后的路径）
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是脚本运行
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    print("Starting LeafAuto Web application...")
    print(f"Application path: {application_path}")

    # 后端路径和可执行文件
    backend_dir = os.path.join(application_path, "backend")
    backend_exe = os.path.join(backend_dir, "LeafAutoBackend.exe")
    
    # 检查后端可执行文件是否存在
    if not os.path.exists(backend_exe):
        print(f"错误：后端可执行文件未找到: {backend_exe}")
        return
    
    # 启动后端服务
    print("Starting backend service...")
    try:
        subprocess.Popen(
            [backend_exe],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        print(f"启动后端服务失败: {str(e)}")
        return
    
    # 等待后端启动
    time.sleep(3)
    
    # 前端路径和可执行文件
    frontend_dir = os.path.join(application_path, "frontend")
    frontend_exe = os.path.join(frontend_dir, "LeafAutoFrontend.exe")
    
    # 检查前端可执行文件是否存在
    if not os.path.exists(frontend_exe):
        print(f"错误：前端可执行文件未找到: {frontend_exe}")
        return
    
    # 启动前端服务
    print("Starting frontend service...")
    try:
        subprocess.Popen(
            [frontend_exe],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        print(f"启动前端服务失败: {str(e)}")
        return
    
    # 等待前端启动
    print("Waiting for frontend service to start...")
    time.sleep(5)
    
    # 打开浏览器
    print("Opening browser...")
    webbrowser.open("http://localhost:8080")
    
    # 显示服务信息
    print("Application is starting...")
    print("Backend service running at: http://localhost:5000")
    print("Frontend service running at: http://localhost:8080")
    print("Browser should open automatically with the application")
    
    # 等待用户按键退出
    input("按任意键退出...")

if __name__ == "__main__":
    main()