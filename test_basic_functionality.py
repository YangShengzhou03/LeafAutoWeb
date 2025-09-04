#!/usr/bin/env python3
"""
基础功能测试脚本
用于验证项目核心功能是否正常工作
"""

import sys

from app import app


def test_data_manager():
    """测试数据管理功能"""
    print("测试数据管理功能...")
    
    try:
        from data_manager import load_tasks, save_home_data, load_home_data
        
        # 测试任务加载
        tasks = load_tasks()
        print(f"✓ 成功加载任务数据: {len(tasks)} 个任务")
        
        # 测试首页数据
        home_data = load_home_data()
        print(f"✓ 成功加载首页数据: {len(home_data.get('pricingPlans', []))} 个定价方案")
        
        return True
    except Exception as e:
        print(f"✗ 数据管理测试失败: {e}")
        return False

def test_wechat_instance():
    """测试微信实例功能"""
    print("测试微信实例功能...")
    
    try:
        from wechat_instance import get_wechat_instance, is_wechat_online, get_status_info
        
        # 测试实例获取
        wx = get_wechat_instance()
        print("✓ 成功获取微信实例")
        
        # 测试在线状态检查
        online = is_wechat_online()
        print(f"✓ 微信在线状态: {online}")
        
        # 测试状态信息获取
        status_info = get_status_info()
        print(f"✓ 状态信息: {status_info}")
        
        return True
    except Exception as e:
        print(f"✗ 微信实例测试失败: {e}")
        return False

def test_flask_app():
    """测试Flask应用"""
    print("测试Flask应用...")
    
    try:
        with app.test_client() as client:
            # 测试首页路由
            response = client.get('/')
            print(f"✓ 首页路由状态码: {response.status_code}")
            
            # 测试微信状态API
            response = client.get('/api/wechat-status')
            data = response.get_json()
            print(f"✓ 微信状态API响应: {data.get('success', False)}")
            
            # 测试任务API
            response = client.get('/api/tasks')
            data = response.get_json()
            print(f"✓ 任务API响应: {data}")
            
            return True
    except Exception as e:
        print(f"✗ Flask应用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("LeafAuto Web 基础功能测试")
    print("=" * 50)
    
    results = []
    
    # 运行所有测试
    results.append(test_data_manager())
    results.append(test_wechat_instance()) 
    results.append(test_flask_app())
    
    print("=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"成功: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return 1

if __name__ == "__main__":
    sys.exit(main())