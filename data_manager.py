import json
import os
import uuid
import datetime
import threading
from logging_config import get_logger

# 初始化日志器
logger = get_logger(__name__)

# 全局数据存储（线程安全）
tasks = {}
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'data.json')

home_data = {}
HOME_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'home_data.json')

ai_settings = {}
AI_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'ai_data.json')

reply_history = []
REPLY_HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'reply_history.json')

# 线程锁确保并发安全
data_lock = threading.Lock()


def load_tasks():
    global tasks
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            logger.info(f"成功加载 {len(tasks)} 个任务")
        else:
            tasks = {}
            logger.info("任务文件不存在，创建空任务列表")
    except json.JSONDecodeError as e:
        logger.error(f"任务文件JSON解析错误: {e}")
        tasks = {}
    except Exception as e:
        logger.error(f"加载任务失败: {e}")
        tasks = {}
    return tasks


def save_home_data():
    """保存首页数据到文件"""
    try:
        os.makedirs(os.path.dirname(HOME_DATA_FILE), exist_ok=True)
        with open(HOME_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(home_data, f, ensure_ascii=False, indent=2)
        logger.info("首页数据保存成功")
        return True
    except Exception as e:
        logger.error(f"保存首页数据失败: {e}")
        return False


def load_home_data():
    global home_data
    try:
        if os.path.exists(HOME_DATA_FILE):
            with open(HOME_DATA_FILE, 'r', encoding='utf-8') as f:
                home_data = json.load(f)
        else:
            # 文件不存在时创建默认数据并保存
            home_data = {
                "pricingPlans": [
                    {
                        "id": 1,
                        "name": "基础版",
                        "price": 299,
                        "period": "/年",
                        "features": [
                            "基础消息发送功能",
                            "每日1000条发送限额",
                            "无数据分析功能",
                            "邮件支持"
                        ],
                        "isPopular": False
                    },
                    {
                        "id": 2,
                        "name": "企业版",
                        "price": 899,
                        "period": "/年",
                        "features": [
                            "无限制消息发送",
                            "高级数据分析与报表",
                            "客户画像分析",
                            "优先技术支持",
                            "API访问权限"
                        ],
                        "isPopular": True
                    },
                    {
                        "id": 3,
                        "name": "定制版",
                        "price": "联系我们",
                        "period": "获取报价",
                        "features": [
                            "完全定制化功能",
                            "专属客户经理",
                            "私有部署选项",
                            "24/7技术支持"
                        ],
                        "isPopular": False
                    }
                ],
                "keyMetrics": [
                    {
                        "id": 1,
                        "value": "500+",
                        "label": "活跃企业客户"
                    },
                    {
                        "id": 2,
                        "value": "9999+",
                        "label": "自动化任务"
                    },
                    {
                        "id": 3,
                        "value": "98%",
                        "label": "系统稳定性"
                    },
                    {
                        "id": 4,
                        "value": "10000+",
                        "label": "消息发送量"
                    }
                ],
                "dashboardData": [
                    {
                        "id": 1,
                        "title": "自动化任务完成率",
                        "trend": "up",
                        "trendValue": 0,
                        "value": 0,
                        "footer": "较昨日"
                    },
                    {
                        "id": 2,
                        "title": "消息送达率",
                        "trend": "up",
                        "trendValue": 0,
                        "value": 0,
                        "footer": "较昨日"
                    },
                    {
                        "id": 3,
                        "title": "AI辅助功能使用率",
                        "trend": "down",
                        "trendValue": 0,
                        "value": 0,
                        "footer": "较昨日"
                    },
                    {
                        "id": 4,
                        "title": "系统状态",
                        "value": "正常运行",
                        "status": "abnormal",
                        "footer": "版本: v1.0.0"
                    }
                ],
                "testimonials": [
                    {
                        "id": 1,
                        "quote": "LeafAuto帮助我们公司节省了大量的人力成本，消息发送效率提升了60%以上。",
                        "customerName": "张三",
                        "customerCompany": "某科技公司市场总监",
                        "customerAvatar": "@/assets/images/user-avatar.svg"
                    },
                    {
                        "id": 2,
                        "quote": "数据分析功能非常强大，让我们能够精准了解客户需求，提升转化率。",
                        "customerName": "李四",
                        "customerCompany": "某电商平台运营主管",
                        "customerAvatar": "@/assets/images/user-avatar.svg"
                    },
                    {
                        "id": 3,
                        "quote": "系统稳定性非常好，从未出现过 downtime，客服响应也非常及时。",
                        "customerName": "王五",
                        "customerCompany": "某金融机构IT负责人",
                        "customerAvatar": "@/assets/images/user-avatar.svg"
                    }
                ]
            }
            # 保存默认数据到文件
            save_home_data()
    except json.JSONDecodeError as e:
        logger.error(f'首页数据JSON解析错误: {e}')
        # JSON解析错误时也创建默认数据
        home_data = {
            "pricingPlans": [
                {
                    "id": 1,
                    "name": "基础版",
                    "price": 299,
                    "period": "/年",
                    "features": [
                        "基础消息发送功能",
                        "每日1000条发送限额",
                        "无数据分析功能",
                        "邮件支持"
                    ],
                    "isPopular": False
                },
                {
                    "id": 2,
                    "name": "企业版",
                    "price": 899,
                    "period": "/年",
                    "features": [
                        "无限制消息发送",
                        "高级数据分析与报表",
                        "客户画像分析",
                        "优先技术支持",
                        "API访问权限"
                    ],
                    "isPopular": True
                },
                {
                    "id": 3,
                    "name": "定制版",
                    "price": "联系我们",
                    "period": "获取报价",
                    "features": [
                        "完全定制化功能",
                        "专属客户经理",
                        "私有部署选项",
                        "24/7技术支持"
                    ],
                    "isPopular": False
                }
            ],
            "keyMetrics": [
                {
                    "id": 1,
                    "value": "500+",
                    "label": "活跃企业客户"
                },
                {
                    "id": 2,
                    "value": "9999+",
                    "label": "自动化任务"
                },
                {
                    "id": 3,
                    "value": "98%",
                    "label": "系统稳定性"
                },
                {
                    "id": 4,
                    "value": "10000+",
                    "label": "消息发送量"
                }
            ],
            "dashboardData": [
                {
                    "id": 1,
                    "title": "自动化任务完成率",
                    "trend": "up",
                    "trendValue": 3.2,
                    "value": 12,
                    "footer": "较昨日"
                },
                {
                    "id": 2,
                    "title": "消息送达率",
                    "trend": "up",
                    "trendValue": 1.8,
                    "value": 97.5,
                    "footer": "较昨日"
                },
                {
                    "id": 3,
                    "title": "AI辅助功能使用率",
                    "trend": "down",
                    "trendValue": 0.5,
                    "value": 6,
                    "footer": "较昨日"
                },
                {
                    "id": 4,
                    "title": "系统状态",
                    "value": "正常运行",
                    "status": "abnormal",
                    "footer": "版本: v1.0.0"
                }
            ],
            "testimonials": [
                {
                    "id": 1,
                    "quote": "LeafAuto帮助我们公司节省了大量的人力成本，消息发送效率提升了60%以上。",
                    "customerName": "张三",
                    "customerCompany": "某科技公司市场总监",
                    "customerAvatar": "@/assets/images/user-avatar.svg"
                },
                {
                    "id": 2,
                    "quote": "数据分析功能非常强大，让我们能够精准了解客户需求，提升转化率。",
                    "customerName": "李四",
                    "customerCompany": "某电商平台运营主管",
                    "customerAvatar": "@/assets/images/user-avatar.svg"
                },
                {
                    "id": 3,
                    "quote": "系统稳定性非常好，从未出现过 downtime，客服响应也非常及时。",
                    "customerName": "王五",
                    "customerCompany": "某金融机构IT负责人",
                    "customerAvatar": "@/assets/images/user-avatar.svg"
                }
            ]
        }
        save_home_data()
    except Exception as e:
        logger.error(f'加载首页数据异常: {e}')
        home_data = {
            "pricingPlans": [],
            "keyMetrics": [],
            "dashboardData": [],
            "testimonials": []
        }

    # 动态更新dashboard数据（与昨日对比）
    try:
        # 获取当前日期和昨日日期
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)
        
        # 加载历史统计数据
        history_stats = load_daily_stats()
        
        # 获取昨日数据（从历史记录中获取）
        yesterday_str = yesterday.isoformat()
        yesterday_data = history_stats.get(yesterday_str, {
            "automation_completion_rate": 0,  # 默认值
            "message_delivery_rate": 0,       # 默认值
            "ai_usage_rate": 0               # 默认值
        })
        
        # 模拟获取今日数据（实际项目中应该从实时数据中计算）
        # 这里使用模拟数据，实际应该从系统运行数据中计算
        today_data = {
            "automation_completion_rate": calculate_automation_completion_rate(),  # 今日自动化任务完成率
            "message_delivery_rate": calculate_message_delivery_rate(),          # 今日消息送达率
            "ai_usage_rate": calculate_ai_usage_rate()                          # 今日AI辅助功能使用率
        }
        
        # 保存今日数据供明天使用
        save_daily_stats(today.isoformat(), today_data)
        
        # 更新dashboard数据
        for item in home_data.get("dashboardData", []):
            if item.get("id") == 1:  # 自动化任务完成率
                today_value = today_data["automation_completion_rate"]
                yesterday_value = yesterday_data["automation_completion_rate"]
                trend_value = round(today_value - yesterday_value, 1)
                
                item["value"] = today_value
                item["trend"] = "up" if trend_value >= 0 else "down"
                item["trendValue"] = abs(trend_value)
                
            elif item.get("id") == 2:  # 消息送达率
                today_value = today_data["message_delivery_rate"]
                yesterday_value = yesterday_data["message_delivery_rate"]
                trend_value = round(today_value - yesterday_value, 1)
                
                item["value"] = today_value
                item["trend"] = "up" if trend_value >= 0 else "down"
                item["trendValue"] = abs(trend_value)
                
            elif item.get("id") == 3:  # AI辅助功能使用率
                today_value = today_data["ai_usage_rate"]
                yesterday_value = yesterday_data["ai_usage_rate"]
                trend_value = round(today_value - yesterday_value, 1)
                
                item["value"] = today_value
                item["trend"] = "up" if trend_value >= 0 else "down"
                item["trendValue"] = abs(trend_value)
    
    except Exception as e:
        logger.error(f'更新dashboard数据失败: {e}')
        # 如果更新失败，保持原有数据不变

    # 动态更新系统状态卡片
    try:
        from wechat_instance import get_wechat_instance
        wx = get_wechat_instance()
        is_logged_in = wx.IsOnline()

        # 查找系统状态卡片（id为4的dashboardData项）
        for item in home_data.get("dashboardData", []):
            if item.get("id") == 4:
                if is_logged_in:
                    item["value"] = "微信正常"
                    item["status"] = "normal"
                    item["footer"] = "微信已登录"
                else:
                    item["value"] = "未登录"
                    item["status"] = "abnormal"
                    item["footer"] = "请登录微信"
                break
    except Exception as e:
        print(f'更新微信状态失败: {e}')
        # 如果获取微信状态失败，设置系统状态为异常
        for item in home_data.get("dashboardData", []):
            if item.get("id") == 4:
                item["value"] = "微信异常"
                item["status"] = "abnormal"
                item["footer"] = "请检查微信客户端"
                break

    return home_data


