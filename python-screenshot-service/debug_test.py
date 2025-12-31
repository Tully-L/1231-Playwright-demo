#!/usr/bin/env python3
"""
调试测试 - 获取详细错误信息
"""
import asyncio
import aiohttp
import json

API_BASE = "http://localhost:8000"

async def debug_screenshot_request():
    """调试截图请求"""
    print("🔍 调试截图请求\n")
    
    test_url = "https://wavelifesciences.com/pipeline/research-and-development/"
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "url": test_url,
                "options": {"headless": True}
            }
            
            print(f"📤 发送请求:")
            print(f"   URL: {API_BASE}/screenshot")
            print(f"   Payload: {json.dumps(payload, indent=2)}")
            
            async with session.post(
                f"{API_BASE}/screenshot",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                print(f"\n📥 响应状态: {response.status}")
                print(f"   响应头: {dict(response.headers)}")
                
                # 获取响应内容
                try:
                    data = await response.json()
                    print(f"\n📄 响应内容:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except Exception as e:
                    text = await response.text()
                    print(f"\n📄 响应文本: {text}")
                    print(f"   JSON解析失败: {e}")
                
                return data if 'data' in locals() else None
                
    except aiohttp.ClientConnectorError as e:
        print(f"❌ 连接错误: {e}")
        print("💡 请确保服务已启动: python start.py")
        return None
    except asyncio.TimeoutError:
        print("❌ 请求超时")
        return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return None

async def check_service_health():
    """检查服务健康状态"""
    print("🔍 检查服务健康状态\n")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                print(f"📥 健康检查响应: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 服务正常运行")
                    print(f"   服务: {data.get('service')}")
                    print(f"   时间: {data.get('timestamp')}")
                    return True
                else:
                    print(f"❌ 服务响应异常: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

async def test_direct_screenshot():
    """直接测试截图服务类"""
    print("🔍 直接测试截图服务类\n")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from screenshot_service import ScreenshotService
        
        service = ScreenshotService("./screenshots")
        
        print("📸 直接调用截图服务...")
        result = await service.take_screenshot(
            "https://wavelifesciences.com/pipeline/research-and-development/",
            {"headless": True}
        )
        
        print(f"\n📄 直接调用结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("🚀 调试Python截图服务\n")
    
    # 1. 检查服务健康状态
    health_ok = await check_service_health()
    
    if health_ok:
        print("\n" + "="*50)
        
        # 2. 测试API请求
        print("2️⃣ 测试API请求")
        api_result = await debug_screenshot_request()
        
        print("\n" + "="*50)
        
        # 3. 直接测试服务类
        print("3️⃣ 直接测试服务类")
        direct_result = await test_direct_screenshot()
        
        print("\n" + "="*50)
        print("📊 调试总结")
        
        if api_result and api_result.get("success"):
            print("✅ API请求成功")
        else:
            print("❌ API请求失败")
            
        if direct_result and direct_result.get("success"):
            print("✅ 直接调用成功")
        else:
            print("❌ 直接调用失败")
            
    else:
        print("❌ 服务未正常运行，请检查服务启动状态")

if __name__ == "__main__":
    asyncio.run(main())