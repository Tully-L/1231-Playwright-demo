#!/usr/bin/env python3
"""
重启并测试服务
"""
import asyncio
import aiohttp
import subprocess
import time
import sys
import os

API_BASE = "http://localhost:8000"

async def wait_for_service(max_wait=30):
    """等待服务启动"""
    print("⏳ 等待服务启动...")
    
    for i in range(max_wait):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_BASE}/health",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    if response.status == 200:
                        print(f"✅ 服务已启动 ({i+1}s)")
                        return True
        except:
            pass
        
        await asyncio.sleep(1)
    
    print(f"❌ 服务启动超时 ({max_wait}s)")
    return False

async def test_api_after_restart():
    """重启后测试API"""
    print("🧪 测试修复后的API\n")
    
    test_url = "https://wavelifesciences.com/pipeline/research-and-development/"
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "url": test_url,
                "options": {"headless": True}
            }
            
            print(f"📸 测试截图: {test_url}")
            
            async with session.post(
                f"{API_BASE}/screenshot",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                data = await response.json()
                
                print(f"📥 响应状态: {response.status}")
                print(f"📄 响应内容:")
                
                if data.get("success"):
                    print(f"   ✅ 截图成功!")
                    print(f"   📁 文件: {data.get('filename')}")
                    print(f"   📍 路径: {data.get('path')}")
                    return True
                else:
                    print(f"   ❌ 截图失败")
                    print(f"   🔍 错误: {data.get('error', '无错误信息')}")
                    return False
                    
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def start_service_in_background():
    """在后台启动服务"""
    print("🚀 启动服务...")
    
    try:
        # 启动服务进程
        process = subprocess.Popen(
            [sys.executable, "start.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        print(f"✅ 服务进程已启动 (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        return None

async def main():
    print("🔄 重启并测试Python截图服务\n")
    
    # 启动服务
    process = start_service_in_background()
    
    if not process:
        print("❌ 无法启动服务")
        return
    
    try:
        # 等待服务启动
        if await wait_for_service():
            # 测试API
            success = await test_api_after_restart()
            
            if success:
                print("\n🎉 API修复成功！现在可以正常截图了")
                print("\n💡 可以运行完整测试:")
                print("   python quick_test.py")
                print("   python test_key_urls.py")
            else:
                print("\n❌ API仍有问题，需要进一步调试")
        else:
            print("❌ 服务启动失败")
            
    finally:
        # 清理进程
        if process:
            print(f"\n🛑 停止服务进程 (PID: {process.pid})")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    asyncio.run(main())