def get_ai_stats():
    global reply_history

    stats = {
        'replyRate': 0,
        'averageTime': 0,
        'satisfactionRate': 100,
    }

    if not reply_history:
        return stats

    total_messages = len(reply_history)
    replied_messages = sum(1 for item in reply_history if item.get('status') == 'replied')
    stats['replyRate'] = round((replied_messages / total_messages) * 100, 2) if total_messages > 0 else 0

    response_times = []
    for item in reply_history:
        if item.get('status') == 'replied' and 'responseTime' in item:
            response_times.append(item['responseTime'])

    stats['averageTime'] = round(sum(response_times) / len(response_times), 2) if response_times else 0
    return stats


def save_tasks():
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        import traceback
        traceback.print_exc()


def load_ai_data():
    global ai_settings
    try:
        if os.path.exists(AI_DATA_FILE):
            with open(AI_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                ai_settings = data.get('settings', {})
        else:
            ai_settings = {}
    except Exception as e:
        ai_settings = {}
    return ai_settings


def load_reply_history():
    """从reply_history.json加载回复历史数据"""
    global reply_history
    try:
        if os.path.exists(REPLY_HISTORY_FILE):
            with open(REPLY_HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reply_history = data.get('history', [])
        else:
            reply_history = []
        
        # 确保reply_history是列表类型
        if not isinstance(reply_history, list):
            reply_history = []
            
    except Exception as e:
        reply_history = []
    return reply_history


def save_ai_data():
    try:
        data = {
            'settings': ai_settings
        }
        with open(AI_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'保存AI数据失败: {e}')


def save_reply_history():
    """保存回复历史数据到reply_history.json"""
    global reply_history
    try:
        # 计算统计数据
        total_replies = len(reply_history)
        successful_replies = sum(1 for item in reply_history if item.get('status') == 'replied')
        failed_replies = total_replies - successful_replies
        
        # 计算平均响应时间
        response_times = [item.get('responseTime', 0) for item in reply_history 
                         if item.get('status') == 'replied' and 'responseTime' in item]
        average_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0
        
        # 构建保存的数据结构
        data = {
            'total_replies': total_replies,
            'successful_replies': successful_replies,
            'failed_replies': failed_replies,
            'average_response_time': average_response_time,
            'history': reply_history
        }
        
        os.makedirs(os.path.dirname(REPLY_HISTORY_FILE), exist_ok=True)
        with open(REPLY_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"成功保存 {total_replies} 条回复历史记录")
        return True
    except Exception as e:
        logger.error(f'保存回复历史失败: {e}')
        return False


def load_daily_stats():
    """加载每日统计数据"""
    daily_stats_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'daily_stats.json')
    try:
        if os.path.exists(daily_stats_file):
            with open(daily_stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        print(f'加载每日统计数据失败: {e}')
        return {}


def save_daily_stats(date, stats):
    """保存每日统计数据"""
    daily_stats_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'daily_stats.json')
    try:
        # 加载现有数据
        existing_data = load_daily_stats()
        # 更新指定日期的数据
        existing_data[date] = stats
        
        # 保存数据
        os.makedirs(os.path.dirname(daily_stats_file), exist_ok=True)
        with open(daily_stats_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'保存每日统计数据失败: {e}')


def calculate_automation_completion_rate():
    """计算自动化任务完成率"""
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks.values() if task.get('status') == 'completed')
    
    if total_tasks > 0:
        return round((completed_tasks / total_tasks) * 100, 1)
    else:
        return 0


