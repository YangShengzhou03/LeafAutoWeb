# 🐳 LeafAuto Web - Docker 部署指南

## 📋 快速开始

### 方式一：使用 Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/YangShengzhou03/LeafAutoWeb.git
cd LeafAutoWeb

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY=your-secret-key-here

# 3. 启动服务
docker-compose up -d

# 4. 访问应用
打开浏览器访问: http://localhost:8080
```

### 方式二：使用提供的脚本

```bash
# 使用启动脚本（Windows）
双击运行 docker-start.bat

# 选择选项 1 启动生产环境
```

### 方式三：直接使用 Docker 命令

```bash
# 构建镜像
docker build -t leafauto-web .

# 运行容器
docker run -d \
  -p 8080:8080 \
  -v ${PWD}/data:/app/data \
  -v ${PWD}/logs:/app/logs \
  -e SECRET_KEY=your-secret-key \
  --name leafauto-web \
  leafauto-web
```

## 🚀 部署模式

### 1. 生产环境
- **端口**: 8080
- **特点**: 优化性能，适合正式部署
- **启动命令**: `docker-compose up -d`

### 2. 开发环境  
- **端口**: 8080 (应用), 5678 (调试)
- **特点**: 支持热重载，便于开发调试
- **启动命令**: `docker-compose up leafauto-dev`

### 3. 仅API模式
- **端口**: 5000
- **特点**: 仅提供API接口，适合集成部署
- **启动命令**: `docker-compose up leafauto-api`

## 📁 目录结构

```
LeafAutoWeb/
├── Dockerfile              # 生产环境Docker配置
├── Dockerfile.dev          # 开发环境Docker配置
├── docker-compose.yml      # Docker Compose配置
├── docker-start.bat        # Windows启动脚本
├── docker-publish.bat      # 镜像发布脚本
├── data/                   # 数据目录（自动创建）
├── logs/                   # 日志目录（自动创建）
├── .env.example           # 环境变量示例
└── README_DOCKER.md       # 本文件
```

## 🔧 环境配置

### 必需配置

创建 `.env` 文件并设置：

```env
# Flask应用密钥（必需）
SECRET_KEY=your-secret-key-here

# 运行环境
FLASK_ENV=production
FLASK_DEBUG=0
```

### 可选配置

```env
# 微信自动化路径
WECHAT_AUTO_PATH=/app/wechat/WeChat.exe

# 仅API模式
API_ONLY=false

# 日志级别
LOG_LEVEL=INFO
```

## 📊 数据持久化

Docker 容器会自动挂载以下目录：

- `./data` - 应用数据（任务配置、AI设置等）
- `./logs` - 应用日志文件
- Docker卷 `wechat-data` - 微信相关数据

## 🔍 容器管理

### 查看状态
```bash
# 查看运行中的容器
docker-compose ps

# 查看容器日志
docker-compose logs

# 实时查看日志
docker-compose logs -f
```

### 常用命令
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 进入容器
docker exec -it leafauto-web /bin/bash
```

## 🚢 镜像分发

### 发布到 Docker Hub

```bash
# 使用发布脚本
双击运行 docker-publish.bat

# 选择选项 3 推送镜像
```

### 手动发布

```bash
# 登录Docker Hub
docker login

# 标记镜像
docker tag leafauto-web:latest username/leafauto-web:latest

# 推送镜像
docker push username/leafauto-web:latest
```

### 保存为文件

```bash
# 保存镜像
docker save -o leafauto-web.tar leafauto-web:latest

# 在其他机器加载
docker load -i leafauto-web.tar
```

## 🐛 常见问题

### Q: 端口冲突
A: 修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "新端口:8080"
```

### Q: 数据丢失
A: 确保数据目录正确挂载，检查：
```bash
docker inspect leafauto-web | grep Mounts
```

### Q: 容器启动失败
A: 查看详细日志：
```bash
docker logs leafauto-web
```

### Q: 微信功能异常
A: 确保微信客户端已安装，并检查路径配置。

## 📞 支持

如果遇到问题：

1. 查看容器日志: `docker-compose logs`
2. 检查应用日志: `cat logs/app.log`
3. 验证数据文件: 检查 `data/` 目录
4. 查看文档: [DOCKER_DEPLOYMENT_GUIDE.md](./DOCKER_DEPLOYMENT_GUIDE.md)

## 📄 许可证

本项目采用 AGPL v3 许可证。详细信息请查看 LICENSE 文件。

---

💡 **提示**: 生产环境部署前请务必：
- 修改默认的 SECRET_KEY
- 配置数据备份策略
- 设置适当的监控和告警