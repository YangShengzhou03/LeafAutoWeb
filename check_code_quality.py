#!/usr/bin/env python3
"""
代码质量检查脚本
用于检查项目中的代码质量问题
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def check_flake8():
    """运行flake8代码检查"""
    print("\n=== 运行flake8代码检查 ===")
    return run_command("python -m flake8 . --max-line-length=120 --exclude=.venv,__pycache__")

def check_black():
    """检查代码格式化"""
    print("\n=== 检查代码格式化 (black) ===")
    return run_command("python -m black --check . --exclude=\".*|.venv|__pycache__\"")

def check_isort():
    """检查import排序"""
    print("\n=== 检查import排序 (isort) ===")
    return run_command("python -m isort --check-only . --skip=.venv --skip=__pycache__")

def check_pytest():
    """运行测试"""
    print("\n=== 运行测试 (pytest) ===")
    return run_command("python -m pytest tests/ -v")

def main():
    """主函数"""
    print("🚀 开始代码质量检查...")
    
    # 检查flake8
    returncode, stdout, stderr = check_flake8()
    if returncode != 0:
        print("❌ flake8检查发现错误:")
        print(stdout)
    else:
        print("✅ flake8检查通过")
    
    # 检查black
    returncode, stdout, stderr = check_black()
    if returncode != 0:
        print("⚠️  代码格式化需要调整 (运行 black . 来修复)")
    else:
        print("✅ 代码格式化检查通过")
    
    # 检查isort
    returncode, stdout, stderr = check_isort()
    if returncode != 0:
        print("⚠️  import排序需要调整 (运行 isort . 来修复)")
    else:
        print("✅ import排序检查通过")
    
    # 运行测试
    returncode, stdout, stderr = check_pytest()
    if returncode != 0:
        print("❌ 测试失败:")
        print(stdout)
    else:
        print("✅ 所有测试通过")
    
    print("\n🎯 代码质量检查完成！")

if __name__ == "__main__":
    main()