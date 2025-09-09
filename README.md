# 🚀 LeafAuto Web - 微信消息自动化管理系统

<div align="center">
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL_v3-blue?style=for-the-badge&logo=gnu" alt="License: AGPL v3">
  </a>
  <a href="https://github.com/YangShengzhou03/LeafAutoWeb">
    <img src="https://img.shields.io/github/stars/YangShengzhou03/LeafAutoWeb?style=for-the-badge&logo=github" alt="GitHub Stars">
  </a>
  <a href="https://github.com/YangShengzhou03/LeafAutoWeb">
    <img src="https://img.shields.io/github/forks/YangShengzhou03/LeafAutoWeb?style=for-the-badge&logo=github" alt="GitHub Forks">
  </a>
  <a href="https://github.com/YangShengzhou03/LeafAutoWeb/issues">
    <img src="https://img.shields.io/github/issues/YangShengzhou03/LeafAutoWeb?style=for-the-badge&logo=github" alt="GitHub Issues">
  </a>
  <a href="https://github.com/YangShengzhou03/LeafAutoWeb/pulls">
    <img src="https://img.shields.io/github/issues-pr/YangShengzhou03/LeafAutoWeb?style=for-the-badge&logo=github" alt="GitHub Pull Requests">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Theme-%231e40af-blue?style=for-the-badge" alt="Theme Color: Klein Blue">
  </a>
  <a href="https://github.com/YangShengzhou03/LeafAutoWeb/commits/main">
    <img src="https://img.shields.io/github/last-commit/YangShengzhou03/LeafAutoWeb?style=for-the-badge&logo=github" alt="Last Commit">
  </a>
</div>

## 📋 目录

