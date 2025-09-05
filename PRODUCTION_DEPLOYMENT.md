# LeafAuto 生产环境部署指南

## 端口配置说明

### 默认端口配置
- **后端Flask服务器**: 5000端口
- **前端Vue服务器**: 8080端口
- **API代理**: 前端通过代理访问后端API (localhost:5000)

### 端口修改方法

#### 后端端口修改
1. 修改启动命令参数：
   ```bash
   python app.py --port <新端口号>
   ```

2. 或者在代码中修改：
   ```python
   app.run(port=<新端口号>)
   ```

#### 前端端口修改
1. 修改启动命令参数：
   ```bash
   npm run serve --port <新端口号>
   ```

2. 或者在 `vue.config.js` 中配置：
   ```javascript
   devServer: {
     port: <新端口号>
   }
   ```

## 启动方式

### 开发环境启动
```bash
python start_app.py
```

### 生产环境启动
```bash
python start_production.py
```

### 手动启动（推荐生产环境）

#### 启动后端
```bash
python app.py --port 5000 --host 0.0.0.0
```

#### 启动前端
```bash
cd frontend
npm run serve --port 8080
```

## 环境要求

- Python 3.8+
- Node.js 14+
- npm 6+

## 安装依赖

### 后端依赖
```bash
pip install -r requirements.txt
```

### 前端依赖
```bash
cd frontend
npm install
```

## 生产环境优化建议

1. **禁用调试模式**: 使用 `--debug` 参数为 `false`
2. **使用生产构建**: 前端使用 `npm run build` 构建生产版本
3. **使用进程管理器**: 推荐使用 pm2 或 supervisor 管理进程
4. **配置反向代理**: 使用 Nginx 或 Apache 作为反向代理
5. **启用HTTPS**: 配置SSL证书启用HTTPS

## 故障排除

### 端口冲突
如果端口被占用，可以：
1. 修改配置文件中的端口号
2. 停止占用端口的进程
3. 使用不同的端口号

### 前端无法访问后端API
检查 `vue.config.js` 中的代理配置：
```javascript
devServer: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000', // 确保与后端端口一致
      changeOrigin: true
    }
  }
}
```

## 监控和维护

- 定期检查日志文件
- 监控系统资源使用情况
- 定期备份数据文件
- 更新依赖包版本