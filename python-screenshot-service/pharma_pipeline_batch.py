#!/usr/bin/env python3
"""
制药公司管线批量截图 - 处理所有提供的URL
包含生物技术公司、大型制药公司等的管线页面
"""
import asyncio
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 所有制药公司管线URL
PHARMA_PIPELINE_URLS = [
    # RNAi和基因治疗公司
    {"name": "Alnylam Pharmaceuticals", "url": "https://www.alnylam.com/alnylam-rnai-pipeline", "category": "RNAi"},
    {"name": "Arrowhead Pharmaceuticals", "url": "https://arrowheadpharma.com/pipeline/", "category": "RNAi"},
    {"name": "Ionis Pharmaceuticals", "url": "https://ionis.com/pipeline/independent?_format=json", "category": "RNAi"},
    {"name": "Wave Life Sciences", "url": "https://wavelifesciences.com/pipeline/research-and-development/", "category": "RNAi"},
    {"name": "Silence Therapeutics", "url": "https://silence-therapeutics.com/our-pipeline/default.aspx", "category": "RNAi"},
    {"name": "SiRNA Omics", "url": "https://www.sirnaomics.com/cn/science-pipeline/pipeline/", "category": "RNAi"},
    {"name": "ProQR Therapeutics", "url": "https://www.proqr.com/pipeline", "category": "RNAi"},
    
    # 基因编辑公司
    {"name": "CRISPR Therapeutics", "url": "https://crisprtx.com/pipeline", "category": "Gene Editing"},
    {"name": "Intellia Therapeutics", "url": "https://www.intelliatx.com/pipeline/", "category": "Gene Editing"},
    {"name": "Beam Therapeutics", "url": "https://beamtx.com/pipeline/", "category": "Gene Editing"},
    {"name": "Metagenomi", "url": "https://metagenomi.co/pipeline", "category": "Gene Editing"},
    
    # 生物技术公司
    {"name": "Avidity Biosciences", "url": "https://www.aviditybiosciences.com/pipeline/pipeline-overview", "category": "Biotech"},
    {"name": "Dyne Therapeutics", "url": "https://www.dyne-tx.com/pipeline/", "category": "Biotech"},
    {"name": "Denali Therapeutics", "url": "https://www.denalitherapeutics.com/pipeline", "category": "Biotech"},
    {"name": "Adarx Pharmaceuticals", "url": "https://www.adarx.com/pipeline/", "category": "Biotech"},
    {"name": "Ribolia", "url": "https://www.ribolia.com/pipeline", "category": "Biotech"},
    {"name": "Atalanta Therapeutics", "url": "https://www.atalantatx.com/pipeline/", "category": "Biotech"},
    {"name": "Sarepta Therapeutics", "url": "https://www.sarepta.com/products-pipeline/pipelinel", "category": "Biotech"},
    {"name": "Rona Therapeutics", "url": "https://www.ronatherapeutics.com/pipeline", "category": "Biotech"},
    {"name": "Entrada Therapeutics", "url": "https://www.entradatx.com/pipeline", "category": "Biotech"},
    {"name": "PepGen", "url": "https://www.pepgen.com/pipeline/", "category": "Biotech"},
    {"name": "Tangram Therapeutics", "url": "https://tangramtx.com/pipeline/", "category": "Biotech"},
    {"name": "Switch Therapeutics", "url": "https://www.switchthera.com/our-science/", "category": "Biotech"},
    {"name": "Arobic Therapeutics", "url": "https://www.arobiotx.com/pipeline", "category": "Biotech"},
    {"name": "Sanegene Bio", "url": "https://www.sanegenebio.com/pipeline/", "category": "Biotech"},
    {"name": "Sirius RNA", "url": "https://www.siriusrna.com/pipeline/index.html#pipeline", "category": "Biotech"},
    {"name": "Aligos Therapeutics", "url": "https://aligos.com/science/scientific-overview/", "category": "Biotech"},
    {"name": "Arbutus Biopharma", "url": "https://www.arbutusbio.com/pipeline/", "category": "Biotech"},
    {"name": "Camp4 Therapeutics", "url": "https://www.camp4tx.com/pipeline/", "category": "Biotech"},
    {"name": "Mina Therapeutics", "url": "https://minatx.com/pipeline/", "category": "Biotech"},
    {"name": "Ractigen Therapeutics", "url": "https://www.ractigen.com/pipeline/", "category": "Biotech"},
    {"name": "Judo Bio", "url": "https://judo.bio/pipeline/", "category": "Biotech"},
    {"name": "Rigerna", "url": "https://www.rigerna.com/page/cpgx/", "category": "Biotech"},
    {"name": "Siran Bio", "url": "https://www.siranbio.com/page/cpgx/", "category": "Biotech"},
    {"name": "VisiRNA Therapeutics", "url": "https://www.visirna.com/pages/client/pplinea?version=v1", "category": "Biotech"},
    {"name": "Apellis Pharmaceuticals", "url": "https://apellis.com/our-science/our-pipeline/", "category": "Biotech"},
    
    # 大型制药公司
    {"name": "Eli Lilly", "url": "https://www.lilly.com/innovation/clinical-development-pipeline", "category": "Big Pharma"},
    {"name": "Novo Nordisk", "url": "https://www.novonordisk.com/science-and-technology/r-d-pipeline.html", "category": "Big Pharma"},
    {"name": "Novartis", "url": "https://www.novartis.com/research-development/novartis-pipeline", "category": "Big Pharma"},
    {"name": "Regeneron", "url": "https://www.regeneron.com/science/investigational-pipeline", "category": "Big Pharma"},
    {"name": "AstraZeneca", "url": "https://www.astrazeneca.com/our-therapy-areas/pipeline.html", "category": "Big Pharma"},
    {"name": "Roche", "url": "https://www.roche.com/solutions/pipeline", "category": "Big Pharma"},
    {"name": "Biogen", "url": "https://www.biogen.com/science-and-innovation/pipeline.html", "category": "Big Pharma"},
    {"name": "Amgen", "url": "https://www.amgenpipeline.com/", "category": "Big Pharma"},
    {"name": "Johnson & Johnson", "url": "https://www.investor.jnj.com/pipeline/development-pipeline/default.aspx", "category": "Big Pharma"},
    {"name": "Takeda", "url": "https://www.takeda.com/science/pipeline/", "category": "Big Pharma"},
    {"name": "GSK", "url": "https://www.gsk.com/en-gb/innovation/pipeline/", "category": "Big Pharma"},
    {"name": "Sanofi", "url": "https://www.sanofi.com/en/our-science/our-pipeline", "category": "Big Pharma"},
    {"name": "AbbVie", "url": "https://www.abbvie.com/science/pipeline.html", "category": "Big Pharma"},
    {"name": "Merck", "url": "https://www.merck.com/research/product-pipeline/", "category": "Big Pharma"},
    {"name": "Gilead Sciences", "url": "https://www.gilead.com/science/pipeline", "category": "Big Pharma"},
    {"name": "Boehringer Ingelheim", "url": "https://www.boehringer-ingelheim.com/science-innovation/human-health-innovation/clinical-pipeline", "category": "Big Pharma"},
    {"name": "Pfizer", "url": "https://www.pfizer.com/science/drug-product-pipeline", "category": "Big Pharma"},
    {"name": "CSL", "url": "https://www.csl.com/research-and-development/product-pipeline", "category": "Big Pharma"},
    {"name": "Bristol Myers Squibb", "url": "https://www.bms.com/researchers-and-partners/in-the-pipeline.html", "category": "Big Pharma"},
    {"name": "Bayer", "url": "https://www.bayer.com/en/pharma/development-pipeline", "category": "Big Pharma"},
    
    # 中国/亚洲公司
    {"name": "Synerk", "url": "https://synerk.cn/productinfo/883480.html", "category": "Asia"},
    {"name": "Hygeia Pharma", "url": "https://www.hygieiapharma.com/Pipeline/3.html", "category": "Asia"},
    {"name": "BeBetterMed (CN)", "url": "http://www.bebettermed.cn/goods-2-view.html#rd_4", "category": "Asia"},
    {"name": "BeBetterMed (COM)", "url": "http://www.bebettermed.com/goods-2-view.html#rd_4", "category": "Asia"},
    
    # 其他专业公司
    {"name": "Olix Pharma", "url": "https://olixpharma.com/rnd/rnd03.php", "category": "Specialty"}
]

