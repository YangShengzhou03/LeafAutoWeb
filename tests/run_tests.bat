@echo off
echo ===============================
echo 🌟 LeafAuto_Web 应用测试脚本
echo ===============================

REM 检查Python
echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查虚拟环境
echo 检查虚拟环境...
if not exist "venv" (
    echo ❌ 未找到虚拟环境，正在创建...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo ✅ 虚拟环境创建成功
)

REM 激活虚拟环境并安装依赖
echo 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ 激活虚拟环境失败
    pause
    exit /b 1
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 安装Python依赖失败
    pause
    exit /b 1
)

REM 检查Node.js
echo 检查Node.js环境...
node --version
if %errorlevel% neq 0 (
    echo ❌ 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

REM 安装前端依赖
echo 安装前端依赖...
npm install
if %errorlevel% neq 0 (
    echo ❌ 安装前端依赖失败
    pause
    exit /b 1
)

echo ✅ 所有依赖安装完成！
echo.
echo 运行测试...
echo ===============================
echo 运行基础功能测试...
python test_basic_functionality.py
echo.
echo ===============================
echo 运行完整功能测试...
python test_basic_functionality_complete.py
echo.
echo ===============================
echo 运行应用测试...
python -m pytest test_app.py -v
echo.
echo ✅ 所有测试完成！

pause