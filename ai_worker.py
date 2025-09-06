import json
import re
import threading
import time
from datetime import datetime

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
                elif match_type == "regex" and re.search(keyword, msg):
                    matched_replies.append(rule["reply"])
            except re.error:
                logger.error(f"Invalid regular expression: {keyword}")
            except Exception as e:
                logger.error(f"Error matching rule: {e}")

        return matched_replies

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

    def _process_message(self, content, who):
        """
        处理接收到的消息
        
        Args:
            content: 消息内容
            who: 发送者标识
        """
        chat_name = self._get_chat_name(who)
        try:
            if self.only_at and self.at_me not in content:
                return

            current_time = time.time()

            # 检查是否为连续重复内容
            if chat_name in self.last_sent_messages:
                last_message_data = self.last_sent_messages[chat_name]
                last_content = last_message_data["content"]
                last_timestamp = last_message_data["timestamp"]

                # 仅在内容完全一致时检查时间间隔
                if content == last_content:
                    if current_time - last_timestamp < self.min_reply_interval:
                        return

            matched_replies = self._match_rule(content)
            if not matched_replies:
                return

            reply_content = matched_replies[0]

            # 先检查消息配额
            from data_manager import increment_message_count, add_ai_history
            if not increment_message_count():
                logger.error(f"信息余量耗尽，无法发送消息给 {chat_name}")
                # 添加历史记录但状态为pending（未回复）
                history_data = {
                    "sender": chat_name,
                    "message": content,
                    "reply": reply_content,
                    "status": "pending",
                    "responseTime": self.reply_delay,
                    "timestamp": datetime.now().isoformat(),
                }
                add_ai_history(history_data)
                return

            if self.reply_delay > 0:
                time.sleep(self.reply_delay)

            response = self.wx_instance.SendMsg(msg=reply_content, who=who)

            if isinstance(response, dict) and response.get("status") == "成功":

                # 存储最后发送的消息内容和时间戳
                self.last_sent_messages[chat_name] = {
                    "content": content,
                    "timestamp": time.time(),
                }

                history_data = {
                    "sender": chat_name,
                    "message": content,
                    "reply": reply_content,
                    "status": "replied",
                    "responseTime": self.reply_delay,
                    "timestamp": datetime.now().isoformat(),
                }
                add_ai_history(history_data)

                logger.info(f"Replied to {chat_name}: {reply_content}")
            else:
                logger.error(f"Failed to send message to {chat_name}: {response}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

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
                            self._process_message(message.content, chat.who)

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
