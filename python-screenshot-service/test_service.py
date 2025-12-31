#!/usr/bin/env python3
"""
测试脚本 - 测试Python截图服务
"""
import asyncio
import aiohttp
import json
import time

API_BASE = "http://localhost:8000"

async def test_health():
    """测试健康检查"""
    print("📋 健康检查...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE}/health") as response:
            data = await response.json()
            print(f"✅ 服务状态: {data}")
            return response.status == 200

async def test_single_screenshot():
    """测试单个URL截图"""
    print("\n📸 单个URL截图测试...")
    
    payload = {
        "url": "https://wavelifesciences.com/pipeline/research-and-development/",
        "options": {"headless": True}
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/screenshot",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=180)
        ) as response:
            data = await response.json()
            print(f"✅ 单个截图结果: {data}")
            return data.get("success", False)

async def test_batch_screenshots():
    """测试批量URL截图"""
    print("\n📸 批量URL截图测试...")
    
    payload = {
        "urls": [
            "https://www.alnylam.com/alnylam-rnai-pipeline",
            "https://arrowheadpharma.com/pipeline/"
        ],
        "options": {"headless": True}
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE}/screenshot/batch",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300)
        ) as response:
            data = await response.json()
            print(f"✅ 批量截图结果: {data}")
            return data.get("success", False)

async def test_list_screenshots():
    """测试获取截图列表"""
    print("\n📋 获取截图列表...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE}/screenshots") as response:
            data = await response.json()
            print(f"✅ 截图列表: {data}")
            return data.get("success", False)

async def check_service():
    """检查服务是否启动"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    print("✅ 服务已启动\n")
                    return True
    except Exception:
        pass
    
    print("❌ 服务未启动，请先运行: python main.py")
    return False

async def main():
    print("🧪 开始API测试\n")
    
    # 检查服务
    if not await check_service():
        return
    
    try:
        # 测试健康检查
        await test_health()
        
        # 测试单个截图
        await test_single_screenshot()
        
        # 测试批量截图
        await test_batch_screenshots()
        
        # 测试截图列表
        await test_list_screenshots()
        
        print("\n🎉 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())