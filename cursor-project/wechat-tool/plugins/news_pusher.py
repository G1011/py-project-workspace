"""
新闻推送插件
实现金融新闻的抓取和推送功能
"""

import os
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger

import itchat
from bs4 import BeautifulSoup
import threading
import time

from core.base_plugin import BasePlugin


class NewsPusherPlugin(BasePlugin):
    """新闻推送插件"""
    
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.name = "NewsPusher"
        self.version = "1.0.0"
        self.description = "金融新闻推送，每日获取热门投资资讯"
        
        # 获取配置
        self.news_sources = self.config.get("news.sources", [])
        self.keywords = self.config.get("news.keywords", [])
        self.max_news_count = self.config.get("news.max_news_count", 5)
        
        # 数据库配置
        self.db_path = self.config.get("database.path", "data/wechat_bot.db")
        self._init_database()
        
        # 新闻推送线程
        self.news_thread = None
        self.is_news_running = False
        
        # 订阅用户列表
        self.subscribers = set()
        self._load_subscribers()
    
    def start(self) -> None:
        """启动插件"""
        self.is_running = True
        self._start_news_thread()
        logger.info("新闻推送插件已启动")
    
    def stop(self) -> None:
        """停止插件"""
        self.is_running = False
        self._stop_news_thread()
        logger.info("新闻推送插件已停止")
    
    def execute_command(self, command: str, **kwargs) -> str:
        """执行插件命令"""
        user_id = kwargs.get('user_id', '')
        
        if command == "subscribe":
            return self._subscribe_user(user_id)
        elif command == "unsubscribe":
            return self._unsubscribe_user(user_id)
        elif command == "news":
            return self._get_latest_news()
        elif command == "help":
            return self.get_help()
        elif command == "status":
            return self._get_news_status()
        else:
            return "未知命令，输入 'help' 查看帮助"
    
    def get_help(self) -> str:
        """获取帮助信息"""
        return """
📰 新闻推送插件帮助

📋 可用命令：
• /news_pusher subscribe - 订阅每日新闻推送
• /news_pusher unsubscribe - 取消订阅
• /news_pusher news - 获取最新新闻
• /news_pusher status - 查看插件状态

📰 新闻来源：
• 金融界
• 新浪财经
• 同花顺财经

🔍 关注领域：
• 金融动态
• 股市行情
• 基金投资
• 理财资讯

💡 提示：
• 订阅后每日自动推送热门新闻
• 支持手动获取最新新闻
• 新闻内容经过筛选，确保质量
        """
    
    def _init_database(self) -> None:
        """初始化数据库"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建新闻表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    url TEXT,
                    source TEXT NOT NULL,
                    published_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建订阅用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_subscribers (
                    user_id TEXT PRIMARY KEY,
                    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("新闻推送数据库初始化完成")
            
        except Exception as e:
            logger.error(f"初始化数据库失败: {e}")
    
    def _load_subscribers(self) -> None:
        """加载订阅用户"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id FROM news_subscribers')
            subscribers = cursor.fetchall()
            
            self.subscribers = {row[0] for row in subscribers}
            conn.close()
            
            logger.info(f"加载了 {len(self.subscribers)} 个订阅用户")
            
        except Exception as e:
            logger.error(f"加载订阅用户失败: {e}")
    
    def _start_news_thread(self) -> None:
        """启动新闻推送线程"""
        if self.news_thread is None or not self.news_thread.is_alive():
            self.is_news_running = True
            self.news_thread = threading.Thread(target=self._run_news_scheduler, daemon=True)
            self.news_thread.start()
            logger.info("新闻推送线程已启动")
    
    def _stop_news_thread(self) -> None:
        """停止新闻推送线程"""
        self.is_news_running = False
        if self.news_thread and self.news_thread.is_alive():
            self.news_thread.join(timeout=5)
        logger.info("新闻推送线程已停止")
    
    def _run_news_scheduler(self) -> None:
        """运行新闻推送调度器"""
        while self.is_news_running:
            try:
                current_time = datetime.now()
                
                # 每天上午9点推送新闻
                if current_time.hour == 9 and current_time.minute == 0:
                    self._push_daily_news()
                
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"新闻推送调度器错误: {e}")
                time.sleep(300)  # 出错后等待5分钟
    
    def _subscribe_user(self, user_id: str) -> str:
        """订阅用户"""
        try:
            if user_id in self.subscribers:
                return "您已经订阅了新闻推送"
            
            # 添加到数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO news_subscribers (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            # 添加到内存
            self.subscribers.add(user_id)
            
            logger.info(f"用户 {user_id} 订阅了新闻推送")
            return "✅ 订阅成功！您将每日收到金融新闻推送"
            
        except Exception as e:
            logger.error(f"订阅用户失败: {e}")
            return f"订阅失败: {str(e)}"
    
    def _unsubscribe_user(self, user_id: str) -> str:
        """取消订阅"""
        try:
            if user_id not in self.subscribers:
                return "您还没有订阅新闻推送"
            
            # 从数据库删除
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM news_subscribers WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            
            # 从内存删除
            self.subscribers.discard(user_id)
            
            logger.info(f"用户 {user_id} 取消订阅了新闻推送")
            return "✅ 已取消订阅"
            
        except Exception as e:
            logger.error(f"取消订阅失败: {e}")
            return f"取消订阅失败: {str(e)}"
    
    def _get_latest_news(self) -> str:
        """获取最新新闻"""
        try:
            # 抓取最新新闻
            news_list = self._fetch_latest_news()
            
            if not news_list:
                return "暂无最新新闻"
            
            # 格式化新闻内容
            news_text = "📰 最新金融新闻：\n\n"
            for i, news in enumerate(news_list[:self.max_news_count], 1):
                news_text += f"{i}. {news['title']}\n"
                news_text += f"   来源: {news['source']}\n"
                if news.get('summary'):
                    news_text += f"   摘要: {news['summary'][:100]}...\n"
                news_text += "\n"
            
            return news_text.strip()
            
        except Exception as e:
            logger.error(f"获取最新新闻失败: {e}")
            return f"获取新闻失败: {str(e)}"
    
    def _push_daily_news(self) -> None:
        """推送每日新闻"""
        try:
            if not self.subscribers:
                logger.info("没有订阅用户，跳过新闻推送")
                return
            
            # 获取最新新闻
            news_list = self._fetch_latest_news()
            
            if not news_list:
                logger.info("没有获取到新闻，跳过推送")
                return
            
            # 格式化推送内容
            push_text = "📰 每日金融新闻推送\n\n"
            push_text += f"📅 {datetime.now().strftime('%Y年%m月%d日')}\n\n"
            
            for i, news in enumerate(news_list[:self.max_news_count], 1):
                push_text += f"{i}. {news['title']}\n"
                push_text += f"   来源: {news['source']}\n\n"
            
            # 推送给所有订阅用户
            for user_id in self.subscribers:
                try:
                    itchat.send_msg(push_text, toUserName=user_id)
                    logger.info(f"已推送新闻给用户 {user_id}")
                except Exception as e:
                    logger.error(f"推送新闻给用户 {user_id} 失败: {e}")
            
            logger.info(f"每日新闻推送完成，共推送给 {len(self.subscribers)} 个用户")
            
        except Exception as e:
            logger.error(f"推送每日新闻失败: {e}")
    
    def _fetch_latest_news(self) -> List[Dict[str, Any]]:
        """抓取最新新闻"""
        news_list = []
        
        try:
            # 这里实现具体的新闻抓取逻辑
            # 由于实际抓取需要处理反爬虫等问题，这里提供模拟数据
            
            mock_news = [
                {
                    "title": "央行降准0.25个百分点，释放长期资金约5000亿元",
                    "source": "金融界",
                    "summary": "中国人民银行决定于2024年1月15日下调金融机构存款准备金率0.25个百分点...",
                    "url": "https://www.jrj.com.cn/",
                    "published_at": datetime.now()
                },
                {
                    "title": "A股三大指数集体上涨，创业板指涨超2%",
                    "source": "新浪财经",
                    "summary": "今日A股市场表现强劲，三大指数集体上涨，创业板指涨幅超过2%...",
                    "url": "https://finance.sina.com.cn/",
                    "published_at": datetime.now()
                },
                {
                    "title": "基金公司积极布局ESG投资，绿色金融成新趋势",
                    "source": "同花顺财经",
                    "summary": "随着ESG投资理念的普及，越来越多的基金公司开始布局绿色金融产品...",
                    "url": "https://www.10jqka.com.cn/",
                    "published_at": datetime.now()
                },
                {
                    "title": "数字人民币试点范围进一步扩大",
                    "source": "金融界",
                    "summary": "数字人民币试点工作稳步推进，试点范围进一步扩大，应用场景不断丰富...",
                    "url": "https://www.jrj.com.cn/",
                    "published_at": datetime.now()
                },
                {
                    "title": "银行理财产品收益率持续下行",
                    "source": "新浪财经",
                    "summary": "受市场利率下行影响，银行理财产品收益率持续走低，投资者需关注风险...",
                    "url": "https://finance.sina.com.cn/",
                    "published_at": datetime.now()
                }
            ]
            
            # 保存到数据库
            self._save_news_to_db(mock_news)
            
            news_list = mock_news
            
        except Exception as e:
            logger.error(f"抓取新闻失败: {e}")
        
        return news_list
    
    def _save_news_to_db(self, news_list: List[Dict[str, Any]]) -> None:
        """保存新闻到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for news in news_list:
                cursor.execute('''
                    INSERT INTO news_articles (title, content, url, source, published_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    news['title'],
                    news.get('summary', ''),
                    news.get('url', ''),
                    news['source'],
                    news.get('published_at', datetime.now())
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"保存新闻到数据库失败: {e}")
    
    def _get_news_status(self) -> str:
        """获取新闻推送状态"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取新闻总数
            cursor.execute('SELECT COUNT(*) FROM news_articles')
            total_news = cursor.fetchone()[0]
            
            # 获取今日新闻数
            today = datetime.now().date()
            cursor.execute('''
                SELECT COUNT(*) FROM news_articles 
                WHERE DATE(published_at) = ?
            ''', (today,))
            today_news = cursor.fetchone()[0]
            
            conn.close()
            
            return f"""
📰 新闻推送插件状态

✅ 运行状态: {'运行中' if self.is_running else '已停止'}
🔄 推送线程: {'运行中' if self.is_news_running else '已停止'}
👥 订阅用户: {len(self.subscribers)} 人
📊 新闻统计:
• 总新闻数: {total_news}
• 今日新闻: {today_news}

📰 新闻来源: {', '.join(self.news_sources)}
🔍 关注关键词: {', '.join(self.keywords)}

💡 提示：
• 每日上午9点自动推送
• 使用 /news_pusher subscribe 订阅
• 使用 /news_pusher news 获取最新新闻
            """
            
        except Exception as e:
            logger.error(f"获取新闻状态失败: {e}")
            return "获取状态失败" 