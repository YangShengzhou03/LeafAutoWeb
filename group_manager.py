import csv
import json
import os
import re
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# 数据存储路径
data_dir = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 消息记录目录
messages_dir = os.path.join(data_dir, "messages")
if not os.path.exists(messages_dir):
    os.makedirs(messages_dir)

# 群聊管理配置
group_manage_config_file = os.path.join(data_dir, "group_manage.json")

# 数据收集配置
collection_config_file = os.path.join(data_dir, "collection_config.json")

# 舆情监控配置
monitoring_config_file = os.path.join(data_dir, "monitoring_config.json")



# 记录目录
RECORDING_DIR = os.path.join(data_dir, "recordings")
if not os.path.exists(RECORDING_DIR):
    os.makedirs(RECORDING_DIR)

# 聊天记录目录（按天存储）
CHAT_DATE_DIR = os.path.join(os.path.dirname(__file__), "chat_date")
if not os.path.exists(CHAT_DATE_DIR):
    os.makedirs(CHAT_DATE_DIR)

# Constants
DATA_DIR = "data"
MESSAGE_TYPES = ["friend", "group"]
SYSTEM_MESSAGE_TYPE = "sys"
SELF_SENDER = "Self"


# 获取按天存储的消息文件路径
def get_daily_messages_file(chat_name: str) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    # 清理文件名中的非法字符
    safe_chat_name = re.sub(r'[\\/:*?"<>|]', '_', chat_name)
    filename = f"{safe_chat_name}_{date_str}.csv"
    return os.path.join(CHAT_DATE_DIR, filename)


class MessageInfo:
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
        record_interval: int = 0,
        sensitive_words: List[str] = None
    ):
        self.wx_instance = wx_instance
        self.receiver = receiver
        self.record_interval = record_interval
        self.sensitive_words = sensitive_words or []


class MessageHistory:
    """消息历史记录类，用于记录消息"""
    
    def __init__(self, sender: str, message: str, chat_name: str):
        self.sender = sender
        self.message = message
        self.chat_name = chat_name
        self.timestamp = datetime.now().isoformat()
        self.id = str(uuid.uuid4())
        self.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "sender": self.sender,
            "message": self.message,
            "chatName": self.chat_name,
            "timestamp": self.timestamp,
            "id": self.id,
            "time": self.time
        }


