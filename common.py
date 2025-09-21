#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
公共函数模块
包含项目中共用的工具函数
"""

import sys
from pathlib import Path
from typing import Union


def is_frozen() -> bool:
    """检查是否在打包环境中运行
    
    Returns:
        bool: True表示在打包环境中，False表示在开发环境中
    """
    return getattr(sys, 'frozen', False)


def get_resource_path(relative_path: Union[str, Path]) -> Path:
    """获取资源文件的绝对路径
    
    Args:
        relative_path: 相对路径
        
    Returns:
        Path: 资源文件的绝对路径
    """
    if is_frozen():
        # 在打包环境中，资源文件在_MEIPASS文件夹中
        # pylint: disable=protected-access
        base_path = Path(sys._MEIPASS)
        # pylint: enable=protected-access
    else:
        # 在开发环境中，使用项目根目录
        base_path = Path(__file__).parent
    return base_path / relative_path


def get_application_path() -> Path:
    """获取应用程序根目录（处理打包后的路径）
    
    Returns:
        Path: 应用程序根目录路径
    """
    if is_frozen():
        # 如果是打包后的exe
        return Path(sys.executable).parent
    # 如果是脚本运行
    return Path(__file__).parent
