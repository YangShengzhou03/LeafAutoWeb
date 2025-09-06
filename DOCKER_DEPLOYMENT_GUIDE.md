# 🐳 LeafAuto Web Docker 部署和使用指南

## 📋 概述

LeafAuto Web 已经提供了完整的 Docker 支持，包括生产环境和开发环境的容器化部署方案。本指南将详细介绍如何使用 Docker 封装和分发项目。

## 🚀 快速开始

### 1. 构建 Docker 镜像

#### 生产环境镜像
```bash
# 在项目根目录执行
docker build -t leafauto-web:latest .
```

#### 开发环境镜像
```bash
docker build -f Dockerfile.dev -t leafauto-web:dev .
```

### 2. 使用 Docker Compose（推荐）

#### 生产环境部署
```bash
# 创建环境变量文件
echo "SECRET_KEY=your-production-secret-key" > .env

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

#### 开发环境部署
```bash
docker-compose -f docker-compose.yml up leafauto-dev
```

## 📦 镜像封装和分发

### 1. 构建完整的发布镜像

```bash
# 构建包含所有依赖的镜像
docker build -t leafauto-web:production .

# 查看镜像大小
docker images leafauto-web
```

### 2. 保存镜像为文件

```bash
# 将镜像保存为tar文件，方便分发
docker save -o leafauto-web.tar leafauto-web:production

# 压缩镜像文件（可选）
gzip leafauto-web.tar
```

### 3. 加载镜像到其他机器

```bash
# 在其他机器上加载镜像
docker load -i leafauto-web.tar

# 或者从压缩文件加载
gunzip -c leafauto-web.tar.gz | docker load
```

## 🔧 环境配置

### 必需的环境变量

创建 `.env` 文件：

```env
# Flask 应用密钥（必需）
SECRET_KEY=your-secret-key-here

# 运行环境
FLASK_ENV=production
FLASK_DEBUG=0

# 微信自动化路径（Docker容器内路径）
WECHAT_AUTO_PATH=/app/wechat/WeChat.exe
```

### 可选的环境变量

```env
# 仅API模式（不包含前端）
API_ONLY=false

# 自定义端口
FLASK_PORT=8080

# 日志级别
LOG_LEVEL=INFO
```

## 📁 数据持久化

### 挂载数据目录

Docker 容器使用以下目录进行数据持久化：

```bash
# 创建本地数据目录
mkdir -p data logs

# 运行容器并挂载数据目录
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v wechat-data:/app/wechat \
  --name leafauto-web \
  leafauto-web:latest
```

### 数据目录说明

- `./data` - 应用数据文件（任务配置、AI设置等）
- `./logs` - 应用日志文件
- `wechat-data` - Docker卷，用于微信相关数据

## 🐳 Docker Compose 配置详解

### 生产环境服务

```yaml
services:
  leafauto-web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - wechat-data:/app/wechat
    restart: unless-stopped
```

### 开发环境服务

```yaml
services:
  leafauto-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8080:8080"
      - "5678:5678"  # 调试端口
    environment:
      - FLASK_ENV=development
    volumes:
      - .:/app  # 代码热重载
      - /app/venv
      - /app/node_modules
    restart: unless-stopped
```

## 🔍 容器管理

### 查看容器状态

```bash
# 查看运行中的容器
docker ps

# 查看所有容器
docker ps -a

# 查看容器日志
docker logs leafauto-web

# 实时查看日志
docker logs -f leafauto-web
```

### 容器操作

```bash
# 启动容器
docker start leafauto-web

# 停止容器
docker stop leafauto-web

# 重启容器
docker restart leafauto-web

# 进入容器终端
docker exec -it leafauto-web /bin/bash

# 删除容器
docker rm leafauto-web
```

## 📊 监控和调试

### 资源监控

```bash
# 查看容器资源使用情况
docker stats leafauto-web

# 查看容器详细信息
docker inspect leafauto-web
```

### 健康检查

容器内置了健康检查机制：

```bash
# 手动执行健康检查
docker exec leafauto-web curl -f http://localhost:8080/api/health
```

## 🚢 分发指南

### 方法一：Docker Hub（推荐）

```bash
# 登录 Docker Hub
docker login

# 标记镜像
docker tag leafauto-web:latest yourusername/leafauto-web:latest

# 推送镜像
docker push yourusername/leafauto-web:latest
```

### 方法二：镜像文件分发

```bash
# 保存镜像
docker save -o leafauto-web.tar leafauto-web:latest

# 在其他机器加载
docker load -i leafauto-web.tar
```

### 方法三：GitHub Packages

```bash
# 标记镜像
docker tag leafauto-web:latest ghcr.io/yourusername/leafauto-web:latest

# 推送镜像
docker push ghcr.io/yourusername/leafauto-web:latest
```

## 🔒 安全建议

### 1. 使用安全的密钥

```bash
# 生成强密钥
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

### 2. 网络安全性

```yaml
# 在docker-compose.yml中限制网络访问
networks:
  leafauto-network:
    internal: true  # 内部网络，不暴露到外部
```

### 3. 资源限制

```yaml
# 限制容器资源使用
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '1'
```

## 🐛 常见问题

### Q: 容器启动失败
A: 检查端口是否被占用，或者查看容器日志：
```bash
docker logs leafauto-web
```

### Q: 数据丢失
A: 确保正确挂载数据卷：
```bash
# 检查挂载情况
docker inspect leafauto-web | grep Mounts
```

### Q: 微信功能异常
A: 确保微信客户端已正确安装，并检查路径配置。

### Q: 性能问题
A: 调整资源限制或使用生产环境配置。

## 📞 支持

如果遇到问题，请检查：
1. Docker 日志：`docker logs leafauto-web`
2. 应用日志：`cat logs/app.log`
3. 数据文件：检查 `data/` 目录下的JSON文件

## 📄 许可证

本项目采用 AGPL v3 许可证。详细信息请查看 LICENSE 文件。

---

💡 **提示**: 在生产环境部署前，请务必：
1. 修改默认的 SECRET_KEY
2. 配置适当的数据备份策略
3. 设置监控和告警机制
4. 定期更新 Docker 镜像以获取安全补丁