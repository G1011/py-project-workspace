"""
配置管理器
负责读取和管理配置文件
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from loguru import logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str):
        """初始化配置管理器"""
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"配置文件 {self.config_path} 不存在，使用默认配置")
                return self._get_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"配置文件加载成功: {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "wechat": {
                "login_timeout": 300,
                "enable_cmd_qr": True,
                "hot_reload": True
            },
            "file_processing": {
                "upload_dir": "uploads",
                "output_dir": "outputs",
                "max_file_size": 50,
                "supported_formats": {
                    "word": [".doc", ".docx"],
                    "pdf": [".pdf"],
                    "image": [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
                }
            },
            "scheduler": {
                "timezone": "Asia/Shanghai",
                "max_jobs": 100
            },
            "news": {
                "sources": [
                    "https://www.jrj.com.cn/",
                    "https://finance.sina.com.cn/",
                    "https://www.10jqka.com.cn/"
                ],
                "keywords": ["金融", "股市", "基金", "理财", "投资"],
                "max_news_count": 5
            },
            "logging": {
                "level": "INFO",
                "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
                "file": "logs/wechat_bot.log"
            },
            "database": {
                "path": "data/wechat_bot.db"
            },
            "plugins": {
                "enabled": ["file_converter", "scheduler", "news_pusher", "help"],
                "auto_reload": True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的键路径"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 遍历到最后一个键的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置最后一个键的值
        config[keys[-1]] = value
    
    def save(self) -> None:
        """保存配置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"配置已保存到: {self.config_path}")
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def reload(self) -> None:
        """重新加载配置"""
        self.config = self._load_config()
        logger.info("配置重新加载完成")
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()
    
    def validate(self) -> bool:
        """验证配置的有效性"""
        required_keys = [
            "wechat.login_timeout",
            "file_processing.upload_dir",
            "file_processing.output_dir",
            "logging.level",
            "database.path"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                logger.error(f"缺少必需的配置项: {key}")
                return False
        
        return True 