class PharmaPipelineBatch:
    def __init__(self):
        self.session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_dir = Path("screenshots")
        self.session_dir = self.base_dir / f"pharma_pipeline_{self.session_time}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建分类目录
        self.images_dir = self.session_dir / "images"
        self.reports_dir = self.session_dir / "reports"
        self.images_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        print(f"🏥 制药公司管线批量截图")
        print(f"📁 截图保存目录: {self.session_dir}")
        print(f"🔢 总计网站: {len(PHARMA_PIPELINE_URLS)}")
        
        # 按类别统计
        categories = {}
        for url_info in PHARMA_PIPELINE_URLS:
            category = url_info["category"]
            categories[category] = categories.get(category, 0) + 1
        
        print(f"📊 分类统计:")
        for category, count in categories.items():
            print(f"   • {category}: {count} 个网站")
    
    async def run_full_batch(self):
        """运行完整批量截图"""
        print(f"\n⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            from screenshot_service import ScreenshotService
            
            # 创建截图服务
            service = ScreenshotService(str(self.images_dir))
            
            # 验证服务
            print("\n🧪 验证截图服务...")
            test_result = await service.take_screenshot("https://httpbin.org/html")
            if not test_result.get("success"):
                print(f"❌ 服务验证失败: {test_result.get('error')}")
                return
            print("✅ 服务验证成功")
            
        except Exception as e:
            print(f"❌ 服务初始化失败: {e}")
            return
        
        print(f"\n{'='*80}")
        print(f"📸 开始制药公司管线截图")
        print(f"{'='*80}")
        
        results = []
        start_time = time.time()
        batch_size = 5  # 每批5个网站
        
        # 按类别分组处理
        categories = {}
        for url_info in PHARMA_PIPELINE_URLS:
            category = url_info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(url_info)
        
        total_processed = 0
        
        for category, urls in categories.items():
            print(f"\n📂 处理类别: {category} ({len(urls)} 个网站)")
            print("-" * 60)
            
            category_start = time.time()
            category_results = []
            
            for i, url_info in enumerate(urls):
                total_processed += 1
                result = await self.screenshot_single_url(
                    service, url_info, total_processed, len(PHARMA_PIPELINE_URLS)
                )
                results.append(result)
                category_results.append(result)
                
                # 进度显示
                success_count = sum(1 for r in results if r.get("success"))
                print(f"   📊 总进度: {total_processed}/{len(PHARMA_PIPELINE_URLS)} | 成功: {success_count}")
                
                # URL间隔
                if i < len(urls) - 1:
                    await asyncio.sleep(1.5)
            
            category_elapsed = time.time() - category_start
            category_success = sum(1 for r in category_results if r.get("success"))
            
            print(f"\n📊 {category} 完成: {category_success}/{len(urls)} 成功 ({category_elapsed:.1f}s)")
            
            # 类别间等待
            if category != list(categories.keys())[-1]:  # 不是最后一个类别
                print("⏳ 类别间等待 3 秒...\n")
                await asyncio.sleep(3)
        
        total_time = time.time() - start_time
        
        # 生成报告
        await self.generate_comprehensive_report(results, total_time)
        
        return results
    
    async def screenshot_single_url(self, service, url_info, index, total):
        """截图单个URL"""
        name = url_info["name"]
        url = url_info["url"]
        category = url_info["category"]
        
        print(f"\n[{index:2d}/{total}] 📸 {name}")
        print(f"           分类: {category}")
        print(f"           URL: {url}")
        
        start_time = time.time()
        
        try:
            result = await service.take_screenshot(url, {"headless": True})
            elapsed = time.time() - start_time
            
            if result.get("success"):
                filename = result.get("filename", "")
                print(f"           ✅ 成功 ({elapsed:.1f}s) - {filename}")
                return {
                    "name": name,
                    "url": url,
                    "category": category,
                    "success": True,
                    "filename": filename,
                    "elapsed": elapsed,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error = result.get("error", "未知错误")
                print(f"           ❌ 失败 ({elapsed:.1f}s) - {error}")
                return {
                    "name": name,
                    "url": url,
                    "category": category,
                    "success": False,
                    "error": error,
                    "elapsed": elapsed,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"           ❌ 异常 ({elapsed:.1f}s) - {str(e)}")
            return {
                "name": name,
                "url": url,
                "category": category,
                "success": False,
                "error": str(e),
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_comprehensive_report(self, results, total_time):
        """生成综合报告"""
        total = len(results)
        success_count = sum(1 for r in results if r.get("success"))
        failed_count = total - success_count
        avg_time = sum(r.get("elapsed", 0) for r in results) / total if results else 0
        
        # 按类别统计
        category_stats = {}
        for result in results:
            category = result["category"]
            if category not in category_stats:
                category_stats[category] = {"total": 0, "success": 0, "failed": 0}
            
            category_stats[category]["total"] += 1
            if result.get("success"):
                category_stats[category]["success"] += 1
            else:
                category_stats[category]["failed"] += 1
        
        # 控制台报告
        print(f"\n{'='*80}")
        print(f"📊 制药公司管线截图完成报告")
        print(f"{'='*80}")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总计网站: {total}")
        print(f"成功截图: {success_count} 个")
        print(f"失败截图: {failed_count} 个")
        print(f"成功率: {success_count/total*100:.1f}%")
        print(f"总耗时: {total_time:.1f}s ({total_time/60:.1f}分钟)")
        print(f"平均耗时: {avg_time:.1f}s")
        
        # 分类统计
        print(f"\n📊 分类统计:")
        for category, stats in category_stats.items():
            success_rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"   • {category}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # 成功列表（按类别）
        print(f"\n✅ 成功截图 ({success_count}个):")
        for category in category_stats.keys():
            category_success = [r for r in results if r.get("success") and r["category"] == category]
            if category_success:
                print(f"\n   📂 {category}:")
                for r in category_success:
                    print(f"      • {r['name']} ({r.get('elapsed', 0):.1f}s)")
        
        # 失败列表
        failed_sites = [r for r in results if not r.get("success")]
        if failed_sites:
            print(f"\n❌ 失败截图 ({len(failed_sites)}个):")
            for category in category_stats.keys():
                category_failed = [r for r in failed_sites if r["category"] == category]
                if category_failed:
                    print(f"\n   📂 {category}:")
                    for r in category_failed:
                        error = r.get('error', '未知错误')[:50]
                        print(f"      • {r['name']} - {error}")
        
        # 保存详细报告
        report_data = {
            "session_info": {
                "session_id": self.session_time,
                "type": "pharma_pipeline_batch",
                "start_time": datetime.now().isoformat(),
                "session_dir": str(self.session_dir)
            },
            "summary": {
                "total": total,
                "success": success_count,
                "failed": failed_count,
                "success_rate": success_count/total*100 if total > 0 else 0,
                "total_time": total_time,
                "average_time": avg_time
            },
            "category_stats": category_stats,
            "results": results
        }
        
        json_report_file = self.reports_dir / f"pharma_pipeline_report_{self.session_time}.json"
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # 生成HTML报告
        html_report_file = self.reports_dir / f"pharma_pipeline_report_{self.session_time}.html"
        await self.generate_html_report(html_report_file, report_data)
        
        print(f"\n📄 报告已保存:")
        print(f"   JSON: {json_report_file}")
        print(f"   HTML: {html_report_file}")
        print(f"   截图: {self.images_dir}")
        
        # 性能评估
        print(f"\n📈 性能评估:")
        if success_count/total >= 0.9:
            print(f"   🏆 优秀! 成功率 {success_count/total*100:.1f}% - Python反检测方案非常有效")
        elif success_count/total >= 0.8:
            print(f"   ✅ 良好! 成功率 {success_count/total*100:.1f}% - 方案表现良好")
        elif success_count/total >= 0.7:
            print(f"   ⚠️ 一般! 成功率 {success_count/total*100:.1f}% - 需要优化")
        else:
            print(f"   ❌ 较差! 成功率 {success_count/total*100:.1f}% - 需要重新评估")
        
        print(f"\n🎯 结论:")
        print(f"   • 成功截图了 {success_count} 个制药公司管线页面")
        print(f"   • Python + Playwright-Stealth 方案在制药行业网站表现{'优秀' if success_count/total >= 0.8 else '良好' if success_count/total >= 0.7 else '一般'}")
        if success_count > 0:
            print(f"   • 可以作为制药行业管线监控的有效工具")
    
    async def generate_html_report(self, html_file, report_data):
        """生成HTML报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>制药公司管线截图报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .category-section {{ margin: 20px 0; }}
        .category-header {{ background: #e9ecef; padding: 10px; border-radius: 4px; font-weight: bold; }}
        .result-item {{ display: flex; align-items: center; padding: 8px; margin: 3px 0; border-radius: 4px; }}
        .success {{ background-color: #d4edda; border-left: 4px solid #28a745; }}
        .failure {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
        .status-icon {{ margin-right: 10px; font-size: 16px; }}
        .company-name {{ font-weight: bold; margin-right: 10px; min-width: 200px; }}
        .company-url {{ color: #666; font-size: 11px; flex: 1; }}
        .elapsed-time {{ margin-left: auto; color: #666; min-width: 60px; }}
        .error-msg {{ color: #dc3545; font-size: 11px; margin-left: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 制药公司管线截图报告</h1>
            <p>会话ID: {report_data['session_info']['session_id']}</p>
            <p>生成时间: {report_data['session_info']['start_time']}</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-value">{report_data['summary']['total']}</div>
                <div class="stat-label">总计网站</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report_data['summary']['success']}</div>
                <div class="stat-label">成功截图</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report_data['summary']['failed']}</div>
                <div class="stat-label">失败截图</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report_data['summary']['success_rate']:.1f}%</div>
                <div class="stat-label">成功率</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report_data['summary']['total_time']:.1f}s</div>
                <div class="stat-label">总耗时</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report_data['summary']['average_time']:.1f}s</div>
                <div class="stat-label">平均耗时</div>
            </div>
        </div>
"""
        
        # 按类别显示结果
        for category, stats in report_data['category_stats'].items():
            category_results = [r for r in report_data['results'] if r['category'] == category]
            success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
            
            html_content += f"""
        <div class="category-section">
            <div class="category-header">
                📂 {category} - {stats['success']}/{stats['total']} 成功 ({success_rate:.1f}%)
            </div>
"""
            
            for result in category_results:
                success = result.get('success', False)
                css_class = 'success' if success else 'failure'
                icon = '✅' if success else '❌'
                
                html_content += f"""
            <div class="result-item {css_class}">
                <span class="status-icon">{icon}</span>
                <div class="company-name">{result['name']}</div>
                <div class="company-url">{result['url']}</div>
                <div class="elapsed-time">{result.get('elapsed', 0):.1f}s</div>
                {f'<div class="error-msg">{result.get("error", "")[:50]}</div>' if not success else ''}
            </div>
"""
            
            html_content += "</div>"
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

async def main():
    print("🏥 制药公司管线批量截图工具")
    print("📋 将截图所有主要制药公司的管线页面")
    
    try:
        batch_manager = PharmaPipelineBatch()
        
        confirm = input(f"\n确认开始截图 {len(PHARMA_PIPELINE_URLS)} 个制药公司网站? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            print(f"\n🚀 开始批量截图...")
            results = await batch_manager.run_full_batch()
            
            success_count = sum(1 for r in results if r.get("success"))
            print(f"\n🎉 批量截图完成!")
            print(f"📊 最终结果: {success_count}/{len(results)} 成功")
            
        else:
            print("❌ 已取消")
            
    except KeyboardInterrupt:
        print(f"\n⏹️ 用户中断")
    except Exception as e:
        print(f"\n❌ 运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())