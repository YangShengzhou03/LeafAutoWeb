#!/usr/bin/env python3
"""
日志配置模块

提供统一的日志格式配置、错误处理装饰器和标准响应格式。
支持控制台和文件日志输出，自动日志轮转和错误处理。

主要功能：
- 统一的日志格式配置
- 错误处理装饰器
- 标准响应格式生成
- 自动日志文件管理
"""

import logging
import logging.handlers
from datetime import datetime
import os

# 日志级别映射表
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# 统一日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def setup_logging(log_level='INFO', log_file=None, max_bytes=10*1024*1024, backup_count=5):
    """
    配置应用程序的日志系统
    
    Args:
        log_level (str): 日志级别，可选值：DEBUG、INFO、WARNING、ERROR、CRITICAL，默认为INFO
        log_file (str): 日志文件路径，如果为None则不输出到文件
        max_bytes (int): 单个日志文件最大大小（字节），默认10MB
        backup_count (int): 备份文件数量，默认5个
    
    Returns:
        logging.Logger: 配置完成的根日志记录器实例
    
    Raises:
        ValueError: 当传入的日志级别无效时
    """
    # 设置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVELS.get(log_level, logging.INFO))
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name):
    """
    获取指定名称的日志器
    
    Args:
        name (str): 日志器名称，通常使用模块名
        
    Returns:
        logging.Logger: 配置好的日志器
    """
    return logging.getLogger(name)


# 错误处理装饰器
def handle_errors(default_return=None, log_errors=True):
    """
    错误处理装饰器，用于统一处理函数中的异常并记录详细错误信息
    
    Args:
        default_return (any): 发生异常时返回的默认值，可以是任意类型
        log_errors (bool): 是否记录错误日志，默认为True
        
    Returns:
        function: 装饰后的函数，自动捕获异常并返回默认值或记录日志
        
    Example:
        @handle_errors(default_return={}, log_errors=True)
        def process_data(data):
            # 数据处理逻辑
            return result
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger = get_logger(func.__module__)
                    logger.error(
                        f"函数 {func.__name__} 执行失败: {str(e)}", 
                        exc_info=True
                    )
                return default_return
        return wrapper
    return decorator


# 标准错误响应格式
def error_response(message, code=500, details=None):
    """
    生成标准的错误响应格式，包含详细的错误信息和时间戳
    
    Args:
        message (str): 错误描述消息，用于客户端显示
        code (int): HTTP状态码或自定义错误码，默认为500
        details (dict): 错误详情信息，包含调试用的额外数据
        
    Returns:
        dict: 标准化的错误响应字典，包含：
            - success: 操作状态（始终为False）
            - error: 错误信息对象，包含code、message、timestamp
            - details: 可选，详细的错误调试信息
    """
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    }
    
    if details:
        response['error']['details'] = details
    
    return response


# 成功响应格式
def success_response(data=None, message="操作成功"):
    """
    生成标准的成功响应格式，包含操作结果和时间戳
    
    Args:
        data (any): 返回的业务数据，可以是任意类型，默认为None
        message (str): 成功提示消息，用于客户端显示，默认为"操作成功"
        
    Returns:
        dict: 标准化的成功响应字典，包含：
            - success: 操作状态（始终为True）
            - message: 成功提示信息
            - timestamp: ISO格式的时间戳
            - data: 可选，返回的业务数据
    """
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    return response


# 初始化默认日志配置
# 在模块导入时自动设置默认配置
setup_logging(log_level='INFO', log_file='logs/app.log')

# 模块级别的日志器
logger = get_logger(__name__)

if __name__ == '__main__':
    # 测试日志配置
    logger.info("日志配置模块加载成功")
    logger.debug("这是一条调试信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")