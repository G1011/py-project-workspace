"""
插件基类
定义所有插件必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger


class BasePlugin(ABC):
    """插件基类"""
    
    def __init__(self, config_manager):
        """初始化插件"""
        self.config = config_manager
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = "插件描述"
        self.is_running = False
        self.is_enabled = True
    
    @abstractmethod
    def start(self) -> None:
        """启动插件"""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """停止插件"""
        pass
    
    def execute_command(self, command: str, **kwargs) -> Any:
        """执行插件命令"""
        raise NotImplementedError(f"插件 {self.name} 不支持命令执行")
    
    def get_help(self) -> str:
        """获取插件帮助信息"""
        return f"插件 {self.name} 的帮助信息"
    
    def get_status(self) -> Dict[str, Any]:
        """获取插件状态"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "is_running": self.is_running,
            "is_enabled": self.is_enabled
        }
    
    def enable(self) -> None:
        """启用插件"""
        self.is_enabled = True
        logger.info(f"插件 {self.name} 已启用")
    
    def disable(self) -> None:
        """禁用插件"""
        self.is_enabled = False
        if self.is_running:
            self.stop()
        logger.info(f"插件 {self.name} 已禁用")
    
    def reload(self) -> None:
        """重新加载插件"""
        if self.is_running:
            self.stop()
        self.start()
        logger.info(f"插件 {self.name} 重新加载完成")
    
    def validate_config(self) -> bool:
        """验证插件配置"""
        return True
    
    def get_config_schema(self) -> Dict[str, Any]:
        """获取插件配置模式"""
        return {} 