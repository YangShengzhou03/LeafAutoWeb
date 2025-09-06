@echo off
echo ========================================
echo    LeafAuto Web Docker 镜像发布脚本
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

REM 设置默认变量
set IMAGE_NAME=leafauto-web
set DEFAULT_TAG=latest

REM 显示当前镜像信息
echo 当前镜像信息：
docker images %IMAGE_NAME%:*
echo.

echo 请选择操作：
echo 1. 构建新镜像
echo 2. 标记现有镜像
echo 3. 推送镜像到Docker Hub
echo 4. 保存镜像到文件
echo 5. 从文件加载镜像
echo.
set /p choice=请输入选择 (1-5): 

echo.

if "%choice%"=="1" (
    echo [信息] 构建生产镜像...
    
    REM 获取版本号
    set /p version=请输入版本标签 (默认为 latest): 
    if "%version%"=="" set version=%DEFAULT_TAG%
    
    echo 构建镜像: %IMAGE_NAME%:%version%
    docker build -t %IMAGE_NAME%:%version% .
    
    echo.
    echo [成功] 镜像构建完成
    echo 镜像: %IMAGE_NAME%:%version%
    
) else if "%choice%"=="2" (
    echo [信息] 标记镜像...
    
    REM 显示现有镜像
echo 现有镜像：
docker images %IMAGE_NAME%:*
echo.
    
    set /p source_tag=请输入源镜像标签 (如: latest): 
    set /p target_tag=请输入目标标签 (如: v1.0.0): 
    set /p registry=请输入目标仓库 (可选，如: username/): 
    
    if "%registry%"=="" (
        docker tag %IMAGE_NAME%:%source_tag% %IMAGE_NAME%:%target_tag%
        echo 标记: %IMAGE_NAME%:%source_tag% -> %IMAGE_NAME%:%target_tag%
    ) else (
        docker tag %IMAGE_NAME%:%source_tag% %registry%%IMAGE_NAME%:%target_tag%
        echo 标记: %IMAGE_NAME%:%source_tag% -> %registry%%IMAGE_NAME%:%target_tag%
    )
    
    echo.
    echo [成功] 镜像标记完成
    
) else if "%choice%"=="3" (
    echo [信息] 推送镜像到Docker Hub...
    
    REM 检查是否登录
    docker info | find "Username" >nul
    if errorlevel 1 (
        echo [警告] 未检测到Docker登录状态
        echo 请先运行: docker login
        pause
        exit /b 1
    )
    
    set /p image_name=请输入完整镜像名称 (如: username/leafauto-web): 
    set /p tag=请输入标签 (默认为 latest): 
    if "%tag%"=="" set tag=%DEFAULT_TAG%
    
    echo 推送镜像: %image_name%:%tag%
    docker push %image_name%:%tag%
    
    echo.
    echo [成功] 镜像推送完成
    
) else if "%choice%"=="4" (
    echo [信息] 保存镜像到文件...
    
    set /p image_name=请输入镜像名称 (如: leafauto-web:latest): 
    set /p output_file=请输入输出文件名 (默认为 leafauto-web.tar): 
    if "%output_file%"=="" set output_file=leafauto-web.tar
    
    echo 保存镜像: %image_name% -> %output_file%
    docker save -o %output_file% %image_name%
    
    echo.
    echo [成功] 镜像保存完成
    echo 文件: %output_file%
    
) else if "%choice%"=="5" (
    echo [信息] 从文件加载镜像...
    
    set /p input_file=请输入镜像文件名 (如: leafauto-web.tar): 
    
    if not exist "%input_file%" (
        echo [错误] 文件不存在: %input_file%
        pause
        exit /b 1
    )
    
    echo 加载镜像: %input_file%
    docker load -i "%input_file%"
    
    echo.
    echo [成功] 镜像加载完成
    
) else (
    echo [错误] 无效的选择
)

echo.
echo ========================================
echo    脚本执行完成
echo ========================================
pause