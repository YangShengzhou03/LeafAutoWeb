"""
Flask应用主模块

提供微信消息自动化管理系统的RESTful API接口，包括任务管理、AI设置、微信状态监控等功能。

主要功能：
- 定时任务管理API
- AI自动回复配置API  
- 微信状态监控API
- 前后端路由转发
"""

from datetime import datetime
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

from ai_worker import AiWorkerManager
from data_manager import (
    load_tasks, load_ai_data, load_reply_history, load_home_data, add_task, delete_task,
    update_task_status, clear_tasks, import_tasks, save_ai_settings, add_ai_history,
    get_ai_stats
)
from logging_config import get_logger
from task_scheduler import start_task_scheduler, task_scheduler
from wechat_instance import start_status_monitor, get_wechat_instance, get_status_info, is_wechat_online

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

# 全局变量
reply_history = []

# 统一错误处理装饰器
def handle_api_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API Error in {func.__name__}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/')
def home():
    """
    首页路由重定向到前端页面
    
    Returns:
        Response: 重定向到前端首页
    """
    return redirect('http://localhost:8080')


@app.route('/auto-info')
def auto_info():
    """
    自动信息页面路由重定向
    
    Returns:
        Response: 重定向到前端自动信息页面
    """
    return redirect('http://localhost:8080/auto_info')


@app.route('/ai-takeover')
def ai_takeover():
    """
    AI接管页面路由重定向
    
    Returns:
        Response: 重定向到前端AI接管页面
    """
    return redirect('http://localhost:8080/ai_takeover')


@app.route('/other_box')
def other_box():
    """
    其他功能页面路由重定向
    
    Returns:
        Response: 重定向到前端其他功能页面
    """
    return redirect('http://localhost:8080/other_box')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """
    获取所有任务列表
    
    Returns:
        Response: JSON格式的任务列表
    """
    return jsonify(list(load_tasks().values()))


@app.route('/api/tasks', methods=['POST'])
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


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
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
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<task_id>/status', methods=['PATCH'])
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
    if 'status' not in data:
        return jsonify({'error': 'Status field is required'}), 400

    updated_task = update_task_status(task_id, data['status'])
    if updated_task:
        return jsonify(updated_task), 200
    return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks', methods=['DELETE'])
def clear_tasks_route():
    """
    清空所有任务
    
    Returns:
        Response: 成功信息
    """
    clear_tasks()
    return jsonify({'success': True}), 200


@app.route('/api/tasks/import', methods=['POST'])
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
        return jsonify({'error': '请求数据必须是一个任务列表'}), 400

    success_count, total_count = import_tasks(tasks_data)
    return jsonify({
        'success': True,
        'imported': success_count,
        'total': total_count,
        'message': f'成功导入 {success_count}/{total_count} 个任务'
    }), 200


@app.route('/api/ai-settings', methods=['GET'])
def get_ai_settings():
    """
    获取AI设置信息
    
    Returns:
        Response: JSON格式的AI设置信息
    """
    return jsonify(load_ai_data())


@app.route('/api/ai-settings', methods=['POST'])
@handle_api_errors
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

    # 根据AI接管状态启动或停止监听
    if settings_data.get('aiStatus'):
        # 启动AI接管
        contact_person = settings_data.get('contactPerson', '')
        if contact_person:
            wx = get_wechat_instance()
            ai_manager = AiWorkerManager()
            success = ai_manager.start_worker(wx, contact_person,
                                              role=settings_data.get('aiPersona', '你很温馨,回复简单明了。'),
                                              only_at=settings_data.get('onlyAt', False),
                                              reply_delay=settings_data.get('replyDelay', 5),
                                              min_reply_interval=settings_data.get('minReplyInterval', 60))
            if success:
                logger.info(f"[AI接管] 已启动监听: {contact_person}")
            else:
                # 检查是否是因为监听器已存在而失败
                workers = ai_manager.get_all_workers()
                worker_key = f"{contact_person}_月之暗面"
                if worker_key in workers:
                    logger.info(f"[AI接管] 监听器已存在: {contact_person}")
                else:
                    logger.error(f"[AI接管] 启动监听失败: {contact_person}")
                    # 如果启动失败，回滚AI状态
                    settings_data['aiStatus'] = False
                    saved_settings = save_ai_settings(settings_data)
    else:
        # 停止AI接管
        contact_person = settings_data.get('contactPerson', '')
        if contact_person:
            ai_manager = AiWorkerManager()
            ai_manager.stop_worker(contact_person)
            logger.info(f"[AI接管] 已停止监听: {contact_person}")

    return jsonify(saved_settings), 200


