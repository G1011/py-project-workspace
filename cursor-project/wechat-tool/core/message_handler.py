"""
消息处理器
处理用户发送的各种消息并路由到相应的插件
"""

import re
import os
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

import itchat


class MessageHandler:
    """消息处理器"""
    
    def __init__(self, config_manager):
        """初始化消息处理器"""
        self.config = config_manager
        self.command_patterns = {
            r'^帮助$|^help$': self._handle_help,
            r'^状态$|^status$': self._handle_status,
            r'^插件$|^plugins$': self._handle_plugins,
            r'^重载$|^reload$': self._handle_reload,
        }
    
    def handle_text_message(self, msg) -> str:
        """处理文本消息"""
        try:
            user_id = msg['FromUserName']
            content = msg['Text'].strip()
            
            logger.info(f"收到文本消息: {content} (来自: {user_id})")
            
            # 检查是否是命令
            for pattern, handler in self.command_patterns.items():
                if re.match(pattern, content, re.IGNORECASE):
                    return handler(msg)
            
            # 检查是否是插件命令
            plugin_response = self._handle_plugin_command(content, user_id)
            if plugin_response:
                return plugin_response
            
            # 默认回复
            return self._get_default_response()
            
        except Exception as e:
            logger.error(f"处理文本消息失败: {e}")
            return "抱歉，处理消息时出现错误。"
    
    def handle_file_message(self, msg) -> str:
        """处理文件消息"""
        try:
            user_id = msg['FromUserName']
            file_name = msg['FileName']
            file_path = msg['Text']
            
            logger.info(f"收到文件: {file_name} (来自: {user_id})")
            
            # 获取文件转换插件
            file_converter = self._get_plugin('file_converter')
            if file_converter:
                return file_converter.handle_file_upload(file_path, file_name, user_id)
            else:
                return "文件转换功能暂不可用。"
                
        except Exception as e:
            logger.error(f"处理文件消息失败: {e}")
            return "抱歉，处理文件时出现错误。"
    
    def handle_friend_request(self, msg) -> str:
        """处理好友请求"""
        try:
            user_id = msg['RecommendInfo']['UserName']
            user_name = msg['RecommendInfo']['NickName']
            
            logger.info(f"收到好友请求: {user_name} ({user_id})")
            
            # 自动接受好友请求
            itchat.add_friend(**msg['Text'])
            itchat.send_msg("你好！我是微信工具机器人，很高兴认识你！", user_id)
            
            return "好友请求已处理"
            
        except Exception as e:
            logger.error(f"处理好友请求失败: {e}")
            return "处理好友请求时出现错误"
    
    def execute_command(self, command: str, user_id: str) -> str:
        """执行命令"""
        try:
            # 检查是否是系统命令
            for pattern, handler in self.command_patterns.items():
                if re.match(pattern, command, re.IGNORECASE):
                    # 创建模拟消息对象
                    mock_msg = {'FromUserName': user_id, 'Text': command}
                    return handler(mock_msg)
            
            # 检查是否是插件命令
            plugin_response = self._handle_plugin_command(command, user_id)
            if plugin_response:
                return plugin_response
            
            return "未知命令，输入 '帮助' 查看可用命令。"
            
        except Exception as e:
            logger.error(f"执行命令失败: {e}")
            return "执行命令时出现错误。"
    
    def _handle_help(self, msg) -> str:
        """处理帮助命令"""
        help_text = """
🤖 微信工具机器人帮助

📋 可用命令：
• 帮助/help - 显示此帮助信息
• 状态/status - 查看机器人状态
• 插件/plugins - 查看已安装插件
• 重载/reload - 重新加载插件

📁 文件处理：
• 发送Word文档 → 自动转换为PDF
• 发送图片文件 → 自动转换为PDF
• 发送PDF文件 → 自动转换为Word

⏰ 定时功能：
• 设置定时提醒
• 定时发送消息

📰 新闻推送：
• 订阅每日金融新闻
• 获取热门投资资讯

💡 提示：直接发送文件即可使用文件转换功能！
        """
        return help_text.strip()
    
    def _handle_status(self, msg) -> str:
        """处理状态命令"""
        try:
            # 获取插件状态
            plugin_manager = self._get_plugin_manager()
            if plugin_manager:
                status = plugin_manager.get_status()
                
                status_text = f"""
🤖 机器人状态

📊 插件统计：
• 总插件数: {status['total_plugins']}
• 已加载: {', '.join(status['loaded_plugins'])}

🔧 系统状态：
• 运行状态: {'运行中' if self._is_bot_running() else '已停止'}
• 配置状态: {'正常' if self.config.validate() else '异常'}
                """
                return status_text.strip()
            else:
                return "无法获取状态信息。"
                
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return "获取状态信息时出现错误。"
    
    def _handle_plugins(self, msg) -> str:
        """处理插件命令"""
        try:
            plugin_manager = self._get_plugin_manager()
            if plugin_manager:
                status = plugin_manager.get_status()
                
                plugins_text = "📦 已安装插件：\n\n"
                for name, details in status['plugin_details'].items():
                    status_icon = "🟢" if details['is_running'] else "🔴"
                    plugins_text += f"{status_icon} {details['name']} v{details['version']}\n"
                    plugins_text += f"   描述: {details['description']}\n\n"
                
                return plugins_text.strip()
            else:
                return "无法获取插件信息。"
                
        except Exception as e:
            logger.error(f"获取插件信息失败: {e}")
            return "获取插件信息时出现错误。"
    
    def _handle_reload(self, msg) -> str:
        """处理重载命令"""
        try:
            plugin_manager = self._get_plugin_manager()
            if plugin_manager:
                plugin_manager.reload_plugins()
                return "✅ 插件重新加载完成！"
            else:
                return "无法重新加载插件。"
                
        except Exception as e:
            logger.error(f"重新加载插件失败: {e}")
            return "重新加载插件时出现错误。"
    
    def _handle_plugin_command(self, content: str, user_id: str) -> Optional[str]:
        """处理插件命令"""
        try:
            # 解析命令格式: /插件名 命令 [参数]
            if content.startswith('/'):
                parts = content[1:].split(' ', 1)
                if len(parts) >= 1:
                    plugin_name = parts[0]
                    command = parts[1] if len(parts) > 1 else ""
                    
                    plugin_manager = self._get_plugin_manager()
                    if plugin_manager:
                        plugin = plugin_manager.get_plugin(plugin_name)
                        if plugin:
                            return plugin.execute_command(command, user_id=user_id)
                        else:
                            return f"插件 '{plugin_name}' 不存在或未加载。"
            
            return None
            
        except Exception as e:
            logger.error(f"处理插件命令失败: {e}")
            return None
    
    def _get_plugin(self, plugin_name: str):
        """获取插件实例"""
        try:
            plugin_manager = self._get_plugin_manager()
            if plugin_manager:
                return plugin_manager.get_plugin(plugin_name)
            return None
        except Exception as e:
            logger.error(f"获取插件 {plugin_name} 失败: {e}")
            return None
    
    def _get_plugin_manager(self):
        """获取插件管理器"""
        return getattr(self, 'plugin_manager', None)
    
    def _is_bot_running(self) -> bool:
        """检查机器人是否正在运行"""
        # 这里需要实现检查机器人运行状态的逻辑
        return True
    
    def _get_default_response(self) -> str:
        """获取默认回复"""
        responses = [
            "有什么可以帮助您的吗？",
            "请发送文件或输入命令，我会为您处理！",
            "输入 '帮助' 查看所有可用功能。",
            "我是您的智能助手，随时为您服务！"
        ]
        import random
        return random.choice(responses) 