def calculate_message_delivery_rate():
    """计算消息送达率"""
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks.values() if task.get('status') == 'completed')
    failed_tasks = sum(1 for task in tasks.values() if task.get('status') == 'failed')
    
    # 送达率 = 成功任务数 / (成功任务数 + 失败任务数)
    if completed_tasks + failed_tasks > 0:
        return round((completed_tasks / (completed_tasks + failed_tasks)) * 100, 1)
    else:
        return 0


def calculate_ai_usage_rate():
    """计算AI辅助功能使用率"""
    global reply_history
    
    # reply_history是列表格式，计算成功回复的比例
    total_replies = len(reply_history)
    successful_replies = sum(1 for item in reply_history if item.get('status') == 'replied')
    
    # 如果有总回复记录，计算使用率
    if total_replies > 0:
        return round((successful_replies / total_replies) * 100, 1)
    else:
        return 0


def add_task(task_data):
    task_id = str(uuid.uuid4())
    task_data['id'] = task_id
    task_data['createdAt'] = datetime.datetime.now().isoformat()
    tasks[task_id] = task_data
    save_tasks()
    return task_data


def delete_task(task_id):
    if task_id in tasks:
        del tasks[task_id]
        save_tasks()
        return True
    return False


def update_task_status(task_id, status, error_message=None):
    if task_id not in tasks:
        return None

    tasks[task_id]['status'] = status
    tasks[task_id]['updatedAt'] = datetime.datetime.now().isoformat()

    # 如果有错误信息，保存到任务中
    if error_message is not None:
        tasks[task_id]['errorMessage'] = error_message
    elif 'errorMessage' in tasks[task_id]:
        # 如果没有错误信息但之前有，则清除
        del tasks[task_id]['errorMessage']

    save_tasks()

    return tasks[task_id]


