"""
定时任务插件
实现定时发送消息和提醒功能
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger

import itchat
import schedule
import time
import threading

from core.base_plugin import BasePlugin


class SchedulerPlugin(BasePlugin):
    """定时任务插件"""
    
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.name = "Scheduler"
        self.version = "1.0.0"
        self.description = "定时任务管理，支持定时发送消息和提醒"
        
        # 数据库配置
        self.db_path = self.config.get("database.path", "data/wechat_bot.db")
        self._init_database()
        
        # 定时任务线程
        self.scheduler_thread = None
        self.is_scheduler_running = False
        
        # 加载现有任务
        self._load_existing_tasks()
    
    def start(self) -> None:
        """启动插件"""
        self.is_running = True
        self._start_scheduler_thread()
        logger.info("定时任务插件已启动")
    
    def stop(self) -> None:
        """停止插件"""
        self.is_running = False
        self._stop_scheduler_thread()
        logger.info("定时任务插件已停止")
    
    def execute_command(self, command: str, **kwargs) -> str:
        """执行插件命令"""
        user_id = kwargs.get('user_id', '')
        
        if command.startswith("add"):
            return self._add_scheduled_task(command, user_id)
        elif command.startswith("list"):
            return self._list_scheduled_tasks(user_id)
        elif command.startswith("delete"):
            return self._delete_scheduled_task(command, user_id)
        elif command.startswith("help"):
            return self.get_help()
        elif command.startswith("status"):
            return self._get_scheduler_status()
        else:
            return "未知命令，输入 'help' 查看帮助"
    
    def get_help(self) -> str:
        """获取帮助信息"""
        return """
⏰ 定时任务插件帮助

📋 可用命令：
• /scheduler add daily 09:00 早安提醒 - 添加每日9点提醒
• /scheduler add weekly 1 18:00 周会提醒 - 添加每周一18点提醒
• /scheduler add once 2024-01-01 10:00 新年快乐 - 添加一次性提醒
• /scheduler list - 查看所有定时任务
• /scheduler delete 任务ID - 删除指定任务
• /scheduler status - 查看插件状态

⏰ 时间格式：
• daily HH:MM - 每日执行
• weekly 0-6 HH:MM - 每周指定天执行 (0=周日)
• once YYYY-MM-DD HH:MM - 一次性执行

