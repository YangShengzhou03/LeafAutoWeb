import json
import os
import random
import re
import threading
import time
import uuid
from datetime import datetime

from data_manager import add_ai_history
from logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


class AiWorkerThread:
    """
    AI工作线程类
    负责处理微信消息的自动回复功能
    
    Attributes:
        wx_instance: 微信实例对象
        receiver: 接收者列表
        model: AI模型名称
        system_content: 系统提示内容
        only_at: 是否仅回复@消息
        reply_delay: 回复延迟时间（秒）
        min_reply_interval: 最小回复间隔时间（秒）
        rules: 自动回复规则列表
        at_me: @我的标识
        receiver_list: 接收者列表
        listen_list: 监听列表
        last_sent_messages: 最后发送的消息缓存
        _message_lock: 消息处理锁
        _stop_event: 停止事件
        _is_running: 运行状态
        _paused: 暂停状态
        _pause_cond: 暂停条件变量
        start_time: 启动时间
    """

    def __init__(
        self,
        wx_instance,
        receiver,
        model="MoonDarkSide",
        role="You are warm and friendly, reply simply and clearly.",
        only_at=False,
        reply_delay=0,
        min_reply_interval=0,
    ):
        """
        初始化AI工作线程
        
        Args:
            wx_instance: 微信实例对象，不能为空
            receiver: 接收者列表，多个接收者用分号分隔
            model: AI模型名称，默认为MoonDarkSide
            role: 系统提示内容，默认为友好简洁的回复风格
            only_at: 是否仅回复@消息，默认为False
            reply_delay: 回复延迟时间（秒），默认为0秒
            min_reply_interval: 最小回复间隔时间（秒），默认为0秒
        
        Raises:
            ValueError: 当wx_instance参数为空时抛出
        """
        if not wx_instance:
            raise ValueError("wx_instance parameter cannot be empty")

        self.wx_instance = wx_instance
        self.receiver = receiver
        self.model = model
        self.system_content = role
        self.only_at = only_at
        self.reply_delay = reply_delay
        self.min_reply_interval = min_reply_interval
        self.rules = self._load_rules()
        self.at_me = "@" + wx_instance.nickname
        self.receiver_list = [
            r.strip() for r in receiver.replace(";", "；").split("；") if r.strip()
        ]
        self.listen_list = []
        self.last_sent_messages = {}
        self.last_reply_time = 0  # 初始化最后回复时间
        self._message_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._is_running = False
        self._paused = False
        self._pause_cond = threading.Condition(threading.Lock())
        self.start_time = None

        logger.info(
            f"AI worker thread initialized: receiver={self.receiver}, delay={self.reply_delay}s, min_interval={self.min_reply_interval}s"
        )

    def _load_rules(self):
        """
        加载自动回复规则
        
        Returns:
            list: 自动回复规则列表，如果加载失败返回空列表
        """
        try:
            with open("data/ai_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                # 检查数据结构是否正确，确保settings和customRules存在
                if isinstance(data, dict) and "settings" in data:
                    settings = data["settings"]
                    if isinstance(settings, dict) and "customRules" in settings:
                        return settings["customRules"]
                return []
        except FileNotFoundError:
            logger.warning("Auto-reply rules file not found")
            return []
        except json.JSONDecodeError:
            logger.error("Auto-reply rules file parsing failed")
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading rules: {e}")
            return []

    def init_listeners(self):
        """
        初始化消息监听器
        
        Returns:
            bool: True表示初始化成功，False表示失败
        """
        if self._should_stop():
            logger.warning("Listener initialization interrupted")
            return False

        for target in self.receiver_list:
            if self._should_stop():
                return False

            try:
                self.wx_instance.AddListenChat(who=target)
                self.listen_list.append(target)
                logger.info(f"Added listener: {target}")
            except Exception as e:
                logger.error(f"Failed to add listener: {target}, error: {str(e)}")
                # 清理已添加的监听器
                self._cleanup()
                raise e
        return True

    def _get_chat_name(self, who):
        """
        获取聊天名称
        
        Args:
            who: 聊天对象标识
        
        Returns:
            str: 聊天名称，如果无法获取则返回原标识
        """
        if not hasattr(self.wx_instance, "GetChatName"):
            return who
        return self.wx_instance.GetChatName(who)

    def _match_rule(self, msg):
        """
        匹配消息与回复规则
        
        Args:
            msg: 消息内容
        
        Returns:
            list: 匹配的回复内容列表
        """
        if not self.rules or self._should_stop():
            return []

        matched_replies = []
        msg = msg.strip()

        for rule in self.rules:
            if self._should_stop():
                return []

            keyword = rule["keyword"].strip()
            if not keyword:
                continue

            match_type = rule["matchType"]
            try:
                if match_type == "equals" and msg == keyword:
                    matched_replies.append(rule["reply"])
                elif match_type == "contains" and keyword in msg:
                    matched_replies.append(rule["reply"])
                elif match_type == "regex":
                    # 预编译正则表达式以提高性能并验证有效性
                    pattern = re.compile(keyword)
                    if pattern.search(msg):
                        matched_replies.append(rule["reply"])
            except re.error as e:
                logger.error(f"Invalid regular expression '{keyword}': {e}")
            except Exception as e:
                logger.error(f"Error matching rule: {e}")

        return matched_replies

    def _is_target_message(self, message):
        """
        检查消息是否来自目标联系人
        
        Args:
            message: 消息对象
        
        Returns:
            bool: True表示来自目标联系人，False表示不是
        """
        try:
            # 获取发送者信息
            if hasattr(message, 'sender'):
                sender = message.sender
            elif hasattr(message, 'get') and callable(getattr(message, 'get')):
                sender = message.get('sender', '')
            else:
                return False
            
            # 检查发送者是否在接收者列表中
            return sender in self.receiver_list
        except Exception as e:
            logger.error(f"Error checking target message: {e}")
            return False

    def _apply_custom_rules(self, message_content):
        """
        应用自定义回复规则
        
        Args:
            message_content: 消息内容
        
        Returns:
            str: 匹配的回复内容，如果没有匹配则返回空字符串
        """
        matched_replies = self._match_rule(message_content)
        if matched_replies:
            return matched_replies[0]  # 返回第一个匹配的回复
        return ""

    def _generate_ai_reply(self, message_content):
        """
        生成AI回复内容
        
        Args:
            message_content: 消息内容
        
        Returns:
            str: AI生成的回复内容
        """
        # 这里应该调用AI模型生成回复
        # 暂时返回一个简单的回复
        return f"已收到您的消息: {message_content}"

    def _send_reply(self, sender, reply_content):
        """
        发送回复消息
        
        Args:
            sender: 发送者标识
            reply_content: 回复内容
        """
        try:
            # 检查回复内容是否直接是一个存在的文件路径
            if os.path.exists(reply_content):
                response = self.wx_instance.SendFiles(reply_content, sender)
                success_msg = "文件发送成功"
            elif reply_content.startswith("SendEmotion:"):
                # 发送表情包
                match = re.search(r'SendEmotion:([\d,，]+)', reply_content)
                if match:
                    # 同时支持中文逗号和英文逗号
                    emotion_str = match.group(1).replace('，', ',')
                    emotion_indices = [int(idx) for idx in emotion_str.split(',')]
                    # 随机选择一个表情包索引
                    emotion_index = random.choice(emotion_indices)
                    response = self.wx_instance.SendEmotion(emotion_index - 1, sender)
                    success_msg = f"表情包发送成功（选择第{emotion_index}个表情）"
                else:
                    logger.error("表情包格式错误，应为SendEmotion:数字或多个数字用逗号（中文或英文）分隔")
                    return
            else:
                response = self.wx_instance.SendMsg(msg=reply_content, who=sender)
                success_msg = "消息发送成功"
            
            if response.get("status") == "失败":
                logger.error(f"Failed to send reply to {sender}: {response.get('message', 'Unknown error')}")
            else:
                logger.info(f"Reply sent to {sender}: {reply_content} ({success_msg})")
        except Exception as e:
            logger.error(f"Error sending reply to {sender}: {e}")

    def _cleanup(self):
        """
        清理监听器资源
        """
        try:
            for target in self.listen_list:
                if hasattr(self.wx_instance, "RemoveListenChat"):
                    try:
                        self.wx_instance.RemoveListenChat(who=target)
                    except Exception as e:
                        logger.error(f"Failed to remove listener for {target}: {e}")
            self.listen_list.clear()
        except Exception as e:
            logger.error(f"清理监听时出错: {str(e)}")

    def pause(self):
        """
        暂停工作线程
        """
        with self._pause_cond:
            self._paused = True

    def resume(self):
        """
        恢复工作线程
        """
        with self._pause_cond:
            self._paused = False
            self._pause_cond.notify()

    def isPaused(self):
        """
        检查线程是否暂停
        
        Returns:
            bool: True表示已暂停，False表示未暂停
        """
        return self._paused

    def wait_for_resume(self):
        """
        等待线程恢复
        """
        with self._pause_cond:
            while self._paused:
                self._pause_cond.wait()

    def stop(self):
        """
        停止工作线程
        """
        self._stop_event.set()
        self._is_running = False
        self.resume()

    def is_running(self):
        """
        检查线程是否运行
        
        Returns:
            bool: True表示正在运行，False表示已停止
        """
        return self._is_running

    def get_uptime(self):
        """
        获取线程运行时间
        
        Returns:
            int: 运行时间（秒），如果未启动则返回0
        """
        return int(time.time() - self.start_time) if self.start_time else 0

    def _is_ignored_message(self, message):
        """
        检查是否为需要忽略的消息
        
        Args:
            message: 消息对象
        
        Returns:
            bool: True表示需要忽略，False表示需要处理
        """
        try:
            if hasattr(message, "type") and message.type.lower() == "sys":
                return True
            if hasattr(message, "sender") and message.sender == "Self":
                return True
            if hasattr(message, "type") and message.type.lower() != "friend":
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking ignored message: {e}")
            return True

    def _should_stop(self):
        """
        检查是否应该停止线程
        
        Returns:
            bool: True表示应该停止，False表示继续运行
        """
        return self._stop_event.is_set() or not self._is_running

    def _process_message(self, msg):
        """处理接收到的消息"""
        try:
            # 记录消息接收时间戳
            receive_time = time.time()
            
            # 检查消息是否来自目标联系人
            if not self._is_target_message(msg):
                return

            # 检查最小回复间隔
            current_time = time.time()
            if current_time - self.last_reply_time < self.min_reply_interval:
                content = msg.content if hasattr(msg, 'content') else str(msg)
                logger.info(f"[AI接管] 未达到最小回复间隔，忽略消息: {content}")
                return

            # 处理消息内容
            if hasattr(msg, 'content'):
                message_content = msg.content
            elif hasattr(msg, 'get') and callable(getattr(msg, 'get')):
                message_content = msg.get("content", "")
            else:
                message_content = str(msg)
                
            if hasattr(msg, 'sender'):
                sender = msg.sender
            elif hasattr(msg, 'get') and callable(getattr(msg, 'get')):
                sender = msg.get("sender", "")
            else:
                sender = ""

            # 应用自定义规则
            custom_reply = self._apply_custom_rules(message_content)
            if custom_reply:
                # 计算实际响应时间
                actual_response_time = round(time.time() - receive_time, 2)
                
                # 发送自定义回复
                self._send_reply(sender, custom_reply)
                self.last_reply_time = time.time()

                # 记录回复历史（使用实际响应时间）
                history_data = {
                    "sender": sender,
                    "message": message_content,
                    "reply": custom_reply,
                    "status": "replied",
                    "responseTime": actual_response_time,  # 使用实际计算的响应时间
                    "timestamp": datetime.now().isoformat(),
                    "id": str(uuid.uuid4()),
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                add_ai_history(history_data)
                return

            # 生成AI回复
            if self.reply_delay > 0:
                time.sleep(self.reply_delay)

            # 计算实际响应时间（包括延迟）
            actual_response_time = round(time.time() - receive_time, 2)
            
            # 生成AI回复内容
            reply_content = self._generate_ai_reply(message_content)

            # 发送回复
            self._send_reply(sender, reply_content)
            self.last_reply_time = time.time()

            # 记录回复历史（使用实际响应时间）
            history_data = {
                "sender": sender,
                "message": message_content,
                "reply": reply_content,
                "status": "replied",
                "responseTime": actual_response_time,  # 使用实际计算的响应时间
                "timestamp": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            add_ai_history(history_data)

        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}")
            # 记录错误历史
            if hasattr(msg, 'sender'):
                error_sender = msg.sender
            elif hasattr(msg, 'get') and callable(getattr(msg, 'get')):
                error_sender = msg.get("sender", "")
            else:
                error_sender = ""
                
            if hasattr(msg, 'content'):
                error_content = msg.content
            elif hasattr(msg, 'get') and callable(getattr(msg, 'get')):
                error_content = msg.get("content", "")
            else:
                error_content = str(msg)
                
            history_data = {
                "sender": error_sender,
                "message": error_content,
                "reply": "",
                "status": "failed",
                "responseTime": 0,
                "timestamp": datetime.now().isoformat(),
                "id": str(uuid.uuid4()),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            add_ai_history(history_data)

    def run(self):
        """
        主运行循环
        负责初始化监听器、处理消息和清理资源
        """
        self._is_running = True
        self.start_time = time.time()
        logger.info("AI worker thread started")

        try:
            if not self.init_listeners():
                return

            # 初始化测试消息发送
            for receiver in self.receiver_list:
                if self._should_stop():
                    return

                try:
                    response = self.wx_instance.SendMsg(msg=" ", who=receiver)
                    if response.get("status") == "失败":
                        raise ValueError(
                            f"Initialization send failed: {response.get('message', 'Friend with this remark not found')}"
                        )
                except Exception as e:
                    logger.error(f"Initialization send failed for {receiver}: {e}")
                    raise e
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            self._cleanup()
            self._is_running = False
            return

        while not self._should_stop():
            try:
                messages_dict = self.wx_instance.GetListenMessage()
                for chat, messages in messages_dict.items():
                    if self._should_stop():
                        break
                    for message in messages:
                        if self._should_stop() or self._is_ignored_message(message):
                            continue

                        with self._message_lock:
                            self._process_message(message)

            except Exception as e:
                logger.error(f"Exception while processing messages: {e}")
                if self._should_stop():
                    break
                time.sleep(1)  # 发生错误时增加等待时间
            else:
                time.sleep(0.1)

        self._cleanup()
        self._is_running = False
        logger.info("AI worker thread stopped")


class AiWorkerManager:
    """
    AI工作管理器类（单例模式）
    负责管理多个AI工作线程的创建、停止和状态查询
    
    Attributes:
        _instance: 单例实例
        workers: 工作线程字典
        lock: 线程安全锁
    """
    
    _instance = None

    def __new__(cls):
        """
        单例模式实现
        
        Returns:
            AiWorkerManager: 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.workers = {}
            cls._instance.lock = threading.Lock()
        return cls._instance

    def start_worker(
        self,
        wx_instance,
        receiver,
        model="MoonDarkSide",
        role="You are warm and friendly, reply simply and clearly.",
        only_at=False,
        reply_delay=0,
        min_reply_interval=0,
    ):
        """
        启动AI工作线程
        
        Args:
            wx_instance: 微信实例对象
            receiver: 接收者列表
            model: AI模型名称
            role: 系统提示内容
            only_at: 是否仅回复@消息
            reply_delay: 回复延迟时间（秒）
            min_reply_interval: 最小回复间隔时间（秒）
        
        Returns:
            bool: True表示启动成功，False表示启动失败
        """
        with self.lock:
            worker_key = f"{receiver}_{model}"
            if worker_key in self.workers:
                return False

            worker = AiWorkerThread(
                wx_instance,
                receiver,
                model,
                role,
                only_at,
                reply_delay,
                min_reply_interval,
            )
            self.workers[worker_key] = worker

            try:
                thread = threading.Thread(target=worker.run, daemon=True)
                thread.start()

                time.sleep(0.1)
                if not worker.is_running():
                    del self.workers[worker_key]
                    return False

                return True
            except Exception as e:
                if worker_key in self.workers:
                    del self.workers[worker_key]
                logger.error(f"Failed to start worker: {e}")
                return False

    def stop_worker(self, receiver, model="MoonDarkSide"):
        """
        停止AI工作线程
        
        Args:
            receiver: 接收者标识
            model: AI模型名称
        
        Returns:
            bool: True表示停止成功，False表示未找到对应线程
        """
        with self.lock:
            worker_key = f"{receiver}_{model}"
            if worker_key in self.workers:
                worker = self.workers[worker_key]
                worker.stop()
                del self.workers[worker_key]
                return True
            return False

    def get_worker_status(self, receiver, model="MoonDarkSide"):
        """
        获取工作线程状态
        
        Args:
            receiver: 接收者标识
            model: AI模型名称
        
        Returns:
            dict: 线程状态信息，如果未找到则返回None
        """
        with self.lock:
            worker_key = f"{receiver}_{model}"
            if worker_key in self.workers:
                worker = self.workers[worker_key]
                return {
                    "running": worker.is_running(),
                    "uptime": worker.get_uptime(),
                    "paused": worker.isPaused(),
                }
            return None

    def get_all_workers(self):
        """
        获取所有工作线程信息
        
        Returns:
            dict: 所有工作线程的状态信息
        """
        with self.lock:
            return list(self.workers.keys())

    def stop_all_workers(self):
        with self.lock:
            for worker in self.workers.values():
                worker.stop()
            self.workers.clear()
