"""
配置管理模块
"""
import json
import os
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "window": {
                "width": 1200,
                "height": 800,
                "x": 100,
                "y": 100
            },
            "database": {
                "path": "accounts.db"
            },
            "security": {
                "auto_lock_minutes": 30,
                "require_password": False
            },
            "ui": {
                "theme": "light",
                "language": "zh_CN",
                "show_sensitive_data": False
            },
            "backup": {
                "auto_backup": True,
                "backup_interval_days": 7,
                "backup_path": "backups"
            }
        }
    
    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_window_geometry(self) -> tuple:
        """获取窗口几何信息"""
        return (
            self.get('window.x', 100),
            self.get('window.y', 100),
            self.get('window.width', 1200),
            self.get('window.height', 800)
        )
    
    def set_window_geometry(self, x: int, y: int, width: int, height: int):
        """设置窗口几何信息"""
        self.set('window.x', x)
        self.set('window.y', y)
        self.set('window.width', width)
        self.set('window.height', height)


# 全局配置管理器实例
_config_manager = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
