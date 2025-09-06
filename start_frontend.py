#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
前端服务启动脚本
启动前端Vue开发服务器，使用端口8080
"""

import os
import subprocess
import sys
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

def is_frozen():
    """检查是否在打包环境中运行"""
    return getattr(sys, 'frozen', False)

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if is_frozen():
        # 在打包环境中，资源文件在_MEIPASS文件夹中
        base_path = Path(sys._MEIPASS)
    else:
        # 在开发环境中，使用项目根目录
        base_path = Path(__file__).parent
    return base_path / relative_path

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
        # 检查是否在打包环境中运行
        if is_frozen():
            logger.info("检测到在打包环境中运行")
            
            # 检查前端构建文件是否存在
            frontend_dist_path = get_resource_path('frontend/dist')
            
            if frontend_dist_path.exists():
                logger.info(f"检测到前端构建文件已存在于: {frontend_dist_path}")
                logger.info("使用Python内置HTTP服务器提供静态文件服务")
                
                # 使用Python内置的http.server提供静态文件服务
                import http.server
                import socketserver
                
                os.chdir(str(frontend_dist_path))
                PORT = 8080
                
                with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
                    logger.info(f"前端静态文件服务运行在: http://localhost:{PORT}")
                    logger.info("按Ctrl+C停止服务")
                    httpd.serve_forever()
                return 0
            else:
                logger.warning(f"未找到前端构建文件: {frontend_dist_path}")
                logger.info("请确保前端文件已正确打包")
                return 1
        
        # 切换到前端目录
        if is_frozen():
            frontend_path = get_resource_path('frontend')
            if frontend_path.exists():
                os.chdir(str(frontend_path))
            else:
                logger.error(f"找不到前端目录: {frontend_path}")
                return 1
        else:
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