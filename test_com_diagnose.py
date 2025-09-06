#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
COM组件诊断测试脚本
用于测试微信COM组件初始化问题和诊断功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wechat_instance import diagnose_com_error, get_wechat_instance, is_wechat_online
from logging_config import get_logger

# 初始化日志器
logger = get_logger(__name__)

def test_com_diagnose():
    """测试COM组件诊断功能"""
    print("=== COM组件诊断测试 ===")
    
    # 测试诊断功能
    print("\n1. 运行COM组件诊断...")
    solutions = diagnose_com_error()
    for solution in solutions:
        print(f"   {solution}")
    
    # 测试微信实例获取
    print("\n2. 测试微信实例获取...")
    try:
        wx_instance = get_wechat_instance()
        if wx_instance is None:
            print("   ✗ 微信实例创建失败")
        else:
            print("   ✓ 微信实例创建成功")
            
            # 测试在线状态
            online = is_wechat_online()
            print(f"   ✓ 微信在线状态: {online}")
            
            if online:
                # 尝试获取用户信息
                try:
                    user_info = wx_instance.nickname
                    print(f"   ✓ 微信用户: {user_info}")
                except Exception as e:
                    print(f"   ⚠ 获取用户信息失败: {e}")
            
    except Exception as e:
        print(f"   ✗ 微信实例获取异常: {e}")
        
        # 检查是否是COM组件错误
        if hasattr(e, 'args') and len(e.args) > 0:
            if isinstance(e.args[0], int) and e.args[0] == -2147467259:
                print("   ⚠ 检测到COM组件初始化错误 (-2147467259)")
                print("   💡 请按照以下步骤排查:")
                print("     1. 确保微信已正确安装并登录")
                print("     2. 重启微信客户端")
                print("     3. 检查微信COM组件是否已正确注册")
                print("     4. 尝试以管理员权限运行程序")

if __name__ == "__main__":
    test_com_diagnose()
    print("\n=== 测试完成 ===")