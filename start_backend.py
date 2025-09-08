#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
后端服务启动脚本
启动Flask后端服务，使用端口5000
"""

import argparse
import logging
import sys
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent

# 添加项目根目录到Python路径
sys.path.insert(0, str(ROOT_DIR))

# 导入应用模块
from app import app

# 导入公共函数
from common import is_frozen, get_resource_path

# 导入任务调度器
from task_scheduler import start_task_scheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def start_backend():
    """启动Flask后端服务"""
    try:
        # 检查是否在打包环境中运行
        if is_frozen():
            logger.info("检测到在打包环境中运行")

            # 检查数据文件是否存在
            data_path = get_resource_path('data')
            if data_path.exists():
                logger.info("检测到数据文件已存在于: %s", data_path)
            else:
                logger.warning("未找到数据文件: %s", data_path)
                logger.info("尝试创建数据目录")
                data_path.mkdir(parents=True, exist_ok=True)

        # 启动任务调度器
        start_task_scheduler()

        logger.info("正在启动Flask后端服务...")
        logger.info("服务地址: http://localhost:5000")
        logger.info("API地址: http://localhost:5000/api")

        # 启动Flask应用
        app.run(debug=False, host='0.0.0.0', port=5000)

    except (OSError, RuntimeError, ValueError) as e:
        logger.error("启动后端服务失败: %s", e)
        return 1

    return 0

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='启动LeafAuto后端服务')
    parser.add_argument('--port', type=int, default=5000, help='后端服务端口号')
    args = parser.parse_args()

    logger.info("LeafAuto后端服务启动中，端口: %d", args.port)
    sys.exit(start_backend())
