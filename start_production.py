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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('production.log')
    ]
)
logger = logging.getLogger(__name__)

# 获取项目根目录
ROOT_DIR = Path(__file__).parent
FRONTEND_DIR = ROOT_DIR / 'frontend'

# 存储子进程对象
processes = {}


def start_flask_backend():
    """启动Flask后端服务"""
    logger.info("正在启动Flask后端服务...")
    try:
        # 使用Python解释器运行app.py
        process = subprocess.Popen(
            [sys.executable, str(ROOT_DIR / 'app.py')],
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # 行缓冲
            universal_newlines=True
        )
        
        processes['flask'] = process
        logger.info(f"Flask后端服务已启动，PID: {process.pid}")
        
        # 实时输出日志
        for line in process.stdout:
            logger.info(f"[Flask] {line.strip()}")
            
        return process
    except Exception as e:
        logger.error(f"启动Flask后端服务失败: {e}")
        return None


def start_frontend():
    """启动前端Vue应用"""
    logger.info("正在启动前端Vue应用...")
    try:
        # 切换到前端目录
        os.chdir(str(FRONTEND_DIR))
        
        # 检查 npm 是否可用
        try:
            subprocess.run(['npm', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            npm_available = True
            logger.info("npm 命令可用")
        except (subprocess.CalledProcessError, FileNotFoundError):
            npm_available = False
            logger.warning("npm 命令不可用，尝试使用 npx")
        
        # 尝试使用 npm 或 npx 启动服务
        if npm_available:
            cmd = ['npm', 'run', 'serve']
        else:
            # 尝试使用 npx
            try:
                subprocess.run(['npx', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                cmd = ['npx', 'npm', 'run', 'serve']
                logger.info("使用 npx 启动前端服务")
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 如果 npx 也不可用，尝试使用 shell
                logger.warning("npm 和 npx 都不可用，尝试使用 shell 启动")
                cmd = 'npm run serve'
        
        # 启动前端服务
        if isinstance(cmd, str):
            # 使用 shell=True
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
        else:
            # 不使用 shell
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
        
        processes['frontend'] = process
        logger.info(f"前端Vue应用已启动，PID: {process.pid}")
        
        # 实时输出日志
        for line in process.stdout:
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
        
        # 检查 Node.js 是否安装
        try:
            node_version = subprocess.run(['node', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            logger.info(f"Node.js 版本: {node_version.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Node.js 未安装或不在系统路径中")
        
        return None
    finally:
        # 切换回原目录
        os.chdir(str(ROOT_DIR))


def signal_handler(sig, frame):
    """处理终止信号，关闭所有子进程"""
    logger.info("接收到终止信号，正在关闭所有服务...")
    for name, process in processes.items():
        if process and process.poll() is None:
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
                if process and process.poll() is not None:
                    logger.warning(f"{name} 服务已意外退出，退出码: {process.returncode}")
                    del processes[name]
                    
                    # 尝试重启服务
                    if name == 'flask':
                        logger.info("尝试重新启动Flask后端服务...")
                        flask_thread = threading.Thread(target=start_flask_backend)
                        flask_thread.daemon = True
                        flask_thread.start()
                    elif name == 'frontend':
                        logger.info("尝试重新启动前端服务...")
                        frontend_thread = threading.Thread(target=start_frontend)
                        frontend_thread.daemon = True
                        frontend_thread.start()
            
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号")
    finally:
        signal_handler(None, None)


if __name__ == "__main__":
    main()