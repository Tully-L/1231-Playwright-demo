#!/usr/bin/env python3
"""
强制重启并测试 - 确保服务重新加载
"""
import asyncio
import aiohttp
import subprocess
import time
import sys
import os
import signal
import psutil

API_BASE = "http://localhost:8000"

def kill_existing_services():
    """杀死现有的服务进程"""
    print("🔍 查找现有服务进程...")
    
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('start.py' in cmd or 'main.py' in cmd for cmd in cmdline):
                if any('python' in cmd for cmd in cmdline):
                    print(f"🔪 终止进程: PID {proc.info['pid']} - {' '.join(cmdline)}")
                    proc.terminate()
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if killed_count > 0:
        print(f"✅ 终止了 {killed_count} 个进程")
        time.sleep(2)  # 等待进程完全终止
    else:
        print("ℹ️ 没有找到现有服务进程")

async def wait_for_service_down(max_wait=10):
    """等待服务完全停止"""
    print("⏳ 等待服务停止...")
    
    for i in range(max_wait):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_BASE}/health",
                    timeout=aiohttp.ClientTimeout(total=1)
                ) as response:
                    pass  # 如果能连接，说明服务还在运行
        except:
            print(f"✅ 服务已停止")
            return True
        
        await asyncio.sleep(1)
    
    print("⚠️ 服务可能仍在运行")
    return False

async def wait_for_service_up(max_wait=30):
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

def start_fresh_service():
    """启动全新的服务"""
    print("🚀 启动全新服务...")
    
    try:
        # 使用新的Python进程启动服务
        process = subprocess.Popen(
            [sys.executable, "-c", """
import uvicorn
from main import app
uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
"""],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        print(f"✅ 新服务进程已启动 (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        return None

async def test_fixed_api():
    """测试修复后的API"""
    print("🧪 测试修复后的API\n")
    
    test_cases = [
        {
            "name": "简单测试",
            "url": "https://httpbin.org/html"
        },
        {
            "name": "Wave Life Sciences",
            "url": "https://wavelifesciences.com/pipeline/research-and-development/"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] 📸 {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "url": test_case['url'],
                    "options": {"headless": True}
                }
                
                async with session.post(
                    f"{API_BASE}/screenshot",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=90)
                ) as response:
                    data = await response.json()
                    
                    if data.get("success"):
                        print(f"   ✅ 成功 - {data.get('filename')}")
                        results.append(True)
                    else:
                        print(f"   ❌ 失败 - {data.get('error', '无错误信息')}")
                        results.append(False)
                        
        except Exception as e:
            print(f"   ❌ 异常 - {e}")
            results.append(False)
        
        print()
    
    return results

async def main():
    print("🔄 强制重启Python截图服务\n")
    
    # 1. 杀死现有服务
    kill_existing_services()
    
    # 2. 等待服务停止
    await wait_for_service_down()
    
    # 3. 启动新服务
    process = start_fresh_service()
    
    if not process:
        print("❌ 无法启动服务")
        return
    
    try:
        # 4. 等待服务启动
        if await wait_for_service_up():
            print("\n" + "="*50)
            
            # 5. 测试API
            results = await test_fixed_api()
            
            success_count = sum(results)
            total_count = len(results)
            
            print("="*50)
            print(f"📊 测试结果: {success_count}/{total_count} 成功")
            
            if success_count == total_count:
                print("🎉 所有测试通过！服务修复成功")
                print("\n💡 现在可以运行完整测试:")
                print("   python test_key_urls.py")
                print("   python test_urls_from_12_folder.py")
            elif success_count > 0:
                print("⚠️ 部分测试通过，服务基本正常")
            else:
                print("❌ 所有测试失败，需要进一步调试")
        else:
            print("❌ 服务启动失败")
            
    finally:
        # 6. 清理进程
        if process:
            print(f"\n🛑 停止服务进程 (PID: {process.pid})")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    # 安装psutil如果没有
    try:
        import psutil
    except ImportError:
        print("📦 安装psutil...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)
        import psutil
    
    asyncio.run(main())