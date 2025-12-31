#!/usr/bin/env python3
"""
测试12文件夹中发现的所有URL
"""
import asyncio
import aiohttp
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

# 从12文件夹代码中提取的所有URL
URLS_TO_TEST = [
    # Python文件中的URL
    "https://wavelifesciences.com/pipeline/research-and-development/",
    "https://silence-therapeutics.com/our-pipeline/default.aspx",
    
    # JavaScript文件中的URL
    "https://www.alnylam.com/alnylam-rnai-pipeline",
    "https://arrowheadpharma.com/pipeline/",
    "https://ionis.com/pipeline/independent?_format=json",
    "https://www.aviditybiosciences.com/pipeline/pipeline-overview",
    "https://www.lilly.com/innovation/clinical-development-pipeline",
    "https://www.novonordisk.com/science-and-technology/r-d-pipeline.html",
    "https://www.novartis.com/research-development/novartis-pipeline",
    "https://www.regeneron.com/science/investigational-pipeline",
    "https://www.dyne-tx.com/pipeline/",
    "https://www.denalitherapeutics.com/pipeline",
    "https://www.adarx.com/pipeline/",
    "https://www.ribolia.com/pipeline",
    "https://www.intelliatx.com/pipeline/",
    "https://beamtx.com/pipeline/",
    "https://www.astrazeneca.com/our-therapy-areas/pipeline.html",
    "https://www.roche.com/solutions/pipeline",
    "https://www.atalantatx.com/pipeline/",
    "https://www.sarepta.com/products-pipeline/pipelinel",
    "https://www.ronatherapeutics.com/pipeline",
    "https://crisprtx.com/pipeline",
    "https://olixpharma.com/rnd/rnd03.php",
    "https://www.entradatx.com/pipeline",
    "https://www.pepgen.com/pipeline/",
    "https://tangramtx.com/pipeline/",
    "https://www.switchthera.com/our-science/",
    "https://www.arobiotx.com/pipeline",
    "https://www.sirnaomics.com/cn/science-pipeline/pipeline/",
    "https://www.sanegenebio.com/pipeline/",
    "https://www.siriusrna.com/pipeline/index.html#pipeline",
    "https://synerk.cn/productinfo/883480.html",
    "https://aligos.com/science/scientific-overview/",
    "https://www.arbutusbio.com/pipeline/",
    "https://www.proqr.com/pipeline",
    "https://metagenomi.co/pipeline",
    "https://www.camp4tx.com/pipeline/",
    "https://minatx.com/pipeline/",
    "https://www.ractigen.com/pipeline/",
    "https://judo.bio/pipeline/",
    "https://www.rigerna.com/page/cpgx/",
    "https://www.siranbio.com/page/cpgx/",
    "https://www.visirna.com/pages/client/pplinea?version=v1",
    "https://www.hygieiapharma.com/Pipeline/3.html"
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
                    print("✅ Python截图服务已启动\n")
                    return True
    except Exception:
        pass
    
    print("❌ Python截图服务未启动")
    print("请先运行: cd python-screenshot-service && python start.py")
    return False

async def test_single_url(session, url, index, total):
    """测试单个URL"""
    print(f"[{index}/{total}] 📸 测试: {url}")
    
    start_time = time.time()
    
    try:
        payload = {
            "url": url,
            "options": {"headless": True}
        }
        
        async with session.post(
            f"{API_BASE}/screenshot",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)  # 2分钟超时
        ) as response:
            data = await response.json()
            elapsed = time.time() - start_time
            
            if data.get("success"):
                print(f"  ✅ 成功 ({elapsed:.1f}s) - {data.get('filename')}")
                return {
                    "url": url,
                    "success": True,
                    "filename": data.get("filename"),
                    "elapsed": elapsed
                }
            else:
                print(f"  ❌ 失败 ({elapsed:.1f}s) - {data.get('error', '未知错误')}")
                return {
                    "url": url,
                    "success": False,
                    "error": data.get("error", "未知错误"),
                    "elapsed": elapsed
                }
                
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"  ⏰ 超时 ({elapsed:.1f}s)")
        return {
            "url": url,
            "success": False,
            "error": "请求超时",
            "elapsed": elapsed
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  ❌ 异常 ({elapsed:.1f}s) - {str(e)}")
        return {
            "url": url,
            "success": False,
            "error": str(e),
            "elapsed": elapsed
        }

async def test_batch_urls(batch_size=5):
    """批量测试URL"""
    print(f"🧪 开始测试 {len(URLS_TO_TEST)} 个URL (批量大小: {batch_size})\n")
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        # 分批处理
        for i in range(0, len(URLS_TO_TEST), batch_size):
            batch = URLS_TO_TEST[i:i + batch_size]
            batch_start = time.time()
            
            print(f"\n📦 批次 {i//batch_size + 1}: 处理 {len(batch)} 个URL")
            
            # 并发处理当前批次
            tasks = []
            for j, url in enumerate(batch):
                task = test_single_url(session, url, i + j + 1, len(URLS_TO_TEST))
                tasks.append(task)
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append({
                        "url": "unknown",
                        "success": False,
                        "error": str(result),
                        "elapsed": 0
                    })
                else:
                    results.append(result)
            
            batch_elapsed = time.time() - batch_start
            success_count = sum(1 for r in batch_results if not isinstance(r, Exception) and r.get("success"))
            
            print(f"  📊 批次完成: {success_count}/{len(batch)} 成功 ({batch_elapsed:.1f}s)")
            
            # 批次间隔
            if i + batch_size < len(URLS_TO_TEST):
                print("  ⏳ 等待 3 秒...")
                await asyncio.sleep(3)
    
    return results

def generate_report(results):
    """生成测试报告"""
    total = len(results)
    success_count = sum(1 for r in results if r.get("success"))
    failed_count = total - success_count
    
    total_time = sum(r.get("elapsed", 0) for r in results)
    avg_time = total_time / total if total > 0 else 0
    
    print(f"\n" + "="*60)
    print(f"📊 测试报告")
    print(f"="*60)
    print(f"总计URL: {total}")
    print(f"成功: {success_count} ({success_count/total*100:.1f}%)")
    print(f"失败: {failed_count} ({failed_count/total*100:.1f}%)")
    print(f"总耗时: {total_time:.1f}s")
    print(f"平均耗时: {avg_time:.1f}s")
    
    # 成功的URL
    if success_count > 0:
        print(f"\n✅ 成功的URL ({success_count}个):")
        for r in results:
            if r.get("success"):
                print(f"  • {r['url']} ({r.get('elapsed', 0):.1f}s)")
    
    # 失败的URL
    if failed_count > 0:
        print(f"\n❌ 失败的URL ({failed_count}个):")
        for r in results:
            if not r.get("success"):
                error = r.get("error", "未知错误")
                print(f"  • {r['url']} - {error}")
    
    # 保存详细报告
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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

async def main():
    print("🚀 开始测试12文件夹中的所有URL\n")
    
    # 检查服务
    if not await check_service():
        return
    
    try:
        # 批量测试
        results = await test_batch_urls(batch_size=3)  # 减小批量大小避免过载
        
        # 生成报告
        generate_report(results)
        
        print(f"\n🎉 测试完成！")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())