#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
前端服务启动脚本
启动前端Vue开发服务器，使用端口8080
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent
FRONTEND_DIR = ROOT_DIR / 'frontend'

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frontend.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_node_installed():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"Node.js版本: {result.stdout.strip()}")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.error("Node.js未安装或不在系统路径中")
        return False
    return False

def start_frontend_dev_server():
    """启动前端开发服务器"""
    try:
        # 切换到前端目录
        os.chdir(str(FRONTEND_DIR))
        
        # 检查Node.js
        if not check_node_installed():
            logger.error("无法启动前端服务，请先安装Node.js")
            return 1
        
        logger.info("正在启动前端开发服务器...")
        
        # 启动npm服务
        process = subprocess.Popen(
            'npm run serve',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时输出日志
        for line in process.stdout:
            line = line.strip()
            if line:
                logger.info(f"[Frontend] {line}")
                # 检测前端服务是否已启动
                if "App running at:" in line:
                    logger.info("前端开发服务器已启动完成")
        
        # 等待进程结束
        process.wait()
        return process.returncode
        
    except Exception as e:
        logger.error(f"启动前端服务失败: {e}")
        return 1
    finally:
        # 切换回原目录
        os.chdir(str(ROOT_DIR))

def start_frontend():
    """启动前端服务"""
    logger.info("LeafAuto前端服务启动中...")
    logger.info("前端开发服务器将运行在: http://localhost:8080")
    logger.info("请确保后端服务已启动在: http://localhost:5000")
    
    return start_frontend_dev_server()

if __name__ == "__main__":
    sys.exit(start_frontend())