class WorkerState:
    """工作线程状态类，用于减少实例属性数量"""
    
    def __init__(self):
        self.listen_list: List[str] = []
        self.last_record_info = {"content": "", "time": 0}
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

        if os.path.exists(group_manage_config_file):
            with open(group_manage_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            config["group"] = self.config.receiver

            with open(group_manage_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

        
        # 初始化状态对象
        self.state = WorkerState()
        
        # 初始化敏感词列表
        self.sensitive_words = self.config.sensitive_words or []
        
        # 初始化正则规则列表
        self.regex_rules = self._load_regex_rules()

        logger.info(
            "Group worker thread initialized: receiver=%s, record_interval=%ss",
            self.config.receiver,
            self.config.record_interval,
        )

    def update_rules(self) -> bool:
        """更新规则（空实现，因为不需要规则处理）
        
        Returns:
            bool: 始终返回False
        """
        return False

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



    def _append_to_daily_file(self, content: str, chat_name: str) -> None:
        """
        将内容追加到按天存储的消息文件（CSV格式）
        
        Args:
            content: 要追加的内容（格式：[时间] 发送者: {sender} | 群聊: {chat_name} | 内容: {message_content}）
            chat_name: 聊天名称
        """
        try:
            daily_file = get_daily_messages_file(chat_name)
            
            # 解析消息内容
            # 格式示例：[2025-09-21 10:30:25] 发送者: 张三 | 群聊: 测试群 | 内容: 你好
            import re
            pattern = r'\[(.*?)\] 发送者: (.*?) \| 群聊: (.*?) \| 内容: (.*)'
            match = re.match(pattern, content)
            
            if match:
                time_str, sender, chat_type, message_content = match.groups()
                
                # 准备CSV行数据
                row_data = {
                    '时间': time_str,
                    '发送者': sender,
                    '聊天类型': chat_type,
                    '聊天名称': chat_name,
                    '消息内容': message_content
                }
                
                # 检查文件是否存在
                file_exists = os.path.exists(daily_file)
                
                # 写入CSV文件
                with open(daily_file, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['时间', '发送者', '聊天类型', '聊天名称', '消息内容'])
                    
                    # 如果文件不存在，写入表头
                    if not file_exists:
                        writer.writeheader()
                        logger.info(f"创建新的按天存储CSV文件: {daily_file}")
                    
                    # 写入数据行
                    writer.writerow(row_data)
            else:
                # 如果格式不匹配，使用原始内容作为消息内容
                row_data = {
                    '时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    '发送者': '未知',
                    '聊天类型': '未知',
                    '聊天名称': chat_name,
                    '消息内容': content
                }
                
                # 检查文件是否存在
                file_exists = os.path.exists(daily_file)
                
                # 写入CSV文件
                with open(daily_file, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['时间', '发送者', '聊天类型', '聊天名称', '消息内容'])
                    
                    # 如果文件不存在，写入表头
                    if not file_exists:
                        writer.writeheader()
                        logger.info(f"创建新的按天存储CSV文件: {daily_file}")
                    
                    # 写入数据行
                    writer.writerow(row_data)
                    
        except IOError as e:
            logger.error(f"写入按天存储CSV文件失败: {e}")
        except Exception as e:
            logger.error(f"处理消息内容失败: {e}")

    def _check_sensitive_words(self, content: str) -> bool:
        """
        检查内容是否包含敏感词
        
        Args:
            content: 要检查的内容
            
        Returns:
            bool: 是否包含敏感词
        """
        if not self.sensitive_words:
            return False
            
        # 检查是否包含任何敏感词
        for word in self.sensitive_words:
            if re.search(re.escape(word), content, re.IGNORECASE):
                return True
        return False

    def _load_regex_rules(self) -> List[Dict[str, str]]:
        """加载正则规则列表
        
        Returns:
            List[Dict[str, str]]: 正则规则列表
        """
        try:
            if os.path.exists(regex_config_file):
                with open(regex_config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    # 提取rules数组
                    return config_data.get("rules", [])
            return []
        except Exception as e:
            logger.error(f"加载正则规则失败: {e}")
            return []

    def _match_regex_rules(self, message_content: str) -> List[Dict[str, Any]]:
        """使用正则规则匹配消息内容
        
        Args:
            message_content: 消息内容
            
        Returns:
            List[Dict[str, Any]]: 匹配到的规则和提取的内容列表
        """
        matched_rules = []
        
        for rule in self.regex_rules:
            pattern = rule.get("pattern", "")
            if not pattern:
                continue
                
            try:
                # 使用正则表达式匹配
                match = re.search(pattern, message_content)
                if match:
                    # 提取所有匹配组的内容
                    extracted_contents = []
                    if len(match.groups()) > 0:
                        # 如果有捕获组，提取所有组的内容
                        extracted_contents = list(match.groups())
                    else:
                        # 如果没有捕获组，使用完整匹配
                        extracted_contents = [match.group(0)]
                    
                    # 将提取的内容用逗号分隔
                    extracted_content_str = ", ".join(extracted_contents)
                    
                    matched_rules.append({
                        "pattern": pattern,
                        "original_message": rule.get("originalMessage", ""),
                        "extracted_content": extracted_content_str,
                        "extracted_contents": extracted_contents,  # 保存原始提取内容列表
                        "full_match": match.group(0)
                    })
            except re.error as e:
                logger.error(f"正则表达式错误 '{pattern}': {e}")
            except Exception as e:
                logger.error(f"正则匹配时发生错误: {e}")
        
        return matched_rules

    def _save_matched_content(self, matched_data: Dict[str, Any], chat_name: str) -> None:
        """保存匹配到的内容到collect目录（CSV格式）
        
        Args:
            matched_data: 匹配到的数据
            chat_name: 聊天名称
        """
        try:
            # 创建collect目录
            collect_dir = os.path.join(CHAT_DATE_DIR, "collect")
            if not os.path.exists(collect_dir):
                os.makedirs(collect_dir)
            
            # 生成文件名：群聊名_YYYY-MM-DD.csv
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{chat_name}_{date_str}.csv"
            filepath = os.path.join(collect_dir, filename)
            
            # 检查文件是否存在，如果不存在则写入表头
            file_exists = os.path.exists(filepath)
            
            # 获取提取内容列表
            extracted_contents = matched_data.get('extracted_contents', [])
            
            # 将提取内容列表转换为字符串表示，例如：[项目1, 项目2, 项目3]
            extracted_content_str = str(extracted_contents)
            
            # 准备CSV行数据
            row_data = {
                '时间': matched_data['time'],
                '发送者': matched_data['sender'],
                '群聊': chat_name,
                '原始消息': matched_data['full_match'],
                '匹配规则': matched_data['pattern'],
                '提取内容': extracted_content_str,
            }
            
            # 固定表头
            fieldnames = ['时间', '发送者', '群聊', '原始消息', '匹配规则', '提取内容']
            
            # 写入CSV文件
            with open(filepath, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writeheader()
                
                # 写入数据行
                writer.writerow(row_data)
                
            logger.info(f"[正则匹配] 已保存匹配内容到CSV文件: {filepath}")
            
        except Exception as e:
            print(e)
            logger.error(f"保存匹配内容到CSV失败: {e}")

    def _process_message(self, msg: Any = None, chat: Any = None) -> None:
        """
        处理接收到的消息，只负责记录，不回复
        
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
            chat_name = chat_info["name"] or "未知聊天"

            # 记录消息接收时间戳
            receive_time = time.time()
            time_str = datetime.fromtimestamp(receive_time).strftime("%Y-%m-%d %H:%M:%S")

            # 获取消息内容
            msg_info = MessageInfo(msg)
            message_content = msg_info.get_content()
            sender = msg_info.get_sender()

            # 1. 检查是否包含敏感词
            if self._check_sensitive_words(message_content):
                logger.warning(f"[敏感内容检测] 检测到敏感内容: {message_content[:50]}... 发送者: {sender}")

            # 2. 存储消息到按天文件
            message_entry = f"[{time_str}] 发送者: {sender} | 群聊: {chat_name if is_group else '私聊'} | 内容: {message_content}"
            self._append_to_daily_file(message_entry, chat_name)
            
            # 3. 正则匹配消息内容
            matched_rules = self._match_regex_rules(message_content)
            if matched_rules:
                for matched_rule in matched_rules:
                    # 保存匹配到的内容到collect目录
                    matched_data = {
                        "time": time_str,
                        "sender": sender,
                        "full_match": matched_rule["full_match"],
                        "pattern": matched_rule["pattern"],
                        "extracted_content": matched_rule["extracted_content"],
                        "extracted_contents": matched_rule.get("extracted_contents", [])
                    }
                    self._save_matched_content(matched_data, chat_name)
                    
                    logger.info(f"[正则匹配] 匹配到规则: {matched_rule['pattern']}, 提取内容: {matched_rule['extracted_content']}")
            
            logger.debug(f"[消息存储] 已保存消息到按天文件: {message_entry[:100]}")

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("处理消息时发生错误: %s", e)
        except OSError as e:
            logger.error("OS error processing message: %s", e)
        except RuntimeError as e:
            logger.error("Runtime error processing message: %s", e)
    
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

    def run(self) -> None:
        """
        主运行循环
        负责初始化监听器、处理消息和清理资源
        """
        self.state.set_running(True)
        self.state.set_start_time(time.time())
        logger.info("AI worker thread started")

        try:
            if not self.init_listeners():
                self._cleanup()
                self.state.set_running(False)
                logger.error("AI worker thread initialization failed")
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
        logger.info("AI worker thread stopped")

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
    _instance: Optional['GroupWorkerManager'] = None
    workers: Dict[str, GroupWorkerThread] = {}
    lock: threading.Lock = threading.Lock()

    def __new__(cls) -> 'GroupWorkerManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.workers = {}
            cls._instance.lock = threading.Lock()
        return cls._instance

    def start_worker(self, config: WorkerConfig) -> bool:
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
                
                # 更新配置文件中的管理状态
                try:
                    if os.path.exists(group_manage_config_file):
                        with open(group_manage_config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        
                        # 无论工作线程是否存在，都设置management_enabled为false
                        config["management_enabled"] = False
                        config["data_collection_enabled"] = False
                        config["sentiment_monitoring_enabled"] = False
                        
                        # 保存更新后的配置
                        with open(group_manage_config_file, 'w', encoding='utf-8') as f:
                            json.dump(config, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    logger.error(f"更新配置状态失败: {e}")
                
                return True
            return False

    def get_worker_status(self, receiver: str) -> Optional[Dict[str, Any]]:
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
    try:
        # 首先验证群组是否在可用群组列表中
        success, available_groups = get_available_groups()
        if not success:
            return False, "获取可用群组失败"
        
        if group_name not in available_groups:
            return False, f"群组 '{group_name}' 不在可用群组列表中"
        
        # 保存选择的群聊到group_manage.json配置文件
        config = {}
        if os.path.exists(group_manage_config_file):
            with open(group_manage_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        config["selected_group"] = group_name
        
        # 保存更新后的配置
        with open(group_manage_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已选择群聊: {group_name}")
        return True, f"已选择群聊: {group_name}"
    except Exception as e:
        logger.error(f"选择群聊失败: {str(e)}")
        return False, f"选择群聊失败: {str(e)}"

def toggle_message_recording(group_name: str, enabled: bool) -> tuple:
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

def get_collected_data(group_name: str, start_date: str = None, end_date: str = None) -> tuple:
    try:
        # 只使用collect目录下的数据
        collect_dir = os.path.join(CHAT_DATE_DIR, "collect")
        
        if not os.path.exists(collect_dir):
            return False, "没有聊天数据目录"
        
        # 收集要返回的消息数据
        collected_data = []
        
        # 只遍历collect目录中的CSV文件
        print(f"扫描目录: {collect_dir}")
        for file_name in os.listdir(collect_dir):
            if not file_name.endswith('.csv'):
                continue
                
            # 检查文件名是否包含群名
            if group_name and not file_name.startswith(group_name):
                continue
                
            # 从文件名中提取日期
            # 文件名格式: 群名_YYYY-MM-DD.csv
            if group_name:
                # 检查文件名是否包含群名
                if file_name.startswith(group_name + "_"):
                    # 提取日期部分
                    date_part = file_name[len(group_name + "_"):-4]  # 去掉群名前缀和.csv后缀
                    file_date_str = date_part
                    print(f"处理文件: {file_name}, 提取的日期: {file_date_str}")
                else:
                    # 尝试使用正则表达式匹配文件名中的日期
                    import re
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_name)
                    if date_match:
                        file_date_str = date_match.group(1)
                        print(f"处理文件: {file_name}, 通过正则提取的日期: {file_date_str}")
                    else:
                        print(f"文件名格式不符合预期: {file_name}")
                        continue
            else:
                # 如果没有指定群名，尝试使用正则表达式提取日期
                import re
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_name)
                if date_match:
                    file_date_str = date_match.group(1)
                    print(f"处理文件: {file_name}, 通过正则提取的日期: {file_date_str}")
                else:
                    print(f"文件名格式不符合预期: {file_name}")
                    continue
            
            # 检查日期是否在指定范围内
            if start_date is not None and file_date_str is not None and file_date_str < start_date:
                continue
            if end_date is not None and file_date_str is not None and file_date_str > end_date:
                continue
            
            file_path = os.path.join(collect_dir, file_name)
            print(f"读取文件路径: {file_path}")
            
            # 读取CSV文件 - collect目录下的文件格式不同
            with open(file_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if len(row) >= 4:  # 确保行有足够的列
                        # collect目录下的文件格式：时间,发送者,群聊,消息内容,正则表达式,提取结果,原始消息
                        processed_row = {
                            'time': row[0] if len(row) > 0 else '',
                            'sender': row[1] if len(row) > 1 else '',
                            'group': row[2] if len(row) > 2 else '',
                            'content': row[3] if len(row) > 3 else '',
                            'type': '文本',
                            'extractedContent': row[5] if len(row) > 5 else '',  # 使用提取结果
                            'extracted_content': row[5] if len(row) > 5 else ''
                        }
                        
                        # 如果没有提取结果，尝试从内容中提取
                        if not processed_row['extractedContent'] and processed_row['content']:
                            content = processed_row['content']
                            # 匹配姓名
                            name_match = re.search(r'我叫([^，,。；;\s]+)', content)
                            # 匹配年龄
                            age_match = re.search(r'我(\d+)岁', content)
                            
                            if name_match and name_match.group(1):
                                extracted_parts = [name_match.group(1)]
                                if age_match and age_match.group(1):
                                    extracted_parts.append(f"{age_match.group(1)}岁")
                                
                                extracted_content = '，'.join(extracted_parts)
                                processed_row['extractedContent'] = extracted_content
                                processed_row['extracted_content'] = extracted_content
                        
                        collected_data.append(processed_row)
        
        if not collected_data:
            date_range = ""
            if start_date and end_date:
                date_range = f" ({start_date} 至 {end_date})"
            elif start_date:
                date_range = f" (从 {start_date} 开始)"
            elif end_date:
                date_range = f" (至 {end_date} 结束)"
                
            return False, f"未找到{group_name}{date_range}的聊天记录"
        
        logger.info(f"已获取{group_name}的聊天数据，共{len(collected_data)}条记录")
        return True, collected_data
    except Exception as e:
        logger.error(f"获取聊天数据失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def start_group_management(group_name: str, settings: dict) -> tuple:
    try:
        # 1. 保存群聊管理配置到group_manage.json
        config = {}
        if os.path.exists(group_manage_config_file):
            with open(group_manage_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 更新配置
        if group_name not in config:
            config[group_name] = {}
        
        config[group_name].update({
            "enabled": True,
            "start_time": datetime.now().isoformat(),
            "settings": settings
        })
        
        # 保存全局配置状态（用于API获取）
        config["management_enabled"] = True
        config["data_collection_enabled"] = settings.get("data_collection_enabled", False)
        config["sentiment_monitoring_enabled"] = settings.get("sentiment_monitoring_enabled", False)
        
        # 保存配置到group_manage.json
        with open(group_manage_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已保存{group_name}的群聊管理配置到group_manage.json")
        
        # 2. 开始监听群聊
        if default_wx_instance:
            # 创建工作线程配置
            worker_config = WorkerConfig(
                wx_instance=default_wx_instance,
                receiver=group_name,
                record_interval=settings.get("record_interval", 0),
                sensitive_words=settings.get("sensitive_words", [])
            )
            
            # 启动工作线程
            success = group_manager.start_worker(worker_config)
            if not success:
                return False, "启动群聊监听失败"
            
            logger.info(f"已开始监听群聊: {group_name}")
        
        return True, f"已成功开始管理群聊: {group_name}"
    except Exception as e:
        logger.error(f"开始群聊管理失败: {str(e)}")
        return False, f"操作失败: {str(e)}"

def start_sentiment_monitoring(group_name: str, sensitive_words: str) -> tuple:
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


def get_available_groups() -> tuple:
    try:
        groups = []
        
        # 从chat_date/collect目录获取群组信息
        collect_dir = os.path.join(os.path.dirname(__file__), "chat_date", "collect")
        if os.path.exists(collect_dir):
            excel_files = [f for f in os.listdir(collect_dir) if f.endswith('.csv')]
            for file_name in excel_files:
                if '_' in file_name:
                    # 移除文件扩展名
                    base_name = file_name.replace('.csv', '')
                    # 分割群名和日期
                    parts = base_name.split('_')
                    if len(parts) >= 2:
                        # 群名是除最后一部分（日期）之外的所有部分
                        group_name = '_'.join(parts[:-1])
                        date_part = parts[-1]
                        
                        # 验证日期格式 (YYYY-MM-DD)
                        try:
                            datetime.strptime(date_part, "%Y-%m-%d")
                            if group_name not in groups:
                                groups.append(group_name)
                        except ValueError:
                            # 如果不是有效的日期格式，可能只是群名
                            if base_name not in groups:
                                groups.append(base_name)
        return True, groups
        
    except Exception as e:
        logger.error(f"获取可用群组失败: {str(e)}")
        return False, f"获取群组失败: {str(e)}"


def get_group_dates(group_name: str) -> tuple:
    try:
        dates = []
        
        # 从chat_date/collect目录获取该群组的日期信息
        collect_dir = os.path.join(os.path.dirname(__file__), "chat_date", "collect")
        if os.path.exists(collect_dir):
            # 获取所有Excel文件
            excel_files = [f for f in os.listdir(collect_dir) if f.endswith('.xlsx')]
            
            for file_name in excel_files:
                # 解析文件名格式：群名_日期.xlsx
                if '_' in file_name and group_name in file_name:
                    # 移除文件扩展名
                    base_name = file_name.replace('.xlsx', '')
                    # 分割群名和日期
                    parts = base_name.split('_')
                    if len(parts) >= 2:
                        # 检查是否匹配群名
                        file_group_name = '_'.join(parts[:-1])
                        date_part = parts[-1]
                        
                        if file_group_name == group_name:
                            # 验证日期格式 (YYYY-MM-DD)
                            try:
                                datetime.strptime(date_part, "%Y-%m-%d")
                                if date_part not in dates:
                                    dates.append(date_part)
                            except ValueError:
                                # 如果不是有效的日期格式，跳过
                                continue
        
        # 按日期排序（最新的在前）
        dates.sort(reverse=True)
        
        return True, dates
        
    except Exception as e:
        logger.error(f"获取群组 '{group_name}' 的日期列表失败: {str(e)}")
        return False, f"获取日期列表失败: {str(e)}"


# 正则规则配置文件
regex_config_file = os.path.join(data_dir, "regex_rules.json")
