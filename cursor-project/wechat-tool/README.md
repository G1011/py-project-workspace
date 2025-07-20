# 微信工具机器人

一个功能丰富的微信对话机器人，支持文件转换、定时任务、新闻推送等多种功能。

## 🎯 主要功能

### 📁 文件转换
- **Word转PDF**: 支持.doc/.docx文件转换为PDF
- **图片转PDF**: 支持jpg/png/bmp等图片格式转换为PDF
- **PDF转Word**: 支持PDF文件转换为Word文档
- **自动处理**: 直接发送文件即可自动转换

### ⏰ 定时任务
- **每日提醒**: 设置每日固定时间提醒
- **每周提醒**: 设置每周指定天提醒
- **一次性提醒**: 设置特定日期时间提醒
- **自定义消息**: 支持自定义提醒内容

### 📰 新闻推送
- **金融新闻**: 每日推送热门金融新闻
- **多源聚合**: 从多个新闻源获取内容
- **智能筛选**: 根据关键词筛选相关新闻
- **订阅管理**: 支持订阅和取消订阅

### 🔧 系统功能
- **插件化架构**: 模块化设计，易于扩展
- **配置管理**: 支持灵活配置
- **日志记录**: 完整的操作日志
- **帮助系统**: 详细的帮助文档

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 微信账号

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动机器人
```bash
python main.py
```

### 配置选项
```bash
# 使用自定义配置文件
python main.py --config my_config.yaml

# 启用调试模式
python main.py --debug

# 设置日志级别
python main.py --log-level DEBUG
```

## 📋 使用指南

### 文件转换
1. 直接发送Word文档 → 自动转换为PDF
2. 直接发送图片文件 → 自动转换为PDF
3. 直接发送PDF文件 → 自动转换为Word

### 定时任务
```
# 添加每日提醒
/scheduler add daily 09:00 早安提醒

# 添加每周提醒
/scheduler add weekly 1 18:00 周会提醒

# 添加一次性提醒
/scheduler add once 2024-01-01 10:00 新年快乐

# 查看所有任务
/scheduler list

# 删除任务
/scheduler delete 任务ID
```

### 新闻推送
```
# 订阅新闻推送
/news_pusher subscribe

# 取消订阅
/news_pusher unsubscribe

# 获取最新新闻
/news_pusher news

# 查看状态
/news_pusher status
```

### 系统命令
```
# 查看帮助
help

# 查看状态
status

# 查看插件
plugins

# 重新加载插件
reload
```

## ⚙️ 配置说明

### 配置文件结构
```yaml
# 微信配置
wechat:
  login_timeout: 300
  enable_cmd_qr: true
  hot_reload: true

# 文件处理配置
file_processing:
  upload_dir: "uploads"
  output_dir: "outputs"
  max_file_size: 50
  supported_formats:
    word: [".doc", ".docx"]
    pdf: [".pdf"]
    image: [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]

# 定时任务配置
scheduler:
  timezone: "Asia/Shanghai"
  max_jobs: 100

# 新闻推送配置
news:
  sources:
    - "https://www.jrj.com.cn/"
    - "https://finance.sina.com.cn/"
    - "https://www.10jqka.com.cn/"
  keywords:
    - "金融"
    - "股市"
    - "基金"
    - "理财"
    - "投资"
  max_news_count: 5

# 日志配置
logging:
  level: "INFO"
  format: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
  file: "logs/wechat_bot.log"

# 数据库配置
database:
  path: "data/wechat_bot.db"

# 插件配置
plugins:
  enabled:
    - "file_converter"
    - "scheduler"
    - "news_pusher"
    - "help"
  auto_reload: true
```

## 📁 项目结构

```
wechat-tool/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
├── README.md              # 项目文档
├── config/
│   └── config.yaml        # 配置文件
├── core/                  # 核心模块
│   ├── __init__.py
│   ├── bot.py            # 机器人主类
│   ├── base_plugin.py    # 插件基类
│   ├── config_manager.py # 配置管理器
│   ├── message_handler.py # 消息处理器
│   └── plugin_manager.py # 插件管理器
├── plugins/               # 插件目录
│   ├── file_converter.py # 文件转换插件
│   ├── scheduler.py      # 定时任务插件
│   ├── news_pusher.py   # 新闻推送插件
│   └── help.py          # 帮助插件
├── uploads/              # 上传文件目录
├── outputs/              # 输出文件目录
├── logs/                 # 日志目录
└── data/                 # 数据目录
```

## 🔧 开发指南

### 插件开发
1. 继承 `BasePlugin` 类
2. 实现 `start()` 和 `stop()` 方法
3. 实现 `execute_command()` 方法处理命令
4. 在配置文件中启用插件

### 示例插件
```python
from core.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self, config_manager):
        super().__init__(config_manager)
        self.name = "MyPlugin"
        self.description = "我的插件"
    
    def start(self):
        self.is_running = True
    
    def stop(self):
        self.is_running = False
    
    def execute_command(self, command, **kwargs):
        return f"执行命令: {command}"
```

### 添加新功能
1. 在 `plugins/` 目录下创建新插件
2. 在配置文件中启用插件
3. 重启机器人即可使用

## 🐛 故障排除

### 常见问题

**Q: 登录失败怎么办？**
A: 检查网络连接，确保微信账号正常，可以尝试重新启动程序。

**Q: 文件转换失败？**
A: 检查文件格式是否支持，文件大小是否超限，确保有足够的磁盘空间。

**Q: 定时任务不执行？**
A: 检查时间格式是否正确，确保机器人正在运行。

**Q: 新闻推送收不到？**
A: 确认已订阅新闻推送，检查网络连接。

### 日志查看
```bash
# 查看运行日志
tail -f logs/wechat_bot.log

# 查看调试日志
tail -f logs/debug.log
```

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请通过以下方式联系：
- 提交 Issue
- 发送邮件
- 微信群讨论

---

**注意**: 使用本机器人时请遵守相关法律法规和微信使用条款。 