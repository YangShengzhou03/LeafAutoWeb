# LeafAuto_Web 测试文件说明

本文件夹包含了LeafAuto_Web项目的所有测试文件，统一管理项目测试相关的内容。

## 文件结构

- `run_tests.bat` - Windows批处理脚本，用于运行所有测试
- `check_code_quality.py` - 代码质量检查脚本，包含代码风格检查和测试运行
- `test_app.py` - 应用层测试，使用pytest框架测试Flask应用的核心功能
- `test_basic_functionality.py` - 基础功能测试脚本，简化版
- `test_basic_functionality_complete.py` - 完整版基础功能测试脚本
- `@AutomationLog.txt` - 自动化测试日志

## 使用方法

### Windows环境

1. 双击运行 `run_tests.bat` 文件，它将自动：
   - 检查Python环境
   - 检查并创建虚拟环境（如果需要）
   - 安装Python依赖
   - 检查Node.js环境
   - 安装前端依赖
   - 运行所有测试脚本

### 手动运行测试

#### 运行基础功能测试
```bash
python test_basic_functionality.py
```

#### 运行完整功能测试
```bash
python test_basic_functionality_complete.py
```

#### 运行应用测试（使用pytest）
```bash
python -m pytest test_app.py -v
```

#### 运行代码质量检查
```bash
python check_code_quality.py
```

代码质量检查脚本会执行以下操作：
- 运行flake8代码风格检查
- 检查代码格式化（black）
- 检查import排序（isort）
- 运行所有测试

## 测试内容

### 基础功能测试
- 数据管理功能测试
- 微信实例功能测试
- Flask应用测试

### 应用测试
- 首页路由重定向测试
- 任务列表API测试
- 微信状态API测试
- 健康检查端点测试

## 注意事项

1. 运行测试前请确保已安装Python 3.7+和Node.js
2. 测试过程中会自动创建虚拟环境并安装依赖
3. 如需单独运行某个测试，请参考上述手动运行测试的方法