def clear_tasks():
    tasks.clear()
    save_tasks()
    return True


def import_tasks(imported_tasks):
    """导入任务列表
    Args:
        imported_tasks: 要导入的任务列表
    Returns:
        tuple: (成功导入的任务数量, 总任务数量)
    """
    total_count = len(imported_tasks)
    success_count = 0

    for task_data in imported_tasks:
        # 检查必要字段
        if not all(key in task_data for key in ['recipient', 'sendTime', 'messageContent']):
            continue

        # 如果任务没有ID，生成一个新的
        if 'id' not in task_data or not task_data['id']:
            task_id = str(uuid.uuid4())
            task_data['id'] = task_id
        else:
            task_id = task_data['id']

        # 确保任务有创建时间
        if 'createdAt' not in task_data:
            task_data['createdAt'] = datetime.datetime.now().isoformat()

        # 设置状态为待执行
        task_data['status'] = 'pending'

        # 添加或更新任务
        tasks[task_id] = task_data
        success_count += 1

    # 保存更改
    save_tasks()
    return success_count, total_count


def save_ai_settings(settings_data):
    global ai_settings
    required_fields = ['aiStatus', 'replyDelay', 'minReplyInterval', 'contactPerson', 'aiPersona', 'customRules', 'onlyAt']
    for field in required_fields:
        if field not in settings_data:
            print(f'警告: 设置数据中缺少字段 {field}')
            if field == 'aiStatus':
                settings_data[field] = False
            elif field == 'replyDelay':
                settings_data[field] = 5
            elif field == 'minReplyInterval':
                settings_data[field] = 60
            elif field == 'contactPerson':
                settings_data[field] = ''
            elif field == 'aiPersona':
                settings_data[field] = '我是一个友好、专业的AI助手，致力于为用户提供准确、及时的帮助。'
            elif field == 'customRules':
                settings_data[field] = []
            elif field == 'onlyAt':
                settings_data[field] = False

    ai_settings = settings_data
    ai_settings['updatedAt'] = datetime.datetime.now().isoformat()
    save_ai_data()
    return ai_settings


def add_ai_history(history_data):
    global reply_history
    history_data['id'] = str(uuid.uuid4())
    history_data['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    reply_history.append(history_data)
    save_reply_history()
    return history_data


# 在函数定义完成后加载数据
load_tasks()
load_ai_data()
load_reply_history()
load_home_data()
