"""
插件管理器
负责插件的动态加载、管理和生命周期控制
"""

import os
import sys
import importlib
import inspect
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from loguru import logger

from core.base_plugin import BasePlugin


class PluginManager:
    """插件管理器"""
    
    def __init__(self, config_manager):
        """初始化插件管理器"""
        self.config = config_manager
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_modules: Dict[str, Any] = {}
        self.plugins_dir = "plugins"
        
        # 确保插件目录存在
        Path(self.plugins_dir).mkdir(exist_ok=True)
    
    def load_plugins(self) -> None:
        """加载所有启用的插件"""
        enabled_plugins = self.config.get("plugins.enabled", [])
        
        for plugin_name in enabled_plugins:
            try:
                self.load_plugin(plugin_name)
            except Exception as e:
                logger.error(f"加载插件 {plugin_name} 失败: {e}")
    
    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """加载单个插件"""
        try:
            # 构建插件模块路径
            plugin_path = os.path.join(self.plugins_dir, f"{plugin_name}.py")
            
            if not os.path.exists(plugin_path):
                logger.warning(f"插件文件不存在: {plugin_path}")
                return None
            
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                logger.error(f"在插件 {plugin_name} 中未找到有效的插件类")
                return None
            
            # 实例化插件
            plugin_instance = plugin_class(self.config)
            
            # 注册插件
            self.plugins[plugin_name] = plugin_instance
            self.plugin_modules[plugin_name] = module
            
            logger.info(f"插件 {plugin_name} 加载成功")
            return plugin_instance
            
        except Exception as e:
            logger.error(f"加载插件 {plugin_name} 失败: {e}")
            return None
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        try:
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                plugin.stop()
                del self.plugins[plugin_name]
                
                if plugin_name in self.plugin_modules:
                    del self.plugin_modules[plugin_name]
                
                logger.info(f"插件 {plugin_name} 卸载成功")
                return True
            else:
                logger.warning(f"插件 {plugin_name} 不存在")
                return False
                
        except Exception as e:
            logger.error(f"卸载插件 {plugin_name} 失败: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """重新加载插件"""
        try:
            # 先卸载
            self.unload_plugin(plugin_name)
            
            # 重新加载
            return self.load_plugin(plugin_name) is not None
            
        except Exception as e:
            logger.error(f"重新加载插件 {plugin_name} 失败: {e}")
            return False
    
    def reload_plugins(self) -> None:
        """重新加载所有插件"""
        logger.info("开始重新加载所有插件...")
        
        # 获取当前启用的插件列表
        enabled_plugins = self.config.get("plugins.enabled", [])
        
        # 卸载所有插件
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
        
        # 重新加载启用的插件
        for plugin_name in enabled_plugins:
            self.load_plugin(plugin_name)
        
        logger.info("插件重新加载完成")
    
    def start_plugins(self) -> None:
        """启动所有插件"""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.start()
                logger.info(f"插件 {plugin_name} 启动成功")
            except Exception as e:
                logger.error(f"启动插件 {plugin_name} 失败: {e}")
    
    def stop_plugins(self) -> None:
        """停止所有插件"""
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin.stop()
                logger.info(f"插件 {plugin_name} 停止成功")
            except Exception as e:
                logger.error(f"停止插件 {plugin_name} 失败: {e}")
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """获取所有插件"""
        return self.plugins.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """获取插件状态"""
        status = {
            "total_plugins": len(self.plugins),
            "enabled_plugins": self.config.get("plugins.enabled", []),
            "loaded_plugins": list(self.plugins.keys()),
            "plugin_details": {}
        }
        
        for name, plugin in self.plugins.items():
            status["plugin_details"][name] = {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "is_running": plugin.is_running
            }
        
        return status
    
    def execute_plugin_command(self, plugin_name: str, command: str, **kwargs) -> Any:
        """执行插件命令"""
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            raise ValueError(f"插件 {plugin_name} 不存在")
        
        if hasattr(plugin, 'execute_command'):
            return plugin.execute_command(command, **kwargs)
        else:
            raise NotImplementedError(f"插件 {plugin_name} 不支持命令执行")
    
    def list_available_plugins(self) -> List[str]:
        """列出可用的插件"""
        available_plugins = []
        plugins_dir = Path(self.plugins_dir)
        
        if plugins_dir.exists():
            for plugin_file in plugins_dir.glob("*.py"):
                if plugin_file.name != "__init__.py":
                    available_plugins.append(plugin_file.stem)
        
        return available_plugins 