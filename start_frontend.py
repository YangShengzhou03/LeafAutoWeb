#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
前端服务启动脚本
启动前端Vue开发服务器，使用端口8080
"""

import os
import subprocess
import sys
import logging
import http.server
import socketserver
from pathlib import Path

from common import is_frozen, get_resource_path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent
FRONTEND_DIR = ROOT_DIR / 'frontend'
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
                              capture_output=True, text=True, timeout=10, check=False)
        if result.returncode == 0:
            logger.info("Node.js版本: %s", result.stdout.strip())
            return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.error("Node.js未安装或不在系统路径中")
        return False
    return False

def _serve_static_files(frontend_dist_path):
    """使用Python内置HTTP服务器提供静态文件服务"""
    # 保存当前工作目录
    original_cwd = os.getcwd()
    try:
        os.chdir(str(frontend_dist_path))
        port = 8080
        
        # 创建自定义请求处理器，支持SPA路由
        class SPARequestHandler(http.server.SimpleHTTPRequestHandler):
            """自定义请求处理器，支持SPA路由"""
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.path = ''
            
            def do_GET(self):
                # 检查请求的文件是否存在
                file_path = self.path.split('?')[0]  # 移除查询参数
                if file_path != '/' and os.path.exists(file_path[1:]):
                    # 文件存在，正常处理
                    super().do_GET()
                else:
                    # 文件不存在，返回index.html
                    self.path = '/index.html'
                    super().do_GET()
        
        with socketserver.TCPServer(("", port), SPARequestHandler) as httpd:
            logger.info("前端静态文件服务运行在: http://localhost:%d", port)
            logger.info("按Ctrl+C停止服务")
            httpd.serve_forever()
    except (OSError, OSError) as e:
        logger.error("静态文件服务启动失败: %s", e)
        return 1
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)
    return 0

def _change_to_frontend_dir():
    """切换到前端目录"""
    original_cwd = os.getcwd()
    try:
        if is_frozen():
            frontend_path = get_resource_path('frontend')
            if frontend_path.exists():
                os.chdir(str(frontend_path))
            else:
                logger.error("找不到前端目录: %s", frontend_path)
                return None
        else:
            os.chdir(str(FRONTEND_DIR))
        return original_cwd
    except (OSError, ValueError) as e:
        logger.error("切换目录失败: %s", e)
        return None

def _start_npm_server():
    """启动npm开发服务器"""
    # 检查Node.js
    if not check_node_installed():
        logger.error("无法启动前端服务，请先安装Node.js")
        return 1
    
    logger.info("正在启动前端开发服务器...")
    
    # 启动npm服务
    # pylint: disable=consider-using-with
    process = subprocess.Popen(
        'npm run serve',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    # pylint: enable=consider-using-with
    
    # 实时输出日志
    for line in process.stdout:
        line = line.strip()
        if line:
            logger.info("[Frontend] %s", line)
            # 检测前端服务是否已启动
            if "App running at:" in line:
                logger.info("前端开发服务器已启动完成")
    
    # 等待进程结束
    process.wait()
    return process.returncode

def start_frontend_dev_server():
    """启动前端开发服务器"""
    original_cwd = None
    return_code = 0
    
    try:
        # 检查是否在打包环境中运行
        if is_frozen():
            logger.info("检测到在打包环境中运行")
            
            # 检查前端构建文件是否存在
            frontend_dist_path = get_resource_path('frontend/dist')
            
            if frontend_dist_path.exists():
                logger.info("检测到前端构建文件已存在于: %s", frontend_dist_path)
                logger.info("使用Python内置HTTP服务器提供静态文件服务")
                return_code = _serve_static_files(frontend_dist_path)
            else:
                logger.warning("未找到前端构建文件: %s", frontend_dist_path)
                logger.info("请确保前端文件已正确打包")
                return_code = 1
        else:
            # 切换到前端目录
            original_cwd = _change_to_frontend_dir()
            if original_cwd is None:
                return_code = 1
            else:
                return_code = _start_npm_server()
    except (OSError, subprocess.SubprocessError) as e:
        logger.error("启动前端服务失败: %s", e)
        return_code = 1
    finally:
        # 切换回原目录，确保无论发生什么情况都恢复目录
        if original_cwd is not None:
            try:
                os.chdir(original_cwd)
            except (OSError, ValueError) as e:
                logger.warning("恢复工作目录失败: %s", e)
                # 如果恢复失败，尝试切换到项目根目录
                try:
                    os.chdir(str(ROOT_DIR))
                except (OSError, ValueError):
                    pass
    
    return return_code

def start_frontend():
    """启动前端服务"""
    logger.info("LeafAuto前端服务启动中...")
    logger.info("前端开发服务器将运行在: http://localhost:8080")
    logger.info("请确保后端服务已启动在: http://localhost:5000")
    
    return start_frontend_dev_server()

if __name__ == "__main__":
    sys.exit(start_frontend())