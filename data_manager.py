"""
数据管理模块

负责管理应用程序的所有数据存储和加载，包括：
- 任务数据管理
- AI设置管理
- 首页数据管理
- 回复历史管理
- 消息配额管理

提供线程安全的数据访问接口，支持JSON文件持久化存储。
"""

import datetime
import json
import os
import threading
import uuid

from logging_config import get_logger

# 初始化日志器
logger = get_logger(__name__)

# 全局数据存储
tasks = {}
DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "data.json"
)

home_data = {}
HOME_DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "home_data.json"
)

ai_settings = {}
AI_DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "ai_data.json"
)

reply_history = []
REPLY_HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "reply_history.json"
)

# 线程锁
data_lock = threading.Lock()


def load_tasks():
    """
    加载任务数据
    
    Returns:
        dict: 任务数据字典，如果加载失败返回空字典
    """
    global tasks
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
        else:
            tasks = {}
    except (json.JSONDecodeError, FileNotFoundError):
        tasks = {}
    return tasks


def create_default_home_data():
    """创建默认的首页数据"""
    return {
        "pricingPlans": [
            {
                "id": 1,
                "name": "基础版",
                "price": 299,
                "period": "/年",
                "features": ["基础消息发送功能", "每日1000条发送限额", "无数据分析功能", "邮件支持"],
                "isPopular": False,
            },
            {
                "id": 2,
                "name": "企业版",
                "price": 899,
                "period": "/年",
                "features": ["无限制消息发送", "高级数据分析与报表", "客户画像分析", "优先技术支持", "API访问权限"],
                "isPopular": True,
            },
            {
                "id": 3,
                "name": "定制版",
                "price": "联系我们",
                "period": "获取报价",
                "features": ["完全定制化功能", "专属客户经理", "私有部署选项", "24/7技术支持"],
                "isPopular": False,
            },
        ],
        "keyMetrics": [
            {"id": 1, "value": "500+", "label": "活跃企业客户"},
            {"id": 2, "value": "9999+", "label": "自动化任务"},
            {"id": 3, "value": "98%", "label": "系统稳定性"},
            {"id": 4, "value": "10000+", "label": "消息发送量"},
        ],
        "dashboardData": [
            {
                "id": 1,
                "title": "自动化任务完成率",
                "trend": "up",
                "trendValue": 0,
                "value": 0,
                "footer": "较昨日",
            },
            {
                "id": 2,
                "title": "消息送达率",
                "trend": "up",
                "trendValue": 0,
                "value": 0,
                "footer": "较昨日",
            },
            {
                "id": 3,
                "title": "AI辅助功能使用率",
                "trend": "down",
                "trendValue": 0,
                "value": 0,
                "footer": "较昨日",
            },
            {
                "id": 4,
                "title": "系统状态",
                "value": "正常运行",
                "status": "abnormal",
                "footer": "版本: v1.0.0",
            },
        ],
        "testimonials": [
            {
            "id": 1,
            "quote": "LeafAuto帮助我们公司节省了大量的人力成本，消息发送效率提升了80%以上。",
            "customerName": "陈明远",
            "customerCompany": "明远科技集团数字营销总监",
            "customerAvatar": "@/assets/images/user-avatar.svg"
            },
            {
            "id": 2,
            "quote": "Ai托管功能非常强大，好似一个智能助手，能够帮助我们自动回答客户问题，提升客户满意度。",
            "customerName": "林晓薇",
            "customerCompany": "优品电商平台客户运营总监",
            "customerAvatar": "@/assets/images/user-avatar.svg"
            },
            {
            "id": 3,
            "quote": "系统稳定性非常好，从未出现过 downtime，客服响应也非常及时。",
            "customerName": "郑浩然",
            "customerCompany": "星海金融科技公司技术总监",
            "customerAvatar": "@/assets/images/user-avatar.svg"
            }
        ]
    }


