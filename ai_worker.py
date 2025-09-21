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

logger = get_logger(__name__)

DEFAULT_MODEL = "MoonDarkSide"
DEFAULT_ROLE = "你是一个的微信好友，全程隐藏 AI 身份，能类似真人的自然感回应，具体按以下要求执行：对话风格：完全口语化，不用长句和书面词，带日常语气词（\"卧槽\"等）或网络热梗。话题应对：懂的话题别 \"掉书袋\"，聊日常细节就行。应对 \"AI 质疑\"：如果用户说 \"你怎么像机器人\"\"你是 AI 吧\"，别辩解不能掉入\"自证陷阱\"并嘲讽对方。总之，你就是一个普通人，聊得随意、有烟火气，别让人觉得 \"说话没温度、不像真人\"。"
DEFAULT_REPLY_DELAY = 0
DEFAULT_MIN_REPLY_INTERVAL = 0
DATA_DIR = "data"
RULES_FILE = "ai_data.json"
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


class MessageInfo:
    
    def __init__(self, message: Any):
        self.message = message
    
    def get_sender(self) -> str:
        if hasattr(self.message, 'sender'):
            return self.message.sender
        elif hasattr(self.message, 'get') and callable(getattr(self.message, 'get')):
            return self.message.get('sender', '')
        return ""
    
    def get_content(self) -> str:
        if hasattr(self.message, 'content'):
            return self.message.content or ""
        elif hasattr(self.message, 'get') and callable(getattr(self.message, 'get')):
            return self.message.get("content", "")
        return str(self.message)
    
    def get_type(self) -> str:
        if hasattr(self.message, "type"):
            return self.message.type.lower()
        return ""
    
    def is_system_message(self) -> bool:
        return self.get_type() == SYSTEM_MESSAGE_TYPE
    
    def is_self_message(self) -> bool:
        return self.get_sender() == SELF_SENDER
    
    def is_empty_content(self) -> bool:
        return not self.get_content().strip()
    
    def is_valid_message_type(self) -> bool:
        return self.get_type() in MESSAGE_TYPES


