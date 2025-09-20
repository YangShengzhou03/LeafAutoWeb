import json
import os
import random
import re
import threading
import time
import uuid
import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional

from data_manager import add_ai_history
from logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# 数据存储路径
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 当前选择的群聊
default_group_file = os.path.join(data_dir, "selected_group.json")

# 数据收集配置
collection_config_file = os.path.join(data_dir, "collection_config.json")

# 舆情监控配置
monitoring_config_file = os.path.join(data_dir, "monitoring_config.json")

# 消息记录目录
messages_dir = os.path.join(data_dir, "messages")
if not os.path.exists(messages_dir):
    os.makedirs(messages_dir)

# Constants
DATA_DIR = "data"
MESSAGE_TYPES = ["friend", "group"]
SYSTEM_MESSAGE_TYPE = "sys"
SELF_SENDER = "Self"
SEND_EMOTION_PREFIX = "SendEmotion:"
STATUS_FAILED = "失败"
ACCOUNT_LEVELS = {
    "free": 100,
    "basic": 1000,
    "enterprise": float("inf")
}
# 存储消息的文件路径
MESSAGES_FILE = os.path.join(DATA_DIR, "group_messages.txt")


class MessageInfo:
    """消息信息类，封装消息相关操作"""
    
    def __init__(self, message: Any):
        self.message = message
    
    def get_sender(self) -> str:
        """获取消息发送者"""
        if hasattr(self.message, 'sender'):
            return self.message.sender
        elif hasattr(self.message, 'get') and callable(getattr(self.message, 'get')):
            return self.message.get('sender', '')
        return ""
    
    def get_content(self) -> str:
        """获取消息内容"""
        if hasattr(self.message, 'content'):
            return self.message.content or ""
        elif hasattr(self.message, 'get') and callable(getattr(self.message, 'get')):
            return self.message.get("content", "")
        return str(self.message)
    
    def get_type(self) -> str:
        """获取消息类型"""
        if hasattr(self.message, "type"):
            return self.message.type.lower()
        return ""
    
    def is_system_message(self) -> bool:
        """检查是否为系统消息"""
        return self.get_type() == SYSTEM_MESSAGE_TYPE
    
    def is_self_message(self) -> bool:
        """检查是否为自己发送的消息"""
        return self.get_sender() == SELF_SENDER
    
    def is_empty_content(self) -> bool:
        """检查消息内容是否为空"""
        return not self.get_content().strip()
    
    def is_valid_message_type(self) -> bool:
        """检查消息类型是否有效"""
        return self.get_type() in MESSAGE_TYPES


class WorkerConfig:
    """工作线程配置类，用于减少参数数量"""
    
    def __init__(
        self,
        wx_instance: Any,
        receiver: str,
        only_at: bool = False,
        group_at_reply: bool = False,
        min_reply_interval: int = 0,
        sensitive_words: List[str] = None
    ):
        self.wx_instance = wx_instance
        self.receiver = receiver
        self.only_at = only_at
        self.group_at_reply = group_at_reply
        self.min_reply_interval = min_reply_interval
        self.sensitive_words = sensitive_words or []


class MessageHistory:
    """消息历史记录类，用于减少参数数量"""
    
    def __init__(self, sender: str, message: str, reply: str, 
                 status: str, response_time: float):
        self.sender = sender
        self.message = message
        self.reply = reply
        self.status = status
        self.response_time = response_time
        self.timestamp = datetime.now().isoformat()
        self.id = str(uuid.uuid4())
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "sender": self.sender,
            "message": self.message,
            "reply": self.reply,
            "status": self.status,
            "responseTime": self.response_time,
            "timestamp": self.timestamp,
            "id": self.id,
            "time": self.time
        }


class WorkerState:
    """工作线程状态类，用于减少实例属性数量"""
    
    def __init__(self):
        self.listen_list: List[str] = []
        self.last_reply_info = {"content": "", "time": 0}
        self._message_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._is_running = False
        self._paused = False
        self._pause_cond = threading.Condition(threading.Lock())
        self.start_time: Optional[float] = None
    
    def get_message_lock(self) -> threading.Lock:
        """获取消息锁"""
        return self._message_lock
    
    def get_stop_event(self) -> threading.Event:
        """获取停止事件"""
        return self._stop_event
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._is_running
    
    def set_running(self, running: bool) -> None:
        """设置运行状态"""
        self._is_running = running
    
    def is_paused(self) -> bool:
        """检查是否暂停"""
        return self._paused
    
    def set_paused(self, paused: bool) -> None:
        """设置暂停状态"""
        self._paused = paused
    
    def get_pause_condition(self) -> threading.Condition:
        """获取暂停条件"""
        return self._pause_cond
    
    def get_start_time(self) -> Optional[float]:
        """获取启动时间"""
        return self.start_time
    
    def set_start_time(self, start_time: Optional[float]) -> None:
        """设置启动时间"""
        self.start_time = start_time


