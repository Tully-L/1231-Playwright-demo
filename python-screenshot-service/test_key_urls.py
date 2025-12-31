#!/usr/bin/env python3
"""
测试12文件夹中的关键URL - 重点测试有Cloudflare保护的网站
"""
import asyncio
import aiohttp
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

# 重点测试的URL（从12文件夹中提取的关键网站）
KEY_URLS = [
    # Python代码中成功抓取的
    {
        "url": "https://wavelifesciences.com/pipeline/research-and-development/",
        "name": "Wave Life Sciences",
        "note": "Python代码中成功抓取数据的网站"
    },
    {
        "url": "https://silence-therapeutics.com/our-pipeline/default.aspx",
        "name": "Silence Therapeutics", 
        "note": "可能有Cloudflare保护"
    },
    
    # 常见的制药公司管线页面
    {
        "url": "https://www.alnylam.com/alnylam-rnai-pipeline",
        "name": "Alnylam",
        "note": "RNAi领域知名公司"
    },
    {
        "url": "https://arrowheadpharma.com/pipeline/",
        "name": "Arrowhead Pharma",
        "note": "RNAi治疗公司"
    },
    {
        "url": "https://www.intelliatx.com/pipeline/",
        "name": "Intellia Therapeutics",
        "note": "CRISPR基因编辑公司"
    },
    {
        "url": "https://crisprtx.com/pipeline",
        "name": "CRISPR Therapeutics",
        "note": "CRISPR基因编辑公司"
    },
    {
        "url": "https://www.sarepta.com/products-pipeline/pipelinel",
        "name": "Sarepta Therapeutics",
        "note": "可能有反爬保护"
    }
]

async def check_service():
    """检查服务是否启动"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Python截图服务已启动")
                    print(f"   服务: {data.get('service')}")
                    print(f"   时间: {data.get('timestamp')}\n")
                    return True
    except Exception as e:
        pass
    
    print("❌ Python截图服务未启动")
    print("请先运行: cd python-screenshot-service && python start.py")
    return False

async def test_url(session, url_info, index, total):
    """测试单个URL"""
    url = url_info["url"]
    name = url_info["name"]
    note = url_info.get("note", "")
    
    print(f"[{index}/{total}] 📸 {name}")
    print(f"         URL: {url}")
    print(f"         备注: {note}")
    
    start_time = time.time()
    
    try:
        payload = {
            "url": url,
            "options": {"headless": True}
        }
        
        async with session.post(
            f"{API_BASE}/screenshot",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=180)  # 3分钟超时
        ) as response:
            data = await response.json()
            elapsed = time.time() - start_time
            
            if data.get("success"):
                filename = data.get("filename", "")
                print(f"         ✅ 成功 ({elapsed:.1f}s) - {filename}")
                return {
                    "name": name,
                    "url": url,
                    "success": True,
                    "filename": filename,
                    "elapsed": elapsed,
                    "note": note
                }
            else:
                error = data.get("error", "未知错误")
                print(f"         ❌ 失败 ({elapsed:.1f}s) - {error}")
                return {
                    "name": name,
                    "url": url,
                    "success": False,
                    "error": error,
                    "elapsed": elapsed,
                    "note": note
                }
                
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"         ⏰ 超时 ({elapsed:.1f}s)")
        return {
            "name": name,
            "url": url,
            "success": False,
            "error": "请求超时",
            "elapsed": elapsed,
            "note": note
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"         ❌ 异常 ({elapsed:.1f}s) - {str(e)}")
        return {
            "name": name,
            "url": url,
            "success": False,
            "error": str(e),
            "elapsed": elapsed,
            "note": note
        }

async def test_key_urls():
    """测试关键URL"""
    print(f"🧪 开始测试 {len(KEY_URLS)} 个关键URL\n")
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for i, url_info in enumerate(KEY_URLS):
            result = await test_url(session, url_info, i + 1, len(KEY_URLS))
            results.append(result)
            
            print()  # 空行分隔
            
            # 每个URL测试后等待2秒
            if i < len(KEY_URLS) - 1:
                print("⏳ 等待 2 秒...\n")
                await asyncio.sleep(2)
    
    return results

def generate_report(results):
    """生成测试报告"""
    total = len(results)
    success_count = sum(1 for r in results if r.get("success"))
    failed_count = total - success_count
    
    total_time = sum(r.get("elapsed", 0) for r in results)
    avg_time = total_time / total if total > 0 else 0
    
    print("="*80)
    print("📊 关键URL测试报告")
    print("="*80)
    print(f"总计: {total} 个网站")
    print(f"成功: {success_count} 个 ({success_count/total*100:.1f}%)")
    print(f"失败: {failed_count} 个 ({failed_count/total*100:.1f}%)")
    print(f"总耗时: {total_time:.1f}s")
    print(f"平均耗时: {avg_time:.1f}s")
    
    # 详细结果
    print(f"\n📋 详细结果:")
    for i, r in enumerate(results, 1):
        status = "✅" if r.get("success") else "❌"
        elapsed = r.get("elapsed", 0)
        print(f"{i:2d}. {status} {r['name']} ({elapsed:.1f}s)")
        if not r.get("success"):
            print(f"     错误: {r.get('error', '未知')}")
    
    # 成功截图的文件
    successful_files = [r for r in results if r.get("success") and r.get("filename")]
    if successful_files:
        print(f"\n📁 成功生成的截图文件:")
        for r in successful_files:
            print(f"   • {r['filename']} - {r['name']}")
    
    # 保存报告
    report_file = f"key_urls_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "success": success_count,
                "failed": failed_count,
                "success_rate": success_count/total*100 if total > 0 else 0,
                "total_time": total_time,
                "average_time": avg_time
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    
    # 给出建议
    print(f"\n💡 建议:")
    if success_count > 0:
        print(f"   • {success_count} 个网站截图成功，Python反检测方案有效")
    if failed_count > 0:
        print(f"   • {failed_count} 个网站失败，可能需要:")
        print(f"     - 增加更多反检测措施")
        print(f"     - 使用代理IP")
        print(f"     - 调整请求间隔")

async def main():
    print("🚀 测试12文件夹中的关键URL")
    print("🎯 重点验证Python反检测截图服务的效果\n")
    
    # 检查服务
    if not await check_service():
        return
    
    try:
        # 测试关键URL
        results = await test_key_urls()
        
        # 生成报告
        generate_report(results)
        
        print(f"\n🎉 测试完成！")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())