#!/usr/bin/env python3
"""
安装脚本 - 自动安装依赖和Playwright浏览器
"""
import subprocess
import sys
import os

def run_command(command, description):
    """执行命令并显示进度"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    print("🚀 开始安装 Python Screenshot Service")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        sys.exit(1)
    
    print(f"✅ Python 版本: {sys.version}")
    
    # 安装依赖
    if not run_command("pip install -r requirements.txt", "安装Python依赖"):
        sys.exit(1)
    
    # 安装Playwright浏览器
    if not run_command("playwright install chromium", "安装Playwright浏览器"):
        sys.exit(1)
    
    # 安装系统依赖（Linux）
    if os.name == 'posix':
        run_command("playwright install-deps chromium", "安装系统依赖")
    
    print("\n🎉 安装完成！")
    print("\n📋 使用方法:")
    print("  启动服务: python main.py")
    print("  测试服务: python test_service.py")
    print("  API文档: http://localhost:8000/docs")

if __name__ == "__main__":
    main()