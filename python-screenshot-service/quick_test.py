#!/usr/bin/env python3
"""
快速测试脚本 - 测试几个关键URL验证服务效果
"""
import asyncio
import aiohttp
import time

API_BASE = "http://localhost:8000"

# 快速测试的URL（从12文件夹中选择的最重要的几个）
QUICK_TEST_URLS = [
    {
        "url": "https://wavelifesciences.com/pipeline/research-and-development/",
        "name": "Wave Life Sciences",
        "reason": "12文件夹Python代码成功抓取的网站"
    },
    {
        "url": "https://www.alnylam.com/alnylam-rnai-pipeline", 
        "name": "Alnylam",
        "reason": "RNAi领域知名公司，可能有反爬保护"
    },
    {
        "url": "https://crisprtx.com/pipeline",
        "name": "CRISPR Therapeutics", 
        "reason": "基因编辑公司，测试反检测效果"
    }
]

async def check_service():
    """检查服务状态"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE}/health", timeout=aiohttp.ClientTimeout(total=3)) as response:
                if response.status == 200:
                    return True
    except:
        pass
    return False

async def quick_screenshot(url_info):
    """快速截图测试"""
    url = url_info["url"]
    name = url_info["name"]
    
    print(f"📸 测试 {name}...")
    print(f"   URL: {url}")
    
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"url": url, "options": {"headless": True}}
            
            async with session.post(
                f"{API_BASE}/screenshot",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=90)
            ) as response:
                data = await response.json()
                elapsed = time.time() - start_time
                
                if data.get("success"):
                    print(f"   ✅ 成功 ({elapsed:.1f}s) - {data.get('filename')}")
                    return True
                else:
                    print(f"   ❌ 失败 ({elapsed:.1f}s) - {data.get('error')}")
                    return False
                    
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ 异常 ({elapsed:.1f}s) - {str(e)}")
        return False

async def main():
    print("🚀 快速测试Python截图服务")
    print("🎯 验证12文件夹URL的截图效果\n")
    
    # 检查服务
    if not await check_service():
        print("❌ 服务未启动，请先运行:")
        print("   cd python-screenshot-service")
        print("   python start.py")
        return
    
    print("✅ 服务已启动，开始测试...\n")
    
    success_count = 0
    
    for i, url_info in enumerate(QUICK_TEST_URLS, 1):
        print(f"[{i}/{len(QUICK_TEST_URLS)}]", end=" ")
        
        if await quick_screenshot(url_info):
            success_count += 1
        
        print(f"   原因: {url_info['reason']}")
        print()
        
        # 测试间隔
        if i < len(QUICK_TEST_URLS):
            await asyncio.sleep(2)
    
    # 结果总结
    total = len(QUICK_TEST_URLS)
    print("="*50)
    print(f"📊 快速测试结果: {success_count}/{total} 成功")
    
    if success_count == total:
        print("🎉 所有测试通过！Python反检测截图服务工作正常")
    elif success_count > 0:
        print(f"⚠️ 部分成功，{success_count}个网站截图成功")
    else:
        print("❌ 所有测试失败，请检查服务配置")
    
    print("\n💡 如需完整测试，运行:")
    print("   python test_key_urls.py")

if __name__ == "__main__":
    asyncio.run(main())