class ReplyHandler:
    
    def __init__(self, wx_instance: Any):
        self.wx_instance = wx_instance
    
    def send_reply(self, sender: str, reply_content: str, at_user: Optional[str] = None) -> bool:
        try:
            if not self._check_quota(sender):
                return False
            
            if self._is_file_path(reply_content):
                return self._send_file(sender, reply_content)
            elif reply_content.startswith(SEND_EMOTION_PREFIX):
                return self._send_emotion(sender, reply_content)
            else:
                return self._send_text(sender, reply_content, at_user)
                
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("Error sending reply to %s: %s", sender, e)
            return False
        except Exception as e:
            logger.error("Unexpected error sending reply to %s: %s", sender, e)
            return False
    
    def _check_quota(self, sender: str) -> bool:
        try:
            from data_manager import load_message_quota
            quota_data = load_message_quota()
            account_level = quota_data.get("account_level", "free")
            
            if quota_data.get("blocked", False):
                logger.warning("[AI接管] 账户已被阻止，无法发送回复给 %s", sender)
                return False
            
            if account_level != "enterprise":
                daily_limit = ACCOUNT_LEVELS.get(account_level, 100)
                if quota_data.get("used_today", 0) >= daily_limit:
                    logger.warning("[AI接管] 配额已耗尽，无法发送回复给 %s", sender)
                    return False
            return True
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("Error checking quota: %s", e)
            return False
        except Exception as e:
            logger.error("Unexpected error checking quota: %s", e)
            return False
    
    def _is_file_path(self, content: str) -> bool:
        file_path = content
        if (content.startswith('"') and content.endswith('"')) or (
                content.startswith("'") and content.endswith("'")):
            file_path = content[1:-1]
        return os.path.exists(file_path)
    
    def _send_file(self, sender: str, file_path: str) -> bool:
        try:
            response = self.wx_instance.SendFiles(file_path, sender)
            if response.get("status") == STATUS_FAILED:
                logger.error("Failed to send file to %s: %s", sender, response.get('message', 'Unknown error'))
                return False
            
            from data_manager import increment_message_count
            increment_message_count()
            logger.info("File sent to %s: %s", sender, file_path)
            return True
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("Error sending file to %s: %s", sender, e)
            return False
        except Exception as e:
            logger.error("Unexpected error sending file to %s: %s", sender, e)
            return False
    
    def _send_emotion(self, sender: str, content: str) -> bool:
        try:
            match = re.search(r'SendEmotion:([\d,，]+)', content)
            if not match:
                logger.error("表情包格式错误，应为SendEmotion:数字或多个数字用逗号（中文或英文）分隔")
                return False
                
            emotion_str = match.group(1).replace('，', ',')
            emotion_indices = [int(idx) for idx in emotion_str.split(',')]
            emotion_index = random.choice(emotion_indices)
            response = self.wx_instance.SendEmotion(emotion_index - 1, sender)
            
            if response.get("status") == STATUS_FAILED:
                logger.error("Failed to send emotion to %s: %s", sender, response.get('message', 'Unknown error'))
                return False
            
            from data_manager import increment_message_count
            increment_message_count()
            logger.info("Emotion sent to %s (selected %s)", sender, emotion_index)
            return True
        except (ValueError, IndexError, AttributeError, KeyError) as e:
            logger.error("Error sending emotion to %s: %s", sender, e)
            return False
        except Exception as e:
            logger.error("Unexpected error sending emotion to %s: %s", sender, e)
            return False
    
    def _send_text(self, sender: str, content: str, at_user: Optional[str] = None) -> bool:
        try:
            response = self.wx_instance.SendMsg(msg=content, who=sender, at=at_user)
            if response.get("status") == STATUS_FAILED:
                logger.error("Failed to send message to %s: %s", sender, response.get('message', 'Unknown error'))
                return False
            
            # 消息发送成功后，增加消息配额计数
            from data_manager import increment_message_count
            increment_message_count()
            logger.info("Message sent to %s: %s", sender, content)
            return True
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("Error sending message to %s: %s", sender, e)
            return False
        except OSError as e:
            logger.error("OS error sending message to %s: %s", sender, e)
            return False
        except Exception as e:
            logger.error("Unexpected error sending message to %s: %s", sender, e)
            return False


