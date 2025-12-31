#!/usr/bin/env python3
"""
修复脚本 - 自动修复Python截图服务的常见问题
"""
import subprocess
import sys
import os

def run_command(command, description, check_success=True):
    """执行命令"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        if result.stdout:
            print(f"   输出: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        if e.stderr:
            print(f"   错误: {e.stderr.strip()}")
        if e.stdout:
            print(f"   输出: {e.stdout.strip()}")
        return not check_success

def main():
    print("🔧 Python截图服务修复工具\n")
    
    # 1. 升级pip
    run_command("python -m pip install --upgrade pip", "升级pip", False)
    
    # 2. 安装/升级依赖
    print("\n📦 安装依赖包...")
    dependencies = [
        "playwright==1.40.0",
        "playwright-stealth==1.0.6", 
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "aiofiles==23.2.1",
        "python-multipart==0.0.6",
        "aiohttp==3.9.1"
    ]
    
    for dep in dependencies:
        run_command(f"pip install {dep}", f"安装 {dep.split('==')[0]}", False)
    
    # 3. 安装Playwright浏览器
    print("\n🌐 安装Playwright浏览器...")
    run_command("playwright install chromium", "安装Chromium浏览器")
    
    # 4. 安装系统依赖（Linux/WSL）
    if os.name == 'posix':
        print("\n🔧 安装系统依赖...")
        run_command("playwright install-deps chromium", "安装系统依赖", False)
    
    # 5. 创建截图目录
    print("\n📁 创建截图目录...")
    os.makedirs("screenshots", exist_ok=True)
    print("✅ 截图目录已创建")
    
    # 6. 测试导入
    print("\n🧪 测试模块导入...")
    test_imports = [
        "playwright.async_api",
        "playwright_stealth", 
        "fastapi",
        "uvicorn"
    ]
    
    for module in test_imports:
        try:
            __import__(module)
            print(f"✅ {module} 导入成功")
        except ImportError as e:
            print(f"❌ {module} 导入失败: {e}")
    
    print(f"\n🎉 修复完成！")
    print(f"\n📋 下一步:")
    print(f"   1. 启动服务: python start.py")
    print(f"   2. 运行诊断: python diagnose.py") 
    print(f"   3. 快速测试: python quick_test.py")

if __name__ == "__main__":
    main()