"""
Flask应用主模块

提供微信消息自动化管理系统的RESTful API接口，包括任务管理、AI设置、微信状态监控等功能。

主要功能：
- 定时任务管理API
- AI自动回复配置API  
- 微信状态监控API
- 前后端路由转发
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory, send_file
from flask_cors import CORS

from ai_worker import AiWorkerManager, WorkerConfig
from data_manager import (add_ai_history, add_task, clear_tasks, delete_task,
                          get_ai_stats, import_tasks, load_ai_data,
                          load_home_data, load_reply_history, load_tasks,
                          save_ai_settings, save_reply_history, update_task_status)
from logging_config import get_logger


# 辅助函数：根据原始消息和目标内容生成基于结构的正则表达式
def generate_structure_based_regex(original_message, target_items):
    """生成能够捕获相似结构但不同内容的正则表达式"""
    try:
        # 找到目标内容在原始消息中的位置
        positions = []
        for item in target_items:
            start_pos = original_message.find(item)
            if start_pos != -1:
                positions.append((item, start_pos, start_pos + len(item)))
        
        # 按位置排序
        positions.sort(key=lambda x: x[1])
        
        if not positions:
            return None
        
        # 构建正则表达式，保留目标内容前后的上下文
        regex_parts = []
        last_end = 0
        
        for i, (item, start, end) in enumerate(positions):
            # 添加目标内容前的上下文
            prefix = original_message[last_end:start]
            if prefix:
                regex_parts.append(re.escape(prefix))
            
            # 对于目标内容，使用捕获组并允许匹配任何内容
            # 根据用户需求，我们需要更灵活的匹配模式
            if item.isdigit():
                # 数字使用\d+匹配
                regex_parts.append("(\\d+)")
            else:
                # 非数字使用.*?匹配，这样可以捕获任何字符（非贪婪模式）
                regex_parts.append("(.*?)")
            
            last_end = end
        
        # 添加最后一个目标内容后的上下文
        suffix = original_message[last_end:]
        if suffix:
            regex_parts.append(re.escape(suffix))
        
        # 组合成完整的正则表达式
        regex_pattern = ''.join(regex_parts)
        
        # 为了提高匹配的准确性，添加开始和结束标记
        if regex_pattern:
            regex_pattern = "^" + regex_pattern + "$"
        
        return regex_pattern
    except Exception as e:
        logger.error(f"生成结构型正则表达式失败: {e}")
        return None

# 辅助函数：使用正则表达式从消息中提取值
def extract_values_with_regex(message, regex_pattern):
    """使用正则表达式从消息中提取值"""
    try:
        extracted_values = {}
        
        # 使用正则表达式匹配
        match = re.search(regex_pattern, message)
        if match:
            # 提取所有捕获组的值
            for i, value in enumerate(match.groups(), 1):
                extracted_values[f"项目{i}"] = value
        
        return extracted_values
    except Exception as e:
        logger.error(f"提取值失败: {e}")
        return {}
from task_scheduler import (start_task_scheduler, stop_task_scheduler,
                            task_scheduler)
from wechat_instance import (get_status_info, get_wechat_instance,
                             is_wechat_online, start_status_monitor, diagnose_com_error)

# 创建Flask应用实例
app = Flask(__name__)
CORS(app)

# 初始化日志器
logger = get_logger(__name__)

# 启动时加载数据
load_tasks()
load_ai_data()
load_reply_history()

# 启动微信状态监控
start_status_monitor()
logger.info("微信状态监控已启动")

# 启动时初始化群聊管理配置状态为false
import json
import os
from group_manager import data_dir
try:
    config_file = os.path.join(data_dir, "group_manage.json")
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保management_enabled为false
        config["management_enabled"] = False
        config["data_collection_enabled"] = False
        config["sentiment_monitoring_enabled"] = False
        
        # 保存更新后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logger.info("已初始化群聊管理配置状态为false")
    else:
        # 如果配置文件不存在，创建默认配置
        default_config = {
            "_comment": "群聊管理配置文件",
            "settings": {
                "default": {
                    "record_interval": 0,
                    "sensitive_words": []
                }
            },
            "management_enabled": False,
            "data_collection_enabled": False,
            "sentiment_monitoring_enabled": False,
            "group": "",
            "version": "1.0"
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        logger.info("已创建默认群聊管理配置文件，状态为false")
except Exception as e:
    logger.error(f"初始化群聊管理配置失败: {e}")

# 设置微信实例到群聊管理器
try:
    from group_manager import set_wechat_instance
    wx_instance = get_wechat_instance()
    if wx_instance:
        set_wechat_instance(wx_instance)
        logger.info("已设置微信实例到群聊管理器")
    else:
        logger.warning("无法获取微信实例，群聊管理功能可能无法正常工作")
except Exception as e:
    logger.error(f"设置微信实例到群聊管理器失败: {e}")

ai_data = load_ai_data()
ai_data["aiStatus"] = False
save_ai_settings(ai_data)


# 添加静态文件服务配置
def is_frozen():
    """检查是否在打包环境中运行"""
    return getattr(sys, 'frozen', False)

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if is_frozen():
        # 在打包环境中，资源文件在_MEIPASS文件夹中
        base_path = Path(sys._MEIPASS)
    else:
        # 在开发环境中，使用项目根目录
        base_path = Path(__file__).parent
    return base_path / relative_path

# 配置静态文件服务
if is_frozen():
    # 在打包环境中，检查前端构建文件是否存在
    frontend_dist_path = get_resource_path('frontend/dist')
    if frontend_dist_path.exists():
        logger.info(f"检测到前端构建文件已存在于: {frontend_dist_path}")
        # 配置静态文件路由
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_static(path):
            if path == "":
                return send_from_directory(str(frontend_dist_path), 'index.html')
            
            file_path = frontend_dist_path / path
            if file_path.exists() and file_path.is_file():
                return send_from_directory(str(frontend_dist_path), path)
            else:
                # 如果文件不存在，返回index.html以支持前端路由
                return send_from_directory(str(frontend_dist_path), 'index.html')
        
        logger.info("已配置静态文件服务")
    else:
        logger.warning(f"未找到前端构建文件: {frontend_dist_path}")


# 统一错误处理装饰器
def handle_api_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API Error in {func.__name__}: {e}")
            return jsonify({"success": False, "error": str(e)}), 500

    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/")
def home():
    """
    首页路由
    在开发环境中重定向到前端页面，在生产环境中提供静态文件服务

    Returns:
        Response: 重定向到前端首页或提供静态文件
    """
    if is_frozen():
        # 在打包环境中，提供静态文件服务
        frontend_dist_path = get_resource_path('frontend/dist')
        if frontend_dist_path.exists():
            return send_from_directory(str(frontend_dist_path), 'index.html')
        else:
            return "前端文件未找到，请确保前端文件已正确打包", 500
    else:
        # 在开发环境中，重定向到前端开发服务器
        return redirect("http://localhost:8080")


@app.route("/auto-info")
def auto_info():
    """
    自动信息页面路由
    在开发环境中重定向到前端页面，在生产环境中提供静态文件服务

    Returns:
        Response: 重定向到前端自动信息页面或提供静态文件
    """
    if is_frozen():
        # 在打包环境中，提供静态文件服务
        frontend_dist_path = get_resource_path('frontend/dist')
        if frontend_dist_path.exists():
            return send_from_directory(str(frontend_dist_path), 'index.html')
        else:
            return "前端文件未找到，请确保前端文件已正确打包", 500
    else:
        # 在开发环境中，重定向到前端开发服务器
        return redirect("http://localhost:8080/auto_info")


@app.route("/ai-takeover")
def ai_takeover():
    """
    AI接管页面路由
    在开发环境中重定向到前端页面，在生产环境中提供静态文件服务

    Returns:
        Response: 重定向到前端AI接管页面或提供静态文件
    """
    if is_frozen():
        # 在打包环境中，提供静态文件服务
        frontend_dist_path = get_resource_path('frontend/dist')
        if frontend_dist_path.exists():
            return send_from_directory(str(frontend_dist_path), 'index.html')
        else:
            return "前端文件未找到，请确保前端文件已正确打包", 500
    else:
        # 在开发环境中，重定向到前端开发服务器
        return redirect("http://localhost:8080/ai_takeover")


@app.route("/other_box")
def other_box():
    """
    其他功能页面路由
    在开发环境中重定向到前端页面，在生产环境中提供静态文件服务

    Returns:
        Response: 重定向到前端其他功能页面或提供静态文件
    """
    if is_frozen():
        # 在打包环境中，提供静态文件服务
        frontend_dist_path = get_resource_path('frontend/dist')
        if frontend_dist_path.exists():
            return send_from_directory(str(frontend_dist_path), 'index.html')
        else:
            return "前端文件未找到，请确保前端文件已正确打包", 500
    else:
        # 在开发环境中，重定向到前端开发服务器
        return redirect("http://localhost:8080/other_box")


@app.route("/group_manager")
def group_manager():
    """
    群聊管家页面路由
    在开发环境中重定向到前端页面，在生产环境中提供静态文件服务

    Returns:
        Response: 重定向到前端群聊管家页面或提供静态文件
    """
    if is_frozen():
        # 在打包环境中，提供静态文件服务
        frontend_dist_path = get_resource_path('frontend/dist')
        if frontend_dist_path.exists():
            return send_from_directory(str(frontend_dist_path), 'index.html')
        else:
            return "前端文件未找到，请确保前端文件已正确打包", 500
    else:
        # 在开发环境中，重定向到前端开发服务器
        return redirect("http://localhost:8080/group_manager")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """
    获取所有任务列表

    Returns:
        Response: JSON格式的任务列表
    """
    return jsonify(list(load_tasks().values()))


@app.route("/api/tasks", methods=["POST"])
def add_task_route():
    """
    添加新任务

    Request Body:
        JSON对象包含任务信息

    Returns:
        Response: 新创建的任务信息和201状态码，或错误信息
    """
    task_data = request.json
    new_task = add_task(task_data)
    return jsonify(new_task), 201


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def delete_task_route(task_id):
    """
    删除指定任务

    Args:
        task_id: 要删除的任务ID

    Returns:
        Response: 成功或失败信息
    """
    success = delete_task(task_id)
    if success:
        return jsonify({"success": True}), 200
    return jsonify({"error": "Task not found"}), 404


@app.route("/api/tasks/<task_id>/status", methods=["PATCH"])
def update_task_status_route(task_id):
    """
    更新任务状态

    Args:
        task_id: 要更新的任务ID

    Request Body:
        JSON对象包含status字段

    Returns:
        Response: 更新后的任务信息或错误信息
    """
    data = request.json
    if "status" not in data:
        return jsonify({"error": "Status field is required"}), 400

    updated_task = update_task_status(task_id, data["status"])
    if updated_task:
        return jsonify(updated_task), 200
    return jsonify({"error": "Task not found"}), 404


@app.route("/api/tasks", methods=["DELETE"])
def clear_tasks_route():
    """
    清空所有任务

    Returns:
        Response: 成功信息
    """
    clear_tasks()
    return jsonify({"success": True}), 200


@app.route("/api/tasks/import", methods=["POST"])
@handle_api_errors
def import_tasks_route():
    """
    批量导入任务

    Request Body:
        JSON数组包含多个任务信息

    Returns:
        Response: 导入结果统计信息或错误信息
    """
    tasks_data = request.json
    if not isinstance(tasks_data, list):
        return jsonify({"error": "请求数据必须是一个任务列表"}), 400

    success_count, total_count = import_tasks(tasks_data)
    return (
        jsonify(
            {
                "success": True,
                "imported": success_count,
                "total": total_count,
                "message": f"成功导入 {success_count}/{total_count} 个任务",
            }
        ),
        200,
    )


@app.route("/api/ai-settings", methods=["GET"])
def get_ai_settings():
    """
    获取AI设置信息

    Returns:
        Response: JSON格式的AI设置信息
    """
    return jsonify(load_ai_data())


@app.route("/api/ai-settings", methods=["POST"])
def save_ai_settings_route():
    """
    保存AI设置信息

    Request Body:
        JSON对象包含AI设置参数

    Returns:
        Response: 保存后的AI设置信息或错误信息
    """
    settings_data = request.json
    saved_settings = save_ai_settings(settings_data)
    return jsonify(saved_settings), 200


@app.route("/api/ai-history", methods=["GET"])
def get_ai_history():
    """
    获取AI回复历史记录

    Returns:
        Response: JSON格式的AI回复历史记录
    """
    try:
        history = load_reply_history()
        return jsonify(history), 200
    except Exception as e:
        logger.error(f"获取AI历史记录失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai-history/delete", methods=["POST"])
@handle_api_errors
def delete_ai_history():
    """
    删除AI回复历史记录

    Request Body:
        JSON对象包含time和message字段

    Returns:
        Response: 删除结果信息
    """
    data = request.json
    if not data or 'time' not in data or 'message' not in data:
        return jsonify({'error': '缺少必要参数'}), 400
        
    time = data['time']
    message = data['message']
    
    # 加载历史记录
    history = load_reply_history()
    
    # 查找并删除匹配的记录
    original_length = len(history)
    history = [h for h in history if not (h.get('time') == time and h.get('message') == message)]
    
    if len(history) == original_length:
        return jsonify({'error': '未找到匹配的历史记录'}), 404
        
    # 更新全局变量并保存历史记录
    from data_manager import reply_history as dm_reply_history
    dm_reply_history[:] = history  # 更新data_manager中的全局变量
    save_reply_history()  # 不传递参数，使用全局变量
    
    return jsonify({'success': True, 'message': '历史记录删除成功'})


@app.route("/api/ai-history", methods=["POST"])
@handle_api_errors
def add_ai_history_route():
    """
    添加AI回复历史记录

    Request Body:
        JSON对象包含回复历史信息

    Returns:
        Response: 新添加的历史记录信息和201状态码
    """
    history_data = request.json
    new_history = add_ai_history(history_data)
    return jsonify(new_history), 201


@app.route("/api/com-diagnose", methods=["GET"])
def get_com_diagnose():
    """
    获取COM组件诊断信息
    
    Returns:
        Response: JSON格式的COM组件诊断信息
    """
    try:
        solutions = diagnose_com_error()
        return jsonify({
            "success": True,
            "diagnose_info": solutions,
            "com_error_code": -2147467259,
            "description": "COM组件初始化错误，通常由于微信未正确安装、未登录或COM组件注册问题"
        }), 200
    except Exception as e:
        logger.error(f"获取COM诊断信息失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/wechat-status", methods=["GET"])
def get_wechat_status():
    """
    获取微信状态信息（异步缓存版本）

    Returns:
        Response: JSON格式的微信状态信息，包含在线状态、用户信息和详细信息
    """
    try:
        # 直接从缓存的状态信息中获取，避免同步调用微信API
        status_info = get_status_info()
        # 获取用户名
        username = None
        if status_info.get("user_info"):
            username = status_info["user_info"]

        return (
            jsonify(
                {
                    "success": True,
                    "online": is_wechat_online(),
                    "username": username,
                    "status_info": status_info,
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"获取微信状态失败: {e}")
        return jsonify({"success": False, "online": False, "error": str(e)}), 500


@app.route("/api/ai-takeover/start", methods=["POST"])
@handle_api_errors
def start_ai_takeover():
    """
    启动AI接管功能

    Returns:
        Response: 启动结果信息
    """
    data = request.json
    contact_person = data.get("contactPerson", "")
    ai_persona = data.get("aiPersona", "你是一个的微信好友，全程隐藏 AI "
                                       "身份，能类似真人的自然感回应，具体按以下要求执行：对话风格：完全口语化，不用长句和书面词，带日常语气词（”卧槽“等）或网络热梗。话题应对：懂的话题别 "
                                       "“掉书袋”，聊日常细节就行。应对 “AI 质疑”：如果用户说 “你怎么像机器人”“你是 AI "
                                       "吧”，别辩解不能掉入“自证陷阱”并嘲讽对方。总之，你就是一个普通人，聊得随意、有烟火气，别让人觉得 “说话没温度、不像真人”。")
    only_at = data.get("onlyAt", False)
    group_at_reply = data.get("groupAtReply", False)

    if not contact_person:
        return jsonify({"success": False, "error": "联系人不能为空", "ai_status": False}), 400

    # 检查微信是否在线
    if not is_wechat_online():
        return jsonify({"success": False, "error": "微信未登录或不可用", "ai_status": False}), 400

    wx = get_wechat_instance()
    ai_manager = AiWorkerManager()
    # 获取AI模型设置，默认为禁用
    ai_model = data.get("aiModel", "disabled")
    config = WorkerConfig(
        wx_instance=wx,
        receiver=contact_person,
        model=ai_model,
        role=ai_persona,
        only_at=only_at,
        group_at_reply=group_at_reply,
        reply_delay=data.get("replyDelay", 0),
        min_reply_interval=data.get("minReplyInterval", 0),
    )
    success = ai_manager.start_worker(config)

    if success:
        logger.info(f"[AI接管] 已启动监听: {contact_person}")
        # 仅在接管操作成功完成后，才将JSON文件中的状态值更新为true
        ai_data = load_ai_data()
        ai_data["aiStatus"] = True
        save_ai_settings(ai_data)
        return (
            jsonify(
                {
                    "success": True,
                    "message": f"已开始监听 {contact_person}",
                    "ai_status": True,
                }
            ),
            200,
        )
    else:
        # 检查是否是因为监听器已存在而失败
        workers = ai_manager.get_all_workers()
        # 获取AI模型设置，默认为禁用
        ai_model = data.get("aiModel", "disabled")
        worker_key = f"{contact_person}_{ai_model}"
        if worker_key in workers:
            logger.info(f"[AI接管] 监听器已存在: {contact_person}, 模型: {ai_model}")
            return jsonify({"success": False, "error": "监听器已存在", "ai_status": False}), 400
        else:
            logger.error(f"[AI接管] 启动监听失败: {contact_person}, 模型: {ai_model}")
            # 若接管失败，则保持原状态不变，不更新JSON文件中的状态值
            return jsonify({"success": False, "error": "启动监听失败，请检查联系人是否正确", "ai_status": False}), 500


@app.route("/api/ai-takeover/stop", methods=["POST"])
@handle_api_errors
def stop_ai_takeover():
    """停止AI接管功能"""
    data = request.json
    contact_person = data.get("contactPerson", "")

    if not contact_person:
        return jsonify({"success": False, "error": "联系人不能为空", "ai_status": False}), 400

    ai_manager = AiWorkerManager()
    # 获取AI模型设置，默认为禁用
    ai_model = data.get("aiModel", "disabled")
    ai_manager.stop_worker(contact_person, ai_model)

    ai_data = load_ai_data()
    ai_data["aiStatus"] = False
    save_ai_settings(ai_data)
    return (
        jsonify(
            {
                "success": True,
                "message": f"已停止监听 {contact_person}",
                "ai_status": False,
            }
        ),
        200,
    )


@app.route("/api/ai-takeover/status", methods=["GET"])
@handle_api_errors
def get_ai_takeover_status():
    """获取AI接管状态"""
    ai_manager = AiWorkerManager()
    workers = ai_manager.get_all_workers()

    status_list = []
    for worker_key in workers:
        receiver, model = worker_key.split("_")
        status = ai_manager.get_worker_status(receiver, model)
        if status:
            status_list.append(
                {
                    "receiver": receiver,
                    "model": model,
                    "running": status["running"],
                    "uptime": status["uptime"],
                    "paused": status["paused"],
                }
            )

    return jsonify({"success": True, "workers": status_list}), 200


@app.route("/api/home-data", methods=["GET"])
def get_home_data():
    return jsonify(load_home_data())


@app.route("/api/ai-stats", methods=["GET"])
@handle_api_errors
def get_ai_stats_route():
    stats = get_ai_stats()
    return jsonify(stats)


# 任务调度器控制API
@app.route("/api/task-scheduler/start", methods=["POST"])
@handle_api_errors
def start_task_scheduler_route():
    start_task_scheduler()
    return jsonify({"success": True, "message": "任务调度器已启动"}), 200


@app.route("/api/task-scheduler/stop", methods=["POST"])
@handle_api_errors
def stop_task_scheduler_route():
    stop_task_scheduler()
    return jsonify({"success": True, "message": "任务调度器已停止"}), 200


@app.route("/api/task-scheduler/status", methods=["GET"])
@handle_api_errors
def get_task_scheduler_status():
    status_info = task_scheduler.get_status_info()
    return (
        jsonify(
            {
                "isRunning": status_info["running"],
                "message": "任务调度器运行中" if status_info["running"] else "任务调度器已停止",
                "statusInfo": status_info,
            }
        ),
        200,
    )


@app.route("/api/health")
@handle_api_errors
def health_check():
    """健康检查端点"""
    load_tasks()
    load_ai_data()

    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "flask": "running",
                    "database": "connected",
                    "scheduler": "active"
                    if hasattr(task_scheduler, "scheduler") and task_scheduler.scheduler
                    else "inactive",
                },
            }
        ),
        200,
    )


@app.route("/api/stats/<time_range>", methods=["GET"])
@handle_api_errors
def get_chart_data(time_range):
    # 获取真实的AI统计数据
    stats = get_ai_stats()

    # 生成基于真实数据的图表数据
    from datetime import datetime, timedelta

    from data_manager import load_reply_history

    # 加载回复历史数据
    reply_history = load_reply_history()

    # 根据时间范围生成日期和计数
    dates = []
    counts = []

    # 获取当前日期
    today = datetime.now()

    # 根据范围统计每天的回复数量
    if time_range == "7d":
        # 统计最近7天的回复数量
        for i in range(6, -1, -1):
            target_date = (today - timedelta(days=i)).date()
            date_str = target_date.strftime("%Y-%m-%d")

            # 统计当天的回复数量
            daily_count = sum(
                1
                for item in reply_history
                if datetime.fromisoformat(
                    item.get("timestamp", item.get("time", ""))
                ).date()
                == target_date
                and item.get("status") == "replied"
            )

            dates.append(date_str)
            counts.append(daily_count)
    elif time_range == "30d":
        # 统计最近30天的回复数量（按周分组）
        for i in range(29, -1, -7):  # 每7天显示一个点
            target_date = (today - timedelta(days=i)).date()
            date_str = target_date.strftime("%Y-%m-%d")

            # 统计从target_date开始7天内的回复数量
            week_count = sum(
                1
                for item in reply_history
                if (
                    target_date
                    <= datetime.fromisoformat(
                        item.get("timestamp", item.get("time", ""))
                    ).date()
                    <= target_date + timedelta(days=6)
                )
                and item.get("status") == "replied"
            )

            dates.append(date_str)
            counts.append(week_count)
    else:  # 90d
        # 统计最近90天的回复数量（按月分组）
        for i in range(89, -1, -30):  # 每30天显示一个点
            target_date = (today - timedelta(days=i)).date()
            date_str = target_date.strftime("%Y-%m-%d")

            # 统计从target_date开始30天内的回复数量
            month_count = sum(
                1
                for item in reply_history
                if (
                    target_date
                    <= datetime.fromisoformat(
                        item.get("timestamp", item.get("time", ""))
                    ).date()
                    <= target_date + timedelta(days=29)
                )
                and item.get("status") == "replied"
            )

            dates.append(date_str)
            counts.append(month_count)

    return jsonify(
        {
            "stats": {
                "replyRate": stats.get("replyRate", 0),
                "averageTime": stats.get("averageTime", 0),
                "satisfactionRate": stats.get("satisfactionRate", 100),
            },
            "chartData": {"dates": dates, "counts": counts},
        }
    )


# 群聊管家API
from group_manager import (
    select_group, toggle_message_recording, set_collection_date, 
    save_collection_template, auto_learn_pattern, export_collected_data,
    start_sentiment_monitoring, stop_sentiment_monitoring, check_sentiment_monitoring_status,
    start_group_management, group_manager, data_dir
)
import re

# 群聊管理API
@app.route("/api/group/select", methods=["POST"])
@handle_api_errors
def api_select_group():
    """选择要管理的群聊"""
    data = request.json
    group_name = data.get("group_name", "")
    
    success, message = select_group(group_name)
    
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 400


@app.route("/api/group/toggle-recording", methods=["POST"])
@handle_api_errors
def api_toggle_message_recording():
    """开启/关闭群消息记录"""
    data = request.json
    group_name = data.get("group_name", "")
    enabled = data.get("enabled", False)
    
    success, message = toggle_message_recording(group_name, enabled)
    
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 400


# 群消息数据收集API
@app.route("/api/group/set-collection-date", methods=["POST"])
@handle_api_errors
def api_set_collection_date():
    """设置收集日期"""
    data = request.json
    group_name = data.get("group_name", "")
    date = data.get("date", "")
    
    success, result = set_collection_date(group_name, date)
    
    if success:
        return jsonify({"success": True, "data": result}), 200
    else:
        return jsonify({"success": False, "error": result}), 400


@app.route("/api/group/save-template", methods=["POST"])
@handle_api_errors
def api_save_collection_template():
    """保存收集模板"""
    data = request.json
    group_name = data.get("group_name", "")
    template = data.get("template", "")
    
    success, message = save_collection_template(group_name, template)
    
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 400


@app.route("/api/group/auto-learn", methods=["POST"])
@handle_api_errors
def api_auto_learn_pattern():
    """自动学习模式，建立正则表达式"""
    data = request.json
    group_name = data.get("group_name", "")
    
    success, message = auto_learn_pattern(group_name)
    
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 400

@app.route("/api/group/auto-learn-pattern", methods=["POST"])
@handle_api_errors
def api_auto_learn_pattern_from_content():
    """根据提供的原始消息和目标内容自动学习模式，建立正则表达式"""
    try:
        data = request.json
        original_message = data.get("original_message", "")
        target_content = data.get("target_content", "")
        
        if not original_message or not target_content:
            return jsonify({"success": False, "error": "原始消息和目标内容不能为空"}), 400
        
        # 解析目标内容，按逗号分隔
        target_items = [item.strip() for item in target_content.split("，") if item.strip()]
        
        if not target_items:
            return jsonify({"success": False, "error": "无法从目标内容中提取有效信息"}), 400
        
        # 提取目标内容在原始消息中的位置和上下文，生成能够捕获相似结构的正则表达式
        regex_pattern = generate_structure_based_regex(original_message, target_items)
        
        # 如果生成了有效的正则表达式，则返回
        if regex_pattern:
            # 提取示例值进行预览
            extracted_values = extract_values_with_regex(original_message, regex_pattern)
            return jsonify({"success": True, "regex": regex_pattern, "extracted_values": extracted_values}), 200
        else:
            # 如果无法生成基于结构的正则表达式，则回退到简单匹配模式
            patterns = []
            for item in target_items:
                # 转义正则表达式特殊字符
                escaped_item = re.escape(item)
                # 为每个目标项创建一个捕获组
                patterns.append(f"({escaped_item})")
            
            if patterns:
                regex_pattern = "|".join(patterns)
                return jsonify({"success": True, "regex": regex_pattern}), 200
            else:
                return jsonify({"success": False, "error": "未能生成有效的正则表达式"}), 400
            
    except Exception as e:
        logger.error(f"自动学习模式失败: {str(e)}")
        return jsonify({"success": False, "error": f"操作失败: {str(e)}"}), 500


@app.route("/api/group/export-collected-data", methods=["POST"])
@handle_api_errors
def api_export_collected_data():
    """导出收集的数据"""
    data = request.json
    group_name = data.get("group_name", "")
    date = data.get("date", "")
    
    success, result = export_collected_data(group_name, date)
    
    if success:
        return jsonify({"success": True, "file_path": result}), 200
    else:
        return jsonify({"success": False, "error": result}), 400


# 群聊管理API
@app.route("/api/group/start-management", methods=["POST"])
@handle_api_errors
def api_start_group_management():
    """开始群聊管理"""
    data = request.json
    group_name = data.get("group_name", "")
    settings = data.get("settings", {})
    
    success, message = start_group_management(group_name, settings)
    
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 400

@app.route("/api/group/stop-management", methods=["POST"])
@handle_api_errors
def api_stop_group_management():
    """停止群聊管理"""
    data = request.json
    group_name = data.get("group_name", "")
    
    if not group_name:
        return jsonify({"success": False, "error": "群聊名称不能为空"}), 400
    
    # 调用group_manager的stop_worker方法停止群聊管理
    success = group_manager.stop_worker(group_name)
    
    # 即使没有找到对应的工作线程，也更新配置文件状态
    # 因为可能存在配置状态与实际运行状态不一致的情况
    import json
    import os
    from group_manager import group_manage_config_file
    
    try:
        if os.path.exists(group_manage_config_file):
            with open(group_manage_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新群聊配置
            if group_name in config:
                config[group_name]["enabled"] = False
                config[group_name]["stop_time"] = datetime.now().isoformat()
            
            # 无论工作线程是否存在，前端请求停止时都设置management_enabled为false
            config["management_enabled"] = False
            
            # 保存更新后的配置
            with open(group_manage_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"更新配置文件失败: {e}")
        # 配置文件更新失败，但仍然返回成功（因为主要目的是停止管理）
    
    if success:
        return jsonify({"success": True, "message": f"已成功停止管理群聊: {group_name}"}), 200
    else:
        # 即使没有找到工作线程，也返回成功，因为配置状态已经更新
        return jsonify({"success": True, "message": f"群聊 {group_name} 的管理状态已更新（未找到运行中的工作线程）"}), 200

# 舆情监控API
@app.route("/api/group/start-monitoring", methods=["POST"])
@handle_api_errors
def api_start_sentiment_monitoring():
    """开始舆情监控"""
    data = request.json
    group_name = data.get("group_name", "")
    sensitive_words = data.get("sensitive_words", "")
    
    success, message = start_sentiment_monitoring(group_name, sensitive_words)
    
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 400


@app.route("/api/group/stop-monitoring", methods=["POST"])
@handle_api_errors
def api_stop_sentiment_monitoring():
    """停止舆情监控"""
    data = request.json
    group_name = data.get("group_name", "")
    
    success, message = stop_sentiment_monitoring(group_name)
    
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 400


@app.route("/api/group/check-monitoring-status", methods=["POST"])
@handle_api_errors
def api_check_sentiment_monitoring_status():
    """检查舆情监控状态"""
    data = request.json
    group_name = data.get("group_name", "")
    
    success, status = check_sentiment_monitoring_status(group_name)
    
    if success:
        return jsonify({"success": True, "status": status}), 200
    else:
        return jsonify({"success": False, "error": status}), 400


@app.route("/api/message-quota", methods=["GET"])
@handle_api_errors
def get_message_quota():
    """
    获取消息配额信息

    Returns:
        Response: JSON格式的消息配额信息
    """
    try:
        from data_manager import get_quota_info

        quota_info = get_quota_info()
        return jsonify({"success": True, "quota": quota_info}), 200
    except Exception as e:
        logger.error(f"获取消息配额失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/export/group-links", methods=["GET"])
def export_group_links():
    return jsonify({"error": "链接数据导出功能正在建设中"}), 501


@app.route("/api/verify-activation", methods=["POST"])
@handle_api_errors
def verify_activation():
    """
    验证激活码
    
    Request Body:
        JSON对象包含randomCode和activationCode字段
    
    Returns:
        Response: 验证结果，包含成功状态、版本和过期时间
    """
    data = request.json
    
    if not data or "randomCode" not in data or "activationCode" not in data:
        return jsonify({"success": False, "error": "请求参数不完整"}), 400
    
    random_code = data["randomCode"]
    activation_code = data["activationCode"]
    
    # 验证randomCode是否为8位数字
    if not random_code or not random_code.isdigit() or len(random_code) != 8:
        return jsonify({"success": False, "error": "随机码格式不正确"}), 400
    
    # 验证activationCode是否为16位字母数字
    if not activation_code or not activation_code.isalnum() or len(activation_code) != 16:
        return jsonify({"success": False, "error": "激活码格式不正确"}), 400
    
    try:
        # 将随机码转换为整数
        random_num = int(random_code)
        
        # 计算basic版和企业版的密钥
        basic_key = hex(random_num + 1)[2:].upper().zfill(16)
        enterprise_key = hex(random_num + 2)[2:].upper().zfill(16)
        
        # 验证激活码
        version = None
        expiry_days = 30  # 默认30天有效期
        
        if activation_code == basic_key:
            version = "basic"
            expiry_days = 30  # 基础版30天
        elif activation_code == enterprise_key:
            version = "enterprise"
            expiry_days = 90  # 企业版90天
        else:
            return jsonify({"success": False, "error": "激活码无效"}), 400
        
        # 计算过期时间
        from datetime import datetime, timedelta
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d")
        
        # 更新用户账户级别
        from data_manager import update_account_level
        update_account_level(version)
        
        return jsonify({
            "success": True,
            "version": version,
            "expiryDate": expiry_date
        }), 200
        
    except Exception as e:
        logger.error(f"激活码验证失败: {e}")
        return jsonify({"success": False, "error": "激活码验证过程中发生错误"}), 500


# 获取配置状态API
@app.route("/api/group/get-config-status", methods=["GET"])
@handle_api_errors
def api_get_config_status():
    """
    获取配置状态（群聊管理、数据收集、舆情监控的开关状态和选择的群聊）
    """
    import json
    import os
    
    # 读取group_manage.json配置文件
    config_file = os.path.join(data_dir, "group_manage.json")
    
    # 默认为False状态
    config_status = {
        "management_status": False,  # 群聊管理状态（原ai_status）
        "data_collection_enabled": False,
        "monitoring_enabled": False,
        "group": ""
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
                # 从配置中提取状态信息
                config_status["management_status"] = config_data.get("management_enabled", False)
                config_status["data_collection_enabled"] = config_data.get("data_collection_enabled", False)
                config_status["monitoring_enabled"] = config_data.get("sentiment_monitoring_enabled", False)
                config_status["group"] = config_data.get("group", "")
        
        return jsonify(config_status), 200
    except Exception as e:
        logger.error(f"读取配置状态失败: {e}")
        return jsonify(config_status), 200  # 即使失败也返回默认状态


# 更新配置状态API
@app.route("/api/group/update-config-status", methods=["POST"])
@handle_api_errors
def api_update_config_status():
    """
    更新配置状态（数据收集、舆情监控的开关状态）
    """
    import json
    import os
    
    data = request.json
    data_collection_enabled = data.get("data_collection_enabled", False)
    monitoring_enabled = data.get("monitoring_enabled", False)
    
    # 读取group_manage.json配置文件
    config_file = os.path.join(data_dir, "group_manage.json")
    
    try:
        config_data = {}
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        
        # 更新配置状态
        config_data["data_collection_enabled"] = data_collection_enabled
        config_data["sentiment_monitoring_enabled"] = monitoring_enabled
        
        # 保存更新后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"配置状态已更新 - 数据收集: {data_collection_enabled}, 舆情监控: {monitoring_enabled}")
        return jsonify({"success": True, "message": "配置状态已更新"}), 200
    except Exception as e:
        logger.error(f"更新配置状态失败: {e}")
        return jsonify({"success": False, "error": f"更新配置状态失败: {e}"}), 500


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Flask应用启动参数')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口号')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    start_task_scheduler()
    app.run(debug=args.debug, host=args.host, port=args.port)

# 获取收集的数据API
@app.route("/api/group/get-collected-data", methods=["GET"])
@handle_api_errors
def api_get_collected_data():
    print("收到请求")
    """获取收集的数据"""
    group_id = request.args.get('group_id', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    try:
        from group_manager import export_collected_data
        
        # 如果没有指定日期，使用当前日期
        date_str = start_date if start_date else datetime.now().strftime("%Y-%m-%d")
        
        success, result = export_collected_data(group_id, date_str)
        
        if success:
            # 读取导出的数据文件
            with open(result, 'r', encoding='utf-8') as f:
                collected_data = json.load(f)

                print(collected_data)
            
            return jsonify({
                "success": True,
                "data": collected_data,
                "total": len(collected_data)
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result,
                "data": [],
                "total": 0
            }), 200
            
    except Exception as e:
        print(e)
        logger.error(f"获取收集的数据失败: {e}")
        return jsonify({
            "success": False,
            "error": f"获取数据失败: {e}",
            "data": [],
            "total": 0
        }), 500

# 获取正则规则API
@app.route("/api/group/get-regex-rules", methods=["GET"])
@handle_api_errors
def api_get_regex_rules():
    """获取正则规则列表"""
    try:
        # 从配置文件读取正则规则
        regex_config_file = os.path.join(data_dir, "regex_rules.json")
        
        regex_rules = []
        if os.path.exists(regex_config_file):
            with open(regex_config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                # 提取rules数组
                regex_rules = config_data.get("rules", [])
        
        return jsonify({
            "success": True,
            "rules": regex_rules
        }), 200
        
    except Exception as e:
        logger.error(f"获取正则规则失败: {e}")
        return jsonify({
            "success": False,
            "error": f"获取规则失败: {e}",
            "rules": []
        }), 500

# 获取敏感词API
@app.route("/api/group/get-sensitive-words", methods=["GET"])
@handle_api_errors
def api_get_sensitive_words():
    """获取敏感词列表"""
    try:
        # 从配置文件读取敏感词
        sensitive_config_file = os.path.join(data_dir, "sensitive_words.json")
        
        sensitive_words = []
        if os.path.exists(sensitive_config_file):
            with open(sensitive_config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                # 提取words数组
                sensitive_words = config_data.get("words", [])
                print(sensitive_words)
        
        return jsonify({
            "success": True,
            "words": sensitive_words
        }), 200
        
    except Exception as e:
        print(f"获取敏感词失败: {e}")
        logger.error(f"获取敏感词失败: {e}")
        return jsonify({
            "success": False,
            "error": f"获取敏感词失败: {e}",
            "words": []
        }), 500

# 保存敏感词API
@app.route("/api/group/save-sensitive-words", methods=["POST"])
@handle_api_errors
def api_save_sensitive_words():
    """保存敏感词列表"""
    try:
        data = request.json
        words = data.get("words", [])

        print(words)
        
        if not isinstance(words, list):
            return jsonify({
                "success": False,
                "error": "words参数必须是一个数组"
            }), 400
        
        # 保存到配置文件
        sensitive_config_file = os.path.join(data_dir, "sensitive_words.json")
        config_data = {"words": words}
        
        with open(sensitive_config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"敏感词已保存，共{len(words)}个敏感词")
        return jsonify({
            "success": True,
            "message": f"敏感词保存成功，共{len(words)}个敏感词"
        }), 200
        
    except Exception as e:
        print(f"保存敏感词失败: {e}")
        logger.error(f"保存敏感词失败: {e}")
        return jsonify({
            "success": False,
            "error": f"保存敏感词失败: {e}"
        }), 500

# 保存正则规则API
@app.route("/api/group/save-regex-rules", methods=["POST"])
@handle_api_errors
def api_save_regex_rules():
    """保存正则规则列表"""
    try:
        data = request.json
        rules = data.get("rules", [])
        
        if not isinstance(rules, list):
            return jsonify({
                "success": False,
                "error": "rules参数必须是一个数组"
            }), 400
        
        # 保存到配置文件
        regex_config_file = os.path.join(data_dir, "regex_rules.json")
        config_data = {"rules": rules}
        
        with open(regex_config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"正则规则已保存，共{len(rules)}条规则")
        return jsonify({
            "success": True,
            "message": f"正则规则保存成功，共{len(rules)}条规则"
        }), 200
        
    except Exception as e:
        logger.error(f"保存正则规则失败: {e}")
        return jsonify({
            "success": False,
            "error": f"保存正则规则失败: {e}"
        }), 500

# 获取可用群组API
@app.route("/api/group/get-available-groups", methods=["GET"])
@handle_api_errors
def api_get_available_groups():
    """获取可用群组列表"""
    try:
        from group_manager import get_available_groups
        
        success, groups = get_available_groups()

        print(success, groups)
        
        if success:
            return jsonify({
                "success": True,
                "groups": groups
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": groups,
                "groups": []
            }), 200
            
    except Exception as e:
        logger.error(f"获取可用群组失败: {e}")
        return jsonify({
                "success": False,
                "error": f"获取群组失败: {e}",
                "groups": []
            }), 500

# 获取群组日期API
@app.route("/api/group/get-group-dates", methods=["GET"])
@handle_api_errors
def api_get_group_dates():
    """获取指定群组的日期列表"""
    try:
        group_name = request.args.get("group_name", "")
        
        if not group_name:
            return jsonify({
                "success": False,
                "error": "群组名称不能为空"
            }), 400
            
        from group_manager import get_group_dates
        
        success, dates = get_group_dates(group_name)
        
        if success:
            return jsonify({
                "success": True,
                "group_name": group_name,
                "dates": dates
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": dates,
                "dates": []
            }), 200
            
    except Exception as e:
        logger.error(f"获取群组 '{group_name}' 的日期列表失败: {e}")
        return jsonify({
            "success": False,
            "error": f"获取日期列表失败: {e}",
            "dates": []
        }), 500

# 文件下载API
@app.route("/api/download-file", methods=["GET"])
def download_file():
    """下载文件API"""
    try:
        file_path = request.args.get("file_path", "")
        
        if not file_path:
            return jsonify({
                "success": False,
                "error": "文件路径不能为空"
            }), 400
        
        # 安全检查：确保文件路径在允许的目录内
        allowed_dirs = [
            os.path.join(os.getcwd(), "chat_date"),
            os.path.join(os.getcwd(), "data")
        ]
        
        file_abs_path = os.path.abspath(file_path)
        is_allowed = False
        
        for allowed_dir in allowed_dirs:
            if file_abs_path.startswith(os.path.abspath(allowed_dir)):
                is_allowed = True
                break
        
        if not is_allowed:
            return jsonify({
                "success": False,
                "error": "文件访问被拒绝"
            }), 403
        
        if not os.path.exists(file_abs_path):
            return jsonify({
                "success": False,
                "error": "文件不存在"
            }), 404
        
        # 返回文件下载
        return send_file(
            file_abs_path,
            as_attachment=True,
            download_name=os.path.basename(file_abs_path)
        )
        
    except Exception as e:
        logger.error(f"文件下载失败: {e}")
        return jsonify({
            "success": False,
            "error": f"文件下载失败: {e}"
        }), 500


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Flask应用启动参数')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口号')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    start_task_scheduler()
    app.run(debug=args.debug, host=args.host, port=args.port)