class GroupWorkerThread:
    """
    群聊管理工作线程类
    负责处理群聊消息的存储和舆情监控功能

    Attributes:
        config: 工作线程配置对象
        at_me: @我的标识
        receiver_list: 接收者列表
        state: 工作线程状态
        rules_manager: 规则管理器
        reply_handler: 回复处理器
    """

    def __init__(self, config: WorkerConfig):
        """
        初始化群聊管理工作线程

        Args:
            config: 工作线程配置对象

        Raises:
            ValueError: 当wx_instance参数为空时抛出
        """
        if not config.wx_instance:
            raise ValueError("wx_instance参数不能为空")

        self.config = config
        self.at_me = f"@{self.config.wx_instance.nickname}"
        self.receiver_list = [
            r.strip() for r in self.config.receiver.replace("，", ",").split(",") if r.strip()
        ]
        
        # 初始化状态对象
        self.state = WorkerState()
        
        # 初始化规则管理器和回复处理器
        rules_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_DIR, "rules.json")
        self.rules_manager = RulesManager(rules_file_path)
        self.reply_handler = ReplyHandler(self.config.wx_instance)

        # 确保数据目录存在
        os.makedirs(DATA_DIR, exist_ok=True)

        logger.info(
            "Group worker thread initialized: receiver=%s, only_at=%s, group_at_reply=%s, min_interval=%ss",
            self.config.receiver,
            self.config.only_at,
            self.config.group_at_reply,
            self.config.min_reply_interval,
        )

    def update_rules(self) -> bool:
        """更新自定义规则，使规则变更立即生效
        
        Returns:
            bool: 规则是否有变化
        """
        return self.rules_manager.update_rules()

    def init_listeners(self) -> bool:
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
                self.config.wx_instance.AddListenChat(who=target)
                self.state.listen_list.append(target)
                logger.info("Added listener: %s", target)
            except (ValueError, TypeError, AttributeError, KeyError) as e:
                logger.error("Failed to add listener: %s, error: %s", target, str(e))
                # 清理已添加的监听器
                self._cleanup()
                return False
            except OSError as e:
                logger.error("OS error adding listener: %s, error: %s", target, str(e))
                # 清理已添加的监听器
                self._cleanup()
                return False
            except RuntimeError as e:
                logger.error("Runtime error adding listener: %s, error: %s", target, str(e))
                # 清理已添加的监听器
                self._cleanup()
                return False
        return True

    def _get_chat_name(self, who: str) -> str:
        """
        获取聊天名称

        Args:
            who: 聊天对象标识

        Returns:
            str: 聊天名称，如果无法获取则返回原标识
        """
        if not hasattr(self.config.wx_instance, "GetChatName"):
            return who
        return self.config.wx_instance.GetChatName(who)

    def _is_target_message(self, message: Any) -> bool:
        """
        检查消息是否来自目标联系人

        Args:
            message: 消息对象

        Returns:
            bool: True表示来自目标联系人，False表示不是
        """
        try:
            msg_info = MessageInfo(message)
            sender = msg_info.get_sender()
            # 检查发送者是否在接收者列表中
            return sender in self.receiver_list
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("Error checking target message: %s", e)
            return False
        except OSError as e:
            logger.error("OS error checking target message: %s", e)
            return False
        except Exception as e:
            logger.error("Unexpected error checking target message: %s", e)
            return False

    def _append_to_file(self, content: str) -> None:
        """
        将内容追加到文件
        
        Args:
            content: 要追加的内容
        """
        try:
            with open(MESSAGES_FILE, 'a', encoding='utf-8') as f:
                f.write(content + '\n')
        except IOError as e:
            logger.error(f"写入文件失败: {e}")

    def _check_sensitive_words(self, content: str) -> bool:
        """
        检查内容是否包含敏感词
        
        Args:
            content: 要检查的内容
            
        Returns:
            bool: 是否包含敏感词
        """
        if not self.config.sensitive_words:
            return False
            
        # 检查是否包含任何敏感词
        for word in self.config.sensitive_words:
            if re.search(re.escape(word), content, re.IGNORECASE):
                return True
        return False

    def _process_message(self, msg: Any = None, chat: Any = None) -> None:
        """
        处理接收到的消息
        
        Args:
            msg: 消息内容
            chat: 消息窗口
        """
        try:
            if msg is None:
                return
                
            # 获取聊天信息
            chat_info = self._get_chat_info(chat)
            is_group = chat_info["type"] == "group"
            group_name = chat.who

            # 记录消息接收时间戳
            receive_time = time.time()
            time_str = datetime.fromtimestamp(receive_time).strftime("%Y-%m-%d %H:%M:%S")

            # 获取消息内容
            msg_info = MessageInfo(msg)
            message_content = msg_info.get_content()
            sender = msg_info.get_sender()

            # 检查only_at功能（仅针对群聊有效）
            if self.config.only_at and is_group:
                if self.at_me not in message_content:
                    logger.debug("[群聊管理] 群聊消息未包含@我，忽略消息: %s", message_content)
                    return
                message_content = message_content.replace(self.at_me, "").strip()

            # 检查最小处理间隔（仅对相同内容的消息）
            if self._should_ignore_due_to_interval(message_content):
                logger.info("[群聊管理] 相同内容未达到最小处理间隔，忽略消息: %s", message_content)
                return

            # 1. 舆情监控：检查是否包含敏感词
            if self._check_sensitive_words(message_content):
                print("危险")  # 包含敏感词时打印"危险"
                logger.warning(f"[舆情监控] 检测到敏感内容: {message_content[:50]}... 发送者: {sender}")

            # 2. 存储消息到txt文件
            message_entry = f"[{time_str}] 发送者: {sender} | 群聊: {group_name if is_group else '私聊'} | 内容: {message_content}"
            self._append_to_file(message_entry)
            logger.debug(f"[消息存储] 已保存消息: {message_entry[:100]}")

            # 应用自定义规则（如果需要回复）
            custom_reply = self.rules_manager.apply_custom_rules(message_content)
            if custom_reply:
                # 发送自定义回复
                reply_sent = False
                if is_group:
                    # 根据group_at_reply设置决定是否@对方
                    at_user = sender if self.config.group_at_reply else ""
                    reply_sent = self.reply_handler.send_reply(group_name, custom_reply, at_user=at_user)
                else:
                    reply_sent = self.reply_handler.send_reply(sender, custom_reply)
                
                # 根据发送结果记录历史记录
                if reply_sent:
                    self.state.last_reply_info = {"content": message_content, "time": time.time()}
                    # 计算实际响应时间
                    actual_response_time = round(time.time() - receive_time, 2)
                    # 记录回复历史（使用实际响应时间）
                    history = MessageHistory(sender, message_content, custom_reply, "replied", actual_response_time)
                    self._record_history(history)
                else:
                    # 发送失败，记录未回复状态
                    history = MessageHistory(sender, message_content, custom_reply, "not_replied", 0)
                    self._record_history(history)
                return

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("处理消息时发生错误: %s", e)
            # 记录错误历史
            if msg is not None:
                msg_info = MessageInfo(msg)
                history = MessageHistory(msg_info.get_sender(), msg_info.get_content(), "", "failed", 0)
                self._record_history(history)
        except OSError as e:
            logger.error("OS error processing message: %s", e)
            # 记录错误历史
            if msg is not None:
                msg_info = MessageInfo(msg)
                history = MessageHistory(msg_info.get_sender(), msg_info.get_content(), "", "failed", 0)
                self._record_history(history)
        except RuntimeError as e:
            logger.error("Runtime error processing message: %s", e)
            # 记录错误历史
            if msg is not None:
                msg_info = MessageInfo(msg)
                history = MessageHistory(msg_info.get_sender(), msg_info.get_content(), "", "failed", 0)
                self._record_history(history)
    
    def _get_chat_info(self, chat: Any) -> Dict[str, str]:
        """获取聊天信息
        
        Args:
            chat: 聊天对象
            
        Returns:
            Dict[str, str]: 包含聊天类型和名称的字典
        """
        try:
            if chat and hasattr(chat, 'ChatInfo'):
                info = chat.ChatInfo()
                return {
                    "type": info.get("chat_type", ""),
                    "name": info.get("chat_name", "")
                }
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("获取聊天信息失败: %s", e)
        except OSError as e:
            logger.error("OS error getting chat info: %s", e)
        except Exception as e:
            logger.error("Unexpected error getting chat info: %s", e)
        
        return {"type": "", "name": ""}
    
    def _should_ignore_due_to_interval(self, message_content: str) -> bool:
        """检查是否因处理间隔而忽略消息
        
        Args:
            message_content: 消息内容
            
        Returns:
            bool: 是否应该忽略
        """
        if self.config.min_reply_interval <= 0:
            return False
            
        current_time = time.time()
        return (
            message_content == self.state.last_reply_info["content"] and
            current_time - self.state.last_reply_info["time"] < self.config.min_reply_interval
        )
    
    def _record_history(self, history: MessageHistory) -> None:
        """记录处理历史
        
        Args:
            history: 消息历史对象
        """
        add_ai_history(history.to_dict())

    def run(self) -> None:
        """
        主运行循环
        负责初始化监听器、处理消息和清理资源
        """
        self.state.set_running(True)
        self.state.set_start_time(time.time())
        logger.info("Group worker thread started")

        try:
            if not self.init_listeners():
                self._cleanup()
                self.state.set_running(False)
                logger.error("Group worker thread initialization failed")
                return
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("Initialization failed: %s", str(e))
            self._cleanup()
            self.state.set_running(False)
            return
        except OSError as e:
            logger.error("OS error during initialization: %s", str(e))
            self._cleanup()
            self.state.set_running(False)
            return
        except RuntimeError as e:
            logger.error("Runtime error during initialization: %s", str(e))
            self._cleanup()
            self.state.set_running(False)
            return

        # 主消息循环
        while not self._should_stop():
            try:
                # 检查是否暂停
                if self.state.is_paused():
                    self.wait_for_resume()
                    continue

                # 定期检查规则更新
                if int(time.time()) % 10 == 0:  # 每10秒检查一次
                    self.update_rules()

                # 获取消息
                messages_dict = self.config.wx_instance.GetListenMessage()
                if not messages_dict:
                    time.sleep(0.1)  # 避免CPU占用过高
                    continue

                # 处理每条消息
                for chat, messages in messages_dict.items():
                    if self._should_stop():
                        break
                    for message in messages:
                        if self._should_stop():
                            break

                        # 使用线程锁保护消息处理
                        with self.state.get_message_lock():
                            # 检查是否为需要忽略的消息
                            if self._is_ignored_message(message):
                                continue
                            # 处理消息
                            self._process_message(message, chat)

            except (ValueError, TypeError, AttributeError, KeyError) as e:
                logger.error("Error in main loop: %s", e)
                if self._should_stop():
                    break
                time.sleep(1)  # 出错时暂停一段时间
            except OSError as e:
                logger.error("OS error in main loop: %s", e)
                if self._should_stop():
                    break
                time.sleep(1)  # 出错时暂停一段时间
            except RuntimeError as e:
                logger.error("Runtime error in main loop: %s", e)
                if self._should_stop():
                    break
                time.sleep(1)  # 出错时暂停一段时间

        # 清理资源
        self._cleanup()
        self.state.set_running(False)
        logger.info("Group worker thread stopped")

    def _is_ignored_message(self, message: Any) -> bool:
        """
        检查是否为需要忽略的消息

        Args:
            message: 消息对象

        Returns:
            bool: True表示需要忽略，False表示需要处理
        """
        try:
            msg_info = MessageInfo(message)
            
            # 忽略系统消息
            if msg_info.is_system_message():
                return True

            # 忽略自己发送的消息
            if msg_info.is_self_message():
                return True

            # 检查消息类型是否有效
            if not msg_info.is_valid_message_type():
                return True

            # 检查消息内容是否为空
            if msg_info.is_empty_content():
                return True

            return False
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("Error checking ignored message: %s", e)
            return True
        except OSError as e:
            logger.error("OS error checking ignored message: %s", e)
            return True
        except Exception as e:
            logger.error("Unexpected error checking ignored message: %s", e)
            return True

    def _should_stop(self) -> bool:
        """
        检查是否应该停止线程

        Returns:
            bool: True表示应该停止，False表示继续运行
        """
        return self.state.get_stop_event().is_set() or not self.state.is_running()

    def _cleanup(self) -> None:
        """
        清理监听器资源
        """
        try:
            for target in self.state.listen_list:
                if hasattr(self.config.wx_instance, "RemoveListenChat"):
                    try:
                        self.config.wx_instance.RemoveListenChat(who=target)
                    except (ValueError, TypeError, AttributeError, KeyError) as e:
                        logger.error("Failed to remove listener for %s: %s", target, e)
                    except OSError as e:
                        logger.error("OS error removing listener for %s: %s", target, e)
                    except RuntimeError as e:
                        logger.error("Runtime error removing listener for %s: %s", target, e)
            self.state.listen_list.clear()
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("清理监听时出错: %s", str(e))
        except OSError as e:
            logger.error("OS error cleaning up listeners: %s", str(e))
        except RuntimeError as e:
            logger.error("Runtime error cleaning up listeners: %s", str(e))

    def pause(self) -> None:
        """
        暂停工作线程
        """
        with self.state.get_pause_condition():
            self.state.set_paused(True)

    def resume(self) -> None:
        """
        恢复工作线程
        """
        with self.state.get_pause_condition():
            self.state.set_paused(False)
            self.state.get_pause_condition().notify()

    def is_paused(self) -> bool:
        """
        检查线程是否暂停

        Returns:
            bool: True表示已暂停，False表示未暂停
        """
        return self.state.is_paused()

    def wait_for_resume(self) -> None:
        """
        等待线程恢复
        """
        with self.state.get_pause_condition():
            while self.state.is_paused():
                self.state.get_pause_condition().wait()

    def stop(self) -> None:
        """
        停止工作线程
        """
        self.state.get_stop_event().set()
        self.state.set_running(False)
        self.resume()

    def is_running(self) -> bool:
        """
        检查线程是否运行

        Returns:
            bool: True表示正在运行，False表示已停止
        """
        return self.state.is_running()

    def get_uptime(self) -> int:
        """
        获取线程运行时间

        Returns:
            int: 运行时间（秒），如果未启动则返回0
        """
        return int(time.time() - self.state.get_start_time()) if self.state.get_start_time() else 0


