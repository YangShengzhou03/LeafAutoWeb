@echo off
echo ========================================
echo    LeafAuto Web Docker 启动脚本
echo ========================================
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未安装或未启动
    echo 请先安装 Docker Desktop: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

echo [信息] 检测到 Docker 已安装
echo.

REM 检查环境变量文件
if not exist .env (
    echo [警告] 未找到 .env 文件，正在创建示例配置...
    copy .env.example .env >nul
    echo 请编辑 .env 文件，设置 SECRET_KEY 和其他配置
    echo.
)

REM 检查数据目录
if not exist data (
    echo [信息] 创建数据目录...
    mkdir data
)

if not exist logs (
    echo [信息] 创建日志目录...
    mkdir logs
)

echo.
echo 请选择部署模式：
echo 1. 生产环境 (docker-compose up -d)
echo 2. 开发环境 (docker-compose up leafauto-dev)
echo 3. 仅构建镜像
echo 4. 查看容器状态
echo 5. 查看容器日志
echo 6. 停止所有服务
echo.
set /p choice=请输入选择 (1-6): 

echo.

if "%choice%"=="1" (
    echo [信息] 启动生产环境...
    docker-compose up -d
    echo.
    echo [成功] 生产环境已启动
    echo 访问地址: http://localhost:8080
) else if "%choice%"=="2" (
    echo [信息] 启动开发环境...
    docker-compose up leafauto-dev
) else if "%choice%"=="3" (
    echo [信息] 构建生产镜像...
    docker build -t leafauto-web:latest .
    echo.
    echo [成功] 镜像构建完成
    echo 镜像名称: leafauto-web:latest
) else if "%choice%"=="4" (
    echo [信息] 容器状态：
    docker-compose ps
) else if "%choice%"=="5" (
    echo [信息] 容器日志：
    docker-compose logs -f
) else if "%choice%"=="6" (
    echo [信息] 停止所有服务...
    docker-compose down
    echo.
    echo [成功] 所有服务已停止
) else (
    echo [错误] 无效的选择
)

echo.
echo ========================================
echo    脚本执行完成
echo ========================================
pause