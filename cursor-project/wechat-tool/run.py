#!/usr/bin/env python3
"""
微信工具机器人启动脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    from main import main
    sys.exit(main()) 