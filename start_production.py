import subprocess
import time
import webbrowser
import os
import sys
import logging
import ctypes
from pathlib import Path
from common import get_application_path


ROOT_DIR = Path(__file__).parent


sys.path.insert(0, str(ROOT_DIR))


try:
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
except (OSError, ValueError) as e:
    logger.error(f"无法设置标准输出编码: {e}")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    
    if not _is_admin():
        logger.warning("当前程序未以管理员权限运行，某些功能可能受限")
        
        
    application_path = get_application_path()

    logger.info("Starting LeafAuto Web application...")
    logger.info("Application path: %s", application_path)


    if not _start_backend_service(application_path):
        
        if _restart_as_admin():
            logger.info("正在以管理员权限重新启动...")
            sys.exit(0)
        return


    time.sleep(3)


    if not _start_frontend_service(application_path):
        
        if _restart_as_admin():
            logger.info("正在以管理员权限重新启动...")
            sys.exit(0)
        return


    logger.info("Waiting for frontend service to start...")
    time.sleep(5)


    _open_browser()


    _show_service_info()
    
    
    logger.info("应用程序启动完成，脚本将自动退出...")
    time.sleep(2)


def _start_backend_service(application_path):
    
    backend_dir = os.path.join(application_path, "backend")
    backend_exe = os.path.join(backend_dir, "LeafAutoBackend.exe")


    if not os.path.exists(backend_exe):
        logger.error("后端可执行文件未找到: %s", backend_exe)
        
        backend_script = os.path.join(ROOT_DIR, "start_backend.py")
        if os.path.exists(backend_script):
            logger.info("尝试使用Python脚本启动后端服务...")
            try:
                subprocess.Popen(
                    [sys.executable, backend_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                
                return True
            except (OSError, subprocess.SubprocessError) as e:
                logger.error("启动后端脚本失败: %s", e)
                logger.warning("请尝试以管理员身份运行此程序")
                return False
        else:
            logger.error("找不到后端可执行文件或启动脚本")
            logger.warning("请尝试以管理员身份运行此程序")
            return False


    logger.info("Starting backend service...")
    try:
        subprocess.Popen(
            [backend_exe],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        return True
    except (OSError, subprocess.SubprocessError) as e:
        logger.error("启动后端服务失败: %s", e)
        logger.warning("请尝试以管理员身份运行此程序")
        return False


def _start_frontend_service(application_path):
    
    frontend_dir = os.path.join(application_path, "frontend")
    frontend_exe = os.path.join(frontend_dir, "LeafAutoFrontend.exe")


    if not os.path.exists(frontend_exe):
        logger.error("前端可执行文件未找到: %s", frontend_exe)
        
        frontend_script = os.path.join(ROOT_DIR, "start_frontend.py")
        if os.path.exists(frontend_script):
            logger.info("尝试使用Python脚本启动前端服务...")
            try:
                subprocess.Popen(
                    [sys.executable, frontend_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                
                return True
            except (OSError, subprocess.SubprocessError) as e:
                logger.error("启动前端脚本失败: %s", e)
                logger.warning("请尝试以管理员身份运行此程序")
                return False
        else:
            logger.error("找不到前端可执行文件或启动脚本")
            logger.warning("请尝试以管理员身份运行此程序")
            return False


    logger.info("Starting frontend service...")
    try:
        subprocess.Popen(
            [frontend_exe],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        return True
    except (OSError, subprocess.SubprocessError) as e:
        logger.error("启动前端服务失败: %s", e)
        logger.warning("请尝试以管理员身份运行此程序")
        return False


def _open_browser():
    
    logger.info("Opening browser...")
    try:
        webbrowser.open("http://localhost:8080")
    except (OSError, webbrowser.Error) as e:
        logger.error("打开浏览器失败: %s", e)


def _show_service_info():
    
    logger.info("Application is starting...")
    logger.info("Backend service running at: http://localhost:5000")
    logger.info("Frontend service running at: http://localhost:8080")
    logger.info("Browser should open automatically with the application")

def _is_admin():
    
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def _restart_as_admin():
    
    if _is_admin():
        return False  
    
    
    try:
        script_path = os.path.abspath(sys.argv[0])
        params = ' '.join([script_path] + sys.argv[1:])
        
        
        logger.info("正在请求管理员权限重新启动程序...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        return True
    except Exception as e:
        logger.error("以管理员权限重新启动失败: %s", e)
        return False


if __name__ == "__main__":
    main()
