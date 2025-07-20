#!/usr/bin/env python3
"""
微信工具机器人主程序
启动微信机器人并管理插件
"""

import os
import sys
import signal
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.bot import WeChatBot
from loguru import logger


def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"收到信号 {signum}，正在优雅关闭...")
    if hasattr(signal_handler, 'bot'):
        signal_handler.bot.stop()
    sys.exit(0)


def setup_signal_handlers(bot):
    """设置信号处理器"""
    signal_handler.bot = bot
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='微信工具机器人')
    parser.add_argument(
        '--config', 
        default='config/config.yaml',
        help='配置文件路径 (默认: config/config.yaml)'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='启用调试模式'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )
    return parser.parse_args()


def main():
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置日志级别
        if args.debug:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")
            logger.add("logs/debug.log", level="DEBUG", rotation="1 day")
        
        logger.info("=" * 50)
        logger.info("🤖 微信工具机器人启动中...")
        logger.info("=" * 50)
        
        # 检查配置文件
        config_path = args.config
        if not os.path.exists(config_path):
            logger.warning(f"配置文件 {config_path} 不存在，将使用默认配置")
        
        # 创建机器人实例
        bot = WeChatBot(config_path)
        
        # 设置信号处理器
        setup_signal_handlers(bot)
        
        # 验证配置
        if not bot.config.validate():
            logger.error("配置验证失败，请检查配置文件")
            return 1
        
        # 显示启动信息
        logger.info("📋 机器人配置信息:")
        logger.info(f"  配置文件: {config_path}")
        logger.info(f"  日志级别: {args.log_level}")
        logger.info(f"  调试模式: {'是' if args.debug else '否'}")
        
        # 显示插件信息
        plugin_status = bot.get_plugin_status()
        logger.info(f"📦 已启用插件: {len(plugin_status.get('loaded_plugins', []))}")
        for plugin_name in plugin_status.get('loaded_plugins', []):
            logger.info(f"  - {plugin_name}")
        
        logger.info("=" * 50)
        logger.info("🚀 启动微信机器人...")
        logger.info("📱 请使用微信扫描二维码登录")
        logger.info("💡 输入 'help' 查看帮助信息")
        logger.info("=" * 50)
        
        # 启动机器人
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("用户中断，正在关闭...")
        return 0
    except Exception as e:
        logger.error(f"启动失败: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 