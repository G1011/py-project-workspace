"""
帮助插件
提供系统帮助和命令说明
"""

from typing import Dict, Any
from loguru import logger

from core.base_plugin import BasePlugin


class HelpPlugin(BasePlugin):
    """帮助插件"""
    
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.name = "Help"
        self.version = "1.0.0"
        self.description = "系统帮助和命令说明"
    
    def start(self) -> None:
        """启动插件"""
        self.is_running = True
        logger.info("帮助插件已启动")
    
    def stop(self) -> None:
        """停止插件"""
        self.is_running = False
        logger.info("帮助插件已停止")
    
    def execute_command(self, command: str, **kwargs) -> str:
        """执行插件命令"""
        if command == "help" or command == "":
            return self.get_main_help()
        elif command == "commands":
            return self.get_commands_help()
        elif command == "plugins":
            return self.get_plugins_help()
        elif command == "about":
            return self.get_about_info()
        else:
            return self.get_command_help(command)
    
    def get_help(self) -> str:
        """获取帮助信息"""
        return """
📖 帮助插件

📋 可用命令：
• /help - 显示主帮助信息
• /help commands - 显示所有命令
• /help plugins - 显示插件信息
• /help about - 显示关于信息
• /help [命令名] - 显示特定命令帮助

💡 提示：
• 输入 'help' 查看主帮助
• 输入 'commands' 查看所有命令
• 输入 'about' 了解机器人信息
        """
    
    def get_main_help(self) -> str:
        """获取主帮助信息"""
        return """
🤖 微信工具机器人 - 帮助中心

🎯 主要功能：
📁 文件转换 - Word、PDF、图片互转
⏰ 定时任务 - 定时发送消息和提醒
📰 新闻推送 - 每日金融新闻推送
📖 帮助系统 - 完整的帮助文档

📋 快速开始：
• 发送文件 → 自动转换格式
• 输入 'help' → 查看帮助
• 输入 'status' → 查看状态
• 输入 'plugins' → 查看插件

🔧 系统命令：
• help/帮助 - 显示帮助信息
• status/状态 - 查看机器人状态
• plugins/插件 - 查看已安装插件
• reload/重载 - 重新加载插件

💡 使用技巧：
• 直接发送文件即可使用转换功能
• 使用 /插件名 help 查看插件帮助
• 使用 /插件名 status 查看插件状态

📞 技术支持：
如有问题，请联系管理员
        """
    
    def get_commands_help(self) -> str:
        """获取命令帮助"""
        return """
📋 系统命令列表

🔧 基础命令：
• help/帮助 - 显示帮助信息
• status/状态 - 查看机器人状态
• plugins/插件 - 查看已安装插件
• reload/重载 - 重新加载插件

📁 文件转换命令：
• 直接发送文件 - 自动转换格式
• /file_converter help - 文件转换帮助
• /file_converter status - 转换状态

⏰ 定时任务命令：
• /scheduler add daily 09:00 早安提醒 - 添加每日提醒
• /scheduler add weekly 1 18:00 周会提醒 - 添加每周提醒
• /scheduler add once 2024-01-01 10:00 新年快乐 - 添加一次性提醒
• /scheduler list - 查看所有任务
• /scheduler delete 任务ID - 删除任务
• /scheduler help - 定时任务帮助

📰 新闻推送命令：
• /news_pusher subscribe - 订阅新闻推送
• /news_pusher unsubscribe - 取消订阅
• /news_pusher news - 获取最新新闻
• /news_pusher help - 新闻推送帮助

💡 命令格式：
• /插件名 命令 [参数]
• 例如: /scheduler add daily 09:00 早安提醒
        """
    
    def get_plugins_help(self) -> str:
        """获取插件帮助"""
        return """
📦 已安装插件

📁 FileConverter (文件转换插件)
• 功能: Word、PDF、图片格式转换
• 命令: /file_converter help
• 状态: 自动处理文件上传

⏰ Scheduler (定时任务插件)
• 功能: 定时发送消息和提醒
• 命令: /scheduler help
• 状态: 支持每日、每周、一次性任务

📰 NewsPusher (新闻推送插件)
• 功能: 金融新闻推送
• 命令: /news_pusher help
• 状态: 每日自动推送热门新闻

📖 Help (帮助插件)
• 功能: 系统帮助和命令说明
• 命令: /help
• 状态: 提供完整的帮助文档

💡 插件使用：
• 每个插件都有独立的帮助系统
• 使用 /插件名 help 查看详细帮助
• 使用 /插件名 status 查看插件状态
        """
    
    def get_about_info(self) -> str:
        """获取关于信息"""
        return """
🤖 关于微信工具机器人

📝 项目信息：
• 名称: 微信工具机器人
• 版本: 1.0.0
• 开发: AI助手
• 架构: 插件化设计

🎯 设计理念：
• 模块化: 功能独立，易于扩展
• 用户友好: 简单易用的交互方式
• 高可用: 稳定的运行和错误处理
• 可扩展: 支持新功能快速集成

🔧 技术特点：
• 插件化架构 - 功能模块化，易于维护
• 配置化管理 - 支持灵活配置
• 数据库存储 - 数据持久化
• 多线程处理 - 并发处理任务
• 日志记录 - 完整的操作日志

📊 功能统计：
• 文件转换: 支持3种格式互转
• 定时任务: 支持多种时间模式
• 新闻推送: 多源新闻聚合
• 帮助系统: 完整的文档支持

🔄 更新计划：
• 更多文件格式支持
• 更多新闻源接入
• 更多定时任务类型
• 更多插件功能

💡 使用建议：
• 定期查看帮助文档
• 及时反馈使用问题
• 关注功能更新通知
        """
    
    def get_command_help(self, command: str) -> str:
        """获取特定命令帮助"""
        command_help = {
            "help": """
📖 help 命令帮助

用法: help [子命令]

子命令:
• help - 显示主帮助信息
• commands - 显示所有命令
• plugins - 显示插件信息
• about - 显示关于信息

示例:
• help - 显示主帮助
• help commands - 显示命令列表
• help plugins - 显示插件信息
            """,
            
            "status": """
📊 status 命令帮助

用法: status

功能: 查看机器人运行状态

显示信息:
• 插件运行状态
• 系统配置状态
• 数据库连接状态
• 各插件统计信息

示例:
• status - 查看系统状态
            """,
            
            "plugins": """
📦 plugins 命令帮助

用法: plugins

功能: 查看已安装插件

显示信息:
• 插件列表
• 插件版本
• 插件描述
• 运行状态

示例:
• plugins - 查看插件列表
            """,
            
            "reload": """
🔄 reload 命令帮助

用法: reload

功能: 重新加载所有插件

注意事项:
• 会重新加载所有启用的插件
• 正在运行的任务会受到影响
• 建议在维护时使用

示例:
• reload - 重新加载插件
            """,
            
            "file_converter": """
📁 file_converter 命令帮助

用法: /file_converter [子命令]

子命令:
• help - 显示文件转换帮助
• status - 查看转换状态

支持格式:
• Word文档 (.doc/.docx) → PDF
• 图片文件 (.jpg/.png等) → PDF
• PDF文件 → Word文档

使用方法:
• 直接发送文件即可自动转换
• 转换后的文件会自动发送给您

示例:
• /file_converter help - 查看帮助
• /file_converter status - 查看状态
            """,
            
            "scheduler": """
⏰ scheduler 命令帮助

用法: /scheduler [子命令] [参数]

子命令:
• add - 添加定时任务
• list - 查看所有任务
• delete - 删除指定任务
• help - 显示帮助
• status - 查看状态

时间格式:
• daily HH:MM - 每日执行
• weekly 0-6 HH:MM - 每周指定天执行
• once YYYY-MM-DD HH:MM - 一次性执行

示例:
• /scheduler add daily 09:00 早安提醒
• /scheduler add weekly 1 18:00 周会提醒
• /scheduler add once 2024-01-01 10:00 新年快乐
• /scheduler list - 查看所有任务
• /scheduler delete 1 - 删除任务ID为1的任务
            """,
            
            "news_pusher": """
📰 news_pusher 命令帮助

用法: /news_pusher [子命令]

子命令:
• subscribe - 订阅新闻推送
• unsubscribe - 取消订阅
• news - 获取最新新闻
• help - 显示帮助
• status - 查看状态

功能说明:
• 每日自动推送金融新闻
• 支持手动获取最新新闻
• 多源新闻聚合

示例:
• /news_pusher subscribe - 订阅新闻
• /news_pusher unsubscribe - 取消订阅
• /news_pusher news - 获取最新新闻
• /news_pusher status - 查看状态
            """
        }
        
        return command_help.get(command, f"未找到命令 '{command}' 的帮助信息，请使用 'help' 查看所有可用命令。") 