- [✨ 项目特色](#-项目特色)
- [🚀 核心功能](#-核心功能)
- [🛠 技术栈](#-技术栈)
- [🏗 系统架构](#-系统架构)
- [📦 快速开始](#-快速开始)
- [🔧 安装指南](#-安装指南)
- [📁 项目结构](#-项目结构)
- [🔌 API 文档](#-api-文档)
- [📄 许可证](#-许可证)

---

## ✨ 项目特色

**LeafAuto Web** 是一款专业的微信消息自动化管理系统，专为需要高效管理微信消息发送的个人和企业用户设计。

### 🎯 解决的核心问题
- **企业用户**：定期向客户发送通知、提醒或营销消息的效率问题
- **个人用户**：自动化生日提醒、节日问候等重复性沟通
- **客服人员**：快速响应常见问题，减轻工作负担

### 💎 核心价值
- 📱 **微信消息自动化**：定时发送任务，解放双手，提高效率
- 🔄 **灵活的重复规则**：支持单次、每日、每周、每月及自定义模式
- 🤖 **AI 自动回复**：智能应对各类咨询，支持多种回复风格
- 📊 **任务管理**：直观查看、编辑和删除自动化任务
- 🔒 **数据安全**：本地部署，数据完全掌控
- 🎨 **现代界面**：采用克莱因蓝主题色，界面美观一致
- ⚡ **优化性能**：清理冗余代码，提升响应速度
- 🔍 **实时监控**：微信状态实时监控，自动重连机制
- 🛡️ **错误处理**：完善的错误处理和重试机制

---

## 🚀 核心功能

### ✅ 已实现功能
- **定时消息发送**：支持具体时间和重复模式设置
- **任务管理**：完整的增删改查功能，状态跟踪
- **数据持久化**：JSON文件存储任务和配置数据
- **前端界面**：Vue 3 + Element Plus现代化管理界面
- **RESTful API**：完整的后端API接口
- **微信自动化**：基于wxautox的消息发送
- **AI自动回复**：配置AI接管消息回复
- **微信状态监控**：30秒间隔自动检查微信连接状态
- **自动重连机制**：微信连接丢失时自动尝试重新初始化
- **线程安全**：数据操作线程安全，避免并发问题
- **详细日志**：完整的操作日志和错误记录

---

## 🛠 技术栈

### 后端技术
- **框架**：Flask 2.2.3
- **数据存储**：JSON文件（线程安全）
- **任务调度**：自定义定时任务调度器
- **微信自动化**：wxautox 3.9.11.17.25b47
- **CORS支持**：flask-cors 4.0.0
- **并发控制**：threading.Lock 确保数据安全
- **状态监控**：后台线程定期检查系统状态
- **错误处理**：统一的错误响应格式和日志记录

### 前端技术
- **框架**：Vue 3 + Composition API
- **UI框架**：Element Plus 2.4.2
- **状态管理**：Pinia 2.1.7
- **路由**：Vue Router 4.0.3
- **构建工具**：Vue CLI 5

### 开发工具
- **代码编辑器**：VS Code / PyCharm
- **版本控制**：Git
- **包管理**：pip + npm

---

## 🏗 系统架构

LeafAuto_Web采用前后端分离架构：

```
前端 (Vue 3) ← HTTP API → 后端 (Flask)
    │                         │
    │                         ├── 任务管理模块 (data_manager.py)
    │                         ├── 定时调度模块 (task_scheduler.py)
    │                         ├── 微信实例模块 (wechat_instance.py)
    │                         ├── AI辅助模块 (ai_worker.py)
    │                         └── 服务器管理模块 (server_manager.py)
    │
    └── 状态管理 (Pinia)
    └── 路由管理 (Vue Router)
    └── UI组件 (Element Plus)
```

---

## 📦 快速开始

### 环境要求
- Python 3.7+
- Node.js 14+
- Windows/macOS/Linux

### 一键启动（Windows）
```bash
# 启动完整应用（前后端）
test_app.bat

# 或仅启动前端服务
test_server.bat
```

访问：http://localhost:8080

---

## 🔧 安装指南

### 方法一：源码安装（推荐）

1. **克隆仓库**
```bash
git clone https://github.com/YangShengzhou03/LeafAutoWeb.git
cd LeafAutoWeb
```

2. **安装后端依赖**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

3. **安装前端依赖**
```bash
npm install
```

4. **初始化数据文件**
```bash
# 数据文件会自动在首次运行时创建
```

5. **运行测试**
```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=.
```

5. **配置环境变量**
```bash
echo 'FLASK_APP=app.py' > .env
echo 'FLASK_ENV=development' >> .env
echo 'SECRET_KEY=your-secret-key-here' >> .env
```

### 生产环境部署

#### 方法一：使用生产启动脚本
```bash
# 启动生产环境（同时启动前后端）
python start_production.py
```

#### 方法二：分别启动前后端
```bash
# 启动后端服务
python start_backend.py

# 启动前端服务（在另一个终端）
python start_frontend.py
```

### 生产环境部署

#### 方法三：Docker部署

LeafAuto Web 提供了完整的 Docker 支持，包括生产环境和开发环境的容器化部署方案。

##### 使用 Docker Compose（推荐）

```bash
# 设置安全密钥
echo "SECRET_KEY=your-production-secret-key" > .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

##### 使用 Docker 直接运行

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

详细部署说明请参考下面的 [Docker 部署指南](#-docker-部署指南) 章节。

---

## 📖 使用说明

### 首次使用

1. **启动应用**
   - 运行 `python start_production.py` 启动完整应用
   - 或分别运行 `python start_backend.py` 和 `python start_frontend.py`

2. **访问应用**
   - 打开浏览器访问 http://localhost:5000
   - 前端开发服务器访问 http://localhost:8080

3. **配置微信**
   - 确保微信客户端已安装并登录
   - 系统会自动检测微信连接状态

### 主要功能使用

#### 定时消息发送
1. 在"定时任务"页面点击"新建任务"
2. 填写接收人、消息内容、发送时间
3. 选择重复模式（单次、每日、每周、每月）
4. 保存任务，系统会自动在指定时间发送

#### AI自动回复
1. 在"AI设置"页面启用AI辅助功能
2. 配置回复延迟、最小回复间隔
3. 设置AI角色和自定义回复规则
4. 选择需要监听的聊天对象

#### 任务管理
- 查看所有定时任务的状态和进度
- 编辑或删除现有任务
- 导出/导入任务数据

### 常见问题

#### 微信连接问题
- 确保微信客户端已安装并正常运行
- 检查微信版本兼容性
- 重启应用或重新登录微信

#### 消息发送失败
- 检查网络连接
- 确认接收人微信号正确
- 查看日志文件获取详细错误信息

#### 性能优化
- 减少同时运行的任务数量
- 调整AI回复延迟时间
- 定期清理历史数据

### 配置文件说明

应用使用 <mcfile name=".env" path="d:\Code\Python\LeafAuto_Web\.env"></mcfile> 文件进行配置，主要配置项：

- `FLASK_ENV`: 运行环境（development/production）
- `FLASK_PORT`: 后端服务端口
- `LOG_LEVEL`: 日志级别
- `SECRET_KEY`: 安全密钥
- `VUE_APP_API_BASE_URL`: 前端API地址

---

## 🔧 故障排除

### 查看日志
应用日志保存在 `logs/` 目录：
- `production.log`: 运行日志
- `error.log`: 错误日志

### 常见错误

#### 依赖缺失
```bash
# 重新安装依赖
pip install -r requirements.txt
npm install
```

#### 端口冲突
```bash
# 修改端口配置
# 在 .env 文件中修改 FLASK_PORT 和前端配置
```

#### 文件权限问题
```bash
# 确保对 data/ 目录有读写权限
chmod 755 data/
```

---

## 📞 支持与贡献

### 问题报告
如遇问题，请提供：
1. 错误日志内容
2. 操作系统和环境信息
3. 复现步骤

### 功能建议
欢迎提交功能建议和改进意见。

### 贡献代码
1. Fork 项目
2. 创建功能分支
3. 提交 Pull Request
4. 确保代码风格一致
5. 添加适当的测试

---

## 📄 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础定时消息功能
- AI自动回复支持
- 现代化管理界面

---

## 🛡️ 安全说明

- 所有数据本地存储，不上传任何信息
- 建议在生产环境修改默认密钥
- 定期备份重要数据
- 关注安全更新和漏洞修复

---

## 📋 版本兼容性

| 组件 | 版本要求 | 备注 |
|------|----------|------|
| Python | 3.7+ | 推荐 3.8+ |
| Node.js | 14+ | 推荐 16+ |
| 微信客户端 | 最新版 | 需要支持COM接口 |
| 操作系统 | Win7+/macOS 10.12+/Linux | |

---

## 🔗 相关资源

- [项目主页](https://github.com/YangShengzhou03/LeafAutoWeb)
- [问题追踪](https://github.com/YangShengzhou03/LeafAutoWeb/issues)
- [讨论区](https://github.com/YangShengzhou03/LeafAutoWeb/discussions)
- [Wiki文档](https://github.com/YangShengzhou03/LeafAutoWeb/wiki)

---

#### 端口配置
- **后端API服务**: 5000端口
- **前端Web服务**: 8080端口
- **API代理**: 前端通过代理访问后端API

#### 启动生产环境
```bash
# 使用生产环境启动脚本
python start_production.py

# 或手动启动
# 启动后端
python app.py --port 5000 --host 0.0.0.0

# 启动前端（在frontend目录）
npm run serve --port 8080
```

详细部署说明请参考 <mcfile name="PRODUCTION_DEPLOYMENT.md" path="d:\Code\Python\LeafAuto_Web\PRODUCTION_DEPLOYMENT.md"></mcfile>

### 方法二：Docker 容器安装

#### 使用 Docker Compose（推荐）
```bash
# 克隆项目
git clone https://github.com/YangShengzhou03/LeafAutoWeb.git
cd LeafAutoWeb

# 设置环境变量
echo "SECRET_KEY=your-secret-key" > .env

# 启动服务
docker-compose up -d

# 访问应用
open http://localhost:8080
```

#### 使用 Docker 直接运行
```bash
# 构建镜像
docker build -t leafauto-web .

# 运行容器
docker run -d -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -e SECRET_KEY=your-secret-key \
  --name leafauto-web \
  leafauto-web
```

详细部署说明请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 方法三：项目完整性验证

运行验证脚本检查所有功能：
```bash
python project_validation.py
```

---

## 📖 使用教程

### 启动应用

1. **启动后端服务**
```bash
python app.py
```

2. **启动前端服务**
```bash
npm run serve
```

3. **访问应用**
打开浏览器访问：http://localhost:8080

### 创建自动化消息任务

1. 点击左侧菜单「自动信息」
2. 填写接收者信息（多个用逗号分隔）
3. 选择发送时间
4. 设置重复选项（可选）
5. 输入消息内容
6. 点击「创建任务」

### 配置 AI 自动回复

1. 点击左侧菜单「AI 接管」
2. 开启「AI 接管状态」
3. 设置回复延迟时间
4. 选择回复风格
5. 设置最大回复长度
6. 配置关键词过滤（可选）
7. 填写回复模板（可选）
8. 点击「保存设置」

### 查看任务统计

1. 点击左侧菜单「统计分析」
2. 查看任务完成率、成功率等指标
3. 查看 AI 回复统计数据
4. 导出统计报告（可选）

---

## 📁 项目结构

```
LeafAuto_Web/
├── app.py                 # Flask应用主文件
├── data_manager.py        # 数据管理模块
├── task_scheduler.py      # 定时任务调度器
├── wechat_instance.py     # 微信实例管理
├── ai_worker.py          # AI自动回复工作线程
├── logging_config.py     # 日志配置模块
├── server_manager.py     # 服务器管理
├── start_app.py          # 应用启动脚本
├── requirements.txt      # Python依赖
├── frontend/             # Vue前端项目
│   ├── package.json
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/
│   │   ├── store/
│   │   └── views/
│   └── vue.config.js
├── data/                 # 数据文件目录
│   ├── data.json         # 任务数据
│   ├── ai_data.json      # AI设置数据
│   ├── home_data.json    # 首页数据
│   └── reply_history.json # 回复历史
├── tests/                # 测试文件
└── logs/                 # 日志目录
```

### 重要文件说明

- **app.py**：Flask后端主应用，提供RESTful API接口
- **data_manager.py**：核心数据管理模块，处理数据持久化操作
- **task_scheduler.py**：定时任务调度器，包含微信消息发送功能
- **project_validation.py**：项目完整性验证脚本
- **start_app.py**：一键启动脚本
- **test_app.bat**：Windows环境启动脚本

---

## 🐳 Docker 部署指南

### 📋 概述

LeafAuto Web 提供了完整的 Docker 支持，包括生产环境和开发环境的容器化部署方案。本指南将详细介绍如何使用 Docker 封装、部署和管理项目。

### 🚀 快速开始

#### 1. 构建 Docker 镜像

##### 生产环境镜像
```bash
# 在项目根目录执行
docker build -t leafauto-web:latest .
```

##### 开发环境镜像
```bash
docker build -f Dockerfile.dev -t leafauto-web:dev .
```

#### 2. 使用 Docker Compose（推荐）

##### 生产环境部署
```bash
# 创建环境变量文件
echo "SECRET_KEY=your-production-secret-key" > .env

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

##### 开发环境部署
```bash
docker-compose -f docker-compose.yml up leafauto-dev
```

### 🔧 环境配置

#### 必需的环境变量

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

#### 可选的环境变量

```env
# 仅API模式（不包含前端）
API_ONLY=false

# 自定义端口
FLASK_PORT=8080

# 日志级别
LOG_LEVEL=INFO
```

### 📁 数据持久化

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

### 📦 镜像封装和分发

#### 构建完整的发布镜像
```bash
# 构建包含所有依赖的镜像
docker build -t leafauto-web:production .

# 查看镜像大小
docker images leafauto-web
```

#### 保存镜像为文件
```bash
# 将镜像保存为tar文件，方便分发
docker save -o leafauto-web.tar leafauto-web:production

# 压缩镜像文件（可选）
gzip leafauto-web.tar
```

#### 加载镜像到其他机器
```bash
# 在其他机器上加载镜像
docker load -i leafauto-web.tar

# 或者从压缩文件加载
gunzip -c leafauto-web.tar.gz | docker load
```

### 🐳 Docker Compose 配置详解

#### 生产环境服务

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

#### 开发环境服务

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

### 🔍 容器管理

#### 查看容器状态

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

#### 容器操作

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

### 📊 监控和调试

#### 资源监控

```bash
# 查看容器资源使用情况
docker stats leafauto-web

# 查看容器详细信息
docker inspect leafauto-web
```

#### 健康检查

容器内置了健康检查机制：

```bash
# 手动执行健康检查
docker exec leafauto-web curl -f http://localhost:8080/api/health
```

### 🚢 分发指南

#### 方法一：Docker Hub（推荐）

```bash
# 登录 Docker Hub
docker login

# 标记镜像
docker tag leafauto-web:latest yourusername/leafauto-web:latest

# 推送镜像
docker push yourusername/leafauto-web:latest
```

#### 方法二：镜像文件分发

```bash
# 保存镜像
docker save -o leafauto-web.tar leafauto-web:latest

# 在其他机器加载
docker load -i leafauto-web.tar
```

#### 方法三：GitHub Packages

```bash
# 标记镜像
docker tag leafauto-web:latest ghcr.io/yourusername/leafauto-web:latest

# 推送镜像
docker push ghcr.io/yourusername/leafauto-web:latest
```

### 🔒 安全建议

#### 1. 使用安全的密钥

```bash
# 生成强密钥
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

#### 2. 网络安全性

```yaml
# 在docker-compose.yml中限制网络访问
networks:
  leafauto-network:
    internal: true  # 内部网络，不暴露到外部
```

#### 3. 资源限制

```yaml
# 限制容器资源使用
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '1'
```

### 🐛 常见问题

#### Q: 容器启动失败
A: 检查端口是否被占用，或者查看容器日志：
```bash
docker logs leafauto-web
```

#### Q: 数据丢失
A: 确保正确挂载数据卷：
```bash
# 检查挂载情况
docker inspect leafauto-web | grep Mounts
```

#### Q: 微信功能异常
A: 确保微信客户端已正确安装，并检查路径配置。

#### Q: 性能问题
A: 调整资源限制或使用生产环境配置。

### 📞 支持

如果遇到问题，请检查：
1. Docker 日志：`docker logs leafauto-web`
2. 应用日志：`cat logs/app.log`
3. 数据文件：检查 `data/` 目录下的JSON文件

---

💡 **提示**: 在生产环境部署前，请务必：
1. 修改默认的 SECRET_KEY
2. 配置适当的数据备份策略
3. 设置监控和告警机制
4. 定期更新 Docker 镜像以获取安全补丁

## ☸️ Kubernetes 部署指南

### 📚 容器技术基础

#### 什么是 Kubernetes (k8s)？
Kubernetes（通常简称为 k8s）是一个开源的容器编排系统，用于自动化容器化应用程序的部署、扩展和管理。它可以管理多个容器实例，确保应用的高可用性和弹性。

#### Docker 和 Kubernetes 的关系
- **Docker** 负责创建和运行单个容器
- **Kubernetes** 负责管理和编排多个容器实例
- Docker 是容器运行时，Kubernetes 是容器编排平台
- 通常使用 Docker 构建容器镜像，然后使用 Kubernetes 来部署和管理这些容器

### 🚀 快速开始

#### 1. 创建 Kubernetes 部署文件

创建 `leafauto-web-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: leafauto-web
  labels:
    app: leafauto-web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: leafauto-web
  template:
    metadata:
      labels:
        app: leafauto-web
    spec:
      containers:
      - name: leafauto-web
        image: leafauto-web:latest
        ports:
        - containerPort: 8080
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: leafauto-secrets
              key: secret-key
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: leafauto-data-pvc
      - name: logs-volume
        persistentVolumeClaim:
          claimName: leafauto-logs-pvc
```

#### 2. 创建服务文件

创建 `leafauto-web-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: leafauto-web-service
spec:
  selector:
    app: leafauto-web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

#### 3. 部署到 Kubernetes

```bash
# 创建命名空间
kubectl create namespace leafauto

# 创建密钥
kubectl create secret generic leafauto-secrets \
  --namespace=leafauto \
  --from-literal=secret-key=your-production-secret-key

# 应用部署
kubectl apply -f leafauto-web-deployment.yaml -n leafauto
kubectl apply -f leafauto-web-service.yaml -n leafauto

# 查看部署状态
kubectl get deployments -n leafauto
kubectl get pods -n leafauto
kubectl get services -n leafauto
```

### 📊 监控和管理

#### 查看资源使用
```bash
# 查看节点资源使用
kubectl top nodes

# 查看Pod资源使用
kubectl top pods -n leafauto

# 查看详细部署信息
kubectl describe deployment leafauto-web -n leafauto
```

#### 日志管理
```bash
# 查看Pod日志
kubectl logs -f deployment/leafauto-web -n leafauto

# 查看所有Pod日志
kubectl logs -f -l app=leafauto-web -n leafauto
```

#### 扩缩容
```bash
# 扩展副本数量
kubectl scale deployment leafauto-web --replicas=5 -n leafauto

# 自动扩缩容（需要Metrics Server）
kubectl autoscale deployment leafauto-web \
  --min=3 \
  --max=10 \
  --cpu-percent=80 \
  -n leafauto
```

### 🔧 高级配置

#### 使用 ConfigMap 管理配置

创建 `leafauto-config.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: leafauto-config
  namespace: leafauto
data:
  flask-env: "production"
  flask-debug: "0"
  log-level: "INFO"
```

#### 使用 Ingress 进行路由

创建 `leafauto-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: leafauto-ingress
  namespace: leafauto
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: leafauto.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: leafauto-web-service
            port:
              number: 80
```

### 🔒 安全最佳实践

#### 使用 Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: leafauto-network-policy
  namespace: leafauto
spec:
  podSelector:
    matchLabels:
      app: leafauto-web
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: leafauto-web
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
```

#### 使用 Resource Quotas

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: leafauto-resource-quota
  namespace: leafauto
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
    services: "10"
```

### 🐛 故障排除

#### 常见问题

**Q: Pod 一直处于 Pending 状态**
A: 检查资源配额和节点资源是否充足

**Q: Pod 不断重启**
A: 检查应用日志和健康检查配置

**Q: 服务无法访问**
A: 检查 Service 和 Ingress 配置

#### 诊断命令

```bash
# 查看事件
kubectl get events -n leafauto

# 查看Pod详细状态
kubectl describe pod <pod-name> -n leafauto

# 进入Pod调试
kubectl exec -it <pod-name> -n leafauto -- /bin/bash

# 端口转发到本地
kubectl port-forward deployment/leafauto-web 8080:8080 -n leafauto
```

### 📚 学习资源

- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [Kubernetes 实战指南](https://kubernetes.io/docs/tutorials/)
- [Kubernetes 最佳实践](https://kubernetes.io/docs/concepts/)

---

🚀 **提示**: 对于生产环境，建议：
1. 使用 Helm 进行包管理
2. 配置监控和告警（Prometheus + Grafana）
3. 设置日志收集（ELK 或 Loki）
4. 实现蓝绿部署或金丝雀发布

## 🔌 API 文档

## 🤖 AI 工作原理详解

### AI 数据看板生成原理

AI 数据看板通过 <mcsymbol name="DataManager" filename="data_manager.py" path="d:\Code\Python\LeafAuto_Web\data_manager.py" startline="1" type="class"></mcsymbol> 类实现，主要包含以下数据收集和处理逻辑：

1. **数据收集机制**：
   - 实时记录所有 AI 回复操作到 <mcfile name="reply_history.json" path="d:\Code\Python\LeafAuto_Web\data\reply_history.json"></mcfile>
   - 统计回复成功率、响应时间、消息类型分布等关键指标
   - 通过定时任务定期聚合数据生成统计报表

2. **看板数据生成流程**：
   ```python
   # 在 data_manager.py 中的实现逻辑
   def calculate_ai_statistics(self):
       """计算AI回复统计数据"""
       history = self.load_reply_history()
       
       # 计算回复率
       total_messages = len(history)
       replied_messages = len([h for h in history if h['status'] == 'replied'])
       reply_rate = (replied_messages / total_messages * 100) if total_messages > 0 else 0
       
       # 计算平均响应时间
       response_times = [h.get('response_time', 0) for h in history if 'response_time' in h]
       avg_response_time = sum(response_times) / len(response_times) if response_times else 0
       
       return {
           'total_messages': total_messages,
           'replied_messages': replied_messages,
           'reply_rate': round(reply_rate, 2),
           'avg_response_time': round(avg_response_time, 2)
       }
   ```

3. **实时更新机制**：
   - 前端通过定时轮询调用 `/api/ai-stats` API 获取最新数据
   - 数据变化时自动触发看板刷新
   - 支持历史数据趋势分析

### 消息发送原理

消息发送功能由 <mcsymbol name="TaskScheduler" filename="task_scheduler.py" path="d:\Code\Python\LeafAuto_Web\task_scheduler.py" startline="1" type="class"></mcsymbol> 类实现：

1. **发送引擎架构**：
   - 基于 wxautox 库实现微信消息发送
   - 使用独立的发送线程避免阻塞主线程
   - 支持同步和异步两种发送模式

2. **发送流程**：
   ```python
   # 在 task_scheduler.py 中的核心发送逻辑
   def send_wechat_message(self, recipient, message):
       """发送微信消息"""
       try:
           # 检查微信实例状态
           if not self.wechat_instance or not self.wechat_instance.is_logged_in():
               self.logger.warning("微信实例未就绪，尝试重新初始化")
               self.initialize_wechat()
           
           # 执行消息发送
           success = self.wechat_instance.send_message(recipient, message)
           
           if success:
               self.logger.info(f"消息发送成功: {recipient} - {message[:50]}...")
               return True
           else:
               self.logger.error(f"消息发送失败: {recipient}")
               return False
               
       except Exception as e:
           self.logger.error(f"发送消息时发生异常: {str(e)}")
           return False
   ```

3. **错误处理机制**：
   - 自动重试机制（最多3次重试）
   - 连接状态监控和自动恢复
   - 详细的错误日志记录

### 等待发送原理

等待发送机制确保消息在正确的时间发送：

1. **时间调度算法**：
   - 使用 Python 的 `threading.Timer` 实现精确定时
   - 支持单次、每日、每周、每月等重复模式
   - 自动处理时区转换和夏令时

2. **任务队列管理**：
   ```python
   # 在 task_scheduler.py 中的等待逻辑
   def schedule_task(self, task):
       """调度任务到指定时间执行"""
       now = datetime.now()
       send_time = datetime.fromisoformat(task['sendTime'])
       
       # 计算等待时间（秒）
       wait_seconds = (send_time - now).total_seconds()
       
       if wait_seconds <= 0:
           # 立即执行过期任务
           self.execute_task(task)
       else:
           # 创建定时器
           timer = threading.Timer(wait_seconds, self.execute_task, args=[task])
           timer.start()
           
           # 存储定时器引用用于后续管理
           self.active_timers[task['id']] = timer
   ```

3. **内存和持久化优化**：
   - 使用轻量级数据结构存储定时任务
   - 支持应用重启后任务恢复
   - 避免内存泄漏的定时器清理机制

### AI 接管原理

AI 接管功能通过 <mcsymbol name="AIWorker" filename="ai_worker.py" path="d:\Code\Python\LeafAuto_Web\ai_worker.py" startline="1" type="class"></mcsymbol> 类实现：

1. **消息监听和处理流水线**：
   - 实时监控微信消息流入
   - 基于规则的消息过滤和分类
   - 智能回复策略选择

2. **AI 回复生成流程**：
   ```python
   # 在 ai_worker.py 中的核心处理逻辑
   def process_incoming_message(self, sender, message):
       """处理 incoming 消息并生成回复"""
       
       # 1. 消息预处理和过滤
       if not self.should_reply(sender, message):
           return None
       
       # 2. 回复延迟控制
       time.sleep(self.reply_delay)
       
       # 3. AI 回复生成
       reply_content = self.generate_ai_reply(message)
       
       # 4. 回复发送和执行
       success = self.send_reply(sender, reply_content)
       
       # 5. 记录历史
       self.record_reply_history(sender, message, reply_content, success)
       
       return success
   ```

3. **智能过滤规则**：
   - 关键词黑名单/白名单过滤
   - 发送频率限制（防骚扰）
   - 特定联系人专属处理
   - @消息优先处理机制

4. **性能优化特性**：
   - 异步消息处理避免阻塞
   - 内存缓存频繁使用的回复模板
   - 连接池管理优化网络请求

## 🔌 API 文档

### 任务管理 API

#### 获取所有任务
```http
GET /api/tasks
```

#### 添加新任务
```http
POST /api/tasks
Content-Type: application/json

{
  "recipient": "好友昵称",
  "messageContent": "消息内容",
  "sendTime": "2023-12-01T10:00:00",
  "repeatType": "daily"
}
```

#### 删除任务
```http
DELETE /api/tasks/{task_id}
```

#### 更新任务状态
```http
PATCH /api/tasks/{task_id}/status
Content-Type: application/json

{
  "status": "completed"
}
```

#### 清空所有任务
```http
DELETE /api/tasks
```

#### 导入任务
```http
POST /api/tasks/import
Content-Type: application/json

[
  {
    "recipient": "好友1",
    "messageContent": "消息1",
    "sendTime": "2023-12-01T10:00:00"
  },
  {
    "recipient": "好友2", 
    "messageContent": "消息2",
    "sendTime": "2023-12-01T11:00:00"
  }
]
```

### AI设置 API

#### 获取AI设置
```http
GET /api/ai-settings
```

#### 保存AI设置
```http
POST /api/ai-settings
Content-Type: application/json

{
  "aiStatus": true,
  "contactPerson": "联系人",
  "aiPersona": "你很温馨,回复简单明了。",
  "onlyAt": false,
  "replyDelay": 5,
  "minReplyInterval": 60
}
```

#### 获取AI回复历史
```http
GET /api/ai-history
```

#### 添加AI回复历史
```http
POST /api/ai-history
Content-Type: application/json

{
  "sender": "发送者",
  "message": "原始消息",
  "reply": "回复内容",
  "status": "replied"
}
```

### 微信状态 API

#### 获取微信状态
```http
GET /api/wechat-status
```

---

## 🧪 项目验证

项目包含完整的验证和测试体系，确保系统稳定可靠：

### 验证包结构
项目验证功能已重构为独立的 `validation` 包，提供更清晰的组织结构：

```bash
LeafAuto_Web/validation/
├── __init__.py           # 包初始化，导出所有验证功能
├── final_validation.py   # 项目验证脚本，检查项目结构、Python功能、前端功能和用户体验
├── scheduler_validation.py # 调度器功能验证，演示动态间隔调整、错误恢复和性能监控
├── robustness_testing.py # 调度器鲁棒性测试，验证系统在异常情况下的稳定性
├── setup.py              # 包安装配置，支持独立安装验证工具
└── README.md             # 包说明文档
```

### 使用方式
```python
# 导入验证包
from validation import validate_project_structure, demonstrate_dynamic_interval

# 运行项目验证
validate_project_structure()

# 运行调度器验证
demonstrate_dynamic_interval()
```

### 测试套件
- **test_app.py**：应用层测试，验证API接口和核心功能
- **test_basic.py**：基础测试，验证数据文件、JSON有效性和依赖安装
- **test_data_manager.py**：数据管理测试，验证数据加载、保存和各类操作

### 运行验证
```bash
# 运行所有验证
python -c "from validation import main; main()"

# 运行特定验证
python -c "from validation import validate_project_structure; validate_project_structure()"

# 运行所有测试
pytest
```

---

## 📊 开发状态

### ✅ 已实现功能
- 任务管理核心功能（增删改查）
- AI设置基础功能
- 数据持久化（JSON文件）
- 前端界面所有页面组件
- API基础CRUD操作
- 项目完整性验证系统

### 🚧 开发中功能
- 用户认证系统（JWT）
- 会员等级管理
- 数据统计面板
- 微信实际集成
- 数据库支持

### 📅 规划功能
- 消息模板管理系统
- 多语言支持
- 高级统计分析
- 移动端适配
- 第三方集成

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. **Fork 项目**
2. **创建特性分支**：`git checkout -b feature/AmazingFeature`
3. **提交更改**：`git commit -m 'Add some AmazingFeature'`
4. **推送到分支**：`git push origin feature/AmazingFeature`
5. **提交 Pull Request**

### 开发规范
- 遵循PEP 8 Python代码规范
- 使用有意义的提交信息
- 添加适当的注释和文档
- 确保代码通过所有测试

---

## 🚀 Next（下一步计划）

### 1. 报告生成
基于聊天记录内容，自动生成日报、周报和月报，帮助用户快速了解群聊活动概况和重要信息。

### 2. 数据提取与汇总
根据预设的信息模板，从聊天记录中提取关键数据并进行汇总分析，为决策提供数据支持。

### 3. 知识库构建
收集整理聊天记录内容，构建AI知识库数据集，用于支持AI问答功能，提升信息检索效率。

### 4. 舆情监控
实时监控群聊内容，及时发现和处理不当言论，帮助群主有效管理群组，避免潜在风险。

> 戴敏：现在都是群主负责制，有违法的事情跟着倒霉。

## 📦 Windows 打包版本使用指南

LeafAuto Web 提供了完整的 Windows 打包版本，无需安装 Python 和 Node.js 环境即可直接运行。

### 🖥️ 系统要求
- **操作系统**: Windows 10 或更高版本
- **内存**: 至少 4GB RAM
- **磁盘空间**: 至少 500MB 可用空间
- **微信客户端**: 已安装并登录微信

### 📥 安装步骤

#### 1. 下载和解压
1. 下载 LeafAuto Web 打包文件（ZIP 格式）
2. 解压到任意目录，建议不要放在系统盘（如 `D:\LeafAutoWeb`）
3. 确保解压后的目录结构完整

#### 2. 启动应用程序
有三种启动方式：

##### 方法一：使用快捷方式（推荐）
- 找到并双击 `LeafAuto Web.lnk` 快捷方式
- 系统会自动启动前后端服务
- 等待控制台窗口显示启动完成信息

##### 方法二：使用批处理文件
- 双击 `start_both.bat` 文件
- 会打开两个命令行窗口分别运行前后端
- 等待服务完全启动

##### 方法三：手动启动
```bash
# 启动后端服务（在 LeafAutoBackend 目录）
LeafAutoBackend.exe

# 启动前端服务（在 LeafAutoFrontend 目录，另一个命令行）
LeafAutoFrontend.exe
```

#### 3. 访问应用
- 打开浏览器访问：http://localhost:8080
- 如果端口被占用，会自动使用其他可用端口
- 查看控制台输出确认实际访问地址

### ⚙️ 端口配置

#### 默认端口
- **前端服务**: 8080 端口
- **后端API**: 5000 端口

#### 修改端口
如果默认端口被占用，可以修改配置文件：

1. **修改前端端口**：
   - 编辑 `LeafAutoFrontend\vue.config.js` 文件
   - 修改 `port` 配置项

2. **修改后端端口**：
   - 编辑 `LeafAutoBackend\.env` 文件
   - 修改 `FLASK_PORT` 配置项

### 🐛 故障排除

#### 1. 端口占用问题
**症状**: 服务启动失败，提示端口被占用
**解决方案**:
- 关闭占用端口的其他程序
- 或修改应用的端口配置
- 或使用 `netstat -ano | findstr :8080` 查找占用进程

#### 2. 服务启动失败
**症状**: 控制台显示错误信息后退出
**解决方案**:
- 检查系统是否满足要求
- 确保微信客户端已安装
- 查看 `logs\` 目录下的错误日志

#### 3. 微信连接问题
**症状**: 微信状态显示未连接
**解决方案**:
- 确保微信客户端已登录
- 检查微信安装路径是否正确
- 重启微信和应用

#### 4. 文件权限问题
**症状**: 无法保存数据或记录日志
**解决方案**:
- 以管理员身份运行应用程序
- 或修改安装目录的权限设置

### ⏹️ 停止服务

#### 正常停止
- 关闭所有打开的命令行窗口
- 或使用任务管理器结束相关进程

#### 进程名称
- 后端服务: `LeafAutoBackend.exe`
- 前端服务: `LeafAutoFrontend.exe`
- 可能的 Python 解释器进程

### 📁 目录结构

打包版本包含以下主要目录：
```
LeafAutoWeb/
├── LeafAutoBackend/          # 后端服务
│   ├── LeafAutoBackend.exe   # 后端可执行文件
│   ├── *.dll                # 依赖库文件
│   └── .env                 # 后端配置
├── LeafAutoFrontend/         # 前端服务
│   ├── LeafAutoFrontend.exe # 前端可执行文件
│   ├── dist/                # 前端构建文件
│   └── vue.config.js        # 前端配置
├── data/                    # 数据文件目录
├── logs/                    # 日志文件目录
├── LeafAuto Web.lnk         # 快捷方式
├── start_both.bat          # 启动脚本
└── 打包使用说明.md          # 使用说明文档
```

### 📋 技术支持

如果遇到问题，请提供以下信息：
1. 操作系统版本和架构（32位/64位）
2. 错误日志内容（在 `logs/` 目录）
3. 问题复现步骤
4. 截图或屏幕录制

### 🔄 更新版本

更新到新版本时：
1. 备份 `data/` 目录中的重要数据
2. 停止当前运行的服务
3. 解压新版本到新目录
4. 恢复数据文件
5. 启动新版本服务

## 📈 Next（下一步计划）

我们计划在未来版本中实现以下功能，进一步提升 LeafAuto Web 的价值和实用性：

### 1. 报告生成
基于聊天记录内容，自动生成日报、周报和月报。
- **智能摘要**：自动提取关键信息，生成简洁的工作报告
- **多格式导出**：支持PDF、Word、Excel等多种格式
- **定时发送**：可设置自动将报告发送给指定联系人
- **自定义模板**：支持用户自定义报告格式和内容

### 2. 数据提取与汇总
根据预设的信息模板，从聊天记录中提取关键数据并进行汇总分析。
- **关键词提取**：自动识别和提取重要信息
- **数据分类**：按类型、时间、联系人等多维度分类
- **趋势分析**：生成数据变化趋势图表
- **异常检测**：自动识别数据中的异常情况并提醒

### 3. 知识库构建
收集整理聊天记录内容，构建AI知识库数据集，用于支持AI问答功能。
- **自动整理**：智能分类和组织聊天内容
- **知识图谱**：构建信息之间的关联关系
- **智能检索**：快速查找历史聊天记录中的相关信息
- **AI训练**：基于历史数据优化AI回复质量

### 4. 舆情监控
实时监控群聊内容，及时发现和处理不当言论。
- **敏感词过滤**：自动识别和标记敏感内容
- **情绪分析**：分析群聊情绪变化趋势
- **实时提醒**：发现异常情况立即通知群主
- **风险预警**：对可能引发问题的内容提前预警

> **特别说明**：舆情监控功能对于群主尤为重要，可以帮助群主及时发现和处理群内的不当言论，避免因群成员违规行为而承担连带责任。

---

## 🔮 下一步计划 (Next)

我们正在规划以下功能，以进一步提升 LeafAuto Web 的价值和实用性：

### 📊 报告生成
- **日报、周报、月报自动生成**：基于聊天记录内容，智能分析并生成格式化的定期报告
- **自定义报告模板**：支持用户自定义报告格式和内容重点
- **定时推送功能**：自动将生成的报告发送给指定联系人或群组

### 📈 数据提取与汇总
- **关键信息提取**：根据预设的信息模板，从聊天记录中智能提取关键数据
- **多维度分析**：对提取的数据进行汇总分析，生成可视化图表和统计信息
- **趋势预测**：基于历史数据分析，提供趋势预测和决策支持

### 🧠 知识库构建
- **聊天记录整理**：自动收集整理聊天记录内容，构建结构化知识库
- **AI问答支持**：基于知识库数据集，提供智能问答功能
- **知识图谱**：构建聊天内容的知识图谱，展示信息间的关联关系

### 🚨 舆情监控
- **敏感内容检测**：实时监控群聊中的敏感或不当内容，及时提醒群主
- **风险预警**：对可能引起法律风险或纠纷的言论进行预警
- **群主责任制支持**：提供群主管理辅助工具，帮助群主履行管理责任，避免因群成员不当言论而承担连带责任

> **群主特别关注**：正如用户戴敏所言，"现在都是群主负责制，有违法的事情跟着倒霉..."。我们的舆情监控功能将帮助群主及时发现并处理群内不当言论，降低管理风险。

---

## 📄 许可证

本项目采用 **AGPL-3.0** 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 📞 联系方式

- **项目作者**：YangShengzhou03
- **GitHub**：[https://github.com/YangShengzhou03/LeafAutoWeb](https://github.com/YangShengzhou03/LeafAutoWeb)
- **问题反馈**：[创建Issue](https://github.com/YangShengzhou03/LeafAutoWeb/issues)
- **功能请求**：[提交Feature Request](https://github.com/YangShengzhou03/LeafAutoWeb/issues/new?template=feature_request.md)

---

## ⭐ 支持项目

如果这个项目对您有帮助，请给它一个星标！您的支持是我们持续改进的动力！

⭐ **Star 增长趋势** - 见证项目的成长历程：
[![Star History Chart](https://api.star-history.com/svg?repos=YangShengzhou03/LeafAutoWeb&type=Date)](https://star-history.com/#YangShengzhou03/LeafAutoWeb&Date)

💝 **如何支持项目**：
- ⭐ 给项目一个 Star
- 🐛 提交 Issue 报告问题
- 💡 提出功能建议
- 🔧 贡献代码改进
- 📢 分享给更多开发者

感谢您的支持，让我们一起打造更好的微信自动化工具！🚀