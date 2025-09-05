#!/usr/bin/env python3
"""
应用层测试 - 测试Flask应用的核心功能
"""

import os
import sys
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


def test_home_route():
    """测试首页路由重定向"""
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 302  # 重定向
        assert 'localhost:8080' in response.location


def test_api_tasks_get():
    """测试获取任务列表API"""
    with app.test_client() as client:
        response = client.get('/api/tasks')
        assert response.status_code == 200
        assert isinstance(response.json, list)


def test_api_wechat_status():
    """测试微信状态API"""
    with app.test_client() as client:
        response = client.get('/api/wechat-status')
        assert response.status_code == 200
        data = response.json
        assert 'success' in data
        assert 'online' in data


def test_health_check():
    """测试健康检查端点"""
    with app.test_client() as client:
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.json
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])