@app.route('/api/ai-history', methods=['GET'])
def get_ai_history():
    """
    获取AI回复历史记录
    
    Returns:
        Response: JSON格式的AI回复历史记录
    """
    try:
        from data_manager import load_reply_history
        history = load_reply_history()
        return jsonify(history), 200
    except Exception as e:
        logger.error(f"获取AI历史记录失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai-history', methods=['POST'])
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


@app.route('/api/wechat-status', methods=['GET'])
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
        if status_info.get('user_info'):
            username = status_info['user_info']
        
        return jsonify({
            'success': True,
            'online': is_wechat_online(),
            'username': username,
            'status_info': status_info
        }), 200
    except Exception as e:
        logger.error(f"获取微信状态失败: {e}")
        return jsonify({
            'success': False,
            'online': False,
            'error': str(e)
        }), 500


@app.route('/api/ai-takeover/start', methods=['POST'])
@handle_api_errors
def start_ai_takeover():
    """
    启动AI接管功能
    
    Returns:
        Response: 启动结果信息
    """
    data = request.json
    contact_person = data.get('contactPerson', '')
    ai_persona = data.get('aiPersona', '你很温馨,回复简单明了。')
    only_at = data.get('onlyAt', False)

    if not contact_person:
        return jsonify({'success': False, 'error': '联系人不能为空'}), 400

    # 检查微信是否在线
    if not is_wechat_online():
        return jsonify({'success': False, 'error': '微信未登录或不可用'}), 400

    wx = get_wechat_instance()
    ai_manager = AiWorkerManager()
    success = ai_manager.start_worker(wx, contact_person,
                                      role=ai_persona,
                                      only_at=only_at,
                                      reply_delay=data.get('replyDelay', 5),
                                      min_reply_interval=data.get('minReplyInterval', 60))

    if success:
        logger.info(f"[AI接管] 已启动监听: {contact_person}")
        # 更新AI设置状态为启动
        ai_data = load_ai_data()
        ai_data['aiStatus'] = True
        save_ai_settings(ai_data)
        return jsonify({'success': True, 'message': f'已开始监听 {contact_person}', 'aiStatus': True}), 200
    else:
        # 检查是否是因为监听器已存在而失败
        workers = ai_manager.get_all_workers()
        worker_key = f"{contact_person}_月之暗面"
        if worker_key in workers:
            logger.info(f"[AI接管] 监听器已存在: {contact_person}")
            return jsonify({'success': False, 'error': '监听器已存在'}), 400
        else:
            logger.error(f"[AI接管] 启动监听失败: {contact_person}")
            return jsonify({'success': False, 'error': '启动监听失败，请检查联系人是否正确'}), 500


@app.route('/api/ai-takeover/stop', methods=['POST'])
@handle_api_errors
def stop_ai_takeover():
    """停止AI接管功能"""
    data = request.json
    contact_person = data.get('contactPerson', '')

    if not contact_person:
        return jsonify({'success': False, 'error': '联系人不能为空'}), 400

    ai_manager = AiWorkerManager()
    success = ai_manager.stop_worker(contact_person)

    if success:
        logger.info(f"[AI接管] 已停止监听: {contact_person}")
        # 更新AI设置状态为停止
        ai_data = load_ai_data()
        ai_data['aiStatus'] = False
        save_ai_settings(ai_data)
        return jsonify({'success': True, 'message': f'已停止监听 {contact_person}', 'aiStatus': False}), 200
    else:
        ai_data = load_ai_data()
        ai_data['aiStatus'] = False
        save_ai_settings(ai_data)
        return jsonify({'success': True, 'message': f'已停止监听 {contact_person}', 'aiStatus': False}), 200


@app.route('/api/ai-takeover/status', methods=['GET'])
@handle_api_errors
def get_ai_takeover_status():
    """获取AI接管状态"""
    ai_manager = AiWorkerManager()
    workers = ai_manager.get_all_workers()

    status_list = []
    for worker_key in workers:
        receiver, model = worker_key.split('_')
        status = ai_manager.get_worker_status(receiver, model)
        if status:
            status_list.append({
                'receiver': receiver,
                'model': model,
                'running': status['running'],
                'uptime': status['uptime'],
                'paused': status['paused']
            })

    return jsonify({'success': True, 'workers': status_list}), 200


@app.route('/api/home-data', methods=['GET'])
def get_home_data():
    return jsonify(load_home_data())


@app.route('/api/ai-stats', methods=['GET'])
@handle_api_errors
def get_ai_stats_route():
    stats = get_ai_stats()
    return jsonify(stats)


# 任务调度器控制API
@app.route('/api/task-scheduler/start', methods=['POST'])
@handle_api_errors
def start_task_scheduler_route():
    start_task_scheduler()
    return jsonify({'success': True, 'message': '任务调度器已启动'}), 200


@app.route('/api/task-scheduler/stop', methods=['POST'])
@handle_api_errors
def stop_task_scheduler_route():
    from task_scheduler import stop_task_scheduler
    stop_task_scheduler()
    return jsonify({'success': True, 'message': '任务调度器已停止'}), 200


@app.route('/api/task-scheduler/status', methods=['GET'])
@handle_api_errors
def get_task_scheduler_status():
    from task_scheduler import task_scheduler
    status_info = task_scheduler.get_status_info()
    return jsonify({
        'isRunning': status_info['running'],
        'message': '任务调度器运行中' if status_info['running'] else '任务调度器已停止',
        'statusInfo': status_info
    }), 200


@app.route('/api/health')
@handle_api_errors
def health_check():
    """健康检查端点"""
    load_tasks()
    load_ai_data()

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'flask': 'running',
            'database': 'connected',
            'scheduler': 'active' if hasattr(task_scheduler, 'scheduler') and task_scheduler.scheduler else
            'inactive'
        }
    }), 200


