import os
import re
import random
import threading
import time
from datetime import datetime, timedelta

from data_manager import (check_message_quota, load_tasks,
                          update_task_status, add_task)
from logging_config import get_logger, handle_errors
from wechat_instance import get_wechat_instance, is_wechat_online

logger = get_logger(__name__)


def send_msg(who, msg):
    try:
        wx = get_wechat_instance()
        if wx is None or not is_wechat_online():
            return {"status": "failed", "message": "微信未登录，无法发送消息"}

        processed_msg = msg.strip()
        if (processed_msg.startswith(("'", '"')) and processed_msg.endswith(("'", '"'))
            and processed_msg.count(processed_msg[0]) == 2):
            processed_msg = processed_msg[1:-1]



        if os.path.exists(processed_msg):
            if not check_message_quota():
                return {"status": "failed", "message": "消息配额已用完，无法发送"}
            
            result = wx.SendFiles(processed_msg, who)
            success_msg = "文件发送成功"
        else:
            windows_path_pattern = re.compile(
                r'^[a-zA-Z]:[\\/]'
                r'([\\/\w\-\.\u4e00-\u9fa5]+)'
                r'$'
            )
            
            if windows_path_pattern.fullmatch(processed_msg):
                logger.warning(f"疑似目录结构但文件不存在：{processed_msg}")
                return {"status": "failed", "message": f"疑似目录结构但文件不存在：{processed_msg}"}  
            else:
                if not check_message_quota():
                    return {"status": "failed", "message": "消息配额已用完，无法发送"}
                if msg.startswith("SendEmotion:"):
                    match = re.search(r'SendEmotion:([\d,，]+)', msg)
                    if match:
                        if not check_message_quota():
                            return {"status": "failed", "message": "消息配额已用完，无法发送"}
                        
                        emotion_str = match.group(1).replace('，', ',')
                        emotion_indices = [int(idx) for idx in emotion_str.split(',')]
                        emotion_index = random.choice(emotion_indices)
                        result = wx.SendEmotion(emotion_index-1, who)
                        success_msg = f"表情包发送成功（选择第{emotion_index}个表情）"
                    else:
                        return {"status": "failed", "message": "表情包格式错误，应为SendEmotion:数字或多个数字用逗号（中文或英文）分隔"}
                else:
                    result = wx.SendMsg(msg, who)
                    success_msg = "消息发送成功"

        if result["status"] == "成功":
            from data_manager import increment_message_count
            increment_message_count()
            return {"status": "success", "message": success_msg}
        else:
            return {"status": "failed", "message": result.get("message", "发送失败")}

    except Exception as e:
        logger.error(f"发送消息/文件时发生错误: {e}")
        return {"status": "failed", "message": f"发送失败: {str(e)}"}

