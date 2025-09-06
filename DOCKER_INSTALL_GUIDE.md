# 🐳 Docker 安装和配置指南

## 📋 概述

本指南将帮助您在 Windows 系统上安装和配置 Docker，以便能够使用 LeafAuto Web 的容器化部署。

## 🚀 Windows Docker 安装

### 系统要求
- Windows 10 64位：专业版、企业版或教育版（Build 15063或更高版本）
- Windows 11 64位：家庭版或更高版本
- 启用虚拟化（BIOS/UEFI设置中）
- 至少 4GB RAM

### 安装步骤

#### 方法一：Docker Desktop for Windows（推荐）

1. **下载 Docker Desktop**
   - 访问: https://www.docker.com/products/docker-desktop/
   - 下载 Windows 版本

2. **运行安装程序**
   - 双击下载的 `Docker Desktop Installer.exe`
   - 按照安装向导完成安装

3. **启用 WSL 2（推荐）**
   - 安装过程中选择 "Enable WSL 2 Features"
   - 或者手动启用：
     ```powershell
     # 以管理员身份运行 PowerShell
     dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
     dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
     ```

4. **重启电脑**
   - 安装完成后需要重启计算机

5. **验证安装**
   ```powershell
   # 打开 PowerShell 或 CMD
   docker --version
   docker-compose --version
   ```

#### 方法二：使用 Winget（Windows 包管理器）

```powershell
# 安装 Winget（如果尚未安装）
# 从 Microsoft Store 安装 "App Installer"

# 使用 Winget 安装 Docker Desktop
winget install Docker.DockerDesktop
```

#### 方法三：Chocolatey 包管理器

```powershell
# 安装 Chocolatey（如果尚未安装）
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 使用 Chocolatey 安装 Docker Desktop
choco install docker-desktop -y
```

## 🔧 安装后配置

### 1. 启动 Docker Desktop
- 在开始菜单中搜索 "Docker Desktop" 并启动
- 或者使用命令：
  ```powershell
  # 启动 Docker Desktop
  Start-Process "Docker Desktop"
  ```

### 2. 配置 Docker
- 右键点击系统托盘中的 Docker 图标
- 选择 "Settings"
- 推荐配置：
  - **General**: 启用 "Start Docker Desktop when you log in"
  - **Resources**: 分配适当的 CPU 和内存资源
  - **Docker Engine**: 配置镜像加速器（可选）

### 3. 验证安装
```powershell
# 检查 Docker 版本
docker --version
# 输出示例: Docker version 20.10.12, build e91ed57

docker-compose --version
# 输出示例: docker-compose version 1.29.2, build 5becea4c

# 运行测试容器
docker run hello-world
```

## 🐳 WSL 2 配置（可选但推荐）

### 启用 WSL 2
```powershell
# 以管理员身份运行 PowerShell

# 启用 WSL 功能
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机平台功能
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启计算机
Restart-Computer
```

### 安装 WSL 2 内核更新
1. 下载: https://aka.ms/wsl2kernel
2. 运行安装程序

### 设置 WSL 2 为默认版本
```powershell
wsl --set-default-version 2
```

### 安装 Linux 发行版
```powershell
# 查看可用发行版
wsl --list --online

# 安装 Ubuntu（推荐）
wsl --install -d Ubuntu

# 或者手动安装
wsl --install -d Ubuntu-20.04
```

## 🔍 故障排除

### 常见问题 1: Docker 命令找不到
```powershell
# 检查 Docker 是否在 PATH 中
Get-Command docker -ErrorAction SilentlyContinue

# 如果找不到，手动添加到 PATH
# Docker 通常安装在: C:\Program Files\Docker\Docker\resources\bin
$env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
```

### 常见问题 2: 虚拟化未启用
1. 重启电脑进入 BIOS/UEFI 设置
2. 找到虚拟化设置（通常称为 Intel VT-x 或 AMD-V）
3. 启用虚拟化功能
4. 保存设置并重启

### 常见问题 3: WSL 2 安装失败
```powershell
# 检查 WSL 状态
wsl --status

# 如果出现问题，尝试重置
wsl --unregister Ubuntu
wsl --install -d Ubuntu
```

### 常见问题 4: 端口冲突
```powershell
# 检查端口占用
netstat -ano | findstr :8080

# 终止占用进程（谨慎操作）
taskkill /PID <进程ID> /F
```

## 📊 性能优化

### Docker Desktop 设置
1. 右键点击系统托盘 Docker 图标 → Settings
2. **Resources** 标签页：
   - CPUs: 分配 4-8 个核心
   - Memory: 分配 4-8GB RAM
   - Disk image size: 至少 64GB

### WSL 2 优化
```bash
# 在 WSL 2 中创建配置文件
sudo nano /etc/wsl.conf

# 添加以下内容
[automount]
enabled = true
options = "metadata,umask=22,fmask=11"
mountFsTab = false

[network]
generateHosts = true
generateResolvConf = true

[interop]
enabled = true
appendWindowsPath = true

[boot]
systemd = true
```

## 🚀 验证 LeafAuto Web 部署

安装完成后，测试 Docker 部署：

```powershell
# 进入项目目录
cd D:\Code\Python\LeafAuto_Web

# 构建测试镜像
docker build -t leafauto-web-test .

# 运行测试容器
docker run -it --rm leafauto-web-test python --version

# 检查 Docker Compose
docker-compose --version
```

## 📞 支持资源

### 官方文档
- Docker Desktop for Windows: https://docs.docker.com/desktop/windows/
- WSL 2 文档: https://docs.microsoft.com/windows/wsl/

### 社区支持
- Docker 社区论坛: https://forums.docker.com/
- Stack Overflow: https://stackoverflow.com/questions/tagged/docker

### 故障排除
- Docker 官方故障排除指南: https://docs.docker.com/desktop/troubleshoot/overview/
- WSL 故障排除: https://docs.microsoft.com/windows/wsl/troubleshooting

---

💡 **提示**: 安装完成后，请运行 `docker-start.bat` 来部署 LeafAuto Web 应用。