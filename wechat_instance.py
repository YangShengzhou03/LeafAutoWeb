"""
微信实例共享模块
提供全局的WeChat实例，避免重复创建
支持定期状态检查和自动重连
"""

import subprocess
import sys
import threading
import time
from datetime import datetime

from wxautox import WeChat

from logging_config import get_logger

# 初始化日志器
logger = get_logger(__name__)

# 全局微信实例
try:
    _wx_instance = WeChat()
except Exception as e:
    _wx_instance = None
# 状态检查线程
_status_check_thread = None
STATUS_CHECK_INTERVAL = 30  # 30秒检查一次
_last_status_check = datetime.now()
# 状态信息缓存
_cached_status_info = None
STATUS_CACHE_TIMEOUT = 10  # 10秒缓存时间
_last_status_update = datetime.now()
# 重试机制
_last_init_attempt = None
INIT_RETRY_INTERVAL = 60  # 60秒重试间隔
MAX_INIT_ATTEMPTS = 3  # 最大重试次数
_init_attempt_count = 0
# COM组件错误冷却
_last_com_error_time = None
COM_ERROR_COOLDOWN = 300  # 5分钟冷却时间


def diagnose_com_error():
    """
    诊断COM组件错误并提供解决方案
    """
    solutions = []
    
    # 检查微信是否运行
    try:
        # 在Windows上检查微信进程
        if sys.platform == "win32":
            result = subprocess.run(['tasklist', '/fi', 'imagename eq WeChat.exe'], 
                                 capture_output=True, text=True, check=False)
            if "WeChat.exe" in result.stdout:
                solutions.append("✓ 微信进程正在运行")
            else:
                solutions.append("✗ 微信进程未运行，请启动微信并登录")
        else:
            solutions.append("⚠ 非Windows系统，COM组件仅支持Windows")
    except (subprocess.SubprocessError, OSError, FileNotFoundError, PermissionError):
        solutions.append("⚠ 无法检查微信进程状态")
    
    # 检查常见问题
    solutions.append("💡 常见解决方案:")
    solutions.append("1. 确保微信已正确安装并登录")
    solutions.append("2. 重启微信客户端（完全退出后重新启动）")
    solutions.append("3. 检查微信版本是否与wxautox兼容")
    solutions.append("4. 如果是打包环境，请确保微信安装在默认路径")
    solutions.append("5. 尝试以管理员权限运行程序")
    
    return solutions


def get_wechat_instance():
    """
    获取全局WeChat实例
    如果实例不存在则创建，存在则直接返回
    """
    global _wx_instance
    if _wx_instance is None:
        try:
            _wx_instance = WeChat()
        except (AttributeError, RuntimeError, TypeError) as e:
            logger.error("微信实例创建失败: %s", e)
            # 特别处理COM组件错误
            if hasattr(e, 'args') and len(e.args) > 0:
                if isinstance(e.args[0], int) and e.args[0] == -2147467259:
                    logger.warning("检测到COM组件初始化错误，详细诊断信息:")
                    solutions = diagnose_com_error()
                    for solution in solutions:
                        logger.warning(solution)
            _wx_instance = None
    return _wx_instance


def init_wechat():
    """
    初始化微信对象，如果微信未登录则返回False
    """
    global _wx_instance, _last_com_error_time
    
    # 检查COM组件错误冷却时间
    current_time = datetime.now()
    
    try:
        # 先释放现有实例（如果存在）
        if _wx_instance is not None:
            try:
                del _wx_instance
            except (AttributeError, RuntimeError, TypeError):
                pass
            _wx_instance = None
        
        # 创建新的微信实例
        _wx_instance = WeChat()
        
        # 检查微信是否在线
        if _wx_instance.IsOnline():
            return True
        
        _wx_instance = None
        return False
    except (AttributeError, RuntimeError, TypeError) as e:
        logger.error("微信初始化失败: %s", e)
        # 特别处理COM组件错误
        if hasattr(e, 'args') and len(e.args) > 0:
            if isinstance(e.args[0], int) and e.args[0] == -2147467259:
                logger.warning("检测到COM组件初始化错误，详细诊断信息:")
                solutions = diagnose_com_error()
                for solution in solutions:
                    logger.warning(solution)
                # 记录COM组件错误时间
                _last_com_error_time = current_time
        _wx_instance = None
        return False


def is_wechat_online():
    """
    检查微信是否在线
    """
    try:
        if _wx_instance is None:
            return False
        return _wx_instance.IsOnline()
    except (AttributeError, RuntimeError, TypeError):
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
                _update_status_monitor()
                time.sleep(STATUS_CHECK_INTERVAL)
            except (AttributeError, RuntimeError, TypeError) as e:
                _handle_monitor_exception(e)
                time.sleep(STATUS_CHECK_INTERVAL)

    _status_check_thread = threading.Thread(target=status_monitor, daemon=True)
    _status_check_thread.start()
    logger.info("[微信监控] 状态监控已启动")


