#!/usr/bin/env python3
"""
微信工具机器人安装脚本
自动安装依赖和设置环境
"""

import os
import sys
import subprocess
from pathlib import Path
from loguru import logger


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True


def install_dependencies():
    """安装依赖包"""
    print("📦 安装依赖包...")
    
    try:
        # 升级pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # 安装依赖
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        print("✅ 依赖包安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False


def create_directories():
    """创建必要的目录"""
    print("📁 创建目录结构...")
    
    directories = [
        "uploads",
        "outputs", 
        "logs",
        "data",
        "plugins"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ 创建目录: {directory}")
    
    print("✅ 目录结构创建完成")


def check_config():
    """检查配置文件"""
    print("⚙️ 检查配置文件...")
    
    config_path = "config/config.yaml"
    if not os.path.exists(config_path):
        print(f"⚠️ 配置文件 {config_path} 不存在，将使用默认配置")
    else:
        print(f"✅ 配置文件存在: {config_path}")
    
    return True


def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    try:
        result = subprocess.run([sys.executable, "test_bot.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        return False


def show_usage():
    """显示使用说明"""
    print("\n" + "=" * 50)
    print("🎉 安装完成！")
    print("=" * 50)
    print("\n📋 使用方法:")
    print("1. 启动机器人:")
    print("   python main.py")
    print("   # 或者")
    print("   python run.py")
    print("\n2. 测试功能:")
    print("   python test_bot.py")
    print("\n3. 查看帮助:")
    print("   python main.py --help")
    print("\n4. 调试模式:")
    print("   python main.py --debug")
    print("\n📖 更多信息请查看 README.md")
    print("=" * 50)


def main():
    """主安装函数"""
    print("🚀 微信工具机器人安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 创建目录结构
    create_directories()
    
    # 检查配置文件
    check_config()
    
    # 安装依赖
    if not install_dependencies():
        return 1
    
    # 运行测试
    if not run_tests():
        print("⚠️ 测试失败，但安装继续...")
    
    # 显示使用说明
    show_usage()
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 