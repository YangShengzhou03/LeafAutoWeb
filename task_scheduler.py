import threading
import time
from datetime import datetime, timedelta

from data_manager import (increment_message_count, load_tasks,
                          update_task_status)
from logging_config import get_logger, handle_errors
from wechat_instance import get_wechat_instance, is_wechat_online


def send_msg(who, msg):
    """发送微信消息"""
    try:
        wx = get_wechat_instance()
        if wx is None:
            return {"status": "failed", "message": "微信未登录，无法发送消息"}

        # 检查微信是否在线
        if not is_wechat_online():
            return {"status": "failed", "message": "微信未登录，无法发送消息"}

        if not increment_message_count():
            # 添加历史记录但状态为pending（未回复）
            from data_manager import add_ai_history
            from datetime import datetime
            history_data = {
                "sender": who,
                "message": "",
                "reply": msg,
                "status": "pending",
                "responseTime": 0,
                "timestamp": datetime.now().isoformat(),
            }
            add_ai_history(history_data)
            return {"status": "failed", "message": "信息余量耗尽，无法发送消息"}

        result = wx.SendMsg(msg, who)
        if result["status"] == "成功":
            # 增加消息配额计数
            return {"status": "success", "message": "消息发送成功"}
        else:
            return {"status": "failed", "message": result.get("message", "发送失败")}
    except Exception as e:
        logger.error(f"发送消息时发生错误: {e}")
        return {"status": "failed", "message": f"发送失败: {str(e)}"}


# 获取日志器
logger = get_logger(__name__)


