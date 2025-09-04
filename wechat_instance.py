"""
微信实例共享模块
提供全局的WeChat实例，避免重复创建
支持定期状态检查和自动重连
"""

import threading
import time
from datetime import datetime
from wxautox import WeChat
from logging_config import get_logger

# 初始化日志器
logger = get_logger(__name__)

# 全局微信实例
_wx_instance = None
# 状态检查线程
_status_check_thread = None
_status_check_interval = 30  # 30秒检查一次
_last_status_check = datetime.now()
# 状态信息缓存
_cached_status_info = None
_status_cache_timeout = 10  # 10秒缓存时间
_last_status_update = datetime.now()

def get_wechat_instance():
    """
    获取全局WeChat实例
    如果实例不存在则创建，存在则直接返回
    """
    global _wx_instance
    if _wx_instance is None:
        try:
            _wx_instance = WeChat()
        except Exception as e:
            logger.error(f"微信实例创建失败: {e}")
            _wx_instance = None
    return _wx_instance

def init_wechat():
    """
    初始化微信对象，如果微信未登录则返回False
    """
    global _wx_instance
    try:
        _wx_instance = WeChat()
        # 检查微信是否在线
        if _wx_instance.IsOnline():
            return True
        else:
            _wx_instance = None
            return False
    except Exception as e:
        logger.error(f"微信初始化失败: {e}")
        _wx_instance = None
        return False

def is_wechat_online():
    """
    检查微信是否在线
    """
    global _wx_instance
    try:
        if _wx_instance is None:
            return False
        return _wx_instance.IsOnline()
    except Exception:
        return False

def start_status_monitor():
    """
    启动微信状态监控线程
    """
    global _status_check_thread
    if _status_check_thread and _status_check_thread.is_alive():
        return
    
    def status_monitor():
        while True:
            try:
                global _last_status_check
                _last_status_check = datetime.now()
                
                # 检查微信状态
                if _wx_instance is None:
                    init_wechat()
                elif not is_wechat_online():
                    logger.warning("[微信监控] 微信连接丢失，尝试重新初始化...")
                    init_wechat()
                
                # 强制更新状态信息缓存
                global _cached_status_info, _last_status_update
                _cached_status_info = {
                    'online': is_wechat_online(),
                    'instance_exists': _wx_instance is not None,
                    'last_check': _last_status_check.isoformat() if _last_status_check else None,
                    'check_interval': _status_check_interval,
                    'user_info': get_wechat_user_info()
                }
                _last_status_update = datetime.now()
                
                time.sleep(_status_check_interval)
            except Exception as e:
                logger.error(f"[微信监控] 状态检查异常: {e}")
                time.sleep(_status_check_interval)
    
    _status_check_thread = threading.Thread(target=status_monitor, daemon=True)
    _status_check_thread.start()
    logger.info("[微信监控] 状态监控已启动")

def get_wechat_user_info():
    """
    获取微信登录用户信息
    
    Returns:
        dict: 用户信息字典，包含id和area字段
    """
    global _wx_instance
    try:
        if _wx_instance is None:
            init_wechat()
        if _wx_instance and is_wechat_online():
            return _wx_instance.nickname
        else:
            return None
    except Exception as e:
        logger.error(f"获取微信用户信息失败: {e}")
        return None


def get_status_info():
    """
    获取微信状态信息（带缓存版本）
    """
    global _cached_status_info, _last_status_update
    
    # 检查缓存是否有效
    current_time = datetime.now()
    if (_cached_status_info is not None and 
        (current_time - _last_status_update).total_seconds() < _status_cache_timeout):
        return _cached_status_info
    
    # 更新缓存
    _cached_status_info = {
        'online': is_wechat_online(),
        'instance_exists': _wx_instance is not None,
        'last_check': _last_status_check.isoformat() if _last_status_check else None,
        'check_interval': _status_check_interval,
        'user_info': get_wechat_user_info()
    }
    _last_status_update = current_time
    
    return _cached_status_info