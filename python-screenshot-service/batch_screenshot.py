#!/usr/bin/env python3
"""
批量截图工具 - 优化版
每次运行创建独立的时间目录，支持多种URL列表
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

# 预定义的URL集合
URL_SETS = {
    "key_sites": {
        "name": "关键网站 (5个)",
        "description": "从12文件夹提取的最重要网站",
        "urls": [
            {"name": "Wave Life Sciences", "url": "https://wavelifesciences.com/pipeline/research-and-development/"},
            {"name": "Silence Therapeutics", "url": "https://silence-therapeutics.com/our-pipeline/default.aspx"},
            {"name": "Alnylam", "url": "https://www.alnylam.com/alnylam-rnai-pipeline"},
            {"name": "Arrowhead Pharma", "url": "https://arrowheadpharma.com/pipeline/"},
            {"name": "CRISPR Therapeutics", "url": "https://crisprtx.com/pipeline"}
        ]
    },
    "rnai_companies": {
        "name": "RNAi公司 (10个)",
        "description": "专注RNAi技术的生物技术公司",
        "urls": [
            {"name": "Alnylam", "url": "https://www.alnylam.com/alnylam-rnai-pipeline"},
            {"name": "Arrowhead Pharma", "url": "https://arrowheadpharma.com/pipeline/"},
            {"name": "Silence Therapeutics", "url": "https://silence-therapeutics.com/our-pipeline/default.aspx"},
            {"name": "Dicerna (Novo Nordisk)", "url": "https://www.novonordisk.com/science-and-technology/r-d-pipeline.html"},
            {"name": "SiRNA Omics", "url": "https://www.sirnaomics.com/cn/science-pipeline/pipeline/"},
            {"name": "Ionis", "url": "https://ionis.com/pipeline/independent?_format=json"},
            {"name": "Wave Life Sciences", "url": "https://wavelifesciences.com/pipeline/research-and-development/"},
            {"name": "Roche (RNAi)", "url": "https://www.roche.com/solutions/pipeline"},
            {"name": "Sarepta", "url": "https://www.sarepta.com/products-pipeline/pipelinel"},
            {"name": "ProQR", "url": "https://www.proqr.com/pipeline"}
        ]
    },
    "gene_editing": {
        "name": "基因编辑公司 (8个)",
        "description": "CRISPR和其他基因编辑技术公司",
        "urls": [
            {"name": "CRISPR Therapeutics", "url": "https://crisprtx.com/pipeline"},
            {"name": "Intellia Therapeutics", "url": "https://www.intelliatx.com/pipeline/"},
            {"name": "Beam Therapeutics", "url": "https://beamtx.com/pipeline/"},
            {"name": "Metagenomi", "url": "https://metagenomi.co/pipeline"},
            {"name": "Dyne Therapeutics", "url": "https://www.dyne-tx.com/pipeline/"},
            {"name": "PepGen", "url": "https://www.pepgen.com/pipeline/"},
            {"name": "Entrada Therapeutics", "url": "https://www.entradatx.com/pipeline"},
            {"name": "Avidity Biosciences", "url": "https://www.aviditybiosciences.com/pipeline/pipeline-overview"}
        ]
    },
    "big_pharma": {
        "name": "大型制药公司 (6个)",
        "description": "传统大型制药公司的管线",
        "urls": [
            {"name": "Novartis", "url": "https://www.novartis.com/research-development/novartis-pipeline"},
            {"name": "Roche", "url": "https://www.roche.com/solutions/pipeline"},
            {"name": "AstraZeneca", "url": "https://www.astrazeneca.com/our-therapy-areas/pipeline.html"},
            {"name": "Lilly", "url": "https://www.lilly.com/innovation/clinical-development-pipeline"},
            {"name": "Novo Nordisk", "url": "https://www.novonordisk.com/science-and-technology/r-d-pipeline.html"},
            {"name": "Regeneron", "url": "https://www.regeneron.com/science/investigational-pipeline"}
        ]
    },
    "all_sites": {
        "name": "所有网站 (44个)",
        "description": "12文件夹中的所有网站",
        "urls": []  # 将在运行时填充
    }
}

# 填充所有网站列表
def populate_all_sites():
    """填充所有网站列表"""
    all_urls = []
    
    # 添加所有其他集合的URL，去重
    seen_urls = set()
    for set_key, url_set in URL_SETS.items():
        if set_key != "all_sites":
            for url_info in url_set["urls"]:
                if url_info["url"] not in seen_urls:
                    all_urls.append(url_info)
                    seen_urls.add(url_info["url"])
    
    # 添加其他未包含的URL
    additional_urls = [
        {"name": "Denali Therapeutics", "url": "https://www.denalitherapeutics.com/pipeline"},
        {"name": "Adarx", "url": "https://www.adarx.com/pipeline/"},
        {"name": "Ribolia", "url": "https://www.ribolia.com/pipeline"},
        {"name": "Atalanta Therapeutics", "url": "https://www.atalantatx.com/pipeline/"},
        {"name": "Rona Therapeutics", "url": "https://www.ronatherapeutics.com/pipeline"},
        {"name": "Olix Pharma", "url": "https://olixpharma.com/rnd/rnd03.php"},
        {"name": "Tangram Therapeutics", "url": "https://tangramtx.com/pipeline/"},
        {"name": "Switch Therapeutics", "url": "https://www.switchthera.com/our-science/"},
        {"name": "Arobic Therapeutics", "url": "https://www.arobiotx.com/pipeline"},
        {"name": "Sanegene Bio", "url": "https://www.sanegenebio.com/pipeline/"},
        {"name": "Sirius RNA", "url": "https://www.siriusrna.com/pipeline/index.html#pipeline"},
        {"name": "Synerk", "url": "https://synerk.cn/productinfo/883480.html"},
        {"name": "Aligos", "url": "https://aligos.com/science/scientific-overview/"},
        {"name": "Arbutus Bio", "url": "https://www.arbutusbio.com/pipeline/"},
        {"name": "Camp4 Therapeutics", "url": "https://www.camp4tx.com/pipeline/"},
        {"name": "Mina Therapeutics", "url": "https://minatx.com/pipeline/"},
        {"name": "Ractigen", "url": "https://www.ractigen.com/pipeline/"},
        {"name": "Judo Bio", "url": "https://judo.bio/pipeline/"},
        {"name": "Rigerna", "url": "https://www.rigerna.com/page/cpgx/"},
        {"name": "Siran Bio", "url": "https://www.siranbio.com/page/cpgx/"},
        {"name": "VisiRNA", "url": "https://www.visirna.com/pages/client/pplinea?version=v1"},
        {"name": "Hygeia Pharma", "url": "https://www.hygieiapharma.com/Pipeline/3.html"}
    ]
    
    for url_info in additional_urls:
        if url_info["url"] not in seen_urls:
            all_urls.append(url_info)
            seen_urls.add(url_info["url"])
    
    URL_SETS["all_sites"]["urls"] = all_urls

class BatchScreenshotManager:
    def __init__(self):
        self.session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_dir = Path("screenshots")
        self.session_dir = self.base_dir / f"batch_{self.session_time}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.images_dir = self.session_dir / "images"
        self.reports_dir = self.session_dir / "reports"
        self.images_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        print(f"📁 本次截图会话目录: {self.session_dir}")
        print(f"🖼️ 截图保存目录: {self.images_dir}")
        print(f"📊 报告保存目录: {self.reports_dir}")
    
    async def run_batch_screenshot(self, url_set_key):
        """运行批量截图"""
        if url_set_key not in URL_SETS:
            print(f"❌ 未知的URL集合: {url_set_key}")
            return
        
        url_set = URL_SETS[url_set_key]
        urls = url_set["urls"]
        
        print(f"\n🚀 开始批量截图: {url_set['name']}")
        print(f"📋 描述: {url_set['description']}")
        print(f"🔢 网站数量: {len(urls)}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            from screenshot_service import ScreenshotService
            
            # 创建截图服务，使用我们的图片目录
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
        print(f"📸 开始截图任务")
        print(f"{'='*80}")
        
        results = []
        start_time = time.time()
        
        for i, url_info in enumerate(urls, 1):
            result = await self.screenshot_single_url(service, url_info, i, len(urls))
            results.append(result)
            
            # 进度显示
            success_count = sum(1 for r in results if r.get("success"))
            print(f"   📊 进度: {i}/{len(urls)} | 成功: {success_count} | 失败: {i - success_count}")
            
            # URL间隔
            if i < len(urls):
                await asyncio.sleep(1.5)
        
        total_time = time.time() - start_time
        
        # 生成报告
        await self.generate_report(url_set_key, url_set, results, total_time)
        
        return results
    
    async def screenshot_single_url(self, service, url_info, index, total):
        """截图单个URL"""
        name = url_info["name"]
        url = url_info["url"]
        
        print(f"\n[{index:2d}/{total}] 📸 {name}")
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
                "success": False,
                "error": str(e),
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_report(self, set_key, url_set, results, total_time):
        """生成详细报告"""
        success_count = sum(1 for r in results if r.get("success"))
        failed_count = len(results) - success_count
        avg_time = sum(r.get("elapsed", 0) for r in results) / len(results) if results else 0
        
        # 控制台报告
        print(f"\n{'='*80}")
        print(f"📊 批量截图完成报告")
        print(f"{'='*80}")
        print(f"任务集合: {url_set['name']}")
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总计网站: {len(results)}")
        print(f"成功截图: {success_count} 个")
        print(f"失败截图: {failed_count} 个")
        print(f"成功率: {success_count/len(results)*100:.1f}%")
        print(f"总耗时: {total_time:.1f}s ({total_time/60:.1f}分钟)")
        print(f"平均耗时: {avg_time:.1f}s")
        
        # 成功列表
        successful_sites = [r for r in results if r.get("success")]
        if successful_sites:
            print(f"\n✅ 成功截图 ({len(successful_sites)}个):")
            for i, r in enumerate(successful_sites, 1):
                print(f"  {i:2d}. {r['name']} ({r.get('elapsed', 0):.1f}s)")
        
        # 失败列表
        failed_sites = [r for r in results if not r.get("success")]
        if failed_sites:
            print(f"\n❌ 失败截图 ({len(failed_sites)}个):")
            for i, r in enumerate(failed_sites, 1):
                error = r.get('error', '未知错误')[:50]
                print(f"  {i:2d}. {r['name']} - {error}")
        
        # 保存JSON报告
        report_data = {
            "session_info": {
                "session_id": self.session_time,
                "url_set_key": set_key,
                "url_set_name": url_set['name'],
                "description": url_set['description'],
                "start_time": datetime.now().isoformat(),
                "session_dir": str(self.session_dir)
            },
            "summary": {
                "total": len(results),
                "success": success_count,
                "failed": failed_count,
                "success_rate": success_count/len(results)*100 if results else 0,
                "total_time": total_time,
                "average_time": avg_time
            },
            "results": results
        }
        
        json_report_file = self.reports_dir / f"report_{set_key}_{self.session_time}.json"
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # 保存HTML报告
        html_report_file = self.reports_dir / f"report_{set_key}_{self.session_time}.html"
        await self.generate_html_report(html_report_file, report_data)
        
        print(f"\n📄 报告已保存:")
        print(f"   JSON: {json_report_file}")
        print(f"   HTML: {html_report_file}")
        print(f"   截图: {self.images_dir}")
    
    async def generate_html_report(self, html_file, report_data):
        """生成HTML报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>批量截图报告 - {report_data['session_info']['url_set_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .results-section {{ margin-top: 30px; }}
        .result-item {{ display: flex; align-items: center; padding: 10px; margin: 5px 0; border-radius: 4px; }}
        .success {{ background-color: #d4edda; border-left: 4px solid #28a745; }}
        .failure {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
        .status-icon {{ margin-right: 10px; font-size: 18px; }}
        .site-name {{ font-weight: bold; margin-right: 10px; }}
        .site-url {{ color: #666; font-size: 12px; }}
        .elapsed-time {{ margin-left: auto; color: #666; }}
        .error-msg {{ color: #dc3545; font-size: 12px; margin-left: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📸 批量截图报告</h1>
            <h2>{report_data['session_info']['url_set_name']}</h2>
            <p>{report_data['session_info']['description']}</p>
            <p>会话ID: {report_data['session_info']['session_id']}</p>
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
        
        <div class="results-section">
            <h3>📋 详细结果</h3>
"""
        
        for i, result in enumerate(report_data['results'], 1):
            success = result.get('success', False)
            css_class = 'success' if success else 'failure'
            icon = '✅' if success else '❌'
            
            html_content += f"""
            <div class="result-item {css_class}">
                <span class="status-icon">{icon}</span>
                <div>
                    <div class="site-name">{i}. {result['name']}</div>
                    <div class="site-url">{result['url']}</div>
                    {f'<div class="error-msg">错误: {result.get("error", "")}</div>' if not success else ''}
                </div>
                <div class="elapsed-time">{result.get('elapsed', 0):.1f}s</div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

def show_menu():
    """显示菜单"""
    print("\n🚀 批量截图工具")
    print("="*50)
    print("请选择要截图的网站集合:")
    print()
    
    for i, (key, url_set) in enumerate(URL_SETS.items(), 1):
        print(f"{i}. {url_set['name']}")
        print(f"   {url_set['description']}")
        print(f"   网站数量: {len(url_set['urls'])}")
        print()
    
    print("0. 退出")
    print("="*50)

async def main():
    # 填充所有网站列表
    populate_all_sites()
    
    while True:
        show_menu()
        
        try:
            choice = input("请输入选择 (0-5): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            
            # 将选择转换为URL集合键
            url_set_keys = list(URL_SETS.keys())
            choice_index = int(choice) - 1
            
            if 0 <= choice_index < len(url_set_keys):
                selected_key = url_set_keys[choice_index]
                
                print(f"\n✅ 已选择: {URL_SETS[selected_key]['name']}")
                confirm = input("确认开始截图? (y/N): ").strip().lower()
                
                if confirm in ['y', 'yes']:
                    manager = BatchScreenshotManager()
                    await manager.run_batch_screenshot(selected_key)
                    
                    print(f"\n🎉 批量截图完成!")
                    input("按回车键继续...")
                else:
                    print("❌ 已取消")
            else:
                print("❌ 无效选择，请重新输入")
                
        except ValueError:
            print("❌ 请输入有效数字")
        except KeyboardInterrupt:
            print(f"\n⏹️ 用户中断")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())