class TaskScheduler:
    """
    定时任务调度器类

    负责管理定时任务的执行，包括任务检查、状态更新和重复任务处理

    Attributes:
        running (bool): 调度器运行状态
        thread (threading.Thread): 调度器线程
        stop_event (threading.Event): 停止事件信号

    Example:
        >>> scheduler = TaskScheduler()
        >>> scheduler.start()
        >>> scheduler.running
        True
    """

    def __init__(self):
        """初始化任务调度器"""
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()
        self.last_system_time = datetime.now()
        self.task_execution_times = {}  # 记录任务执行时间，用于性能监控

    @handle_errors()
    def check_and_execute_tasks(self):
        """
        检查并执行到期任务

        遍历所有待执行任务，执行已到期的任务并更新状态

        Returns:
            int: 本次执行的任务数量

        Example:
            >>> scheduler = TaskScheduler()
            >>> executed = scheduler.check_and_execute_tasks()
            >>> executed >= 0
            True
        """
        # 监控系统时间突变
        current_time = datetime.now()
        time_diff = (current_time - self.last_system_time).total_seconds()
        self.last_system_time = current_time

        # 如果检测到系统时间向后调整超过1小时，记录警告
        if time_diff < -3600:
            logger.warning(f"检测到系统时间向后调整: {time_diff:.1f}秒，可能影响任务调度")
        # 如果检测到系统时间向前跳跃超过1小时，记录警告
        elif time_diff > 3600:
            logger.warning(f"检测到系统时间向前跳跃: {time_diff:.1f}秒，可能影响任务调度")

        tasks = load_tasks()
        executed_count = 0

        # 检查是否还有待执行的任务
        pending_tasks = [
            task for task in tasks.values() if task.get("status") == "pending"
        ]

        # 如果没有待执行的任务，自动停止调度器
        if not pending_tasks:
            logger.info("没有待执行的任务，调度器将自动停止")
            self.stop()
            return executed_count

        for task_id, task in tasks.items():
            if task.get("status") == "pending":
                send_time_str = task.get("sendTime")
                if send_time_str:
                    try:
                        # 处理时间格式，支持带时区和不带时区的时间
                        if "Z" in send_time_str:
                            send_time = datetime.fromisoformat(
                                send_time_str.replace("Z", "+00:00")
                            )
                        elif "+" in send_time_str or "-" in send_time_str:
                            send_time = datetime.fromisoformat(send_time_str)
                        else:
                            # 如果没有时区信息，假设为本地时间
                            send_time = datetime.fromisoformat(send_time_str)

                        # 精确到秒级别的时间比较
                        # 将时间都截断到秒级别进行比较
                        current_time_seconds = current_time.replace(microsecond=0)
                        send_time_seconds = send_time.replace(microsecond=0)

                        if current_time_seconds >= send_time_seconds:
                            # 记录任务执行开始时间
                            start_time = time.time()

                            # 执行任务
                            self.execute_task(task_id, task)
                            executed_count += 1

                            # 记录任务执行时间
                            execution_time = time.time() - start_time
                            self.task_execution_times[task_id] = execution_time

                            # 如果任务执行时间过长（超过5秒），记录警告
                            if execution_time > 5.0:
                                logger.warning(
                                    f"任务 {task_id} 执行时间过长: {execution_time:.2f}秒"
                                )

                    except (ValueError, TypeError) as e:
                        logger.error(f"任务 {task_id} 时间格式错误: {e}")
                        update_task_status(task_id, "failed", str(e))

        if executed_count > 0:
            avg_execution_time = (
                sum(self.task_execution_times.values()) / len(self.task_execution_times)
                if self.task_execution_times
                else 0
            )
            logger.info(
                f"本次检查执行了 {executed_count} 个任务，平均执行时间: {avg_execution_time:.3f}秒"
            )
        else:
            logger.info("没有到期的任务")
            return executed_count

    def execute_task(self, task_id, task):
        """执行单个任务"""
        try:
            # 检查微信是否在线
            if not is_wechat_online():
                logger.warning(f"微信未登录，跳过任务 {task_id}")
                update_task_status(task_id, "failed", "微信未登录")
                return

            recipient = task.get("recipient", "")
            message_content = task.get("messageContent", "")

            if recipient and message_content:
                # 发送消息
                result = send_msg(recipient, message_content)

                if result.get("status") == "success":
                    # 更新任务状态为已完成
                    update_task_status(task_id, "completed")
                    logger.info(f"任务执行成功: {task_id} -> {recipient}")

                    # 处理重复任务
                    self.handle_repeat_task(task_id, task)
                else:
                    # 发送失败，更新任务状态为失败
                    error_msg = result.get("message", "未知错误")
                    logger.error(f"任务发送失败 {task_id}: {error_msg}")
                    update_task_status(task_id, "failed", error_msg)
            else:
                logger.warning(f"任务数据不完整: {task_id}")
                update_task_status(task_id, "failed", "任务数据不完整")

        except Exception as e:
            error_msg = f"执行任务时发生异常: {str(e)}"
            logger.error(f"任务执行失败 {task_id}: {error_msg}")
            update_task_status(task_id, "failed", error_msg)

        # 检查是否所有任务都已完成或失败，自动停止调度器
        tasks = load_tasks()
        pending_tasks = [
            task for task in tasks.values() if task.get("status") == "pending"
        ]
        if not pending_tasks:
            logger.info("所有任务已完成或失败，调度器将自动停止")
            self.stop()

    def handle_repeat_task(self, task_id, task):
        """处理重复任务逻辑"""
        repeat_type = task.get("repeatType", "none")

        if repeat_type != "none":
            # 创建新的重复任务
            new_task = task.copy()

            # 根据重复类型计算下一次执行时间
            current_time = datetime.now()

            # 处理时间格式，支持带时区和不带时区的时间
            send_time_str = task["sendTime"]
            if "Z" in send_time_str:
                send_time = datetime.fromisoformat(send_time_str.replace("Z", "+00:00"))
            elif "+" in send_time_str or "-" in send_time_str:
                send_time = datetime.fromisoformat(send_time_str)
            else:
                # 如果没有时区信息，假设为本地时间
                send_time = datetime.fromisoformat(send_time_str)

            if repeat_type == "daily":
                # 每天重复（保持原有的秒精度）
                new_send_time = send_time.replace(
                    hour=send_time.hour,
                    minute=send_time.minute,
                    second=send_time.second,
                    microsecond=0,
                ) + timedelta(days=1)
            elif repeat_type == "workday":
                # 工作日重复（周一到周五）
                next_day = send_time
                while True:
                    next_day += timedelta(days=1)
                    if next_day.weekday() < 5:  # 0-4 表示周一到周五
                        break
                new_send_time = next_day.replace(
                    hour=send_time.hour,
                    minute=send_time.minute,
                    second=send_time.second,
                    microsecond=0,
                )
            elif repeat_type == "holiday":
                # 节假日重复（周六和周日）
                next_day = send_time
                while True:
                    next_day += timedelta(days=1)
                    if next_day.weekday() >= 5:  # 5-6 表示周六和周日
                        break
                new_send_time = next_day.replace(
                    hour=send_time.hour,
                    minute=send_time.minute,
                    second=send_time.second,
                    microsecond=0,
                )
            elif repeat_type == "custom" and task.get("repeatDays"):
                # 自定义重复天数
                repeat_days = int(task.get("repeatDays", 1))
                new_send_time = send_time.replace(
                    hour=send_time.hour,
                    minute=send_time.minute,
                    second=send_time.second,
                    microsecond=0,
                ) + timedelta(days=repeat_days)
            else:
                return

            # 更新任务时间为下一次执行时间
            new_task["sendTime"] = new_send_time.isoformat()
            new_task["status"] = "pending"
            new_task["createdAt"] = datetime.now().isoformat()

            # 确保删除原任务的错误信息（如果有）
            if "errorMessage" in new_task:
                del new_task["errorMessage"]

            # 保存新任务
            from data_manager import add_task

            add_task(new_task)

    @handle_errors()
    def start(self):
        """
        启动任务调度器

        启动后台线程定期检查并执行任务

        Returns:
            bool: 启动成功返回True，如果已经在运行返回False

        Example:
            >>> scheduler = TaskScheduler()
            >>> scheduler.start()
            True
        """
        if self.running:
            logger.warning("定时任务调度器已经在运行中")
            return False

        self.running = True
        self.stop_event.clear()

        # 创建调度线程
        def scheduler_loop():
            last_check_time = datetime.now()
            consecutive_errors = 0
            adaptive_interval = 1.0  # 初始间隔1秒

            while self.running:
                try:
                    executed_count = self.check_and_execute_tasks()
                    consecutive_errors = 0  # 重置连续错误计数

                    # 动态调整检查间隔，处理时间突变
                    current_time = datetime.now()
                    time_diff = (current_time - last_check_time).total_seconds()
                    last_check_time = current_time

                    # 如果没有执行任何任务，根据时间差动态调整等待时间
                    if executed_count == 0:
                        # 处理时间突变（如系统时间被调整）
                        if abs(time_diff) > 5.0:  # 放宽时间突变阈值到5秒
                            logger.warning(f"检测到时间突变: {time_diff:.3f}秒，重新校准调度器")
                            # 立即进行下一次检查，不等待
                            continue

                        # 自适应间隔调整：根据系统负载动态调整检查频率
                        if adaptive_interval > 0.1:  # 最小间隔100ms
                            # 如果没有任务执行，逐渐增加间隔以减少CPU占用
                            adaptive_interval = min(
                                adaptive_interval * 1.1, 5.0
                            )  # 最大5秒

                        # 计算到下一秒开始需要等待的毫秒数，结合自适应间隔
                        now = datetime.now()
                        wait_ms = min(
                            1000 - now.microsecond // 1000,
                            int(adaptive_interval * 1000),
                        )

                        # 确保等待时间在合理范围内（50ms - 5000ms）
                        wait_ms = max(50, min(wait_ms, 5000))

                        if wait_ms > 0:
                            time.sleep(wait_ms / 1000.0)
                    else:
                        # 如果有任务执行，重置自适应间隔到更积极的值
                        adaptive_interval = 0.5  # 执行任务后使用更短的间隔

                except Exception as e:
                    consecutive_errors += 1
                    logger.error(f"调度器循环发生错误 ({consecutive_errors}): {e}")

                    # 根据连续错误次数动态调整等待时间
                    if consecutive_errors <= 3:
                        # 前3次错误使用指数退避
                        wait_time = min(2**consecutive_errors, 30)  # 最大30秒
                    else:
                        # 超过3次错误，使用固定长间隔
                        wait_time = 30

                    logger.warning(f"调度器将在 {wait_time} 秒后重试")
                    time.sleep(wait_time)

        self.thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.thread.start()
        logger.info("定时任务调度器已启动")
        return True

    def get_status_info(self):
        """
        获取调度器状态信息

        Returns:
            dict: 包含调度器运行状态、性能指标和统计信息的字典

        Example:
            >>> scheduler = TaskScheduler()
            >>> status = scheduler.get_status_info()
            >>> 'running' in status
            True
        """
        tasks = load_tasks()
        pending_tasks = [
            task for task in tasks.values() if task.get("status") == "pending"
        ]
        completed_tasks = [
            task for task in tasks.values() if task.get("status") == "completed"
        ]
        failed_tasks = [
            task for task in tasks.values() if task.get("status") == "failed"
        ]

        # 计算平均执行时间
        avg_execution_time = 0.0
        if self.task_execution_times:
            avg_execution_time = sum(self.task_execution_times.values()) / len(
                self.task_execution_times
            )

        return {
            "running": self.running,
            "pending_tasks_count": len(pending_tasks),
            "completed_tasks_count": len(completed_tasks),
            "failed_tasks_count": len(failed_tasks),
            "total_tasks_executed": len(self.task_execution_times),
            "avg_execution_time_seconds": round(avg_execution_time, 3),
            "max_execution_time_seconds": round(
                max(self.task_execution_times.values(), default=0.0), 3
            ),
            "min_execution_time_seconds": round(
                min(self.task_execution_times.values(), default=0.0), 3
            ),
        }

    @handle_errors()
    def stop(self):
        """
        停止任务调度器

        发送停止信号并等待调度器线程结束

        Returns:
            bool: 停止成功返回True，如果已经停止返回False

        Example:
            >>> scheduler = TaskScheduler()
            >>> scheduler.start()
            >>> scheduler.stop()
            True
        """
        if not self.running:
            logger.warning("定时任务调度器已经停止")
            return False

        self.running = False
        self.stop_event.set()
        logger.info("正在停止定时任务调度器...")

        # 等待线程结束（避免在当前线程中join自己）
        if (
            self.thread
            and self.thread.is_alive()
            and self.thread != threading.current_thread()
        ):
            self.thread.join(timeout=5)

        logger.info("定时任务调度器已停止")
        return True


# 全局调度器实例
task_scheduler = TaskScheduler()


def start_task_scheduler():
    """启动定时任务调度器"""
    task_scheduler.start()


def stop_task_scheduler():
    """停止定时任务调度器"""
    task_scheduler.stop()
