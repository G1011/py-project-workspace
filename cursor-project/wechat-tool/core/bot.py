"""
微信机器人核心类
实现插件化架构，支持功能扩展
"""

import os
import sys
import asyncio
import importlib
from typing import Dict, List, Any, Optional
from pathlib import Path

import itchat
from itchat.content import *
from loguru import logger
import yaml

from core.plugin_manager import PluginManager
from core.message_handler import MessageHandler
from core.config_manager import ConfigManager


class WeChatBot:
    """微信机器人主类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化机器人"""
        self.config = ConfigManager(config_path)
        self.plugin_manager = PluginManager(self.config)
        self.message_handler = MessageHandler(self.config)
        # 将插件管理器注入到消息处理器中
        self.message_handler.plugin_manager = self.plugin_manager
        self.is_running = False
        
        # 创建必要的目录
        self._create_directories()
        
        # 设置日志
        self._setup_logging()
        
        logger.info("微信机器人初始化完成")
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.config.get("file_processing.upload_dir"),
            self.config.get("file_processing.output_dir"),
            "logs",
            "data",
            "plugins"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """设置日志配置"""
        log_config = self.config.get("logging")
        logger.remove()
        logger.add(
            log_config["file"],
            level=log_config["level"],
            format=log_config["format"],
            rotation="1 day",
            retention="7 days"
        )
        logger.add(sys.stderr, level=log_config["level"])
    
    def start(self):
        """启动机器人"""
        try:
            logger.info("正在启动微信机器人...")
            
            # 注册消息处理器
            self._register_handlers()
            
            # 启动插件
            self.plugin_manager.start_plugins()
            
            # 登录微信
            itchat.auto_login(
                enableCmdQR=self.config.get("wechat.enable_cmd_qr"),
                hotReload=self.config.get("wechat.hot_reload")
            )
            
            self.is_running = True
            logger.info("微信机器人启动成功")
            
            # 运行机器人
            itchat.run()
            
        except Exception as e:
            logger.error(f"启动微信机器人失败: {e}")
            raise
    
    def stop(self):
        """停止机器人"""
        try:
            logger.info("正在停止微信机器人...")
            
            # 停止插件
            self.plugin_manager.stop_plugins()
            
            # 退出微信
            itchat.logout()
            
            self.is_running = False
            logger.info("微信机器人已停止")
            
        except Exception as e:
            logger.error(f"停止微信机器人失败: {e}")
    
    def _register_handlers(self):
        """注册消息处理器"""
        
        @itchat.msg_register([TEXT])
        def handle_text_message(msg):
            """处理文本消息"""
            return self.message_handler.handle_text_message(msg)
        
        @itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
        def handle_file_message(msg):
            """处理文件消息"""
            return self.message_handler.handle_file_message(msg)
        
        @itchat.msg_register(FRIENDS)
        def handle_friend_request(msg):
            """处理好友请求"""
            return self.message_handler.handle_friend_request(msg)
        
        logger.info("消息处理器注册完成")
    
    def reload_plugins(self):
        """重新加载插件"""
        self.plugin_manager.reload_plugins()
        logger.info("插件重新加载完成")
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """获取插件状态"""
        return self.plugin_manager.get_status()
    
    def execute_command(self, command: str, user_id: str) -> str:
        """执行命令"""
        return self.message_handler.execute_command(command, user_id)


if __name__ == "__main__":
    bot = WeChatBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.stop() 