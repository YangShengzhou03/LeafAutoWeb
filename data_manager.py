import datetime
import json
import os
import threading
import uuid
from typing import Any, Dict, List

from logging_config import get_logger

logger = get_logger(__name__)

tasks: Dict[str, Any] = {}
DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "data.json"
)

home_data: Dict[str, Any] = {}
HOME_DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "home_data.json"
)

ai_settings: Dict[str, Any] = {}
AI_DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "ai_data.json"
)

reply_history: List[Dict[str, Any]] = []
REPLY_HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "reply_history.json"
)

data_lock = threading.Lock()


def load_tasks():
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
    return {
        "pricingPlans": [
            {
                "id": 1,
                "name": "基础版",
                "price": 299,
                "period": "/年",
                "features": [
                    "社区支持",
                    "基础数据看板",
                    "基础消息发送功能",
                    "每日100条发送限额"
                ],
                "isPopular": False,
            },
            {
                "id": 2,
                "name": "企业版",
                "price": 899,
                "period": "/年",
                "features": [
                    "聊天舆情监控",
                    "无限制消息发送",
                    "尊享VIP技术支持",
                    "高级数据分析与报表",
                    "消息分析与自定义统计"
                ],
                "isPopular": True,
            },
            {
                "id": 3,
                "name": "定制版",
                "price": "联系我们",
                "period": "获取报价",
                "features": [
                    "24*7技术支持",
                    "专属客户经理",
                    "完全定制化功能",
                    "私有化部署选项"
                ],
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
    global home_data
    try:
        os.makedirs(os.path.dirname(HOME_DATA_FILE), exist_ok=True)
        with open(HOME_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(home_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_home_data():
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
    try:
        today = datetime.datetime.now().date()
        yesterday = today - datetime.timedelta(days=1)

        history_stats = load_daily_stats()

        yesterday_str = yesterday.isoformat()
        yesterday_data = history_stats.get(
            yesterday_str,
            {
                "automation_completion_rate": 0,
                "message_delivery_rate": 0,
                "ai_usage_rate": 0,
            },
        )

        today_data = {
            "automation_completion_rate": calculate_automation_completion_rate(),
            "message_delivery_rate": calculate_message_delivery_rate(),
            "ai_usage_rate": calculate_ai_usage_rate(),
        }

        save_daily_stats(today.isoformat(), today_data)

        for item in home_data.get("dashboardData", []):
            if item.get("id") == 1:
                today_value = today_data["automation_completion_rate"]
                yesterday_value = yesterday_data["automation_completion_rate"]
                trend_value = round(today_value - yesterday_value, 1)

                item["value"] = today_value
                item["trend"] = "up" if trend_value >= 0 else "down"
                item["trendValue"] = abs(trend_value)

            elif item.get("id") == 2:
                today_value = today_data["message_delivery_rate"]
                yesterday_value = yesterday_data["message_delivery_rate"]
                trend_value = round(today_value - yesterday_value, 1)

                item["value"] = today_value
                item["trend"] = "up" if trend_value >= 0 else "down"
                item["trendValue"] = abs(trend_value)

            elif item.get("id") == 3:
                today_value = today_data["ai_usage_rate"]
                yesterday_value = yesterday_data["ai_usage_rate"]
                trend_value = round(today_value - yesterday_value, 1)

                item["value"] = today_value
                item["trend"] = "up" if trend_value >= 0 else "down"
                item["trendValue"] = abs(trend_value)

    except Exception as e:
        logger.error(f"更新dashboard数据失败: {e}")

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
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_ai_data():
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
    try:
        data = {"settings": ai_settings}
        with open(AI_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存AI数据失败: {e}")


def save_reply_history():
    global reply_history
    try:
        total_replies = len(reply_history)
        successful_replies = sum(
            1 for item in reply_history if item.get("status") == "replied"
        )
        failed_replies = total_replies - successful_replies

        response_times = [
            item.get("responseTime", 0)
            for item in reply_history
            if item.get("status") == "replied" and "responseTime" in item
        ]

        average_response_time = (
            round(sum(response_times) / len(response_times), 2) if response_times else 0
        )

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
    daily_stats_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "daily_stats.json"
    )
    try:
        existing_data = load_daily_stats()
        existing_data[date] = stats

        os.makedirs(os.path.dirname(daily_stats_file), exist_ok=True)
        with open(daily_stats_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("保存每日统计数据失败")


def calculate_automation_completion_rate():
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
    try:
        total_tasks = len(tasks)
        completed_tasks = sum(
            1 for task in tasks.values() if task.get("status") == "completed"
        )
        failed_tasks = sum(1 for task in tasks.values() if task.get("status") == "failed")

        if completed_tasks + failed_tasks > 0:
            return round((completed_tasks / (completed_tasks + failed_tasks)) * 100, 1)
        else:
            return 0
    except Exception as e:
        logger.error(f"计算消息送达率失败: {e}")
        return 0


def calculate_ai_usage_rate():
    global reply_history

    try:
        total_replies = len(reply_history)
        successful_replies = sum(
            1 for item in reply_history if item.get("status") == "replied"
        )

        if total_replies > 0:
            return round((successful_replies / total_replies) * 100, 1)
        else:
            return 0
    except Exception as e:
        logger.error(f"计算AI辅助功能使用率失败: {e}")
        return 0


def add_task(task_data):
    if "sendTime" in task_data:
        try:
            send_time_str = task_data["sendTime"]
            
            if "Z" in send_time_str:
                dt = datetime.datetime.fromisoformat(send_time_str.replace("Z", "+00:00"))
            elif "+" in send_time_str or "-" in send_time_str:
                dt = datetime.datetime.fromisoformat(send_time_str)
            else:
                dt = datetime.datetime.fromisoformat(send_time_str)
            
            if dt.second != 0:
                dt = dt.replace(second=0, microsecond=0)
            
            task_data["sendTime"] = dt.isoformat()
            
        except (ValueError, TypeError) as e:
            logger.warning(f"任务时间格式错误: {send_time_str}, 错误: {e}")
            task_data["sendTime"] = datetime.datetime.now().replace(second=0, microsecond=0).isoformat()
    
    task_id = str(uuid.uuid4())
    task_data["id"] = task_id
    task_data["createdAt"] = datetime.datetime.now().isoformat()
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

    tasks[task_id]["status"] = status
    tasks[task_id]["updatedAt"] = datetime.datetime.now().isoformat()

    if error_message is not None:
        tasks[task_id]["errorMessage"] = error_message
    elif "errorMessage" in tasks[task_id]:
        del tasks[task_id]["errorMessage"]

    save_tasks()

    return tasks[task_id]


def clear_tasks():
    tasks.clear()
    save_tasks()
    return True


def import_tasks(imported_tasks):
    total_count = len(imported_tasks)
    success_count = 0

    for task_data in imported_tasks:
        if not all(
                key in task_data for key in ["recipient", "sendTime", "messageContent"]
        ):
            continue

        if "sendTime" in task_data:
            try:
                send_time_str = task_data["sendTime"]
                
                if "Z" in send_time_str:
                    dt = datetime.datetime.fromisoformat(send_time_str.replace("Z", "+00:00"))
                elif "+" in send_time_str or "-" in send_time_str:
                    dt = datetime.datetime.fromisoformat(send_time_str)
                else:
                    dt = datetime.datetime.fromisoformat(send_time_str)
                
                if dt.second != 0:
                    dt = dt.replace(second=0, microsecond=0)
                
                task_data["sendTime"] = dt.isoformat()
                
            except (ValueError, TypeError) as e:
                logger.warning(f"任务时间格式错误: {send_time_str}, 错误: {e}")
                continue

        if "id" not in task_data or not task_data["id"]:
            task_id = str(uuid.uuid4())
            task_data["id"] = task_id
        else:
            task_id = task_data["id"]

        if "createdAt" not in task_data:
            task_data["createdAt"] = datetime.datetime.now().isoformat()

        task_data["status"] = "pending"

        tasks[task_id] = task_data
        success_count += 1

    save_tasks()
    return success_count, total_count


def save_ai_settings(settings_data):
    global ai_settings
    required_fields = [
        "aiStatus",
        "replyDelay",
        "minReplyInterval",
        "contactPerson",
        "aiPersona",
        "customRules",
        "onlyAt",
        "groupAtReply",
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
            elif field == "groupAtReply":
                settings_data[field] = False

    ai_settings = settings_data
    ai_settings["updatedAt"] = datetime.datetime.now().isoformat()
    save_ai_data()
    return ai_settings


def add_ai_history(history_data):
    global reply_history
    history_data["id"] = str(uuid.uuid4())
    history_data["time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reply_history.append(history_data)
    save_reply_history()
    return history_data


def load_message_quota():
    quota_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "message_quota.json"
    )
    try:
        if os.path.exists(quota_file):
            with open(quota_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            default_quota = {
                "daily_limit": 30,
                "used_today": 0,
                "last_reset_date": datetime.datetime.now().date().isoformat(),
                "blocked": False,
                "account_level": "free",
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
    quota_data = load_message_quota()
    account_level = quota_data.get("account_level", "free")

    if account_level == "enterprise":
        daily_limit = "unlimited"
    elif account_level == "basic":
        daily_limit = 100
    else:
        daily_limit = 30

    current_date = datetime.datetime.now().date().isoformat()
    last_reset_date = quota_data.get("last_reset_date")
    if last_reset_date != current_date:
        quota_data["used_today"] = 0
        quota_data["last_reset_date"] = current_date
        save_message_quota(quota_data)

    used_today = quota_data.get("used_today", 0)
    if daily_limit != "unlimited":
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


def check_message_quota():
    quota_data = load_message_quota()

    account_level = quota_data.get("account_level", "free")
    if account_level != "enterprise":
        daily_limit = 100 if account_level == "basic" else 30
        if quota_data.get("used_today", 0) >= daily_limit:
            return False

    return True


def increment_message_count():
    quota_data = load_message_quota()

    account_level = quota_data.get("account_level", "free")
    if account_level != "enterprise":
        daily_limit = 100 if account_level == "basic" else 30
        if quota_data.get("used_today", 0) >= daily_limit:
            return False

    quota_data["used_today"] = quota_data.get("used_today", 0) + 1

    if account_level != "enterprise":
        daily_limit = 100 if account_level == "basic" else 30
        if quota_data["used_today"] >= daily_limit:
            quota_data["blocked"] = True

    save_message_quota(quota_data)
    return True


def update_account_level(level):
    try:
        if level not in ["free", "basic", "enterprise"]:
            logger.error(f"无效的账户级别: {level}")
            return False

        quota_data = load_message_quota()

        quota_data["account_level"] = level

        if level == "enterprise":
            quota_data["daily_limit"] = "unlimited"
            quota_data["blocked"] = False
        elif level == "basic":
            quota_data["daily_limit"] = 100
            if quota_data.get("used_today", 0) > 100:
                quota_data["used_today"] = 100
        else:
            quota_data["daily_limit"] = 30
            if quota_data.get("used_today", 0) > 30:
                quota_data["used_today"] = 30

        save_message_quota(quota_data)

        logger.info(f"账户级别已更新为: {level}")
        return True
    except Exception as e:
        logger.error(f"更新账户级别失败: {e}")
        return False


if __name__ == "__main__":
    load_tasks()
    load_ai_data()
    load_reply_history()
    load_home_data()
