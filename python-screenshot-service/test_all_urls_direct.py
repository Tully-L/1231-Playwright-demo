#!/usr/bin/env python3
"""
测试所有44个URL - 直接调用截图服务
"""
import asyncio
import sys
import os
import time
import json
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 从12文件夹中提取的所有44个URL
ALL_URLS = [
    # Python文件中的URL
    {"name": "Wave Life Sciences", "url": "https://wavelifesciences.com/pipeline/research-and-development/"},
    {"name": "Silence Therapeutics", "url": "https://silence-therapeutics.com/our-pipeline/default.aspx"},
    
    # JavaScript文件中的URL
    {"name": "Alnylam", "url": "https://www.alnylam.com/alnylam-rnai-pipeline"},
    {"name": "Arrowhead Pharma", "url": "https://arrowheadpharma.com/pipeline/"},
    {"name": "Ionis", "url": "https://ionis.com/pipeline/independent?_format=json"},
    {"name": "Avidity Biosciences", "url": "https://www.aviditybiosciences.com/pipeline/pipeline-overview"},
    {"name": "Lilly", "url": "https://www.lilly.com/innovation/clinical-development-pipeline"},
    {"name": "Novo Nordisk", "url": "https://www.novonordisk.com/science-and-technology/r-d-pipeline.html"},
    {"name": "Novartis", "url": "https://www.novartis.com/research-development/novartis-pipeline"},
    {"name": "Regeneron", "url": "https://www.regeneron.com/science/investigational-pipeline"},
    {"name": "Dyne Therapeutics", "url": "https://www.dyne-tx.com/pipeline/"},
    {"name": "Denali Therapeutics", "url": "https://www.denalitherapeutics.com/pipeline"},
    {"name": "Adarx", "url": "https://www.adarx.com/pipeline/"},
    {"name": "Ribolia", "url": "https://www.ribolia.com/pipeline"},
    {"name": "Intellia Therapeutics", "url": "https://www.intelliatx.com/pipeline/"},
    {"name": "Beam Therapeutics", "url": "https://beamtx.com/pipeline/"},
    {"name": "AstraZeneca", "url": "https://www.astrazeneca.com/our-therapy-areas/pipeline.html"},
    {"name": "Roche", "url": "https://www.roche.com/solutions/pipeline"},
    {"name": "Atalanta Therapeutics", "url": "https://www.atalantatx.com/pipeline/"},
    {"name": "Sarepta", "url": "https://www.sarepta.com/products-pipeline/pipelinel"},
    {"name": "Rona Therapeutics", "url": "https://www.ronatherapeutics.com/pipeline"},
    {"name": "CRISPR Therapeutics", "url": "https://crisprtx.com/pipeline"},
    {"name": "Olix Pharma", "url": "https://olixpharma.com/rnd/rnd03.php"},
    {"name": "Entrada Therapeutics", "url": "https://www.entradatx.com/pipeline"},
    {"name": "PepGen", "url": "https://www.pepgen.com/pipeline/"},
    {"name": "Tangram Therapeutics", "url": "https://tangramtx.com/pipeline/"},
    {"name": "Switch Therapeutics", "url": "https://www.switchthera.com/our-science/"},
    {"name": "Arobic Therapeutics", "url": "https://www.arobiotx.com/pipeline"},
    {"name": "SiRNA Omics", "url": "https://www.sirnaomics.com/cn/science-pipeline/pipeline/"},
    {"name": "Sanegene Bio", "url": "https://www.sanegenebio.com/pipeline/"},
    {"name": "Sirius RNA", "url": "https://www.siriusrna.com/pipeline/index.html#pipeline"},
    {"name": "Synerk", "url": "https://synerk.cn/productinfo/883480.html"},
    {"name": "Aligos", "url": "https://aligos.com/science/scientific-overview/"},
    {"name": "Arbutus Bio", "url": "https://www.arbutusbio.com/pipeline/"},
    {"name": "ProQR", "url": "https://www.proqr.com/pipeline"},
    {"name": "Metagenomi", "url": "https://metagenomi.co/pipeline"},
    {"name": "Camp4 Therapeutics", "url": "https://www.camp4tx.com/pipeline/"},
    {"name": "Mina Therapeutics", "url": "https://minatx.com/pipeline/"},
    {"name": "Ractigen", "url": "https://www.ractigen.com/pipeline/"},
    {"name": "Judo Bio", "url": "https://judo.bio/pipeline/"},
    {"name": "Rigerna", "url": "https://www.rigerna.com/page/cpgx/"},
    {"name": "Siran Bio", "url": "https://www.siranbio.com/page/cpgx/"},
    {"name": "VisiRNA", "url": "https://www.visirna.com/pages/client/pplinea?version=v1"},
    {"name": "Hygeia Pharma", "url": "https://www.hygieiapharma.com/Pipeline/3.html"}
]

async def test_single_url(service, url_info, index, total):
    """测试单个URL"""
    name = url_info["name"]
    url = url_info["url"]
    
    print(f"[{index:2d}/{total}] 📸 {name}")
    print(f"           URL: {url}")
    
    start_time = time.time()
    
    try:
        # 直接调用截图服务
        result = await service.take_screenshot(url, {"headless": True})
        elapsed = time.time() - start_time
        
        if result.get("success"):
            filename = result.get("filename", "")
            print(f"           ✅ 成功 ({elapsed:.1f}s) - {filename}")
            return {
                "name": name,
                "url": url,
                "success": True,
                "filename": filename,
                "elapsed": elapsed
            }
        else:
            error = result.get("error", "未知错误")
            print(f"           ❌ 失败 ({elapsed:.1f}s) - {error}")
            return {
                "name": name,
                "url": url,
                "success": False,
                "error": error,
                "elapsed": elapsed
            }
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"           ❌ 异常 ({elapsed:.1f}s) - {str(e)}")
        return {
            "name": name,
            "url": url,
            "success": False,
            "error": str(e),
            "elapsed": elapsed
        }

