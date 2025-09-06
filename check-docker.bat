@echo off
echo ========================================
echo    Docker 安装检查脚本
echo ========================================
echo.

echo [信息] 检查 Docker 安装状态...
echo.

REM 检查 Docker 命令
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] ❌ Docker 未安装或未在 PATH 中
    echo.
    echo 请按照以下步骤安装 Docker:
    echo 1. 下载 Docker Desktop: https://www.docker.com/products/docker-desktop/
    echo 2. 运行安装程序并按照向导完成安装
    echo 3. 安装完成后重启计算机
    echo 4. 运行此脚本再次检查
    echo.
    echo 详细安装指南请查看: DOCKER_INSTALL_GUIDE.md
    pause
    exit /b 1
) else (
    echo [成功] ✅ Docker 已安装
    docker --version
)

echo.

REM 检查 Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [警告] ⚠ Docker Compose 未找到
    echo  Docker Desktop 通常包含 Docker Compose
    echo  请检查 Docker Desktop 安装是否完整
) else (
    echo [成功] ✅ Docker Compose 已安装
    docker-compose --version
)

echo.

REM 检查 Docker 服务状态
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] ❌ Docker 服务未运行
    echo.
    echo 请确保:
    echo 1. Docker Desktop 已启动
    echo 2. 系统托盘中有 Docker 图标
    echo 3. 等待 Docker 服务完全启动
    echo.
    echo 如果问题持续，请尝试:
    echo - 重启 Docker Desktop
    echo - 重启计算机
    echo - 检查虚拟化是否在 BIOS 中启用
) else (
    echo [成功] ✅ Docker 服务正在运行
)

echo.

REM 检查虚拟化
echo [信息] 检查系统虚拟化支持...
systeminfo | find "Virtualization" >nul
if errorlevel 1 (
    echo [警告] ⚠ 无法检测虚拟化状态
    echo  请在 BIOS/UEFI 设置中启用虚拟化
) else (
    systeminfo | find "Virtualization"
)

echo.

REM 测试运行简单容器
echo [信息] 测试运行 Hello World 容器...
docker run --rm hello-world >nul 2>&1
if errorlevel 1 (
    echo [错误] ❌ Docker 运行测试失败
    echo  可能存在权限或配置问题
) else (
    echo [成功] ✅ Docker 运行测试通过
)

echo.
echo ========================================
echo    检查完成
echo ========================================
echo.
echo 下一步建议:
echo 1. 如果所有检查通过，可以运行 docker-start.bat
echo 2. 如果有问题，请查看 DOCKER_INSTALL_GUIDE.md
echo 3. 确保已安装微信客户端（如果需要微信功能）
echo.
pause