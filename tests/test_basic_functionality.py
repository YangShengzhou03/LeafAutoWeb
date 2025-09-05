#!/usr/bin/env python3
"""
基础功能测试脚本
用于验证项目核心功能是否正常工作
"""

import sys

from app import app


def test_data_manager():
    """测试数据管理功能"""

    try:
        from data_manager import load_tasks, save_home_data, load_home_data

        # 测试任务加载
        tasks = load_tasks()

        # 测试首页数据
        home_data = load_home_data()

        return True
    except Exception as e:
        print(f"✗ 数据管理测试失败: {e}")
        return False


def test_wechat_instance():
    """测试微信实例功能"""

    try:
        from wechat_instance import (
            get_wechat_instance,
            is_wechat_online,
            get_status_info,
        )

        # 测试实例获取
        wx = get_wechat_instance()

        # 测试在线状态检查
        online = is_wechat_online()

        # 测试状态信息获取
        status_info = get_status_info()

        return True
    except Exception as e:
        print(f"✗ 微信实例测试失败: {e}")
        return False


def test_flask_app():
    """测试Flask应用"""

    try:
        with app.test_client() as client:
            # 测试首页路由
            response = client.get("/")

            # 测试微信状态API
            response = client.get("/api/wechat-status")
            data = response.get_json()

            # 测试任务API
            response = client.get("/api/tasks")
            data = response.get_json()

            return True
    except Exception as e:
        print(f"✗ Flask应用测试失败: {e}")
        return False


def main():
    """主测试函数"""

    results = []

    # 运行所有测试
    results.append(test_data_manager())
    results.append(test_wechat_instance())
    results.append(test_flask_app())

    success_count = sum(results)
    total_count = len(results)

    if success_count == total_count:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
