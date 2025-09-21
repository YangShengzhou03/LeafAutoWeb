#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import subprocess
import sys
import logging
import http.server
import socketserver
from pathlib import Path

from common import is_frozen, get_resource_path


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
    
    original_cwd = os.getcwd()
    try:
        os.chdir(str(frontend_dist_path))
        port = 8080
        
        class SPARequestHandler(http.server.SimpleHTTPRequestHandler):
            
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.path = ''
            
            def do_GET(self):
                
                file_path = self.path.split('?')[0]  
                if file_path != '/' and os.path.exists(file_path[1:]):
                    
                    super().do_GET()
                else:
                    
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
        
        os.chdir(original_cwd)
    return 0

def _change_to_frontend_dir():
    
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
    
    if not check_node_installed():
        logger.error("无法启动前端服务，请先安装Node.js")
        return 1
    
    logger.info("正在启动前端开发服务器...")
    
    
    process = subprocess.Popen(
        'npm run serve',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    
    for line in process.stdout:
        line = line.strip()
        if line:
            logger.info("[Frontend] %s", line)
            
            if "App running at:" in line:
                logger.info("前端开发服务器已启动完成")
    
    process.wait()
    return process.returncode

def start_frontend_dev_server():
    
    original_cwd = None
    return_code = 0
    
    try:
        
        if is_frozen():
            logger.info("检测到在打包环境中运行")
            
            
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
            
            original_cwd = _change_to_frontend_dir()
            if original_cwd is None:
                return_code = 1
            else:
                return_code = _start_npm_server()
    except (OSError, subprocess.SubprocessError) as e:
        logger.error("启动前端服务失败: %s", e)
        return_code = 1
    finally:
        
        if original_cwd is not None:
            try:
                os.chdir(original_cwd)
            except (OSError, ValueError) as e:
                logger.warning("恢复工作目录失败: %s", e)
                
                try:
                    os.chdir(str(ROOT_DIR))
                except (OSError, ValueError):
                    pass
    
    return return_code

def start_frontend():
    
    logger.info("LeafAuto前端服务启动中...")
    logger.info("前端开发服务器将运行在: http://localhost:8080")
    logger.info("请确保后端服务已启动在: http://localhost:5000")
    
    return start_frontend_dev_server()

if __name__ == "__main__":
    sys.exit(start_frontend())