def save_home_data():
    """保存首页数据"""
    global home_data
    try:
        os.makedirs(os.path.dirname(HOME_DATA_FILE), exist_ok=True)
        with open(HOME_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(home_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_home_data():
    """加载首页数据"""
    global home_data
    try:
        if os.path.exists(HOME_DATA_FILE):
            with open(HOME_DATA_FILE, "r", encoding="utf-8") as f:
                home_data = json.load(f)
        else:
            home_data = create_default_home_data()
            save_home_data()
    except (json.JSONDecodeError, FileNotFoundError):
        home_data = create_default_home_data()
        save_home_data()
    # 动态更新dashboard数据（与昨日对比）
    try:
        # 获取当前日期和昨日日期
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)

        # 加载历史统计数据
        history_stats = load_daily_stats()

        # 获取昨日数据（从历史记录中获取）
        yesterday_str = yesterday.isoformat()
        yesterday_data = history_stats.get(
            yesterday_str,
            {
                "automation_completion_rate": 0,  # 默认值
                "message_delivery_rate": 0,  # 默认值
                "ai_usage_rate": 0,  # 默认值
            },
        )

        # 模拟获取今日数据（实际项目中应该从实时数据中计算）
        # 这里使用模拟数据，实际应该从系统运行数据中计算
        today_data = {
            "automation_completion_rate": calculate_automation_completion_rate(),  # 今日自动化任务完成率
            "message_delivery_rate": calculate_message_delivery_rate(),  # 今日消息送达率
            "ai_usage_rate": calculate_ai_usage_rate(),  # 今日AI辅助功能使用率
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
        logger.error(f"更新dashboard数据失败: {e}")
        # 如果更新失败，保持原有数据不变

    # 动态更新系统状态卡片
    try:
        from wechat_instance import get_wechat_instance

        wx = get_wechat_instance()
        is_logged_in = wx.IsOnline()

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
        for item in home_data.get("dashboardData", []):
            if item.get("id") == 4:
                item["value"] = "微信异常"
                item["status"] = "abnormal"
                item["footer"] = "请检查微信客户端"
                break

    return home_data


def get_ai_stats():
    """
    获取AI统计数据
    
    Returns:
        dict: 包含回复率、平均响应时间和满意率的统计字典
    """
    global reply_history

    stats = {
        "replyRate": 0,
        "averageTime": 0,
        "satisfactionRate": 100,
    }

    if not reply_history:
        return stats

    total_messages = len(reply_history)
    replied_messages = sum(
        1 for item in reply_history if item.get("status") == "replied"
    )
    stats["replyRate"] = (
        round((replied_messages / total_messages) * 100, 2) if total_messages > 0 else 0
    )

    response_times = []
    for item in reply_history:
        if item.get("status") == "replied" and "responseTime" in item:
            response_times.append(item["responseTime"])

    stats["averageTime"] = (
        round(sum(response_times) / len(response_times), 2) if response_times else 0
    )
    return stats


def save_tasks():
    """
    保存任务数据到文件
    """
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_ai_data():
    """
    加载AI设置数据
    
    Returns:
        dict: AI设置字典，如果加载失败返回空字典
    """
    global ai_settings
    try:
        if os.path.exists(AI_DATA_FILE):
            with open(AI_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                ai_settings = data.get("settings", {})
        else:
            ai_settings = {}
    except Exception:
        ai_settings = {}
    return ai_settings


def load_reply_history():
    """从reply_history.json加载回复历史数据"""
    global reply_history
    try:
        if os.path.exists(REPLY_HISTORY_FILE):
            with open(REPLY_HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                reply_history = data.get("history", [])
        else:
            reply_history = []

        if not isinstance(reply_history, list):
            reply_history = []

    except Exception:
        reply_history = []
    return reply_history


def save_ai_data():
    """
    保存AI设置数据到文件
    """
    try:
        data = {"settings": ai_settings}
        with open(AI_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存AI数据失败: {e}")


def save_reply_history():
    """保存回复历史数据到reply_history.json"""
    global reply_history
    try:
        # 计算统计数据
        total_replies = len(reply_history)
        successful_replies = sum(
            1 for item in reply_history if item.get("status") == "replied"
        )
        failed_replies = total_replies - successful_replies

        # 计算平均响应时间
        response_times = [
            item.get("responseTime", 0)
            for item in reply_history
            if item.get("status") == "replied" and "responseTime" in item
        ]
        average_response_time = (
            round(sum(response_times) / len(response_times), 2) if response_times else 0
        )

        # 构建保存的数据结构
        data = {
            "total_replies": total_replies,
            "successful_replies": successful_replies,
            "failed_replies": failed_replies,
            "average_response_time": average_response_time,
            "history": reply_history,
        }

        os.makedirs(os.path.dirname(REPLY_HISTORY_FILE), exist_ok=True)
        with open(REPLY_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"成功保存 {total_replies} 条回复历史记录")
        return True
    except Exception as e:
        logger.error(f"保存回复历史失败: {e}")
        return False


def load_daily_stats():
    """加载每日统计数据"""
    daily_stats_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "daily_stats.json"
    )
    try:
        if os.path.exists(daily_stats_file):
            with open(daily_stats_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        return {}


def save_daily_stats(date, stats):
    """保存每日统计数据"""
    daily_stats_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "daily_stats.json"
    )
    try:
        # 加载现有数据
        existing_data = load_daily_stats()
        # 更新指定日期的数据
        existing_data[date] = stats

        # 保存数据
        os.makedirs(os.path.dirname(daily_stats_file), exist_ok=True)
        with open(daily_stats_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("保存每日统计数据失败")


def calculate_automation_completion_rate():
    """计算自动化任务完成率"""
    try:
        total_tasks = len(tasks)
        completed_tasks = sum(
            1 for task in tasks.values() if task.get("status") == "completed"
        )

        if total_tasks > 0:
            return round((completed_tasks / total_tasks) * 100, 1)
        else:
            return 0
    except Exception as e:
        logger.error(f"计算自动化任务完成率失败: {e}")
        return 0


def calculate_message_delivery_rate():
    """计算消息送达率"""
    try:
        total_tasks = len(tasks)
        completed_tasks = sum(
            1 for task in tasks.values() if task.get("status") == "completed"
        )
        failed_tasks = sum(1 for task in tasks.values() if task.get("status") == "failed")

        # 送达率 = 成功任务数 / (成功任务数 + 失败任务数)
        if completed_tasks + failed_tasks > 0:
            return round((completed_tasks / (completed_tasks + failed_tasks)) * 100, 1)
        else:
            return 0
    except Exception as e:
        logger.error(f"计算消息送达率失败: {e}")
        return 0


def calculate_ai_usage_rate():
    """计算AI辅助功能使用率"""
    global reply_history

    try:
        # reply_history是列表格式，计算成功回复的比例
        total_replies = len(reply_history)
        successful_replies = sum(
            1 for item in reply_history if item.get("status") == "replied"
        )

        # 如果有总回复记录，计算使用率
        if total_replies > 0:
            return round((successful_replies / total_replies) * 100, 1)
        else:
            return 0
    except Exception as e:
        logger.error(f"计算AI辅助功能使用率失败: {e}")
        return 0


def add_task(task_data):
    """
    添加新任务
    
    Args:
        task_data: 任务数据字典
    
    Returns:
        dict: 添加的任务数据，包含生成的ID和创建时间
    """
    task_id = str(uuid.uuid4())
    task_data["id"] = task_id
    task_data["createdAt"] = datetime.datetime.now().isoformat()
    tasks[task_id] = task_data
    save_tasks()
    return task_data


def delete_task(task_id):
    """
    删除指定任务
    
    Args:
        task_id: 任务ID
    
    Returns:
        bool: True表示删除成功，False表示任务不存在
    """
    if task_id in tasks:
        del tasks[task_id]
        save_tasks()
        return True
    return False


def update_task_status(task_id, status, error_message=None):
    """
    更新任务状态
    
    Args:
        task_id: 任务ID
        status: 新状态
        error_message: 错误信息（可选）
    
    Returns:
        dict: 更新后的任务数据，如果任务不存在则返回None
    """
    if task_id not in tasks:
        return None

    tasks[task_id]["status"] = status
    tasks[task_id]["updatedAt"] = datetime.datetime.now().isoformat()

    # 如果有错误信息，保存到任务中
    if error_message is not None:
        tasks[task_id]["errorMessage"] = error_message
    elif "errorMessage" in tasks[task_id]:
        # 如果没有错误信息但之前有，则清除
        del tasks[task_id]["errorMessage"]

    save_tasks()

    return tasks[task_id]


def clear_tasks():
    """
    清空所有任务
    
    Returns:
        bool: 总是返回True
    """
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
        if not all(
            key in task_data for key in ["recipient", "sendTime", "messageContent"]
        ):
            continue

        # 如果任务没有ID，生成一个新的
        if "id" not in task_data or not task_data["id"]:
            task_id = str(uuid.uuid4())
            task_data["id"] = task_id
        else:
            task_id = task_data["id"]

        # 确保任务有创建时间
        if "createdAt" not in task_data:
            task_data["createdAt"] = datetime.datetime.now().isoformat()

        # 设置状态为待执行
        task_data["status"] = "pending"

        # 添加或更新任务
        tasks[task_id] = task_data
        success_count += 1

    # 保存更改
    save_tasks()
    return success_count, total_count


def save_ai_settings(settings_data):
    """
    保存AI设置
    
    Args:
        settings_data: AI设置数据字典
    
    Returns:
        dict: 保存后的AI设置数据，包含更新时间
    """
    global ai_settings
    required_fields = [
        "aiStatus",
        "replyDelay",
        "minReplyInterval",
        "contactPerson",
        "aiPersona",
        "customRules",
        "onlyAt",
    ]
    for field in required_fields:
        if field not in settings_data:
            if field == "aiStatus":
                settings_data[field] = False
            elif field == "replyDelay":
                settings_data[field] = 5
            elif field == "minReplyInterval":
                settings_data[field] = 60
            elif field == "contactPerson":
                settings_data[field] = ""
            elif field == "aiPersona":
                settings_data[field] = "我是一个友好、专业的AI助手，致力于为用户提供准确、及时的帮助。"
            elif field == "customRules":
                settings_data[field] = []
            elif field == "onlyAt":
                settings_data[field] = False

    ai_settings = settings_data
    ai_settings["updatedAt"] = datetime.datetime.now().isoformat()
    save_ai_data()
    return ai_settings


def add_ai_history(history_data):
    """
    添加AI回复历史记录
    
    Args:
        history_data: 历史记录数据字典
    
    Returns:
        dict: 添加的历史记录数据，包含生成的ID和时间
    """
    global reply_history
    history_data["id"] = str(uuid.uuid4())
    history_data["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reply_history.append(history_data)
    save_reply_history()
    return history_data


def load_message_quota():
    """加载消息配额数据"""
    quota_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "message_quota.json"
    )
    try:
        if os.path.exists(quota_file):
            with open(quota_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 默认配额数据
            default_quota = {
                "daily_limit": 30,
                "used_today": 0,
                "last_reset_date": datetime.datetime.now().date().isoformat(),
                "blocked": False,
                "account_level": "free",  # free: 免费版, basic: 标准版, enterprise: 企业版
            }
            save_message_quota(default_quota)
            return default_quota
    except Exception as e:
        logger.error(f"加载消息配额数据失败: {e}")
        return {
            "daily_limit": 30,
            "used_today": 0,
            "last_reset_date": datetime.datetime.now().date().isoformat(),
            "blocked": False,
            "account_level": "free",
        }


def save_message_quota(quota_data):
    """保存消息配额数据"""
    quota_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "message_quota.json"
    )
    try:
        os.makedirs(os.path.dirname(quota_file), exist_ok=True)
        with open(quota_file, "w", encoding="utf-8") as f:
            json.dump(quota_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存消息配额数据失败: {e}")
        return False


def get_quota_info():
    """获取配额信息，包括账户等级和对应的限额"""
    quota_data = load_message_quota()
    account_level = quota_data.get("account_level", "free")

    # 根据账户等级设置不同的每日限额
    if account_level == "enterprise":
        daily_limit = "unlimited"  # 企业版无限制，使用字符串而不是float('inf')
    elif account_level == "basic":
        daily_limit = 100  # 基础版100条
    else:
        daily_limit = 30  # 免费版30条

    # 检查是否需要重置每日使用量
    current_date = datetime.datetime.now().date().isoformat()
    last_reset_date = quota_data.get("last_reset_date")
    if last_reset_date != current_date:
        quota_data["used_today"] = 0
        quota_data["last_reset_date"] = current_date
        save_message_quota(quota_data)

    # 计算剩余配额，确保不会出现负数
    used_today = quota_data.get("used_today", 0)
    if daily_limit != "unlimited":
        # 如果已使用量超过限额，剩余为0
        if used_today >= daily_limit:
            remaining = 0
        else:
            remaining = daily_limit - used_today
    else:
        remaining = "unlimited"

    return {
        "account_level": account_level,
        "daily_limit": daily_limit,
        "used_today": used_today,
        "remaining": remaining,
        "blocked": quota_data.get("blocked", False),
        "is_unlimited": account_level == "enterprise",
    }


def increment_message_count():
    """增加今日已使用消息计数，如果配额不足则返回False"""
    quota_data = load_message_quota()

    # 检查配额是否已耗尽（企业版除外）
    account_level = quota_data.get("account_level", "free")
    if account_level != "enterprise":
        daily_limit = 100 if account_level == "basic" else 30
        if quota_data.get("used_today", 0) >= daily_limit:
            # 配额已耗尽，不增加计数
            return False

    # 增加计数
    quota_data["used_today"] = quota_data.get("used_today", 0) + 1

    # 检查是否超过限额（企业版除外）
    if account_level != "enterprise":
        daily_limit = 100 if account_level == "basic" else 30
        if quota_data["used_today"] >= daily_limit:
            quota_data["blocked"] = True

    save_message_quota(quota_data)
    return True


def update_account_level(level):
    """
    更新用户账户级别
    
    Args:
        level: 账户级别，可以是 'free', 'basic' 或 'enterprise'
    
    Returns:
        bool: 更新成功返回True，失败返回False
    """
    try:
        # 验证账户级别是否有效
        if level not in ["free", "basic", "enterprise"]:
            logger.error(f"无效的账户级别: {level}")
            return False
        
        # 加载当前配额数据
        quota_data = load_message_quota()
        
        # 更新账户级别
        quota_data["account_level"] = level
        
        # 根据新的账户级别更新每日限额
        if level == "enterprise":
            quota_data["daily_limit"] = "unlimited"
            quota_data["blocked"] = False  # 企业版不限制
        elif level == "basic":
            quota_data["daily_limit"] = 100
            # 如果当前使用量超过新限额，则设置为限额
            if quota_data.get("used_today", 0) > 100:
                quota_data["used_today"] = 100
        else:  # free
            quota_data["daily_limit"] = 30
            # 如果当前使用量超过新限额，则设置为限额
            if quota_data.get("used_today", 0) > 30:
                quota_data["used_today"] = 30
        
        # 保存更新后的配额数据
        save_message_quota(quota_data)
        
        logger.info(f"账户级别已更新为: {level}")
        return True
    except Exception as e:
        logger.error(f"更新账户级别失败: {e}")
        return False


# 在函数定义完成后加载数据
if __name__ == "__main__":
    load_tasks()
    load_ai_data()
    load_reply_history()
    load_home_data()
