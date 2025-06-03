"""
日志管理工具
"""
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from enum import Enum


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class CustomLogger:
    """自定义日志管理器"""
    
    def __init__(self, name="ai_tools_manager"):
        self.name = name
        self.log_dir = "logs"
        self.log_file = os.path.join(self.log_dir, f"{name}.log")
        self.json_log_file = os.path.join(self.log_dir, f"{name}_structured.json")
        
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 设置Python标准日志
        self.setup_standard_logger()
        
        # 内存中的日志缓存
        self.log_cache = []
        self.max_cache_size = 1000
    
    def setup_standard_logger(self):
        """设置标准日志记录器"""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # 清除现有处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _log_to_cache(self, level: str, message: str, **kwargs):
        """添加日志到缓存"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'logger': self.name,
            **kwargs
        }
        
        self.log_cache.append(log_entry)
        
        # 限制缓存大小
        if len(self.log_cache) > self.max_cache_size:
            self.log_cache = self.log_cache[-self.max_cache_size:]
        
        # 保存到JSON文件
        self._save_to_json_file(log_entry)
    
    def _save_to_json_file(self, log_entry: Dict[str, Any]):
        """保存日志条目到JSON文件"""
        try:
            # 读取现有日志
            logs = []
            if os.path.exists(self.json_log_file):
                try:
                    with open(self.json_log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    logs = []
            
            # 添加新日志
            logs.append(log_entry)
            
            # 限制文件大小（保留最近1000条）
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            # 保存到文件
            with open(self.json_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            # 如果JSON保存失败，至少记录到标准日志
            self.logger.error(f"保存结构化日志失败: {e}")
    
    def debug(self, message: str, **kwargs):
        """调试日志"""
        self.logger.debug(message)
        self._log_to_cache(LogLevel.DEBUG.value, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """信息日志"""
        self.logger.info(message)
        self._log_to_cache(LogLevel.INFO.value, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告日志"""
        self.logger.warning(message)
        self._log_to_cache(LogLevel.WARNING.value, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """错误日志"""
        self.logger.error(message)
        self._log_to_cache(LogLevel.ERROR.value, message, **kwargs)
    
    def log_operation(self, operation: str, details: Dict[str, Any] = None, success: bool = True):
        """记录操作日志"""
        status = "成功" if success else "失败"
        message = f"操作{status}: {operation}"

        log_data = {
            'operation': operation,
            'success': success,
            'details': details or {}
        }

        if success:
            self.info(message, **log_data)
        else:
            self.error(message, **log_data)
    
    def log_automation(self, tool: str, action: str, result: str, details: Dict[str, Any] = None):
        """记录自动化操作日志"""
        message = f"自动化操作 - {tool}: {action} - {result}"
        
        log_data = {
            'category': 'automation',
            'tool': tool,
            'action': action,
            'result': result,
            'details': details or {}
        }
        
        if "成功" in result or "success" in result.lower():
            self.info(message, **log_data)
        else:
            self.error(message, **log_data)
    
    def log_account_operation(self, operation: str, account_name: str, account_type: str, success: bool = True):
        """记录账号操作日志"""
        status = "成功" if success else "失败"
        message = f"账号操作{status}: {operation} - {account_name} ({account_type})"
        
        log_data = {
            'category': 'account',
            'operation': operation,
            'account_name': account_name,
            'account_type': account_type,
            'success': success
        }
        
        if success:
            self.info(message, **log_data)
        else:
            self.error(message, **log_data)
    
    def get_recent_logs(self, limit: int = 100, level: str = None) -> List[Dict[str, Any]]:
        """获取最近的日志"""
        logs = self.log_cache.copy()
        
        # 按级别筛选
        if level and level != "ALL":
            logs = [log for log in logs if log.get('level') == level]
        
        # 按时间排序（最新的在前）
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return logs[:limit]
    
    def get_logs_from_file(self, limit: int = 100) -> List[Dict[str, Any]]:
        """从文件获取日志"""
        try:
            if os.path.exists(self.json_log_file):
                with open(self.json_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    # 返回最近的日志
                    return logs[-limit:] if len(logs) > limit else logs
        except Exception as e:
            self.error(f"读取日志文件失败: {e}")
        
        return []
    
    def clear_logs(self):
        """清空日志"""
        try:
            # 清空缓存
            self.log_cache.clear()
            
            # 清空文件
            if os.path.exists(self.log_file):
                open(self.log_file, 'w').close()
            
            if os.path.exists(self.json_log_file):
                with open(self.json_log_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            
            self.info("日志已清空")
            
        except Exception as e:
            self.error(f"清空日志失败: {e}")
    
    def get_log_stats(self) -> Dict[str, int]:
        """获取日志统计"""
        stats = {
            'total': len(self.log_cache),
            'debug': 0,
            'info': 0,
            'warning': 0,
            'error': 0
        }
        
        for log in self.log_cache:
            level = log.get('level', '').lower()
            if level in stats:
                stats[level] += 1
        
        return stats
    
    def export_logs(self, filename: str, format: str = 'json'):
        """导出日志"""
        try:
            if format.lower() == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.log_cache, f, ensure_ascii=False, indent=2)
            else:
                # 文本格式
                with open(filename, 'w', encoding='utf-8') as f:
                    for log in self.log_cache:
                        timestamp = log.get('timestamp', '')
                        level = log.get('level', '')
                        message = log.get('message', '')
                        f.write(f"[{timestamp}] {level}: {message}\n")
            
            self.info(f"日志已导出到: {filename}")
            return True
            
        except Exception as e:
            self.error(f"导出日志失败: {e}")
            return False


# 全局日志实例
_logger_instance = None


def get_logger(name: str = "ai_tools_manager") -> CustomLogger:
    """获取日志实例"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = CustomLogger(name)
    return _logger_instance


def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """设置日志系统"""
    global _logger_instance
    _logger_instance = CustomLogger("ai_tools_manager")
    _logger_instance.log_dir = log_dir
    
    # 设置日志级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    
    if log_level.upper() in level_map:
        _logger_instance.logger.setLevel(level_map[log_level.upper()])
    
    return _logger_instance


# 便捷函数
def log_info(message: str, **kwargs):
    """记录信息日志"""
    logger = get_logger()
    logger.info(message, **kwargs)


def log_error(message: str, **kwargs):
    """记录错误日志"""
    logger = get_logger()
    logger.error(message, **kwargs)


def log_warning(message: str, **kwargs):
    """记录警告日志"""
    logger = get_logger()
    logger.warning(message, **kwargs)


def log_debug(message: str, **kwargs):
    """记录调试日志"""
    logger = get_logger()
    logger.debug(message, **kwargs)


def log_operation(operation: str, success: bool = True, details: Dict[str, Any] = None):
    """记录操作日志"""
    logger = get_logger()
    logger.log_operation(operation, details, success)


def log_automation(tool: str, action: str, result: str, details: Dict[str, Any] = None):
    """记录自动化日志"""
    logger = get_logger()
    logger.log_automation(tool, action, result, details)


def log_account_operation(operation: str, account_name: str, account_type: str, success: bool = True):
    """记录账号操作日志"""
    logger = get_logger()
    logger.log_account_operation(operation, account_name, account_type, success)
