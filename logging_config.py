#!/usr/bin/env python3

import logging
import logging.handlers
import os
from datetime import datetime

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level="INFO", log_file=None, max_bytes=10 * 1024 * 1024, backup_count=5
):
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVELS.get(log_level, logging.INFO))

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def handle_errors(default_return=None, log_errors=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger = get_logger(func.__module__)
                    logger.error(f"函数 {func.__name__} 执行失败: {str(e)}", exc_info=True)
                return default_return

        return wrapper

    return decorator


def error_response(message, code=500, details=None):
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        },
    }

    if details:
        response["error"]["details"] = details

    return response


def success_response(data=None, message="操作成功"):
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }

    if data is not None:
        response["data"] = data

    return response


setup_logging(log_level="INFO", log_file="logs/app.log")

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("日志配置模块加载成功")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