class GroupWorkerManager:
    """
    群聊管理工作管理器类（单例模式）
    负责管理多个群聊管理工作线程的创建、停止和状态查询

    Attributes:
        _instance: 单例实例
        workers: 工作线程字典
        lock: 线程安全锁
    """

    _instance: Optional['GroupWorkerManager'] = None
    workers: Dict[str, GroupWorkerThread] = {}
    lock: threading.Lock = threading.Lock()

    def __new__(cls) -> 'GroupWorkerManager':
        """
        单例模式实现

        Returns:
            GroupWorkerManager: 单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.workers = {}
            cls._instance.lock = threading.Lock()
        return cls._instance

    def start_worker(self, config: WorkerConfig) -> bool:
        """
        启动群聊管理工作线程

        Args:
            config: 工作线程配置对象

        Returns:
            bool: True表示启动成功，False表示启动失败
        """
        with self.lock:
            worker_key = f"{config.receiver}_group"
            if worker_key in self.workers:
                return False

            worker = GroupWorkerThread(config)
            self.workers[worker_key] = worker

            try:
                thread = threading.Thread(target=worker.run, daemon=True)
                thread.start()

                # 等待线程启动
                time.sleep(0.1)
                if not worker.is_running():
                    del self.workers[worker_key]
                    return False

                # 等待初始化完成，最多等待5秒
                max_wait_time = 5
                wait_interval = 0.1
                total_wait_time = 0
                
                while total_wait_time < max_wait_time:
                    # 检查线程是否仍在运行且初始化是否完成
                    if not worker.is_running():
                        # 线程已经停止，说明初始化失败
                        del self.workers[worker_key]
                        return False
                    
                    # 检查监听器是否已成功添加
                    if hasattr(worker.state, 'listen_list') and len(worker.state.listen_list) > 0:
                        # 监听器已添加，初始化成功
                        return True
                    
                    # 继续等待
                    time.sleep(wait_interval)
                    total_wait_time += wait_interval
                
                # 超时后，检查线程状态
                if worker.is_running() and hasattr(worker.state, 'listen_list') and len(worker.state.listen_list) > 0:
                    return True
                else:
                    # 初始化超时，停止线程并清理
                    worker.stop()
                    del self.workers[worker_key]
                    return False

            except (ValueError, TypeError, AttributeError, KeyError) as e:
                if worker_key in self.workers:
                    del self.workers[worker_key]
                logger.error("Failed to start worker: %s", e)
                return False
            except OSError as e:
                if worker_key in self.workers:
                    del self.workers[worker_key]
                logger.error("OS error starting worker: %s", e)
                return False
            except RuntimeError as e:
                if worker_key in self.workers:
                    del self.workers[worker_key]
                logger.error("Runtime error starting worker: %s", e)
                return False

    def stop_worker(self, receiver: str) -> bool:
        """
        停止群聊管理工作线程

        Args:
            receiver: 接收者标识

        Returns:
            bool: True表示停止成功，False表示未找到对应线程
        """
        with self.lock:
            worker_key = f"{receiver}_group"
            if worker_key in self.workers:
                worker = self.workers[worker_key]
                worker.stop()
                del self.workers[worker_key]
                return True
            return False

    def get_worker_status(self, receiver: str) -> Optional[Dict[str, Any]]:
        """
        获取工作线程状态

        Args:
            receiver: 接收者标识

        Returns:
            dict: 线程状态信息，如果未找到则返回None
        """
        with self.lock:
            worker_key = f"{receiver}_group"
            if worker_key in self.workers:
                worker = self.workers[worker_key]
                return {
                    "running": worker.is_running(),
                    "uptime": worker.get_uptime(),
                    "paused": worker.is_paused(),
                }
            return None

    def get_all_workers(self) -> List[str]:
        """
        获取所有工作线程信息

        Returns:
            List[str]: 所有工作线程的键列表
        """
        with self.lock:
            return list(self.workers.keys())

    def stop_all_workers(self) -> None:
        """停止所有工作线程"""
        with self.lock:
            for worker in self.workers.values():
                worker.stop()
            self.workers.clear()

    def update_all_workers_rules(self) -> bool:
        """通知所有工作线程更新规则
        
        Returns:
            bool: 是否有工作线程更新了规则
        """
        updated_count = 0
        for _, worker in self.workers.items():
            if worker.update_rules():
                updated_count += 1

        if updated_count > 0:
            logger.info("[群聊管理] 已通知 %s 个工作线程更新规则", updated_count)
        else:
            logger.debug("[群聊管理] 没有工作线程需要更新规则")

        return updated_count > 0

# 全局的群聊管理器实例
group_manager = GroupWorkerManager()

# 默认的微信实例，实际使用时会被注入
default_wx_instance = None

def set_wechat_instance(wx_instance):
    """设置微信实例"""
    global default_wx_instance
    default_wx_instance = wx_instance

def get_wechat_instance():
    """获取微信实例"""
    return default_wx_instance

# 群聊管理相关功能实现
def select_group(group_name: str) -> tuple:
    """选择要管理的群聊
    
    Args:
        group_name: 群聊名称
        
    Returns:
        tuple: (success, message/error)
    """
    try:
        # 保存选择的群聊
        with open(default_group_file, 'w', encoding='utf-8') as f:
            json.dump({"group_name": group_name}, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已选择群聊: {group_name}")
        return True, f"已选择群聊: {group_name}"
    except Exception as e:
        logger.error(f"选择群聊失败: {str(e)}")
        return False, f"选择群聊失败: {str(e)}"

def toggle_message_recording(group_name: str, enabled: bool) -> tuple:
    """开启/关闭群消息记录
    
    Args:
        group_name: 群聊名称
        enabled: 是否开启
        
    Returns:
        tuple: (success, message/error)
    """
    try:
        # 加载配置
        config = {}
        if os.path.exists(collection_config_file):
            with open(collection_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 更新配置
        if group_name not in config:
            config[group_name] = {}
        config[group_name]["recording_enabled"] = enabled
        
        # 保存配置
        with open(collection_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        status = "开启" if enabled else "关闭"
        logger.info(f"已{status}{group_name}的消息记录功能")
        
        # 如果开启记录，确保对应的消息目录存在
        if enabled:
            group_messages_dir = os.path.join(messages_dir, group_name)
            if not os.path.exists(group_messages_dir):
                os.makedirs(group_messages_dir)
        
        return True, f"已{status}{group_name}的消息记录功能"
    except Exception as e:
        logger.error(f"切换消息记录状态失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def set_collection_date(group_name: str, date: str) -> tuple:
    """设置收集日期
    
    Args:
        group_name: 群聊名称
        date: 日期字符串 (YYYY-MM-DD)
        
    Returns:
        tuple: (success, result/error)
    """
    try:
        # 验证日期格式
        datetime.strptime(date, "%Y-%m-%d")
        
        # 加载配置
        config = {}
        if os.path.exists(collection_config_file):
            with open(collection_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 更新配置
        if group_name not in config:
            config[group_name] = {}
        config[group_name]["collection_date"] = date
        
        # 保存配置
        with open(collection_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已设置{group_name}的数据收集日期为: {date}")
        return True, {"date": date}
    except ValueError:
        return False, "无效的日期格式，请使用YYYY-MM-DD格式"
    except Exception as e:
        logger.error(f"设置收集日期失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def save_collection_template(group_name: str, template: str) -> tuple:
    """保存收集模板
    
    Args:
        group_name: 群聊名称
        template: 模板内容
        
    Returns:
        tuple: (success, message/error)
    """
    try:
        # 加载配置
        config = {}
        if os.path.exists(collection_config_file):
            with open(collection_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 更新配置
        if group_name not in config:
            config[group_name] = {}
        config[group_name]["template"] = template
        
        # 保存配置
        with open(collection_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已保存{group_name}的数据收集模板")
        return True, "模板保存成功"
    except Exception as e:
        logger.error(f"保存收集模板失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def auto_learn_pattern(group_name: str) -> tuple:
    """自动学习模式，建立正则表达式
    
    Args:
        group_name: 群聊名称
        
    Returns:
        tuple: (success, message/error)
    """
    try:
        # 获取群消息目录
        group_messages_dir = os.path.join(messages_dir, group_name)
        if not os.path.exists(group_messages_dir):
            return False, "该群聊没有消息记录，无法学习模式"
        
        # 加载最近的消息文件
        message_files = [f for f in os.listdir(group_messages_dir) if f.endswith('.json')]
        if not message_files:
            return False, "该群聊没有消息记录，无法学习模式"
        
        # 取最新的消息文件
        message_files.sort(reverse=True)
        latest_file = message_files[0]
        
        with open(os.path.join(group_messages_dir, latest_file), 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        # 简单的模式学习逻辑示例
        # 提取消息内容中的关键词和模式
        content_patterns = []
        for msg in messages:
            content = msg.get("content", "")
            if content and len(content) > 10:
                # 尝试提取简单的模式
                if "=" in content and len(content.split("=")) > 1:
                    content_patterns.append("\\w+=")
                if ":" in content and len(content.split(":")) > 1:
                    content_patterns.append("\\w+:")
                
        # 生成正则表达式
        if content_patterns:
            unique_patterns = list(set(content_patterns))
            regex = "|".join(unique_patterns)
            
            # 保存生成的正则表达式
            save_collection_template(group_name, regex)
            return True, f"已自动学习模式，生成正则表达式: {regex}"
        else:
            return False, "未能从消息中学习到有效的模式"
            
    except Exception as e:
        logger.error(f"自动学习模式失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def export_collected_data(group_name: str, date: str) -> tuple:
    """导出收集的数据
    
    Args:
        group_name: 群聊名称
        date: 日期字符串 (YYYY-MM-DD)，如果为空则导出所有数据
        
    Returns:
        tuple: (success, file_path/error)
    """
    try:
        # 获取群消息目录
        group_messages_dir = os.path.join(messages_dir, group_name)
        if not os.path.exists(group_messages_dir):
            return False, "该群聊没有消息记录"
        
        # 收集要导出的消息
        exported_messages = []
        message_files = [f for f in os.listdir(group_messages_dir) if f.endswith('.json')]
        
        for file_name in message_files:
            # 如果指定了日期，只导出对应日期的文件
            if date and not file_name.startswith(date):
                continue
            
            file_path = os.path.join(group_messages_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                exported_messages.extend(messages)
        
        if not exported_messages:
            if date:
                return False, f"未找到{date}的消息记录"
            else:
                return False, "未找到消息记录"
        
        # 创建导出文件
        export_dir = os.path.join(data_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        export_filename = f"{group_name}_messages_{date if date else datetime.now().strftime('%Y-%m-%d')}.json"
        export_path = os.path.join(export_dir, export_filename)
        
        # 保存导出文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(exported_messages, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已导出{group_name}的消息数据到: {export_path}")
        return True, export_path
    except Exception as e:
        logger.error(f"导出数据失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def start_sentiment_monitoring(group_name: str, sensitive_words: str) -> tuple:
    """开始舆情监控
    
    Args:
        group_name: 群聊名称
        sensitive_words: 敏感词列表，用逗号分隔
        
    Returns:
        tuple: (success, message/error)
    """
    try:
        # 加载配置
        config = {}
        if os.path.exists(monitoring_config_file):
            with open(monitoring_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 更新配置
        if group_name not in config:
            config[group_name] = {}
        
        # 处理敏感词列表
        sensitive_words_list = [word.strip() for word in sensitive_words.split(',') if word.strip()]
        
        config[group_name].update({
            "enabled": True,
            "sensitive_words": sensitive_words_list,
            "start_time": datetime.now().isoformat()
        })
        
        # 保存配置
        with open(monitoring_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已开始{group_name}的舆情监控，敏感词: {', '.join(sensitive_words_list)}")
        return True, f"已开始舆情监控，共设置{len(sensitive_words_list)}个敏感词"
    except Exception as e:
        logger.error(f"开始舆情监控失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def stop_sentiment_monitoring(group_name: str) -> tuple:
    """停止舆情监控
    
    Args:
        group_name: 群聊名称
        
    Returns:
        tuple: (success, message/error)
    """
    try:
        # 加载配置
        if not os.path.exists(monitoring_config_file):
            return False, "没有舆情监控配置"
        
        with open(monitoring_config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查群聊是否在配置中
        if group_name not in config:
            return False, "该群聊未开启舆情监控"
        
        # 更新配置
        config[group_name]["enabled"] = False
        config[group_name]["stop_time"] = datetime.now().isoformat()
        
        # 保存配置
        with open(monitoring_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已停止{group_name}的舆情监控")
        return True, "已停止舆情监控"
    except Exception as e:
        logger.error(f"停止舆情监控失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def check_sentiment_monitoring_status(group_name: str) -> tuple:
    """检查舆情监控状态
    
    Args:
        group_name: 群聊名称
        
    Returns:
        tuple: (success, status_info/error)
    """
    try:
        # 加载配置
        if not os.path.exists(monitoring_config_file):
            return True, {"enabled": False}
        
        with open(monitoring_config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 获取状态信息
        if group_name not in config or not config[group_name].get("enabled", False):
            return True, {"enabled": False}
        
        # 返回详细状态
        return True, {
            "enabled": True,
            "sensitive_words": config[group_name].get("sensitive_words", []),
            "start_time": config[group_name].get("start_time", ""),
            "monitoring_duration": "监控中"
        }
    except Exception as e:
        logger.error(f"检查舆情监控状态失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

# 导出各类群数据的函数
def export_group_messages(group_name: str, date: str = "") -> tuple:
    """导出群消息
    
    Args:
        group_name: 群聊名称
        date: 可选，日期过滤
        
    Returns:
        tuple: (success, file_path/error)
    """
    # 复用export_collected_data函数的逻辑
    return export_collected_data(group_name, date)

def export_group_files(group_name: str, date: str = "") -> tuple:
    """导出群文件
    
    Args:
        group_name: 群聊名称
        date: 可选，日期过滤
        
    Returns:
        tuple: (success, file_path/error)
    """
    try:
        # 获取群消息目录
        group_messages_dir = os.path.join(messages_dir, group_name)
        if not os.path.exists(group_messages_dir):
            return False, "该群聊没有消息记录"
        
        # 收集文件消息
        file_messages = []
        message_files = [f for f in os.listdir(group_messages_dir) if f.endswith('.json')]
        
        for file_name in message_files:
            if date and not file_name.startswith(date):
                continue
            
            file_path = os.path.join(group_messages_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                # 过滤出文件消息
                for msg in messages:
                    if msg.get("type") == "file":
                        file_messages.append(msg)
        
        if not file_messages:
            return False, "未找到文件消息"
        
        # 创建导出文件
        export_dir = os.path.join(data_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        export_filename = f"{group_name}_files_{date if date else datetime.now().strftime('%Y-%m-%d')}.json"
        export_path = os.path.join(export_dir, export_filename)
        
        # 保存导出文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(file_messages, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已导出{group_name}的文件消息到: {export_path}")
        return True, export_path
    except Exception as e:
        logger.error(f"导出文件消息失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def export_group_images(group_name: str, date: str = "") -> tuple:
    """导出群图片
    
    Args:
        group_name: 群聊名称
        date: 可选，日期过滤
        
    Returns:
        tuple: (success, file_path/error)
    """
    try:
        # 获取群消息目录
        group_messages_dir = os.path.join(messages_dir, group_name)
        if not os.path.exists(group_messages_dir):
            return False, "该群聊没有消息记录"
        
        # 收集图片消息
        image_messages = []
        message_files = [f for f in os.listdir(group_messages_dir) if f.endswith('.json')]
        
        for file_name in message_files:
            if date and not file_name.startswith(date):
                continue
            
            file_path = os.path.join(group_messages_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                # 过滤出图片消息
                for msg in messages:
                    if msg.get("type") == "image":
                        image_messages.append(msg)
        
        if not image_messages:
            return False, "未找到图片消息"
        
        # 创建导出文件
        export_dir = os.path.join(data_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        export_filename = f"{group_name}_images_{date if date else datetime.now().strftime('%Y-%m-%d')}.json"
        export_path = os.path.join(export_dir, export_filename)
        
        # 保存导出文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(image_messages, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已导出{group_name}的图片消息到: {export_path}")
        return True, export_path
    except Exception as e:
        logger.error(f"导出图片消息失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def export_group_voices(group_name: str, date: str = "") -> tuple:
    """导出群语音
    
    Args:
        group_name: 群聊名称
        date: 可选，日期过滤
        
    Returns:
        tuple: (success, file_path/error)
    """
    try:
        # 获取群消息目录
        group_messages_dir = os.path.join(messages_dir, group_name)
        if not os.path.exists(group_messages_dir):
            return False, "该群聊没有消息记录"
        
        # 收集语音消息
        voice_messages = []
        message_files = [f for f in os.listdir(group_messages_dir) if f.endswith('.json')]
        
        for file_name in message_files:
            if date and not file_name.startswith(date):
                continue
            
            file_path = os.path.join(group_messages_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                # 过滤出语音消息
                for msg in messages:
                    if msg.get("type") == "voice":
                        voice_messages.append(msg)
        
        if not voice_messages:
            return False, "未找到语音消息"
        
        # 创建导出文件
        export_dir = os.path.join(data_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        export_filename = f"{group_name}_voices_{date if date else datetime.now().strftime('%Y-%m-%d')}.json"
        export_path = os.path.join(export_dir, export_filename)
        
        # 保存导出文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(voice_messages, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已导出{group_name}的语音消息到: {export_path}")
        return True, export_path
    except Exception as e:
        logger.error(f"导出语音消息失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def export_group_videos(group_name: str, date: str = "") -> tuple:
    """导出群视频
    
    Args:
        group_name: 群聊名称
        date: 可选，日期过滤
        
    Returns:
        tuple: (success, file_path/error)
    """
    try:
        # 获取群消息目录
        group_messages_dir = os.path.join(messages_dir, group_name)
        if not os.path.exists(group_messages_dir):
            return False, "该群聊没有消息记录"
        
        # 收集视频消息
        video_messages = []
        message_files = [f for f in os.listdir(group_messages_dir) if f.endswith('.json')]
        
        for file_name in message_files:
            if date and not file_name.startswith(date):
                continue
            
            file_path = os.path.join(group_messages_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                # 过滤出视频消息
                for msg in messages:
                    if msg.get("type") == "video":
                        video_messages.append(msg)
        
        if not video_messages:
            return False, "未找到视频消息"
        
        # 创建导出文件
        export_dir = os.path.join(data_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        export_filename = f"{group_name}_videos_{date if date else datetime.now().strftime('%Y-%m-%d')}.json"
        export_path = os.path.join(export_dir, export_filename)
        
        # 保存导出文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(video_messages, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已导出{group_name}的视频消息到: {export_path}")
        return True, export_path
    except Exception as e:
        logger.error(f"导出视频消息失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def export_group_links(group_name: str, date: str = "") -> tuple:
    """导出群链接
    
    Args:
        group_name: 群聊名称
        date: 可选，日期过滤
        
    Returns:
        tuple: (success, file_path/error)
    """
    try:
        # 获取群消息目录
        group_messages_dir = os.path.join(messages_dir, group_name)
        if not os.path.exists(group_messages_dir):
            return False, "该群聊没有消息记录"
        
        # 收集链接消息
        link_messages = []
        message_files = [f for f in os.listdir(group_messages_dir) if f.endswith('.json')]
        
        for file_name in message_files:
            if date and not file_name.startswith(date):
                continue
            
            file_path = os.path.join(group_messages_dir, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
                # 过滤出链接消息
                for msg in messages:
                    content = msg.get("content", "")
                    # 简单的链接检测
                    if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content):
                        link_messages.append(msg)
        
        if not link_messages:
            return False, "未找到链接消息"
        
        # 创建导出文件
        export_dir = os.path.join(data_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        export_filename = f"{group_name}_links_{date if date else datetime.now().strftime('%Y-%m-%d')}.json"
        export_path = os.path.join(export_dir, export_filename)
        
        # 保存导出文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(link_messages, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已导出{group_name}的链接消息到: {export_path}")
        return True, export_path
    except Exception as e:
        logger.error(f"导出链接消息失败: {str(e)}")
        return False, f"操作失败: {str(e)}"
