#!/usr/bin/env python3
"""
微信工具机器人测试脚本
用于测试各个功能模块
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config_manager import ConfigManager
from core.plugin_manager import PluginManager
from plugins.file_converter import FileConverterPlugin
from plugins.scheduler import SchedulerPlugin
from plugins.news_pusher import NewsPusherPlugin
from plugins.help import HelpPlugin
from loguru import logger


def test_config_manager():
    """测试配置管理器"""
    print("🔧 测试配置管理器...")
    
    config = ConfigManager("config/config.yaml")
    
    # 测试配置读取
    assert config.get("wechat.login_timeout") == 300
    assert config.get("file_processing.max_file_size") == 50
    assert config.get("logging.level") == "INFO"
    
    print("✅ 配置管理器测试通过")


def test_plugins():
    """测试插件系统"""
    print("📦 测试插件系统...")
    
    config = ConfigManager("config/config.yaml")
    plugin_manager = PluginManager(config)
    
    # 测试插件加载
    plugin_manager.load_plugins()
    
    # 检查插件状态
    status = plugin_manager.get_status()
    print(f"📊 插件状态: {status}")
    
    print("✅ 插件系统测试通过")


def test_file_converter():
    """测试文件转换插件"""
    print("📁 测试文件转换插件...")
    
    config = ConfigManager("config/config.yaml")
    plugin = FileConverterPlugin(config)
    
    # 测试插件启动
    plugin.start()
    assert plugin.is_running == True
    
    # 测试帮助信息
    help_text = plugin.get_help()
    assert "文件转换插件帮助" in help_text
    
    # 测试插件停止
    plugin.stop()
    assert plugin.is_running == False
    
    print("✅ 文件转换插件测试通过")


def test_scheduler():
    """测试定时任务插件"""
    print("⏰ 测试定时任务插件...")
    
    config = ConfigManager("config/config.yaml")
    plugin = SchedulerPlugin(config)
    
    # 测试插件启动
    plugin.start()
    assert plugin.is_running == True
    
    # 测试帮助信息
    help_text = plugin.get_help()
    assert "定时任务插件帮助" in help_text
    
    # 测试插件停止
    plugin.stop()
    assert plugin.is_running == False
    
    print("✅ 定时任务插件测试通过")


def test_news_pusher():
    """测试新闻推送插件"""
    print("📰 测试新闻推送插件...")
    
    config = ConfigManager("config/config.yaml")
    plugin = NewsPusherPlugin(config)
    
    # 测试插件启动
    plugin.start()
    assert plugin.is_running == True
    
    # 测试帮助信息
    help_text = plugin.get_help()
    assert "新闻推送插件帮助" in help_text
    
    # 测试插件停止
    plugin.stop()
    assert plugin.is_running == False
    
    print("✅ 新闻推送插件测试通过")


def test_help():
    """测试帮助插件"""
    print("📖 测试帮助插件...")
    
    config = ConfigManager("config/config.yaml")
    plugin = HelpPlugin(config)
    
    # 测试插件启动
    plugin.start()
    assert plugin.is_running == True
    
    # 测试帮助信息
    help_text = plugin.get_help()
    assert "帮助插件" in help_text
    
    # 测试主帮助
    main_help = plugin.get_main_help()
    assert "微信工具机器人" in main_help
    
    # 测试插件停止
    plugin.stop()
    assert plugin.is_running == False
    
    print("✅ 帮助插件测试通过")


def main():
    """主测试函数"""
    print("🧪 开始测试微信工具机器人...")
    print("=" * 50)
    
    try:
        test_config_manager()
        test_plugins()
        test_file_converter()
        test_scheduler()
        test_news_pusher()
        test_help()
        
        print("=" * 50)
        print("🎉 所有测试通过！")
        return 0
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logger.error(f"测试失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 