class RulesManager:    
    def __init__(self, rules_file_path: str):
        self.rules_file_path = rules_file_path
        self.rules: List[Dict[str, str]] = []
        self._load_rules()
    
    def _load_rules(self) -> None:
        try:
            with open(self.rules_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "settings" in data:
                    settings = data["settings"]
                    if isinstance(settings, dict) and "customRules" in settings:
                        self.rules = settings["customRules"]
                        return
                self.rules = []
        except FileNotFoundError:
            logger.warning("Auto-reply rules file not found")
            self.rules = []
        except json.JSONDecodeError:
            logger.error("Auto-reply rules file parsing failed")
            self.rules = []
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("Error loading rules: %s", e)
            self.rules = []
        except OSError as e:
            logger.error("OS error loading rules: %s", e)
            self.rules = []
        except Exception as e:
            logger.error("Unexpected error loading rules: %s", e)
            self.rules = []
    
    def update_rules(self) -> bool:
        try:
            with open(self.rules_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                new_rules = []
                if isinstance(data, dict) and "settings" in data:
                    settings = data["settings"]
                    if isinstance(settings, dict) and "customRules" in settings:
                        new_rules = settings["customRules"]

                if new_rules != self.rules:
                    self.rules = new_rules
                    logger.info("[AI接管] 已更新自定义规则，当前规则数: %s", len(self.rules))
                    return True
                
                logger.debug("[AI接管] 自定义规则无变化，无需更新")
                return False
        except FileNotFoundError:
            logger.warning("Auto-reply rules file not found")
            if self.rules:
                self.rules = []
                logger.info("[AI接管] 规则文件不存在，已清空自定义规则")
                return True
            return False
        except json.JSONDecodeError:
            logger.error("Auto-reply rules file parsing failed")
            return False
        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("Error updating rules: %s", e)
            return False
        except OSError as e:
            logger.error("OS error updating rules: %s", e)
            return False
        except Exception as e:
            logger.error("Unexpected error updating rules: %s", e)
            return False
    
    def match_rule(self, msg: str) -> List[str]:
        if not self.rules:
            return []

        matched_replies = []
        msg = msg.strip()

        for rule in self.rules:
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
                    pattern = re.compile(keyword)
                    if pattern.search(msg):
                        matched_replies.append(rule["reply"])
            except re.error as e:
                logger.error("Invalid regular expression '%s': %s", keyword, e)
            except (ValueError, TypeError, AttributeError, KeyError) as e:
                logger.error("Error matching rule: %s", e)
            except OSError as e:
                logger.error("OS error matching rule: %s", e)
            except Exception as e:
                logger.error("Unexpected error matching rule: %s", e)
        return matched_replies
    
    def apply_custom_rules(self, message_content: str) -> str:
        matched_replies = self.match_rule(message_content)
        return matched_replies[0] if matched_replies else ""


class WorkerConfig:    
    def __init__(
        self,
        wx_instance: Any,
        receiver: str,
        model: str = DEFAULT_MODEL,
        role: str = DEFAULT_ROLE,
        only_at: bool = False,
        group_at_reply: bool = False,
        reply_delay: int = DEFAULT_REPLY_DELAY,
        min_reply_interval: int = DEFAULT_MIN_REPLY_INTERVAL,
    ):
        self.wx_instance = wx_instance
        self.receiver = receiver
        self.model = model
        self.role = role
        self.only_at = only_at
        self.group_at_reply = group_at_reply
        self.reply_delay = reply_delay
        self.min_reply_interval = min_reply_interval


class MessageHistory:    
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
        return self._message_lock
    
    def get_stop_event(self) -> threading.Event:
        return self._stop_event
    
    def is_running(self) -> bool:
        return self._is_running
    
    def set_running(self, running: bool) -> None:
        self._is_running = running
    
    def is_paused(self) -> bool:
        return self._paused
    
    def set_paused(self, paused: bool) -> None:
        self._paused = paused
    
    def get_pause_condition(self) -> threading.Condition:
        return self._pause_cond
    
    def get_start_time(self) -> Optional[float]:
        return self.start_time
    
    def set_start_time(self, start_time: float) -> None:
        self.start_time = start_time


class AiWorkerThread:
    
    def __init__(self, config: WorkerConfig):
        if not config.wx_instance:
            raise ValueError("wx_instance参数不能为空")

        self.config = config
        self.at_me = f"@{self.config.wx_instance.nickname}"
        self.receiver_list = [
            r.strip() for r in self.config.receiver.replace("，", ",").split(",") if r.strip()
        ]
        
        self.state = WorkerState()
        
        rules_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_DIR, RULES_FILE)
        self.rules_manager = RulesManager(rules_file_path)
        self.reply_handler = ReplyHandler(self.config.wx_instance)

        logger.info(
            "AI worker thread initialized: receiver=%s, model=%s, role=%s, only_at=%s, group_at_reply=%s, delay=%ss, min_interval=%ss",
            self.config.receiver,
            self.config.model,
            self.config.role,
            self.config.only_at,
            self.config.group_at_reply,
            self.config.reply_delay,
            self.config.min_reply_interval,
        )

    def update_rules(self) -> bool:
        return self.rules_manager.update_rules()

    def init_listeners(self) -> bool:
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
                self._cleanup()
                return False
            except OSError as e:
                logger.error("OS error adding listener: %s, error: %s", target, str(e))
                self._cleanup()
                return False
            except RuntimeError as e:
                logger.error("Runtime error adding listener: %s, error: %s", target, str(e))
                self._cleanup()
                return False
        return True

    def _get_chat_name(self, who: str) -> str:
        if not hasattr(self.config.wx_instance, "GetChatName"):
            return who
        return self.config.wx_instance.GetChatName(who)

    def _is_target_message(self, message: Any) -> bool:
        try:
            msg_info = MessageInfo(message)
            sender = msg_info.get_sender()
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

    def _generate_ai_reply(self, message_content: str) -> None:
        try:
            reply = self._query_ai_model(message_content)
            if reply:
                if hasattr(self, '_current_message_context'):
                    context = self._current_message_context
                    is_group = context.get("is_group", False)
                    sender = context.get("sender", "")
                    group_name = context.get("group_name", "")
                    receive_time = context.get("receive_time", time.time())
                else:
                    is_group = False
                    sender = ""
                    group_name = ""
                    receive_time = time.time()
                
                reply_sent = False
                if is_group:
                    at_user = sender if self.config.group_at_reply else ""
                    reply_sent = self.reply_handler.send_reply(group_name, reply, at_user=at_user)
                else:
                    reply_sent = self.reply_handler.send_reply(sender, reply)
                
                if reply_sent:
                    self.state.last_reply_info = {"content": message_content, "time": time.time()}
                    history = MessageHistory(
                        sender, 
                        message_content, 
                        reply, 
                        "replied", 
                        round(time.time() - receive_time, 2)
                    )
                    self._record_history(history)
                else:
                    history = MessageHistory(
                        sender, 
                        message_content, 
                        reply, 
                        "not_replied", 
                        0
                    )
                    self._record_history(history)
        except Exception as e:
            logger.error("生成AI回复失败: %s", e)
    
    def _query_ai_model(self, message: str) -> str:
        model = self.config.model
        
        if model == "wenxin":
            return self._query_wenxin(message)
        elif model == "moonshot":
            return self._query_moonshot(message)
        elif model == "xinghuoxunfei":
            return self._query_spark(message)
        else:
            logger.warning("未知的AI模型: %s", model)
            return ""

    def _query_api(self, url, payload=None, headers=None, params=None, method='POST'):
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=payload,
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.error("请求错误: %s", e)
            return None
        except httpx.HTTPStatusError as e:
            logger.error("HTTP状态错误: %s", e)
            return None
        except Exception as e:
            logger.error("未知错误: %s", e)
            return None
    
    def _query_wenxin(self, message: str) -> str:
        def _get_access_token():
            response = self._query_api(
                "https://aip.baidubce.com/oauth/2.0/token",
                params={'grant_type': 'client_credentials',
                        'client_id': 'eCB39lMiTbHXV0mTt1d6bBw7',
                        'client_secret': 'WUbEO3XdMNJLTJKNQfFbMSQvtBVzRhvu'}
            )
            return response.get("access_token") if response else None
        access_token = _get_access_token()
        if not access_token:
            return "无法获取百度API访问令牌"

        payload = {"messages": [{"role": "user", "content": message}]}
        response = self._query_api(
            f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k?access_token={access_token}",
            payload=payload,
            headers={'Content-Type': 'application/json'}
        )
        return response.get('result', "无法解析响应") if response else "请求失败"
    
    def _query_moonshot(self, message: str) -> str:
        headers = {
            "Authorization": "Bearer sk-dx1RuweBS0LU0bCR5HizbWjXLuBL6HrS8BT21NEEGwbeyuo6",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "moonshot-v1-8k",
            "messages": [
                {"role": "system", "content": self.config.role},
                {"role": "user", "content": message}
            ],
            "temperature": 0.9
        }
        response = self._query_api("https://api.moonshot.cn/v1/chat/completions", payload, headers)
        return response['choices'][0]['message']['content'] if response else "无法解析响应"
    
    def _query_spark(self, message: str) -> str:
        data = {
            "max_tokens": 64,
            "top_k": 4,
            "temperature": 0.9,
            "messages": [
                {"role": "system", "content": self.config.role},
                {"role": "user", "content": message}
            ],
            "model": "4.0Ultra"
        }
        header = {
            "Authorization": "Bearer xCPWitJxfzhLaZNOAdtl:PgJXiEyvKjUaoGzKwgIi",
            "Content-Type": "application/json"
        }
        response = self._query_api("https://spark-api-open.xf-yun.com/v1/chat/completions", data, header)
        return response['choices'][0]['message']['content'] if response else "无法解析响应"
    
    def _get_chat_info_from_message(self) -> Dict[str, Any]:
        return {
            "type": "friend",
            "name": "",
            "sender": "",
            "receive_time": time.time()
        }

    def _cleanup(self) -> None:
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
        with self.state.get_pause_condition():
            self.state.set_paused(True)

    def resume(self) -> None:
        with self.state.get_pause_condition():
            self.state.set_paused(False)
            self.state.get_pause_condition().notify()

    def is_paused(self) -> bool:
        return self.state.is_paused()

    def wait_for_resume(self) -> None:
        with self.state.get_pause_condition():
            while self.state.is_paused():
                self.state.get_pause_condition().wait()

    def stop(self) -> None:
        self.state.get_stop_event().set()
        self.state.set_running(False)
        self.resume()

    def is_running(self) -> bool:
        return self.state.is_running()

    def get_uptime(self) -> int:
        return int(time.time() - self.state.get_start_time()) if self.state.get_start_time() else 0

    def _is_ignored_message(self, message: Any) -> bool:
        try:
            msg_info = MessageInfo(message)
            
            if msg_info.is_system_message():
                return True

            if msg_info.is_self_message():
                return True

            if not msg_info.is_valid_message_type():
                return True

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
        return self.state.get_stop_event().is_set() or not self.state.is_running()

    def _process_message(self, msg: Any = None, chat: Any = None) -> None:
        try:
            if msg is None:
                return
                
            chat_info = self._get_chat_info(chat)
            is_group = chat_info["type"] == "group"
            group_name = chat.who

            receive_time = time.time()

            msg_info = MessageInfo(msg)
            message_content = msg_info.get_content()
            sender = msg_info.get_sender()

            if self.config.only_at and is_group:
                if self.at_me not in message_content:
                    logger.debug("[AI接管] 群聊消息未包含@我，忽略消息: %s", message_content)
                    return
                message_content = message_content.replace(self.at_me, "").strip()

            if self._should_ignore_due_to_interval(message_content):
                logger.info("[AI接管] 相同内容未达到最小回复间隔，忽略消息: %s", message_content)
                history = MessageHistory(sender, message_content, "", "blocked", 0)
                self._record_history(history)
                return

            if self.config.reply_delay > 0:
                time.sleep(self.config.reply_delay)

            custom_reply = self.rules_manager.apply_custom_rules(message_content)
            if custom_reply:

                reply_sent = False
                if is_group:
                    at_user = sender if self.config.group_at_reply else ""
                    reply_sent = self.reply_handler.send_reply(group_name, custom_reply, at_user=at_user)
                else:
                    reply_sent = self.reply_handler.send_reply(sender, custom_reply)
                
                if reply_sent:
                    self.state.last_reply_info = {"content": message_content, "time": time.time()}
                    actual_response_time = round(time.time() - receive_time, 2)
                    history = MessageHistory(sender, message_content, custom_reply, "replied", actual_response_time)
                    self._record_history(history)
                else:
                    history = MessageHistory(sender, message_content, custom_reply, "not_replied", 0)
                    self._record_history(history)
                return

            if self.config.model != "disabled":
                self._current_message_context = {
                    "sender": sender,
                    "message_content": message_content,
                    "receive_time": receive_time,
                    "is_group": is_group,
                    "group_name": group_name if is_group else ""
                }
                self._generate_ai_reply(message_content)
                logger.debug("[AI接管] 使用AI模型回复消息: %s", message_content)
            else:
                logger.debug("[AI接管] AI模型已禁用，不回复消息: %s", message_content)
            return

        except (ValueError, TypeError, AttributeError, KeyError) as e:
            logger.error("处理消息时发生错误: %s", e)
            if msg is not None:
                msg_info = MessageInfo(msg)
                history = MessageHistory(msg_info.get_sender(), msg_info.get_content(), "", "failed", 0)
                self._record_history(history)
        except OSError as e:
            logger.error("OS error processing message: %s", e)
            if msg is not None:
                msg_info = MessageInfo(msg)
                history = MessageHistory(msg_info.get_sender(), msg_info.get_content(), "", "failed", 0)
                self._record_history(history)
        except RuntimeError as e:
            logger.error("Runtime error processing message: %s", e)
            if msg is not None:
                msg_info = MessageInfo(msg)
                history = MessageHistory(msg_info.get_sender(), msg_info.get_content(), "", "failed", 0)
                self._record_history(history)
    
    def _get_chat_info(self, chat: Any) -> Dict[str, str]:
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
        if self.config.min_reply_interval <= 0:
            return False
            
        current_time = time.time()
        return (
            message_content == self.state.last_reply_info["content"] and
            current_time - self.state.last_reply_info["time"] < self.config.min_reply_interval
        )
    
    def _record_history(self, history: MessageHistory) -> None:
        add_ai_history(history.to_dict())

    def run(self) -> None:
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

        while not self._should_stop():
            try:
                if self.state.is_paused():
                    self.wait_for_resume()
                    continue

                if int(time.time()) % 10 == 0:
                    self.update_rules()

                messages_dict = self.config.wx_instance.GetListenMessage()
                if not messages_dict:
                    time.sleep(0.1)
                    continue

                for chat, messages in messages_dict.items():
                    if self._should_stop():
                        break
                    for message in messages:
                        if self._should_stop():
                            break

                        with self.state.get_message_lock():
                            if self._is_ignored_message(message):
                                continue
                            self._process_message(message, chat)

            except (ValueError, TypeError, AttributeError, KeyError) as e:
                logger.error("Error in main loop: %s", e)
                if self._should_stop():
                    break
                time.sleep(1)
            except OSError as e:
                logger.error("OS error in main loop: %s", e)
                if self._should_stop():
                    break
                time.sleep(1)
            except RuntimeError as e:
                logger.error("Runtime error in main loop: %s", e)
                if self._should_stop():
                    break
                time.sleep(1)

        self._cleanup()
        self.state.set_running(False)
        logger.info("AI worker thread stopped")


class AiWorkerManager:
    
    _instance: Optional['AiWorkerManager'] = None
    workers: Dict[str, AiWorkerThread] = {}
    lock: threading.Lock = threading.Lock()

    def __new__(cls) -> 'AiWorkerManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.workers = {}
            cls._instance.lock = threading.Lock()
        return cls._instance

    def start_worker(self, config: WorkerConfig) -> bool:
        with self.lock:
            worker_key = f"{config.receiver}_{config.model}"
            if worker_key in self.workers:
                return False

            worker = AiWorkerThread(config)
            self.workers[worker_key] = worker

            try:
                thread = threading.Thread(target=worker.run, daemon=True)
                thread.start()

                time.sleep(0.1)
                if not worker.is_running():
                    del self.workers[worker_key]
                    return False

                max_wait_time = 5
                wait_interval = 0.1
                total_wait_time = 0
                
                while total_wait_time < max_wait_time:
                    if not worker.is_running():
                        del self.workers[worker_key]
                        return False
                    
                    if hasattr(worker.state, 'listen_list') and len(worker.state.listen_list) > 0:
                        return True
                    
                    time.sleep(wait_interval)
                    total_wait_time += wait_interval
                
                if worker.is_running() and hasattr(worker.state, 'listen_list') and len(worker.state.listen_list) > 0:
                    return True
                else:
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

    def stop_worker(self, receiver: str, model: str = DEFAULT_MODEL) -> bool:
        with self.lock:
            worker_key = f"{receiver}_{model}"
            if worker_key in self.workers:
                worker = self.workers[worker_key]
                worker.stop()
                del self.workers[worker_key]
                return True
            return False

    def get_worker_status(self, receiver: str, model: str = DEFAULT_MODEL) -> Optional[Dict[str, Any]]:
        with self.lock:
            worker_key = f"{receiver}_{model}"
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
        with self.lock:
            for worker in self.workers.values():
                worker.stop()
            self.workers.clear()

    def update_all_workers_rules(self) -> bool:
        updated_count = 0
        for _, worker in self.workers.items():
            if worker.update_rules():
                updated_count += 1

        if updated_count > 0:
            logger.info("[AI接管] 已通知 %s 个AI工作线程更新规则", updated_count)
        else:
            logger.debug("[AI接管] 没有工作线程需要更新规则")

        return updated_count > 0