class TaskScheduler:

    def __init__(self):
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()
        self.last_system_time = datetime.now()
        self.task_execution_times = {}

    @handle_errors()
    def check_and_execute_tasks(self):
        current_time = datetime.now()
        time_diff = (current_time - self.last_system_time).total_seconds()
        self.last_system_time = current_time

        if time_diff < -3600:
            logger.warning("检测到系统时间向后调整: %.1f秒，可能影响任务调度", time_diff)
        elif time_diff > 3600:
            logger.warning("检测到系统时间向前跳跃: %.1f秒，可能影响任务调度", time_diff)

        tasks = load_tasks()
        executed_count = 0

        pending_tasks = [
            task for task in tasks.values() if task.get("status") == "pending"
        ]

        if not pending_tasks:
            logger.info("没有待执行的任务，调度器将自动停止")
            self.stop()
            return executed_count

        for task_id, task in tasks.items():
            if task.get("status") == "pending":
                send_time_str = task.get("sendTime")
                if send_time_str:
                    try:
                        if "Z" in send_time_str:
                            send_time = datetime.fromisoformat(
                                send_time_str.replace("Z", "+00:00")
                            ).astimezone()
                        elif "+" in send_time_str or "-" in send_time_str:
                            send_time = datetime.fromisoformat(send_time_str).astimezone()
                        else:
                            send_time = datetime.fromisoformat(send_time_str)

                        current_time_seconds = current_time.replace(microsecond=0)
                        send_time_seconds = send_time.replace(microsecond=0)
                        
                        if send_time_seconds.tzinfo is not None and current_time_seconds.tzinfo is None:
                            current_time_seconds = current_time_seconds.astimezone(send_time_seconds.tzinfo)
                        elif send_time_seconds.tzinfo is None and current_time_seconds.tzinfo is not None:
                            send_time_seconds = send_time_seconds.astimezone(current_time_seconds.tzinfo)

                        if current_time_seconds >= send_time_seconds:
                            start_time = time.time()

                            self.execute_task(task_id, task)
                            executed_count += 1

                            execution_time = time.time() - start_time
                            self.task_execution_times[task_id] = execution_time

                            if execution_time > 5.0:
                                logger.warning(
                                    "任务 %s 执行时间过长: %.2f秒",
                                    task_id, execution_time
                                )

                    except (ValueError, TypeError) as e:
                        logger.error("任务 %s 时间格式错误: %s", task_id, e)
                        update_task_status(task_id, "failed", str(e))
                    except (RuntimeError, ValueError, OSError) as e:
                        logger.error("任务 %s 处理过程中发生未知错误: %s", task_id, e)
                        update_task_status(task_id, "failed", f"处理错误: {str(e)}")

        if executed_count > 0:
            avg_execution_time = (
                sum(self.task_execution_times.values()) / len(self.task_execution_times)
                if self.task_execution_times
                else 0
            )
            logger.info(
                "本次检查执行了 %d 个任务，平均执行时间: %.3f秒",
                executed_count, avg_execution_time
            )
        else:
            logger.info("没有到期的任务")
            return executed_count

    def execute_task(self, task_id, task):
        try:
            if not is_wechat_online():
                logger.warning("微信未登录，跳过任务 %s", task_id)
                update_task_status(task_id, "failed", "微信未登录")
                return

            recipient = task.get("recipient", "")
            message_content = task.get("messageContent", "")

            if recipient and message_content:
                result = send_msg(recipient, message_content)

                if result.get("status") == "success":
                    update_task_status(task_id, "completed")
                    logger.info("任务执行成功: %s -> %s", task_id, recipient)

                    self.handle_repeat_task(task_id, task)
                else:
                    error_msg = result.get("message", "未知错误")
                    logger.error("任务发送失败 %s: %s", task_id, error_msg)
                    update_task_status(task_id, "failed", error_msg)
            else:
                logger.warning("任务数据不完整: %s", task_id)
                update_task_status(task_id, "failed", "任务数据不完整")

        except (RuntimeError, ValueError, OSError, AttributeError) as e:
            error_msg = "执行任务时发生异常: {}".format(str(e))
            logger.error("任务执行失败 %s: %s", task_id, error_msg)
            update_task_status(task_id, "failed", error_msg)

        tasks = load_tasks()
        pending_tasks = [
            task for task in tasks.values() if task.get("status") == "pending"
        ]
        if not pending_tasks:
            logger.info("所有任务已完成或失败，调度器将自动停止")
            self.stop()

    def handle_repeat_task(self, task_id, task):
        repeat_type = task.get("repeatType", "none")

        if repeat_type != "none":
            new_task = task.copy()

            send_time_str = task["sendTime"]
            if "Z" in send_time_str:
                send_time = datetime.fromisoformat(send_time_str.replace("Z", "+00:00"))
            elif "+" in send_time_str or "-" in send_time_str:
                send_time = datetime.fromisoformat(send_time_str)
            else:
                send_time = datetime.fromisoformat(send_time_str)

            if repeat_type == "daily":
                new_send_time = send_time.replace(
                    hour=send_time.hour,
                    minute=send_time.minute,
                    second=send_time.second,
                    microsecond=0,
                ) + timedelta(days=1)
            elif repeat_type == "workday":
                next_day = send_time
                while True:
                    next_day += timedelta(days=1)
                    if next_day.weekday() < 5:
                        break
                new_send_time = next_day.replace(
                    hour=send_time.hour,
                    minute=send_time.minute,
                    second=send_time.second,
                    microsecond=0,
                )
            elif repeat_type == "holiday":
                next_day = send_time
                while True:
                    next_day += timedelta(days=1)
                    if next_day.weekday() >= 5:
                        break
                new_send_time = next_day.replace(
                    hour=send_time.hour,
                    minute=send_time.minute,
                    second=send_time.second,
                    microsecond=0,
                )
            elif repeat_type == "custom":
                repeat_days = task.get("repeatDays", [])
                
                if isinstance(repeat_days, list) and repeat_days:
                    target_days = [int(day) for day in repeat_days]
                    
                    current_day = send_time.weekday()
                    current_day_adjusted = (current_day + 1) % 7
                    
                    next_day = send_time
                    found_next = False
                    
                    for i in range(1, 8):
                        candidate = send_time + timedelta(days=i)
                        candidate_day = (candidate.weekday() + 1) % 7
                        
                        if candidate_day in target_days:
                            next_day = candidate
                            found_next = True
                            break
                    
                    if found_next:
                        new_send_time = next_day.replace(
                            hour=send_time.hour,
                            minute=send_time.minute,
                            second=send_time.second,
                            microsecond=0,
                        )
                    else:
                        new_send_time = send_time.replace(
                            hour=send_time.hour,
                            minute=send_time.minute,
                            second=send_time.second,
                            microsecond=0,
                        ) + timedelta(days=7)
                else:
                    new_send_time = send_time.replace(
                        hour=send_time.hour,
                        minute=send_time.minute,
                        second=send_time.second,
                        microsecond=0,
                    ) + timedelta(days=1)
            else:
                return

            new_task["sendTime"] = new_send_time.isoformat()
            new_task["status"] = "pending"
            new_task["createdAt"] = datetime.now().isoformat()

            if "errorMessage" in new_task:
                del new_task["errorMessage"]

            add_task(new_task)

    @handle_errors()
    def start(self):
        if self.running:
            logger.warning("定时任务调度器已经在运行中")
            return False

        self.running = True
        self.stop_event.clear()

        def scheduler_loop():
            last_check_time = datetime.now()
            consecutive_errors = 0
            adaptive_interval = 1.0

            while self.running:
                try:
                    executed_count = self.check_and_execute_tasks()
                    consecutive_errors = 0

                    time_diff = (datetime.now() - last_check_time).total_seconds()
                    last_check_time = datetime.now()

                    if executed_count == 0:
                        if abs(time_diff) > 5.0:
                            logger.warning("检测到时间突变: %.3f秒，重新校准调度器", time_diff)
                            continue

                        if adaptive_interval > 0.1:
                            adaptive_interval = min(
                                adaptive_interval * 1.1, 5.0
                            )

                        wait_ms = min(
                            1000 - datetime.now().microsecond // 1000,
                            int(adaptive_interval * 1000),
                        )

                        wait_ms = max(50, min(wait_ms, 5000))

                        if wait_ms > 0:
                            time.sleep(wait_ms / 1000.0)
                    else:
                        adaptive_interval = 0.5

                except (RuntimeError, ValueError, OSError, AttributeError) as e:
                    consecutive_errors += 1
                    logger.error("调度器循环发生错误 (%d): %s", consecutive_errors, e)

                    if consecutive_errors <= 3:
                        wait_time = min(2**consecutive_errors, 30)
                    else:
                        wait_time = 30

                    logger.warning("调度器将在 %d 秒后重试", wait_time)
                    time.sleep(wait_time)

        self.thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.thread.start()
        logger.info("定时任务调度器已启动")
        return True

    def get_status_info(self):
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
        if not self.running:
            logger.warning("定时任务调度器已经停止")
            return False

        self.running = False
        self.stop_event.set()
        logger.info("正在停止定时任务调度器...")

        if (
            self.thread
            and self.thread.is_alive()
            and self.thread != threading.current_thread()
        ):
            self.thread.join(timeout=5)

        logger.info("定时任务调度器已停止")
        return True


task_scheduler = TaskScheduler()


def start_task_scheduler():
    task_scheduler.start()


def stop_task_scheduler():
    task_scheduler.stop()
