"""
核心模块
包含机器人的核心功能组件
"""

from .bot import WeChatBot
from .base_plugin import BasePlugin
from .config_manager import ConfigManager
from .message_handler import MessageHandler
from .plugin_manager import PluginManager

__all__ = [
    'WeChatBot',
    'BasePlugin', 
    'ConfigManager',
    'MessageHandler',
    'PluginManager'
] 