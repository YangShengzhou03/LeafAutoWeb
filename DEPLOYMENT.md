# 🐳 LeafAuto_Web Docker & Kubernetes 部署指南

## 📚 容器技术基础

### 什么是 Docker？
Docker 是一个开源的容器化平台，允许开发者将应用程序及其依赖打包到一个轻量级、可移植的容器中。容器包含了运行应用所需的一切：代码、运行时环境、系统工具、系统库和设置。

### 什么是 Kubernetes (k8s)？
Kubernetes（通常简称为 k8s）是一个开源的容器编排系统，用于自动化容器化应用程序的部署、扩展和管理。它可以管理多个容器实例，确保应用的高可用性和弹性。

### Docker 和 Kubernetes 的关系
- **Docker** 负责创建和运行单个容器
- **Kubernetes** 负责管理和编排多个容器实例
- Docker 是容器运行时，Kubernetes 是容器编排平台
- 通常使用 Docker 构建容器镜像，然后使用 Kubernetes 来部署和管理这些容器

### Docker 平台支持
Docker 不仅可以在 Linux 上运行，也完全支持 Windows 和 macOS：

#### Windows 上的 Docker 使用
1. **Docker Desktop for Windows**: 官方提供的 Windows 桌面版本
2. **WSL 2 (Windows Subsystem for Linux)**: 推荐使用 WSL 2 后端以获得更好的性能
3. **Hyper-V**: 传统虚拟化方式
4. **安装方式**:
   ```bash
   # 下载并安装 Docker Desktop for Windows
   # 启用 WSL 2 后端（推荐）
   # 或启用 Hyper-V 功能
   ```

#### Windows 使用示例
```bash
# 在 Windows PowerShell 或 CMD 中运行 Docker 命令
# 与 Linux 命令完全一致
docker --version
docker images
docker ps
docker run hello-world
```

## 🐳 常用 Docker 命令

### 镜像管理
```bash
# 查看本地镜像
docker images
# 拉取镜像
docker pull nginx:latest
# 删除镜像
docker rmi <image_id>
# 构建镜像
docker build -t my-app:latest .
```

### 容器管理
```bash
# 运行容器
docker run -d -p 8080:80 --name my-nginx nginx
# 查看运行中的容器
docker ps
# 查看所有容器（包括已停止的）
docker ps -a
# 停止容器
docker stop <container_id>
# 启动已停止的容器
docker start <container_id>
# 删除容器
docker rm <container_id>
# 进入容器终端
docker exec -it <container_id> /bin/bash
```

### 日志和监控
```bash
# 查看容器日志
docker logs <container_id>
# 实时查看日志
docker logs -f <container_id>
# 查看容器资源使用
docker stats
# 查看容器详细信息
docker inspect <container_id>
```

### 网络和卷管理
```bash
# 查看网络
docker network ls
# 创建网络
docker network create my-network
# 查看卷
docker volume ls
# 创建卷
docker volume create my-volume
```

### Docker Compose 命令
```bash
# 启动服务
docker-compose up -d
# 停止服务
docker-compose down
# 查看服务状态
docker-compose ps
# 查看服务日志
docker-compose logs
# 重新构建镜像
docker-compose build
```

## 📦 部署方式

本文档提供 LeafAuto_Web 项目的 Docker 容器化部署说明。

## 📦 部署方式

### 1. 使用 Docker Compose（推荐）

#### 生产环境部署
```bash
# 克隆项目
git clone https://github.com/YangShengzhou03/LeafAutoWeb.git
cd LeafAutoWeb

# 设置安全密钥
echo "SECRET_KEY=your-production-secret-key" > .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 开发环境部署
```bash
# 使用开发配置
docker-compose -f docker-compose.yml up leafauto-dev
```

### 2. 使用 Docker 直接运行

```bash
# 构建镜像
docker build -t leafauto-web .

# 运行容器
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e SECRET_KEY=your-secret-key \
  --name leafauto-web \
  leafauto-web
```

## 🔧 环境配置

### 必需环境变量

| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `SECRET_KEY` | Flask应用密钥 | 无 | ✅ |
| `FLASK_ENV` | 运行环境 | `production` | ❌ |
| `FLASK_DEBUG` | 调试模式 | `0` | ❌ |

### 可选环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `WECHAT_AUTO_PATH` | 微信自动化路径 | `/app/wechat/WeChat.exe` |
| `API_ONLY` | 仅API模式 | `false` |

## 📁 数据持久化

Docker 容器使用以下卷进行数据持久化：

- `./data` - 应用数据文件（任务、设置等）
- `./logs` - 应用日志文件
- `wechat-data` - 微信相关数据（Docker卷）

## 🚀 服务说明

### leafauto-web（生产服务）
- **端口**: 8080
- **环境**: production
- **特点**: 优化性能，适合生产部署

### leafauto-dev（开发服务）
- **端口**: 8080 (应用), 5678 (调试)
- **环境**: development
- **特点**: 支持热重载，便于开发调试

### leafauto-api（仅API服务）
- **端口**: 5000
- **环境**: production
- **特点**: 仅提供API接口，适合集成部署

## 🔍 健康检查

容器包含健康检查配置，可以通过以下方式验证：

```bash
# 检查服务状态
docker-compose ps

# 查看健康状态
docker inspect --format='{{json .State.Health}}' leafauto-web

# 手动健康检查
curl http://localhost:8080/api/health
```

## 📊 监控和日志

### 查看日志
```bash
# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs leafauto-web

# 查看最近100行日志
docker-compose logs --tail=100
```

### 资源监控
```bash
# 查看容器资源使用
docker stats

# 进入容器
docker-compose exec leafauto-web bash
```

## 🛠 维护操作

### 更新应用
```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

### 备份数据
```bash
# 备份数据文件
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# 从备份恢复
tar -xzf backup-20231201.tar.gz
```

### 故障排除

#### 常见问题

1. **端口冲突**
   ```bash
   # 修改端口映射
docker-compose -p 8081:8080 up -d
   ```

2. **权限问题**
   ```bash
   # 修改文件权限
chmod -R 755 data/ logs/
   ```

3. **构建失败**
   ```bash
   # 清理缓存重建
docker-compose build --no-cache
   ```

## 🔒 安全建议

1. **修改默认密钥**: 生产环境务必修改 `SECRET_KEY`
2. **限制网络访问**: 使用防火墙限制外部访问
3. **定期更新**: 保持Docker镜像和依赖库更新
4. **数据备份**: 定期备份重要数据
5. **日志监控**: 监控异常日志并及时处理

## 📝 版本信息

- **Docker版本**: 要求 Docker 20.10+
- **Docker Compose**: 要求 2.0+
- **基础镜像**: Python 3.7-slim
- **Node.js版本**: 16+

## 🤝 支持

如有部署问题，请参考：
- [项目README](../README.md)
- [Docker文档](https://docs.docker.com/)
- [问题反馈](https://github.com/YangShengzhou03/LeafAutoWeb/issues)

---

*最后更新: 2024年*