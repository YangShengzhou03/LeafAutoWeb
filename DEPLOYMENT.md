# 🐳 LeafAuto_Web Docker 部署指南

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