async def test_all_urls():
    """测试所有URL"""
    print("🚀 测试所有44个URL - 直接调用截图服务")
    print("🎯 验证Python反检测方案的完整效果\n")
    
    try:
        from screenshot_service import ScreenshotService
        
        # 创建服务实例
        service = ScreenshotService("./screenshots")
        print("✅ 截图服务实例创建成功")
        
        # 先测试简单URL验证服务正常
        print("\n🧪 验证服务正常...")
        simple_result = await service.take_screenshot("https://httpbin.org/html")
        
        if not simple_result.get("success"):
            print(f"❌ 服务验证失败: {simple_result.get('error')}")
            return
        
        print("✅ 服务验证成功，开始批量测试\n")
        
    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        return
    
    print("="*80)
    print("📸 开始批量截图测试")
    print("="*80)
    
    results = []
    batch_size = 5  # 每批处理5个
    
    for i in range(0, len(ALL_URLS), batch_size):
        batch = ALL_URLS[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(ALL_URLS) + batch_size - 1) // batch_size
        
        print(f"\n📦 批次 {batch_num}/{total_batches}: 处理 {len(batch)} 个URL")
        print("-" * 60)
        
        batch_start = time.time()
        
        for j, url_info in enumerate(batch):
            result = await test_single_url(service, url_info, i + j + 1, len(ALL_URLS))
            results.append(result)
            
            # 每个URL之间等待1秒
            if j < len(batch) - 1:
                await asyncio.sleep(1)
        
        batch_elapsed = time.time() - batch_start
        success_in_batch = sum(1 for r in batch if results[i + batch.index(r)].get("success"))
        
        print(f"\n📊 批次 {batch_num} 完成: {success_in_batch}/{len(batch)} 成功 ({batch_elapsed:.1f}s)")
        
        # 批次间等待3秒
        if i + batch_size < len(ALL_URLS):
            print("⏳ 批次间等待 3 秒...\n")
            await asyncio.sleep(3)
    
    # 生成最终报告
    generate_final_report(results)

def generate_final_report(results):
    """生成最终报告"""
    total = len(results)
    success_count = sum(1 for r in results if r.get("success"))
    failed_count = total - success_count
    
    total_time = sum(r.get("elapsed", 0) for r in results)
    avg_time = total_time / total if total > 0 else 0
    
    print("\n" + "="*80)
    print("📊 完整测试报告 - Python反检测截图服务")
    print("="*80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总计网站: {total}")
    print(f"成功截图: {success_count} 个")
    print(f"失败截图: {failed_count} 个")
    print(f"成功率: {success_count/total*100:.1f}%")
    print(f"总耗时: {total_time:.1f}s ({total_time/60:.1f}分钟)")
    print(f"平均耗时: {avg_time:.1f}s")
    
    # 成功的网站
    successful_sites = [r for r in results if r.get("success")]
    if successful_sites:
        print(f"\n✅ 成功截图的网站 ({len(successful_sites)}个):")
        for i, r in enumerate(successful_sites, 1):
            print(f"  {i:2d}. {r['name']} ({r.get('elapsed', 0):.1f}s)")
    
    # 失败的网站
    failed_sites = [r for r in results if not r.get("success")]
    if failed_sites:
        print(f"\n❌ 失败的网站 ({len(failed_sites)}个):")
        for i, r in enumerate(failed_sites, 1):
            error = r.get('error', '未知错误')
            print(f"  {i:2d}. {r['name']} - {error}")
    
    # 保存详细报告
    report_file = f"complete_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_type": "complete_direct_screenshot_test",
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
    
    # 性能分析
    print(f"\n📈 性能分析:")
    if success_count/total >= 0.9:
        print(f"   🎉 优秀! 成功率 {success_count/total*100:.1f}% - Python反检测方案非常有效")
    elif success_count/total >= 0.7:
        print(f"   ✅ 良好! 成功率 {success_count/total*100:.1f}% - 方案基本有效")
    elif success_count/total >= 0.5:
        print(f"   ⚠️ 一般! 成功率 {success_count/total*100:.1f}% - 需要优化")
    else:
        print(f"   ❌ 较差! 成功率 {success_count/total*100:.1f}% - 需要重新评估方案")
    
    if avg_time <= 10:
        print(f"   ⚡ 速度优秀! 平均 {avg_time:.1f}s/网站")
    elif avg_time <= 20:
        print(f"   🚀 速度良好! 平均 {avg_time:.1f}s/网站")
    else:
        print(f"   🐌 速度较慢! 平均 {avg_time:.1f}s/网站")
    
    print(f"\n🎯 结论:")
    if success_count > 0:
        print(f"   • Python + Playwright-Stealth 方案可行")
        print(f"   • 成功绕过了 {success_count} 个网站的反爬保护")
        print(f"   • 可以作为JavaScript方案的有效补充")
        
        if success_count == total:
            print(f"   • 🏆 完美表现! 可以替代原有方案")

async def main():
    try:
        await test_all_urls()
    except KeyboardInterrupt:
        print(f"\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())