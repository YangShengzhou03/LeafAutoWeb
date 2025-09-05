#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生产环境启动脚本
同时启动Flask后端服务和前端Vue应用
"""

import os
import subprocess
import sys
import time
import signal
import threading
import logging
from pathlib import Path

# 配置日志
# 配置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 配置文件处理器，指定utf-8编码
file_handler = logging.FileHandler('production.log', encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# 配置控制台处理器，使用errors='replace'处理编码问题
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# 设置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 获取项目根目录
ROOT_DIR = Path(__file__).parent
FRONTEND_DIR = ROOT_DIR / 'frontend'

# 存储子进程对象
processes = {}


def start_flask_backend():
    """启动Flask后端服务"""
    logger.info("正在启动Flask后端服务...")
    try:
        # 检查是否在打包环境中运行
        if getattr(sys, 'frozen', False):
            # 在打包环境中，直接导入并运行app.py
            import app
            # 在新线程中运行Flask应用，使用不阻塞的方式
            def run_flask():
                from werkzeug.serving import make_server
                # 创建WSGI服务器
                server = make_server('0.0.0.0', 5000, app.app)
                logger.info("Flask WSGI服务器已启动")
                # 输出访问网址信息
                logger.info("服务已启动，请通过浏览器访问: http://localhost:5000")
                logger.info("或使用网络IP地址访问: http://<您的IP地址>:5000")
                # 启动服务器（这会阻塞当前线程）
                server.serve_forever()
            
            flask_thread = threading.Thread(target=run_flask)
            flask_thread.daemon = True
            flask_thread.start()
            processes['flask'] = flask_thread
            logger.info("Flask后端服务已启动")
            return flask_thread
        else:
            # 在开发环境中，使用Python解释器运行app.py
            process = subprocess.Popen(
                [sys.executable, str(ROOT_DIR / 'app.py')],
                cwd=str(ROOT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True,
                encoding='utf-8',  # 指定编码为utf-8
                errors='replace'  # 替换无法解码的字符
            )
            
            processes['flask'] = process
            logger.info(f"Flask后端服务已启动，PID: {process.pid}")
            
            # 实时输出日志，过滤掉一些不需要的日志
            for line in process.stdout:
                # 过滤掉 comtypes 相关的日志
                if "comtypes.client._code_cache" in line:
                    continue
                logger.info(f"[Flask] {line.strip()}")
                
            return process
    except Exception as e:
        logger.error(f"启动Flask后端服务失败: {e}")
        return None


def start_frontend():
    """启动前端Vue应用"""
    logger.info("正在启动前端Vue应用...")
    
    # 检查是否在打包环境中运行
    if getattr(sys, 'frozen', False):
        logger.info("检测到在打包环境中运行")
        
        # 检查前端构建文件是否存在
        frontend_dist_path = Path(sys._MEIPASS) / 'frontend' / 'dist' if hasattr(sys, '_MEIPASS') else ROOT_DIR / 'frontend' / 'dist'
        
        if frontend_dist_path.exists():
            logger.info(f"检测到前端构建文件已存在于: {frontend_dist_path}")
            logger.info("前端文件已包含在打包中，Flask将自动提供静态文件服务")
            return None
        else:
            logger.warning(f"未找到前端构建文件: {frontend_dist_path}")
            logger.info("请确保前端文件已正确打包")
            return None
    
    try:
        # 切换到前端目录
        os.chdir(str(FRONTEND_DIR))
        
        # 检查 Node.js 是否安装
        try:
            node_version = subprocess.run(['node', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logger.info(f"Node.js 版本: {node_version.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Node.js 未安装或不在系统路径中，无法启动前端服务")
            logger.info("请手动启动前端服务或使用已构建的前端文件")
            return None
        
        # 检查前端构建文件是否存在
        if (FRONTEND_DIR / 'dist').exists():
            logger.info("检测到前端构建文件已存在，可以直接使用")
        
        # 直接使用 shell 启动 npm 服务
        process = subprocess.Popen(
            'npm run serve',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # 行缓冲
            universal_newlines=True
        )
        
        processes['frontend'] = process
        logger.info(f"前端Vue应用已启动，PID: {process.pid}")
        
        # 实时输出日志，过滤掉一些不需要的日志
        for line in process.stdout:
            # 过滤掉构建过程中的详细日志
            if any(skip_text in line for skip_text in [
                "setup (watch run)",
                "setup (normal module factory)",
                "setup (context module factory)",
                "setup (before compile)",
                "setup (compile)",
                "setup (compilation)",
                "[","]",
                "%",
                "building",
                "WARN  \"vue\" field in package.json ignored",
                "You should migrate it into vue.config.js"
            ]):
                continue
                
            logger.info(f"[Frontend] {line.strip()}")
            # 检测前端服务是否已启动
            if "App running at:" in line:
                logger.info("前端服务已完全启动，可通过浏览器访问")
            
        return process
    except Exception as e:
        logger.error(f"启动前端Vue应用失败: {e}")
        logger.error(f"错误详情: {type(e).__name__}")
        # 提供更多诊断信息
        logger.error(f"当前工作目录: {os.getcwd()}")
        logger.error(f"前端目录: {FRONTEND_DIR}")
        logger.error(f"package.json 存在: {(FRONTEND_DIR / 'package.json').exists()}")
        
        return None
    finally:
        # 切换回原目录
        os.chdir(str(ROOT_DIR))


def signal_handler(sig, frame):
    """处理终止信号，关闭所有子进程"""
    logger.info("接收到终止信号，正在关闭所有服务...")
    for name, process in list(processes.items()):
        if process is None:
            continue
            
        if name == 'flask' and isinstance(process, threading.Thread):
            # 对于Flask线程，我们无法直接停止，只能记录日志
            logger.info(f"Flask服务线程正在运行，程序退出后将自动终止")
        elif process.poll() is None:
            # 对于子进程，尝试正常终止
            logger.info(f"正在关闭 {name} 服务 (PID: {process.pid})...")
            process.terminate()
            try:
                process.wait(timeout=5)
                logger.info(f"{name} 服务已关闭")
            except subprocess.TimeoutExpired:
                logger.warning(f"{name} 服务未在5秒内关闭，强制终止")
                process.kill()
    logger.info("所有服务已关闭")
    sys.exit(0)


def main():
    """主函数"""
    logger.info("正在启动LeafAuto Web生产环境...")
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查环境
    if not (ROOT_DIR / 'app.py').exists():
        logger.error("找不到app.py文件，请确保在正确的目录中运行此脚本")
        sys.exit(1)
        
    if not (FRONTEND_DIR / 'package.json').exists():
        logger.error("找不到前端package.json文件，请确保前端项目存在")
        sys.exit(1)
    
    # 启动Flask后端
    flask_thread = threading.Thread(target=start_flask_backend)
    flask_thread.daemon = True
    flask_thread.start()
    
    # 等待后端启动
    time.sleep(2)
    
    # 启动前端
    frontend_thread = threading.Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    logger.info("所有服务正在启动中...")
    logger.info("按 Ctrl+C 可停止所有服务")
    
    try:
        # 保持主线程运行
        while True:
            # 检查进程状态
            for name, process in list(processes.items()):
                if process is None:
                    continue
                    
                if name == 'flask' and isinstance(process, threading.Thread):
                    # 对于Flask线程，检查是否仍在运行
                    if not process.is_alive():
                        logger.warning(f"Flask服务线程已意外退出")
                        del processes[name]
                        
                        # 尝试重启服务
                        logger.info("尝试重新启动Flask后端服务...")
                        flask_thread = threading.Thread(target=start_flask_backend)
                        flask_thread.daemon = True
                        flask_thread.start()
                        processes['flask'] = flask_thread
                elif isinstance(process, subprocess.Popen) and process.poll() is not None:
                    logger.warning(f"{name} 服务已意外退出，退出码: {process.returncode}")
                    del processes[name]
                    
                    # 尝试重启服务
                    if name == 'frontend':
                        logger.info("尝试重新启动前端服务...")
                        frontend_thread = threading.Thread(target=start_frontend)
                        frontend_thread.daemon = True
                        frontend_thread.start()
                        processes['frontend'] = frontend_thread
            
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号")
    finally:
        signal_handler(None, None)


if __name__ == "__main__":
    main()