def _update_status_monitor():
    """更新状态监控"""
    global _last_status_check
    _last_status_check = datetime.now()

    # 检查微信状态（带重试机制）
    current_time = datetime.now()
    
    # 检查COM组件错误冷却时间
    com_error_cooldown_active = _check_com_error_cooldown(current_time)
    
    # 只有在非冷却时间才进行状态检查和重试
    if not com_error_cooldown_active:
        should_retry = _check_retry_condition(current_time)
        _handle_wechat_instance(current_time, should_retry)

    # 强制更新状态信息缓存
    _update_status_cache(current_time, com_error_cooldown_active)


def _check_com_error_cooldown(current_time):
    """检查COM组件错误冷却时间"""
    if _last_com_error_time is None:
        return False
        
    time_since_last_error = (current_time - _last_com_error_time).total_seconds()
    if time_since_last_error < COM_ERROR_COOLDOWN:
        logger.info("[微信监控] COM组件错误冷却中，跳过状态检查")
        return True
    return False


def _check_retry_condition(current_time):
    """检查是否需要重试"""
    global _init_attempt_count
    
    if _last_init_attempt is None:
        return True
        
    time_since_last_attempt = (current_time - _last_init_attempt).total_seconds()
    if time_since_last_attempt >= INIT_RETRY_INTERVAL:
        _init_attempt_count = 0  # 重置重试计数
        return True
    return False


def _handle_wechat_instance(current_time, should_retry):
    """处理微信实例状态"""
    global _init_attempt_count, _last_init_attempt
    
    if _wx_instance is None:
        if should_retry and _init_attempt_count < MAX_INIT_ATTEMPTS:
            logger.info("[微信监控] 尝试初始化微信实例 (尝试 %d/%d)", 
                       _init_attempt_count + 1, MAX_INIT_ATTEMPTS)
            if init_wechat():
                _init_attempt_count = 0
                _last_init_attempt = None
            else:
                _init_attempt_count += 1
                _last_init_attempt = current_time
    elif not is_wechat_online():
        if should_retry and _init_attempt_count < MAX_INIT_ATTEMPTS:
            logger.warning("[微信监控] 微信连接丢失，尝试重新初始化 (尝试 %d/%d)", 
                          _init_attempt_count + 1, MAX_INIT_ATTEMPTS)
            if init_wechat():
                _init_attempt_count = 0
                _last_init_attempt = None
            else:
                _init_attempt_count += 1
                _last_init_attempt = current_time


def _update_status_cache(current_time, com_error_cooldown_active):
    """更新状态信息缓存"""
    global _cached_status_info, _last_status_update
    
    time_since_last_error = 0
    if com_error_cooldown_active and _last_com_error_time is not None:
        time_since_last_error = (current_time - _last_com_error_time).total_seconds()
        
    _cached_status_info = {
        "online": is_wechat_online(),
        "instance_exists": _wx_instance is not None,
        "last_check": _last_status_check.isoformat() if _last_status_check else None,
        "check_interval": STATUS_CHECK_INTERVAL,
        "user_info": get_wechat_user_info(),
        "com_error_cooldown": com_error_cooldown_active,
        "com_error_cooldown_remaining": int(COM_ERROR_COOLDOWN - time_since_last_error) 
        if com_error_cooldown_active else 0
    }
    _last_status_update = current_time


def _handle_monitor_exception(e):
    """处理监控线程异常"""
    global _last_com_error_time
    
    logger.error("[微信监控] 状态检查异常: %s", e)
    # 特别处理COM组件错误
    if hasattr(e, 'args') and len(e.args) > 0:
        if isinstance(e.args[0], int) and e.args[0] == -2147467259:
            logger.warning("[微信监控] 检测到COM组件初始化错误，详细诊断信息:")
            solutions = diagnose_com_error()
            for solution in solutions:
                logger.warning("[微信监控] %s", solution)
            # 记录COM组件错误时间
            _last_com_error_time = datetime.now()


def get_wechat_user_info():
    """
    获取微信登录用户信息

    Returns:
        dict: 用户信息字典，包含id和area字段
    """
    try:
        # 只有在实例存在且在线时才获取用户信息
        # 避免频繁初始化导致COM组件问题
        if _wx_instance and is_wechat_online():
            return _wx_instance.nickname
        return None
    except (AttributeError, RuntimeError, TypeError) as e:
        logger.error("获取微信用户信息失败: %s", e)
        return None


def get_status_info():
    """
    获取微信状态信息（带缓存版本）
    """
    global _cached_status_info, _last_status_update

    # 检查缓存是否有效
    current_time = datetime.now()
    if (
        _cached_status_info is not None
        and (current_time - _last_status_update).total_seconds() < STATUS_CACHE_TIMEOUT
    ):
        return _cached_status_info

    # 更新缓存
    _cached_status_info = {
        "online": is_wechat_online(),
        "instance_exists": _wx_instance is not None,
        "last_check": _last_status_check.isoformat() if _last_status_check else None,
        "check_interval": STATUS_CHECK_INTERVAL,
        "user_info": get_wechat_user_info(),
    }
    _last_status_update = current_time

    return _cached_status_info
