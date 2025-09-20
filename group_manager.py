"""
群聊管家模块
处理群聊管理、消息收集、舆情监控等功能
"""

import os
import re
import json
import datetime
import pandas as pd
from flask import jsonify, request, send_file, current_app
from werkzeug.utils import secure_filename
import logging
from functools import wraps

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
GROUP_DATA_DIR = os.path.join(DATA_DIR, 'group_data')
MONITORING_DIR = os.path.join(DATA_DIR, 'monitoring')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(GROUP_DATA_DIR, exist_ok=True)
os.makedirs(MONITORING_DIR, exist_ok=True)

# 群聊数据存储
group_data = {}
# 群聊消息记录状态
message_recording_status = {}
# 收集模板
collection_templates = {}
# 自动学习模式
auto_learning_patterns = {}
# 舆情监控状态
sentiment_monitoring_status = {}
# 敏感词列表
sensitive_words_list = {}


def handle_errors(f):
    """错误处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    return decorated_function


def get_group_data_path(group_name):
    """获取群聊数据存储路径"""
    return os.path.join(GROUP_DATA_DIR, secure_filename(group_name))


def get_monitoring_data_path(group_name):
    """获取监控数据存储路径"""
    return os.path.join(MONITORING_DIR, secure_filename(group_name))


def save_group_data(group_name, data):
    """保存群聊数据"""
    group_path = get_group_data_path(group_name)
    os.makedirs(group_path, exist_ok=True)
    
    data_file = os.path.join(group_path, 'data.json')
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved data for group: {group_name}")


def load_group_data(group_name):
    """加载群聊数据"""
    group_path = get_group_data_path(group_name)
    data_file = os.path.join(group_path, 'data.json')
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {}


def save_monitoring_data(group_name, data):
    """保存监控数据"""
    monitoring_path = get_monitoring_data_path(group_name)
    os.makedirs(monitoring_path, exist_ok=True)
    
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    data_file = os.path.join(monitoring_path, f"{today}.json")
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved monitoring data for group: {group_name}, date: {today}")


def load_monitoring_data(group_name, date=None):
    """加载监控数据"""
    monitoring_path = get_monitoring_data_path(group_name)
    
    if date:
        data_file = os.path.join(monitoring_path, f"{date}.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    else:
        # 获取最新的监控数据
        if os.path.exists(monitoring_path):
            files = [f for f in os.listdir(monitoring_path) if f.endswith('.json')]
            if files:
                latest_file = sorted(files)[-1]
                with open(os.path.join(monitoring_path, latest_file), 'r', encoding='utf-8') as f:
                    return json.load(f)
    
    return {}


# ===== 群聊管理功能 =====
def select_group(group_name):
    """选择要管理的群聊"""
    if not group_name:
        return False, "群聊名称不能为空"
    
    # 初始化群聊数据
    if group_name not in group_data:
        group_data[group_name] = {
            "name": group_name,
            "created_at": datetime.datetime.now().isoformat(),
            "message_recording": False,
            "collection_template": "",
            "auto_learning": False,
            "monitoring": False,
            "sensitive_words": []
        }
        save_group_data(group_name, group_data[group_name])
    
    logger.info(f"Selected group: {group_name}")
    return True, f"已选择群聊: {group_name}"


def toggle_message_recording(group_name, enabled):
    """开启/关闭群消息记录"""
    if not group_name:
        return False, "请先选择群聊"
    
    if group_name not in group_data:
        group_data[group_name] = load_group_data(group_name)
    
    group_data[group_name]["message_recording"] = enabled
    message_recording_status[group_name] = enabled
    save_group_data(group_name, group_data[group_name])
    
    status = "开启" if enabled else "关闭"
    logger.info(f"Message recording {status} for group: {group_name}")
    return True, f"消息记录已{status}"


# ===== 群消息数据收集功能 =====
def set_collection_date(group_name, date):
    """设置收集日期"""
    if not group_name:
        return False, "请先选择群聊"
    
    if not date:
        return False, "请选择日期"
    
    if group_name not in group_data:
        group_data[group_name] = load_group_data(group_name)
    
    # 检查是否有收集的数据
    has_data = check_collected_data(group_name, date)
    
    logger.info(f"Set collection date for group {group_name}: {date}, has data: {has_data}")
    return True, {"has_data": has_data}


def check_collected_data(group_name, date):
    """检查是否有收集的数据"""
    group_path = get_group_data_path(group_name)
    data_file = os.path.join(group_path, f"collected_data_{date}.json")
    
    return os.path.exists(data_file)


def save_collection_template(group_name, template):
    """保存收集模板"""
    if not group_name:
        return False, "请先选择群聊"
    
    if not template.strip():
        return False, "模板内容不能为空"
    
    if group_name not in group_data:
        group_data[group_name] = load_group_data(group_name)
    
    group_data[group_name]["collection_template"] = template
    collection_templates[group_name] = template
    save_group_data(group_name, group_data[group_name])
    
    logger.info(f"Saved collection template for group {group_name}")
    return True, "模板保存成功"


def auto_learn_pattern(group_name):
    """自动学习模式，建立正则表达式"""
    if not group_name:
        return False, "请先选择群聊"
    
    if group_name not in group_data:
        group_data[group_name] = load_group_data(group_name)
    
    template = group_data[group_name].get("collection_template", "")
    if not template:
        return False, "请先设置收集模板"
    
    # 根据模板生成正则表达式
    # 这里简化处理，实际应用中可能需要更复杂的逻辑
    fields = [field.strip() for field in template.split(',')]
    pattern_parts = []
    
    for field in fields:
        # 为每个字段生成匹配模式
        if "姓名" in field or "名字" in field:
            pattern_parts.append(r"([\u4e00-\u9fa5]{2,4})")  # 匹配中文名字
        elif "电话" in field or "手机" in field:
            pattern_parts.append(r"(1[3-9]\d{9})")  # 匹配手机号
        elif "邮箱" in field:
            pattern_parts.append(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})")  # 匹配邮箱
        elif "地址" in field:
            pattern_parts.append(r"([\u4e00-\u9fa5]{2,10}[市省区][\u4e00-\u9fa5]{2,10}[区县][\u4e00-\u9fa5]{2,20})")  # 匹配地址
        else:
            pattern_parts.append(r"([^\s,]+)")  # 通用匹配
    
    pattern = r"\s*".join(pattern_parts)
    
    # 保存生成的正则表达式
    auto_learning_patterns[group_name] = {
        "template": template,
        "pattern": pattern,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    group_data[group_name]["auto_learning"] = True
    save_group_data(group_name, group_data[group_name])
    
    logger.info(f"Auto-learned pattern for group {group_name}: {pattern}")
    return True, f"自动学习已启动，正则表达式: {pattern}"


def export_collected_data(group_name, date):
    """导出收集的数据"""
    if not group_name:
        return False, "请先选择群聊"
    
    if not date:
        return False, "请选择日期"
    
    group_path = get_group_data_path(group_name)
    data_file = os.path.join(group_path, f"collected_data_{date}.json")
    
    if not os.path.exists(data_file):
        return False, f"未找到 {date} 的收集数据"
    
    # 读取收集的数据
    with open(data_file, 'r', encoding='utf-8') as f:
        collected_data = json.load(f)
    
    # 转换为DataFrame
    df = pd.DataFrame(collected_data)
    
    # 生成Excel文件
    output_file = os.path.join(group_path, f"collected_data_{date}.xlsx")
    df.to_excel(output_file, index=False)
    
    logger.info(f"Exported collected data for group {group_name}, date: {date}")
    return True, output_file


# ===== 舆情监控功能 =====
def start_sentiment_monitoring(group_name, sensitive_words):
    """开始舆情监控"""
    if not group_name:
        return False, "请先选择群聊"
    
    if not sensitive_words.strip():
        return False, "请输入敏感词"
    
    if group_name not in group_data:
        group_data[group_name] = load_group_data(group_name)
    
    # 处理敏感词
    words = [word.strip() for word in sensitive_words.split(',') if word.strip()]
    
    # 保存敏感词列表
    group_data[group_name]["sensitive_words"] = words
    group_data[group_name]["monitoring"] = True
    sensitive_words_list[group_name] = words
    sentiment_monitoring_status[group_name] = "运行中"
    
    save_group_data(group_name, group_data[group_name])
    
    logger.info(f"Started sentiment monitoring for group {group_name} with words: {words}")
    return True, "舆情监控已启动"


def stop_sentiment_monitoring(group_name):
    """停止舆情监控"""
    if not group_name:
        return False, "请先选择群聊"
    
    if group_name not in group_data:
        group_data[group_name] = load_group_data(group_name)
    
    group_data[group_name]["monitoring"] = False
    sentiment_monitoring_status[group_name] = "已停止"
    
    save_group_data(group_name, group_data[group_name])
    
    logger.info(f"Stopped sentiment monitoring for group {group_name}")
    return True, "舆情监控已停止"


def check_sentiment_monitoring_status(group_name):
    """检查舆情监控状态"""
    if not group_name:
        return False, "请先选择群聊"
    
    status = sentiment_monitoring_status.get(group_name, "未启动")
    return True, status


# ===== 数据导出功能 =====
def export_group_messages(group_name):
    """导出群消息"""
    if not group_name:
        return False, "请先选择群聊"
    
    # 模拟数据导出
    group_path = get_group_data_path(group_name)
    os.makedirs(group_path, exist_ok=True)
    
    # 创建示例数据
    messages = [
        {"sender": "张三", "content": "大家好，今天天气不错", "time": "2023-06-01 10:30:00"},
        {"sender": "李四", "content": "是啊，适合出去走走", "time": "2023-06-01 10:32:15"},
        {"sender": "王五", "content": "有人一起去公园吗？", "time": "2023-06-01 10:35:22"}
    ]
    
    # 转换为DataFrame
    df = pd.DataFrame(messages)
    
    # 生成Excel文件
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(group_path, f"group_messages_{today}.xlsx")
    df.to_excel(output_file, index=False)
    
    logger.info(f"Exported messages for group {group_name}")
    return True, output_file


def export_group_files(group_name):
    """导出群文件"""
    if not group_name:
        return False, "请先选择群聊"
    
    # 模拟数据导出
    group_path = get_group_data_path(group_name)
    os.makedirs(group_path, exist_ok=True)
    
    # 创建示例数据
    files = [
        {"name": "项目计划.docx", "size": "2.5MB", "uploader": "张三", "upload_time": "2023-06-01 09:15:00"},
        {"name": "会议记录.pdf", "size": "1.8MB", "uploader": "李四", "upload_time": "2023-06-01 14:20:00"},
        {"name": "财务报表.xlsx", "size": "3.2MB", "uploader": "王五", "upload_time": "2023-06-02 11:05:00"}
    ]
    
    # 转换为DataFrame
    df = pd.DataFrame(files)
    
    # 生成Excel文件
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(group_path, f"group_files_{today}.xlsx")
    df.to_excel(output_file, index=False)
    
    logger.info(f"Exported files for group {group_name}")
    return True, output_file


def export_group_images(group_name):
    """导出群图片"""
    if not group_name:
        return False, "请先选择群聊"
    
    # 模拟数据导出
    group_path = get_group_data_path(group_name)
    os.makedirs(group_path, exist_ok=True)
    
    # 创建示例数据
    images = [
        {"name": "风景照.jpg", "size": "3.5MB", "uploader": "张三", "upload_time": "2023-06-01 09:15:00"},
        {"name": "会议照片.png", "size": "2.8MB", "uploader": "李四", "upload_time": "2023-06-01 14:20:00"},
        {"name": "产品截图.jpeg", "size": "1.2MB", "uploader": "王五", "upload_time": "2023-06-02 11:05:00"}
    ]
    
    # 转换为DataFrame
    df = pd.DataFrame(images)
    
    # 生成Excel文件
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(group_path, f"group_images_{today}.xlsx")
    df.to_excel(output_file, index=False)
    
    logger.info(f"Exported images for group {group_name}")
    return True, output_file


def export_group_voices(group_name):
    """导出群语音"""
    if not group_name:
        return False, "请先选择群聊"
    
    # 模拟数据导出
    group_path = get_group_data_path(group_name)
    os.makedirs(group_path, exist_ok=True)
    
    # 创建示例数据
    voices = [
        {"name": "会议录音.mp3", "duration": "15:30", "uploader": "张三", "upload_time": "2023-06-01 09:15:00"},
        {"name": "语音留言.wav", "duration": "02:45", "uploader": "李四", "upload_time": "2023-06-01 14:20:00"},
        {"name": "产品介绍.m4a", "duration": "08:12", "uploader": "王五", "upload_time": "2023-06-02 11:05:00"}
    ]
    
    # 转换为DataFrame
    df = pd.DataFrame(voices)
    
    # 生成Excel文件
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(group_path, f"group_voices_{today}.xlsx")
    df.to_excel(output_file, index=False)
    
    logger.info(f"Exported voices for group {group_name}")
    return True, output_file


def export_group_videos(group_name):
    """导出群视频"""
    if not group_name:
        return False, "请先选择群聊"
    
    # 模拟数据导出
    group_path = get_group_data_path(group_name)
    os.makedirs(group_path, exist_ok=True)
    
    # 创建示例数据
    videos = [
        {"name": "产品演示.mp4", "duration": "15:30", "size": "125MB", "uploader": "张三", "upload_time": "2023-06-01 09:15:00"},
        {"name": "会议录像.avi", "duration": "45:20", "size": "380MB", "uploader": "李四", "upload_time": "2023-06-01 14:20:00"},
        {"name": "培训视频.mkv", "duration": "32:15", "size": "210MB", "uploader": "王五", "upload_time": "2023-06-02 11:05:00"}
    ]
    
    # 转换为DataFrame
    df = pd.DataFrame(videos)
    
    # 生成Excel文件
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(group_path, f"group_videos_{today}.xlsx")
    df.to_excel(output_file, index=False)
    
    logger.info(f"Exported videos for group {group_name}")
    return True, output_file


def export_group_links(group_name):
    """导出群链接"""
    if not group_name:
        return False, "请先选择群聊"
    
    # 模拟数据导出
    group_path = get_group_data_path(group_name)
    os.makedirs(group_path, exist_ok=True)
    
    # 创建示例数据
    links = [
        {"title": "公司官网", "url": "https://example.com", "sender": "张三", "time": "2023-06-01 10:30:00"},
        {"title": "产品文档", "url": "https://docs.example.com", "sender": "李四", "time": "2023-06-01 14:20:00"},
        {"title": "项目代码", "url": "https://github.com/example/project", "sender": "王五", "time": "2023-06-02 11:05:00"}
    ]
    
    # 转换为DataFrame
    df = pd.DataFrame(links)
    
    # 生成Excel文件
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(group_path, f"group_links_{today}.xlsx")
    df.to_excel(output_file, index=False)
    
    logger.info(f"Exported links for group {group_name}")
    return True, output_file


# ===== 模拟消息处理 =====
def process_message(group_name, message):
    """处理群消息，用于模拟数据收集和舆情监控"""
    if not group_name or group_name not in group_data:
        return
    
    # 如果开启了消息记录，保存消息
    if group_data[group_name].get("message_recording", False):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        group_path = get_group_data_path(group_name)
        os.makedirs(group_path, exist_ok=True)
        
        messages_file = os.path.join(group_path, f"messages_{today}.json")
        
        # 读取现有消息
        messages = []
        if os.path.exists(messages_file):
            with open(messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        
        # 添加新消息
        messages.append({
            "content": message,
            "time": datetime.datetime.now().isoformat()
        })
        
        # 保存消息
        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    
    # 如果开启了自动学习，尝试从消息中提取数据
    if group_data[group_name].get("auto_learning", False) and group_name in auto_learning_patterns:
        pattern = auto_learning_patterns[group_name]["pattern"]
        match = re.search(pattern, message)
        
        if match:
            # 提取数据
            extracted_data = match.groups()
            
            # 保存提取的数据
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            group_path = get_group_data_path(group_name)
            os.makedirs(group_path, exist_ok=True)
            
            data_file = os.path.join(group_path, f"collected_data_{today}.json")
            
            # 读取现有数据
            collected_data = []
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    collected_data = json.load(f)
            
            # 添加新数据
            template = auto_learning_patterns[group_name]["template"]
            fields = [field.strip() for field in template.split(',')]
            
            if len(fields) == len(extracted_data):
                data_entry = {}
                for i, field in enumerate(fields):
                    data_entry[field] = extracted_data[i]
                
                data_entry["source_message"] = message
                data_entry["extracted_time"] = datetime.datetime.now().isoformat()
                
                collected_data.append(data_entry)
                
                # 保存数据
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(collected_data, f, ensure_ascii=False, indent=2)
    
    # 如果开启了舆情监控，检查敏感词
    if group_data[group_name].get("monitoring", False) and group_name in sensitive_words_list:
        for word in sensitive_words_list[group_name]:
            if word in message:
                # 发现敏感词，记录到监控数据
                today = datetime.datetime.now().strftime('%Y-%m-%d')
                
                monitoring_data = load_monitoring_data(group_name, today)
                
                if "sensitive_words_detected" not in monitoring_data:
                    monitoring_data["sensitive_words_detected"] = []
                
                monitoring_data["sensitive_words_detected"].append({
                    "word": word,
                    "message": message,
                    "time": datetime.datetime.now().isoformat()
                })
                
                save_monitoring_data(group_name, monitoring_data)
                
                # 这里可以添加触发后续操作的逻辑
                logger.warning(f"Detected sensitive word '{word}' in group {group_name}: {message}")
                break