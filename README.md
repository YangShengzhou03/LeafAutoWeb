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