@app.route('/api/stats/<time_range>', methods=['GET'])
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
    if time_range == '7d':
        # 统计最近7天的回复数量
        for i in range(6, -1, -1):
            target_date = (today - timedelta(days=i)).date()
            date_str = target_date.strftime('%Y-%m-%d')
            
            # 统计当天的回复数量
            daily_count = sum(1 for item in reply_history 
                            if datetime.fromisoformat(item.get('timestamp', item.get('time', ''))).date() == target_date
                            and item.get('status') == 'replied')
            
            dates.append(date_str)
            counts.append(daily_count)
    elif time_range == '30d':
        # 统计最近30天的回复数量（按周分组）
        for i in range(29, -1, -7):  # 每7天显示一个点
            target_date = (today - timedelta(days=i)).date()
            date_str = target_date.strftime('%Y-%m-%d')
            
            # 统计从target_date开始7天内的回复数量
            week_count = sum(1 for item in reply_history 
                           if (target_date <= datetime.fromisoformat(item.get('timestamp', item.get('time', ''))).date() <= target_date + timedelta(days=6))
                           and item.get('status') == 'replied')
            
            dates.append(date_str)
            counts.append(week_count)
    else:  # 90d
        # 统计最近90天的回复数量（按月分组）
        for i in range(89, -1, -30):  # 每30天显示一个点
            target_date = (today - timedelta(days=i)).date()
            date_str = target_date.strftime('%Y-%m-%d')
            
            # 统计从target_date开始30天内的回复数量
            month_count = sum(1 for item in reply_history 
                            if (target_date <= datetime.fromisoformat(item.get('timestamp', item.get('time', ''))).date() <= target_date + timedelta(days=29))
                            and item.get('status') == 'replied')
            
            dates.append(date_str)
            counts.append(month_count)
    
    return jsonify({
        "stats": {
            "replyRate": stats.get('replyRate', 0),
            "averageTime": stats.get('averageTime', 0),
            "satisfactionRate": stats.get('satisfactionRate', 100)
        },
        "chartData": {
            "dates": dates,
            "counts": counts
        }
    })


# 导出功能API
@app.route('/api/export/group-members', methods=['GET'])
def export_group_members():
    try:
        # 这里应该实现实际的群成员导出逻辑
        # 返回一个空的Excel文件作为示例
        import io
        import pandas as pd

        # 创建示例数据
        data = pd.DataFrame({
            '群名称': ['示例群1', '示例群2'],
            '成员数量': [100, 200],
            '导出时间': [pd.Timestamp.now(), pd.Timestamp.now()]
        })

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data.to_excel(writer, index=False, sheet_name='群成员')

        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename=group_members_export.xlsx'
        }
    except Exception as e:
        return jsonify({'error': f'群成员导出功能正在建设中: {str(e)}'}), 500


@app.route('/api/export/group-messages', methods=['GET'])
def export_group_messages():
    return jsonify({'error': '消息记录导出功能正在建设中'}), 501


@app.route('/api/export/group-files', methods=['GET'])
def export_group_files():
    return jsonify({'error': '文件数据导出功能正在建设中'}), 501


@app.route('/api/export/group-images', methods=['GET'])
def export_group_images():
    return jsonify({'error': '图片数据导出功能正在建设中'}), 501


@app.route('/api/export/group-voices', methods=['GET'])
def export_group_voices():
    return jsonify({'error': '语音数据导出功能正在建设中'}), 501


@app.route('/api/export/group-videos', methods=['GET'])
def export_group_videos():
    return jsonify({'error': '视频数据导出功能正在建设中'}), 501


@app.route('/api/export/group-links', methods=['GET'])
def export_group_links():
    return jsonify({'error': '链接数据导出功能正在建设中'}), 501


if __name__ == '__main__':
    print('开始仅启动Flask后端服务器...')
    start_task_scheduler()
    app.run(debug=True)
