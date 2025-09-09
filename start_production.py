"""LeafAuto Web生产环境启动脚本

该脚本用于启动LeafAuto Web应用程序的生产环境版本，包括后端和前端服务。
"""

import subprocess
import time
import webbrowser
import os
import sys
import logging
import ctypes
from pathlib import Path
from common import get_application_path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent

# 添加项目根目录到Python路径
sys.path.insert(0, str(ROOT_DIR))

# 设置编码以确保中文正常显示
try:
    # pylint: disable=consider-using-with
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    # pylint: enable=consider-using-with
except (OSError, ValueError) as e:
    print(f"无法设置标准输出编码: {e}")

# 配置日志
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
    """启动LeafAuto Web应用程序"""
    # 检查管理员权限
    if not _is_admin():
        logger.warning("当前程序未以管理员权限运行，某些功能可能受限")
        
    # 获取应用程序根目录
    application_path = get_application_path()

    logger.info("Starting LeafAuto Web application...")
    logger.info("Application path: %s", application_path)

    # 启动后端服务
    if not _start_backend_service(application_path):
        # 尝试以管理员权限重新启动
        if _restart_as_admin():
            logger.info("正在以管理员权限重新启动...")
            sys.exit(0)
        return

    # 等待后端启动
    time.sleep(3)

    # 启动前端服务
    if not _start_frontend_service(application_path):
        # 尝试以管理员权限重新启动
        if _restart_as_admin():
            logger.info("正在以管理员权限重新启动...")
            sys.exit(0)
        return

    # 等待前端启动
    logger.info("Waiting for frontend service to start...")
    time.sleep(5)

    # 打开浏览器
    _open_browser()

    # 显示服务信息
    _show_service_info()
    
    # 自动退出，不再等待用户按键
    logger.info("应用程序启动完成，脚本将自动退出...")
    time.sleep(2)


def _start_backend_service(application_path):
    """启动后端服务"""
    # 后端路径和可执行文件
    backend_dir = os.path.join(application_path, "backend")
    backend_exe = os.path.join(backend_dir, "LeafAutoBackend.exe")

    # 检查后端可执行文件是否存在
    if not os.path.exists(backend_exe):
        logger.error("后端可执行文件未找到: %s", backend_exe)
        # 尝试使用Python脚本启动
        backend_script = os.path.join(ROOT_DIR, "start_backend.py")
        if os.path.exists(backend_script):
            logger.info("尝试使用Python脚本启动后端服务...")
            try:
                # pylint: disable=consider-using-with
                subprocess.Popen(
                    [sys.executable, backend_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                # pylint: enable=consider-using-with
                return True
            except (OSError, subprocess.SubprocessError) as e:
                logger.error("启动后端脚本失败: %s", e)
                logger.warning("请尝试以管理员身份运行此程序")
                return False
        else:
            logger.error("找不到后端可执行文件或启动脚本")
            logger.warning("请尝试以管理员身份运行此程序")
            return False

    # 启动后端服务
    logger.info("Starting backend service...")
    try:
        # pylint: disable=consider-using-with
        subprocess.Popen(
            [backend_exe],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        # pylint: enable=consider-using-with
        return True
    except (OSError, subprocess.SubprocessError) as e:
        logger.error("启动后端服务失败: %s", e)
        logger.warning("请尝试以管理员身份运行此程序")
        return False


def _start_frontend_service(application_path):
    """启动前端服务"""
    # 前端路径和可执行文件
    frontend_dir = os.path.join(application_path, "frontend")
    frontend_exe = os.path.join(frontend_dir, "LeafAutoFrontend.exe")

    # 检查前端可执行文件是否存在
    if not os.path.exists(frontend_exe):
        logger.error("前端可执行文件未找到: %s", frontend_exe)
        # 尝试使用Python脚本启动
        frontend_script = os.path.join(ROOT_DIR, "start_frontend.py")
        if os.path.exists(frontend_script):
            logger.info("尝试使用Python脚本启动前端服务...")
            try:
                # pylint: disable=consider-using-with
                subprocess.Popen(
                    [sys.executable, frontend_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                # pylint: enable=consider-using-with
                return True
            except (OSError, subprocess.SubprocessError) as e:
                logger.error("启动前端脚本失败: %s", e)
                logger.warning("请尝试以管理员身份运行此程序")
                return False
        else:
            logger.error("找不到前端可执行文件或启动脚本")
            logger.warning("请尝试以管理员身份运行此程序")
            return False

    # 启动前端服务
    logger.info("Starting frontend service...")
    try:
        # pylint: disable=consider-using-with
        subprocess.Popen(
            [frontend_exe],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        # pylint: enable=consider-using-with
        return True
    except (OSError, subprocess.SubprocessError) as e:
        logger.error("启动前端服务失败: %s", e)
        logger.warning("请尝试以管理员身份运行此程序")
        return False


def _open_browser():
    """打开浏览器"""
    logger.info("Opening browser...")
    try:
        webbrowser.open("http://localhost:8080")
    except (OSError, webbrowser.Error) as e:
        logger.error("打开浏览器失败: %s", e)


def _show_service_info():
    """显示服务信息"""
    logger.info("Application is starting...")
    logger.info("Backend service running at: http://localhost:5000")
    logger.info("Frontend service running at: http://localhost:8080")
    logger.info("Browser should open automatically with the application")

def _is_admin():
    """检查当前程序是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def _restart_as_admin():
    """以管理员权限重新启动程序"""
    if _is_admin():
        return False  # 已经是管理员权限，无需重新启动
    
    try:
        script_path = os.path.abspath(sys.argv[0])
        params = ' '.join([script_path] + sys.argv[1:])
        
        # 请求管理员权限重新启动
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
