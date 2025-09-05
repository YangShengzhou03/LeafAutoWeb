import threading
import time
import json
import re
from datetime import datetime
from data_manager import add_ai_history
from logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)


class AiWorkerThread:
    def __init__(self, wx_instance, receiver, model="MoonDarkSide",
                 role="You are warm and friendly, reply simply and clearly.", only_at=False, reply_delay=5,
                 min_reply_interval=60):
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
        self.receiver_list = [r.strip() for r in receiver.replace(';', '；').split('；') if r.strip()]
        self.listen_list = []
        self.last_sent_messages = {}
        self._message_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._is_running = False
        self._paused = False
        self._pause_cond = threading.Condition(threading.Lock())
        self.start_time = None

        logger.info(
            f"AI worker thread initialized: receiver={self.receiver}, delay={self.reply_delay}s, min_interval={self.min_reply_interval}s")

    def _load_rules(self):
        try:
            with open('data/ai_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 检查数据结构是否正确，确保settings和customRules存在
                if isinstance(data, dict) and 'settings' in data:
                    settings = data['settings']
                    if isinstance(settings, dict) and 'customRules' in settings:
                        return settings['customRules']
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
        if not hasattr(self.wx_instance, 'GetChatName'):
            return who
        return self.wx_instance.GetChatName(who)

    def _match_rule(self, msg):
        if not self.rules or self._should_stop():
            return []

        matched_replies = []
        msg = msg.strip()

        for rule in self.rules:
            if self._should_stop():
                return []

            keyword = rule['keyword'].strip()
            if not keyword:
                continue

            match_type = rule['matchType']
            try:
                if match_type == 'equals' and msg == keyword:
                    matched_replies.append(rule['reply'])
                elif match_type == 'contains' and keyword in msg:
                    matched_replies.append(rule['reply'])
                elif match_type == 'regex' and re.search(keyword, msg):
                    matched_replies.append(rule['reply'])
            except re.error:
                logger.error(f"Invalid regular expression: {keyword}")
            except Exception as e:
                logger.error(f"Error matching rule: {e}")

        return matched_replies

    def _cleanup(self):
        try:
            for target in self.listen_list:
                if hasattr(self.wx_instance, 'RemoveListenChat'):
                    try:
                        self.wx_instance.RemoveListenChat(who=target)
                    except Exception as e:
                        logger.error(f"Failed to remove listener for {target}: {e}")
            self.listen_list.clear()
        except Exception as e:
            logger.error(f"清理监听时出错: {str(e)}")

    def pause(self):
        with self._pause_cond:
            self._paused = True

    def resume(self):
        with self._pause_cond:
            self._paused = False
            self._pause_cond.notify()

    def isPaused(self):
        return self._paused

    def wait_for_resume(self):
        with self._pause_cond:
            while self._paused:
                self._pause_cond.wait()

    def stop(self):
        self._stop_event.set()
        self._is_running = False
        self.resume()

    def is_running(self):
        return self._is_running

    def get_uptime(self):
        return int(time.time() - self.start_time) if self.start_time else 0

    def _is_ignored_message(self, message):
        try:
            if hasattr(message, 'type') and message.type.lower() == 'sys':
                return True
            if hasattr(message, 'sender') and message.sender == 'Self':
                return True
            if hasattr(message, 'type') and message.type.lower() != 'friend':
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking ignored message: {e}")
            return True

    def _should_stop(self):
        return self._stop_event.is_set() or not self._is_running

    def _process_message(self, content, who):
        chat_name = self._get_chat_name(who)
        try:
            if self.only_at and self.at_me not in content:
                return

            current_time = time.time()

            # 检查是否为连续重复内容
            if chat_name in self.last_sent_messages:
                last_message_data = self.last_sent_messages[chat_name]
                last_content = last_message_data['content']
                last_timestamp = last_message_data['timestamp']

                # 仅在内容完全一致时检查时间间隔
                if content == last_content:
                    if current_time - last_timestamp < self.min_reply_interval:
    
                        return

            matched_replies = self._match_rule(content)
            if not matched_replies:
                return

            reply_content = matched_replies[0]

            if self.reply_delay > 0:

                time.sleep(self.reply_delay)

            response = self.wx_instance.SendMsg(msg=reply_content, who=who)

            if isinstance(response, dict) and response.get("status") == "成功":
                # 增加消息配额计数
                from data_manager import increment_message_count
                if not increment_message_count():
                    logger.error(f"信息余量耗尽，无法发送消息给 {chat_name}")
                    return
                
                # 存储最后发送的消息内容和时间戳
                self.last_sent_messages[chat_name] = {
                    'content': content,
                    'timestamp': time.time()
                }

                history_data = {
                    'sender': chat_name,
                    'message': content,
                    'reply': reply_content,
                    'status': 'replied',
                    'responseTime': self.reply_delay,
                    'timestamp': datetime.now().isoformat()
                }
                add_ai_history(history_data)

                logger.info(f"Replied to {chat_name}: {reply_content}")
            else:
                logger.error(f"Failed to send message to {chat_name}: {response}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def run(self):
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
                    if response.get('status') == '失败':
                        raise ValueError(
                            f"Initialization send failed: {response.get('message', 'Friend with this remark not found')}")
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
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.workers = {}
            cls._instance.lock = threading.Lock()
        return cls._instance

    def start_worker(self, wx_instance, receiver, model="MoonDarkSide",
                     role="You are warm and friendly, reply simply and clearly.", only_at=False, reply_delay=5,
                     min_reply_interval=60):
        with self.lock:
            worker_key = f"{receiver}_{model}"
            if worker_key in self.workers:
                return False

            worker = AiWorkerThread(wx_instance, receiver, model, role, only_at, reply_delay, min_reply_interval)
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
        with self.lock:
            worker_key = f"{receiver}_{model}"
            if worker_key in self.workers:
                worker = self.workers[worker_key]
                worker.stop()
                del self.workers[worker_key]
                return True
            return False

    def get_worker_status(self, receiver, model="MoonDarkSide"):
        with self.lock:
            worker_key = f"{receiver}_{model}"
            if worker_key in self.workers:
                worker = self.workers[worker_key]
                return {
                    'running': worker.is_running(),
                    'uptime': worker.get_uptime(),
                    'paused': worker.isPaused()
                }
            return None

    def get_all_workers(self):
        with self.lock:
            return list(self.workers.keys())

    def stop_all_workers(self):
        with self.lock:
            for worker in self.workers.values():
                worker.stop()
            self.workers.clear()
