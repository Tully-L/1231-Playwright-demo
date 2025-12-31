#!/usr/bin/env python3
"""
隔离问题 - 逐步测试每个组件
"""
import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_screenshot_service_directly():
    """直接测试截图服务"""
    print("1️⃣ 直接测试ScreenshotService类\n")
    
    try:
        from screenshot_service import ScreenshotService
        
        service = ScreenshotService("./screenshots")
        print("✅ 服务实例创建成功")
        
        # 测试简单URL
        print("\n📸 测试简单URL...")
        result1 = await service.take_screenshot("https://httpbin.org/html")
        print(f"结果1: success={result1.get('success')}, error='{result1.get('error', '')}'")
        
        # 测试目标URL
        print("\n📸 测试目标URL...")
        result2 = await service.take_screenshot("https://wavelifesciences.com/pipeline/research-and-development/")
        print(f"结果2: success={result2.get('success')}, error='{result2.get('error', '')}'")
        
        return result1, result2
        
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

async def test_fastapi_integration():
    """测试FastAPI集成"""
    print("\n2️⃣ 测试FastAPI集成\n")
    
    try:
        # 导入FastAPI应用
        from main import app, screenshot_service
        from fastapi.testclient import TestClient
        
        print("✅ FastAPI应用导入成功")
        
        # 创建测试客户端
        client = TestClient(app)
        
        # 测试健康检查
        print("\n🔍 测试健康检查...")
        health_response = client.get("/health")
        print(f"健康检查: {health_response.status_code} - {health_response.json()}")
        
        # 测试截图API
        print("\n📸 测试截图API...")
        screenshot_payload = {
            "url": "https://httpbin.org/html",
            "options": {"headless": True}
        }
        
        screenshot_response = client.post("/screenshot", json=screenshot_payload)
        print(f"截图API: {screenshot_response.status_code}")
        print(f"响应: {screenshot_response.json()}")
        
        return screenshot_response.json()
        
    except Exception as e:
        print(f"❌ FastAPI集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_async_context():
    """测试异步上下文问题"""
    print("\n3️⃣ 测试异步上下文\n")
    
    try:
        from screenshot_service import ScreenshotService
        
        # 在不同的异步上下文中测试
        service = ScreenshotService("./screenshots")
        
        async def wrapper():
            return await service.take_screenshot("https://httpbin.org/html")
        
        result = await wrapper()
        print(f"异步包装测试: success={result.get('success')}")
        
        return result
        
    except Exception as e:
        print(f"❌ 异步上下文测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("🔍 隔离问题诊断\n")
    
    # 1. 直接测试服务类
    result1, result2 = await test_screenshot_service_directly()
    
    # 2. 测试异步上下文
    result3 = await test_async_context()
    
    # 3. 测试FastAPI集成
    try:
        # 先安装testclient
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "httpx"], 
                      capture_output=True, check=True)
        
        result4 = await test_fastapi_integration()
    except Exception as e:
        print(f"⚠️ FastAPI测试跳过: {e}")
        result4 = None
    
    # 总结
    print("\n" + "="*60)
    print("📊 诊断总结")
    print("="*60)
    
    if result1 and result1.get('success'):
        print("✅ 直接调用服务类 - 简单URL成功")
    else:
        print("❌ 直接调用服务类 - 简单URL失败")
    
    if result2 and result2.get('success'):
        print("✅ 直接调用服务类 - 目标URL成功")
    else:
        print("❌ 直接调用服务类 - 目标URL失败")
    
    if result3 and result3.get('success'):
        print("✅ 异步上下文测试成功")
    else:
        print("❌ 异步上下文测试失败")
    
    if result4 and result4.get('success'):
        print("✅ FastAPI集成测试成功")
    else:
        print("❌ FastAPI集成测试失败")
    
    # 分析问题
    print(f"\n💡 问题分析:")
    if result1 and result1.get('success') and result2 and result2.get('success'):
        print("   • 截图服务类本身工作正常")
        if not (result4 and result4.get('success')):
            print("   • 问题可能在FastAPI集成层")
    else:
        print("   • 截图服务类本身有问题")
        if result1 and result1.get('success'):
            print("   • 简单URL可以，复杂URL不行 - 可能是网络或反爬问题")

if __name__ == "__main__":
    asyncio.run(main())