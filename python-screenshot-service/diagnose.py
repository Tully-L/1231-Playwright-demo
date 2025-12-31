#!/usr/bin/env python3
"""
诊断脚本 - 检查Python截图服务的问题
"""
import sys
import subprocess
import importlib
import os
import asyncio
import aiohttp

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    print(f"   Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("   ❌ 需要Python 3.8或更高版本")
        return False
    else:
        print("   ✅ Python版本符合要求")
        return True

def check_dependencies():
    """检查依赖包"""
    print("\n🔍 检查依赖包...")
    
    required_packages = [
        'playwright',
        'playwright_stealth', 
        'fastapi',
        'uvicorn',
        'pydantic',
        'aiofiles'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 安装缺失的包:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_playwright_browsers():
    """检查Playwright浏览器"""
    print("\n🔍 检查Playwright浏览器...")
    
    try:
        result = subprocess.run(
            ['playwright', 'install', '--dry-run'], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if 'chromium' in result.stdout.lower():
            print("   ⚠️ Chromium浏览器可能未安装")
            print("   💡 运行: playwright install chromium")
            return False
        else:
            print("   ✅ Playwright浏览器已安装")
            return True
            
    except subprocess.TimeoutExpired:
        print("   ⚠️ 检查超时")
        return False
    except FileNotFoundError:
        print("   ❌ playwright命令未找到")
        print("   💡 先安装: pip install playwright")
        return False
    except Exception as e:
        print(f"   ⚠️ 检查异常: {e}")
        return False

async def check_service_startup():
    """检查服务启动"""
    print("\n🔍 检查服务启动...")
    
    try:
        # 尝试导入主模块
        sys.path.insert(0, '.')
        import main
        print("   ✅ main.py 可以正常导入")
        
        # 检查FastAPI应用
        if hasattr(main, 'app'):
            print("   ✅ FastAPI应用已创建")
        else:
            print("   ❌ FastAPI应用未找到")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        return False

async def check_service_connection():
    """检查服务连接"""
    print("\n🔍 检查服务连接...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'http://localhost:8000/health',
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ 服务正常运行")
                    print(f"      服务: {data.get('service')}")
                    return True
                else:
                    print(f"   ❌ 服务响应异常: {response.status}")
                    return False
                    
    except aiohttp.ClientConnectorError:
        print("   ❌ 无法连接到服务 (端口8000)")
        print("   💡 请确保服务已启动: python start.py")
        return False
    except Exception as e:
        print(f"   ❌ 连接异常: {e}")
        return False

def check_file_structure():
    """检查文件结构"""
    print("\n🔍 检查文件结构...")
    
    required_files = [
        'main.py',
        'screenshot_service.py', 
        'requirements.txt',
        'start.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - 文件不存在")
            missing_files.append(file)
    
    return len(missing_files) == 0

async def test_simple_screenshot():
    """测试简单截图"""
    print("\n🔍 测试简单截图...")
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "url": "https://httpbin.org/html",
                "options": {"headless": True}
            }
            
            async with session.post(
                'http://localhost:8000/screenshot',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                data = await response.json()
                
                if data.get('success'):
                    print("   ✅ 简单截图测试成功")
                    print(f"      文件: {data.get('filename')}")
                    return True
                else:
                    print(f"   ❌ 截图失败: {data.get('error')}")
                    return False
                    
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")
        return False

async def main():
    print("🚀 Python截图服务诊断工具\n")
    
    issues = []
    
    # 1. 检查Python版本
    if not check_python_version():
        issues.append("Python版本过低")
    
    # 2. 检查依赖包
    if not check_dependencies():
        issues.append("缺少依赖包")
    
    # 3. 检查文件结构
    if not check_file_structure():
        issues.append("文件结构不完整")
    
    # 4. 检查Playwright浏览器
    if not check_playwright_browsers():
        issues.append("Playwright浏览器未安装")
    
    # 5. 检查服务启动
    if not await check_service_startup():
        issues.append("服务启动异常")
    
    # 6. 检查服务连接
    service_running = await check_service_connection()
    if not service_running:
        issues.append("服务未运行")
    
    # 7. 如果服务运行，测试截图
    if service_running:
        if not await test_simple_screenshot():
            issues.append("截图功能异常")
    
    # 总结
    print("\n" + "="*60)
    print("📊 诊断结果")
    print("="*60)
    
    if not issues:
        print("🎉 所有检查通过！服务应该正常工作")
    else:
        print(f"❌ 发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n💡 修复建议:")
        if "缺少依赖包" in issues:
            print("   • 运行: python install.py")
        if "Playwright浏览器未安装" in issues:
            print("   • 运行: playwright install chromium")
        if "服务未运行" in issues:
            print("   • 运行: python start.py")
        if "截图功能异常" in issues:
            print("   • 检查防火墙和网络连接")
            print("   • 查看服务日志输出")

if __name__ == "__main__":
    asyncio.run(main())