#!/usr/bin/env python3
"""
LeafAuto项目打包脚本
使用PyInstaller将项目打包为可执行文件
"""

import os
import subprocess
import sys
import shutil

def build_project():
    """构建项目"""
    print("🚀 开始构建LeafAuto项目...")
    
    # 检查前端构建文件是否存在
    frontend_dist = os.path.join("frontend", "dist")
    if not os.path.exists(frontend_dist):
        print("❌ 前端构建文件不存在，请先运行 'npm run build'")
        return False
    
    # PyInstaller打包命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包为单个exe文件
        "--name", "LeafAuto",  # 输出文件名
        "--add-data", f"{frontend_dist};frontend/dist",  # 包含前端构建文件
        "--add-data", "data;data",  # 包含数据文件夹
        "--hidden-import", "werkzeug.wrappers",  # 隐藏导入
        "--hidden-import", "flask_cors",
        "--hidden-import", "python_dotenv",
        "--console",  # 显示控制台窗口
        "start_production.py"  # 入口文件
    ]
    
    print("📦 正在打包项目...")
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功完成!")
        
        # 显示输出信息
        if result.stdout:
            print("输出信息:")
            print(result.stdout)
        
        # 检查生成的文件
        dist_dir = "dist"
        if os.path.exists(dist_dir):
            exe_files = [f for f in os.listdir(dist_dir) if f.endswith('.exe')]
            if exe_files:
                print(f"\n🎉 打包完成! 可执行文件位于: {os.path.abspath(dist_dir)}")
                for exe in exe_files:
                    print(f"   - {exe}")
                
                # 复制必要的文件到dist目录
                print("\n📋 复制必要文件...")
                
                # 复制数据文件夹
                data_dest = os.path.join(dist_dir, "data")
                if os.path.exists("data") and not os.path.exists(data_dest):
                    shutil.copytree("data", data_dest)
                    print("✅ 数据文件夹已复制")
                
                # 复制.env.example
                if os.path.exists(".env.example"):
                    shutil.copy2(".env.example", os.path.join(dist_dir, ".env.example"))
                    print("✅ 环境配置文件已复制")
                
                print(f"\n🚀 启动说明:")
                print(f"1. 进入目录: cd {os.path.abspath(dist_dir)}")
                print(f"2. 运行程序: LeafAuto.exe")
                print(f"3. 浏览器访问: http://localhost:5000")
                
                return True
            else:
                print("❌ 未找到生成的exe文件")
                return False
        else:
            print("❌ dist目录不存在")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        if e.stderr:
            print("错误信息:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ 打包过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    # 切换到脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    success = build_project()
    
    if success:
        print("\n🎊 项目打包完成!")
        sys.exit(0)
    else:
        print("\n💥 打包失败!")
        sys.exit(1)