#!/usr/bin/env python3
"""
简单测试 - 验证基本功能
"""
import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试基本功能\n")
    
    try:
        # 1. 测试导入
        print("1️⃣ 测试模块导入...")
        
        try:
            from playwright.async_api import async_playwright
            print("   ✅ playwright导入成功")
        except ImportError as e:
            print(f"   ❌ playwright导入失败: {e}")
            return False
        
        try:
            from playwright_stealth import stealth_async
            print("   ✅ playwright_stealth导入成功")
        except ImportError as e:
            print(f"   ❌ playwright_stealth导入失败: {e}")
            print("   💡 运行: pip install playwright-stealth")
            return False
        
        try:
            import fastapi
            print("   ✅ fastapi导入成功")
        except ImportError as e:
            print(f"   ❌ fastapi导入失败: {e}")
            return False
        
        # 2. 测试Playwright启动
        print("\n2️⃣ 测试Playwright启动...")
        
        playwright = await async_playwright().start()
        print("   ✅ Playwright启动成功")
        
        browser = await playwright.chromium.launch(headless=True)
        print("   ✅ 浏览器启动成功")
        
        context = await browser.new_context()
        print("   ✅ 浏览器上下文创建成功")
        
        page = await context.new_page()
        print("   ✅ 页面创建成功")
        
        # 3. 测试简单页面访问
        print("\n3️⃣ 测试页面访问...")
        
        await page.goto("https://httpbin.org/html", timeout=30000)
        print("   ✅ 页面访问成功")
        
        title = await page.title()
        print(f"   页面标题: {title}")
        
        # 4. 测试截图
        print("\n4️⃣ 测试截图功能...")
        
        screenshot_path = "test_screenshot.png"
        await page.screenshot(path=screenshot_path)
        
        if os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            print(f"   ✅ 截图成功: {screenshot_path} ({file_size} bytes)")
            
            # 清理测试文件
            os.remove(screenshot_path)
            print("   🧹 测试文件已清理")
        else:
            print("   ❌ 截图文件未生成")
            return False
        
        # 5. 清理资源
        print("\n5️⃣ 清理资源...")
        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()
        print("   ✅ 资源清理完成")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_screenshot_service():
    """测试截图服务类"""
    print("\n🧪 测试截图服务类\n")
    
    try:
        from screenshot_service import ScreenshotService
        print("✅ ScreenshotService导入成功")
        
        # 创建服务实例
        service = ScreenshotService("./screenshots")
        print("✅ 服务实例创建成功")
        
        # 测试简单截图
        print("\n📸 测试简单截图...")
        result = await service.take_screenshot("https://httpbin.org/html")
        
        if result.get("success"):
            print(f"✅ 截图成功: {result.get('filename')}")
            return True
        else:
            print(f"❌ 截图失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Python截图服务简单测试\n")
    
    # 测试基本功能
    basic_ok = await test_basic_functionality()
    
    if basic_ok:
        print("\n" + "="*50)
        print("🎉 基本功能测试通过！")
        
        # 测试服务类
        service_ok = await test_screenshot_service()
        
        if service_ok:
            print("\n🎉 截图服务测试通过！")
            print("\n💡 下一步:")
            print("   • 启动服务: python start.py")
            print("   • 运行API测试: python quick_test.py")
        else:
            print("\n❌ 截图服务测试失败")
    else:
        print("\n❌ 基本功能测试失败")
        print("\n💡 修复建议:")
        print("   • 运行修复脚本: python fix_service.py")
        print("   • 手动安装依赖: pip install -r requirements.txt")
        print("   • 安装浏览器: playwright install chromium")

if __name__ == "__main__":
    asyncio.run(main())