💡 提示：
• 时间格式为24小时制
• 任务ID在list命令中查看
• 支持自定义消息内容
        """
    
    def _init_database(self) -> None:
        """初始化数据库"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建定时任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    schedule_time TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("定时任务数据库初始化完成")
            
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
    
    def _load_existing_tasks(self) -> None:
        """加载现有任务"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, user_id, task_type, schedule_time, message 
                FROM scheduled_tasks 
                WHERE is_active = 1
            ''')
            
            tasks = cursor.fetchall()
            for task in tasks:
                self._schedule_task(task[0], task[1], task[2], task[3], task[4])
            
            conn.close()
            logger.info(f"加载了 {len(tasks)} 个现有定时任务")
            
        except Exception as e:
            logger.error(f"加载现有任务失败: {e}")
    
    def _start_scheduler_thread(self) -> None:
        """启动定时任务线程"""
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            self.is_scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            logger.info("定时任务线程已启动")
    
    def _stop_scheduler_thread(self) -> None:
        """停止定时任务线程"""
        self.is_scheduler_running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        logger.info("定时任务线程已停止")
    
    def _run_scheduler(self) -> None:
        """运行定时任务调度器"""
        while self.is_scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"定时任务调度器错误: {e}")
                time.sleep(5)
    
    def _add_scheduled_task(self, command: str, user_id: str) -> str:
        """添加定时任务"""
        try:
            # 解析命令: add daily 09:00 早安提醒
            parts = command.split(' ', 3)
            if len(parts) < 4:
                return "命令格式错误，请使用: add 类型 时间 消息"
            
            task_type = parts[1]
            schedule_time = parts[2]
            message = parts[3]
            
            # 验证时间格式
            if not self._validate_time_format(task_type, schedule_time):
                return "时间格式错误，请检查格式"
            
            # 保存到数据库
            task_id = self._save_task_to_db(user_id, task_type, schedule_time, message)
            
            # 添加到调度器
            self._schedule_task(task_id, user_id, task_type, schedule_time, message)
            
            return f"✅ 定时任务已添加！\n任务ID: {task_id}\n时间: {schedule_time}\n消息: {message}"
            
        except Exception as e:
            logger.error(f"添加定时任务失败: {e}")
            return f"添加任务失败: {str(e)}"
    
    def _list_scheduled_tasks(self, user_id: str) -> str:
        """列出定时任务"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, task_type, schedule_time, message, created_at
                FROM scheduled_tasks 
                WHERE user_id = ? AND is_active = 1
                ORDER BY created_at DESC
            ''', (user_id,))
            
            tasks = cursor.fetchall()
            conn.close()
            
            if not tasks:
                return "您还没有定时任务"
            
            result = "📋 您的定时任务：\n\n"
            for task in tasks:
                task_id, task_type, schedule_time, message, created_at = task
                result += f"🆔 任务ID: {task_id}\n"
                result += f"⏰ 类型: {task_type}\n"
                result += f"🕐 时间: {schedule_time}\n"
                result += f"💬 消息: {message}\n"
                result += f"📅 创建时间: {created_at}\n"
                result += "─" * 30 + "\n"
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"列出定时任务失败: {e}")
            return f"获取任务列表失败: {str(e)}"
    
    def _delete_scheduled_task(self, command: str, user_id: str) -> str:
        """删除定时任务"""
        try:
            # 解析命令: delete 任务ID
            parts = command.split(' ')
            if len(parts) < 2:
                return "请指定要删除的任务ID"
            
            task_id = int(parts[1])
            
            # 从数据库删除
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE scheduled_tasks 
                SET is_active = 0 
                WHERE id = ? AND user_id = ?
            ''', (task_id, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                
                # 从调度器中移除
                self._unschedule_task(task_id)
                
                return f"✅ 任务 {task_id} 已删除"
            else:
                conn.close()
                return "任务不存在或您没有权限删除"
            
        except ValueError:
            return "任务ID必须是数字"
        except Exception as e:
            logger.error(f"删除定时任务失败: {e}")
            return f"删除任务失败: {str(e)}"
    
    def _validate_time_format(self, task_type: str, schedule_time: str) -> bool:
        """验证时间格式"""
        try:
            if task_type == "daily":
                # 格式: HH:MM
                time.strptime(schedule_time, "%H:%M")
                return True
            elif task_type == "weekly":
                # 格式: 0-6 HH:MM
                parts = schedule_time.split(' ')
                if len(parts) != 2:
                    return False
                day = int(parts[0])
                if day < 0 or day > 6:
                    return False
                time.strptime(parts[1], "%H:%M")
                return True
            elif task_type == "once":
                # 格式: YYYY-MM-DD HH:MM
                datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
                return True
            else:
                return False
        except:
            return False
    
    def _save_task_to_db(self, user_id: str, task_type: str, schedule_time: str, message: str) -> int:
        """保存任务到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scheduled_tasks (user_id, task_type, schedule_time, message)
            VALUES (?, ?, ?, ?)
        ''', (user_id, task_type, schedule_time, message))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def _schedule_task(self, task_id: int, user_id: str, task_type: str, schedule_time: str, message: str) -> None:
        """添加任务到调度器"""
        try:
            if task_type == "daily":
                # 每日任务
                time_parts = schedule_time.split(':')
                schedule.every().day.at(schedule_time).do(
                    self._send_scheduled_message, user_id, message, task_id
                )
                
            elif task_type == "weekly":
                # 每周任务
                parts = schedule_time.split(' ')
                day = int(parts[0])
                time_str = parts[1]
                
                if day == 0:
                    schedule.every().sunday.at(time_str).do(
                        self._send_scheduled_message, user_id, message, task_id
                    )
                elif day == 1:
                    schedule.every().monday.at(time_str).do(
                        self._send_scheduled_message, user_id, message, task_id
                    )
                elif day == 2:
                    schedule.every().tuesday.at(time_str).do(
                        self._send_scheduled_message, user_id, message, task_id
                    )
                elif day == 3:
                    schedule.every().wednesday.at(time_str).do(
                        self._send_scheduled_message, user_id, message, task_id
                    )
                elif day == 4:
                    schedule.every().thursday.at(time_str).do(
                        self._send_scheduled_message, user_id, message, task_id
                    )
                elif day == 5:
                    schedule.every().friday.at(time_str).do(
                        self._send_scheduled_message, user_id, message, task_id
                    )
                elif day == 6:
                    schedule.every().saturday.at(time_str).do(
                        self._send_scheduled_message, user_id, message, task_id
                    )
                    
            elif task_type == "once":
                # 一次性任务
                schedule.every().day.at(schedule_time.split(' ')[1]).do(
                    self._send_scheduled_message, user_id, message, task_id
                )
            
            logger.info(f"任务 {task_id} 已添加到调度器")
            
        except Exception as e:
            logger.error(f"添加任务到调度器失败: {e}")
    
    def _unschedule_task(self, task_id: int) -> None:
        """从调度器中移除任务"""
        # 注意：schedule库没有直接的方法来移除特定任务
        # 这里只是记录日志，实际的任务清理需要在下次重启时进行
        logger.info(f"任务 {task_id} 已标记为删除")
    
    def _send_scheduled_message(self, user_id: str, message: str, task_id: int) -> None:
        """发送定时消息"""
        try:
            # 检查任务是否仍然有效
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT is_active FROM scheduled_tasks WHERE id = ?
            ''', (task_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 1:
                # 发送消息
                itchat.send_msg(message, toUserName=user_id)
                logger.info(f"已发送定时消息: {message} 给用户 {user_id}")
            else:
                logger.info(f"任务 {task_id} 已被删除，跳过发送")
                
        except Exception as e:
            logger.error(f"发送定时消息失败: {e}")
    
    def _get_scheduler_status(self) -> str:
        """获取调度器状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM scheduled_tasks WHERE is_active = 1
            ''')
            
            total_tasks = cursor.fetchone()[0]
            conn.close()
            
            return f"""
⏰ 定时任务插件状态

✅ 运行状态: {'运行中' if self.is_running else '已停止'}
🔄 调度器状态: {'运行中' if self.is_scheduler_running else '已停止'}
📊 总任务数: {total_tasks}
📅 数据库: {self.db_path}

💡 提示：
• 使用 /scheduler help 查看详细帮助
• 使用 /scheduler list 查看您的任务
            """
            
        except Exception as e:
            logger.error(f"获取调度器状态失败: {e}")
            return "获取状态失败" 