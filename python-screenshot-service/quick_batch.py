#!/usr/bin/env python3
"""
快速批量截图 - 简化版
直接运行关键网站截图，每次运行创建独立目录
"""
import asyncio
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 关键网站列表
KEY_SITES = [
    {"name": "Wave Life Sciences", "url": "https://wavelifesciences.com/pipeline/research-and-development/"},
    {"name": "Silence Therapeutics", "url": "https://silence-therapeutics.com/our-pipeline/default.aspx"},
    {"name": "Alnylam", "url": "https://www.alnylam.com/alnylam-rnai-pipeline"},
    {"name": "Arrowhead Pharma", "url": "https://arrowheadpharma.com/pipeline/"},
    {"name": "CRISPR Therapeutics", "url": "https://crisprtx.com/pipeline"},
    {"name": "Intellia Therapeutics", "url": "https://www.intelliatx.com/pipeline/"},
    {"name": "Beam Therapeutics", "url": "https://beamtx.com/pipeline/"},
    {"name": "Novartis", "url": "https://www.novartis.com/research-development/novartis-pipeline"}
]

async def quick_batch_screenshot():
    """快速批量截图"""
    # 创建时间目录
    session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path("screenshots")
    session_dir = base_dir / f"quick_{session_time}"
    session_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 快速批量截图")
    print(f"📁 截图保存到: {session_dir}")
    print(f"🔢 网站数量: {len(KEY_SITES)}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        from screenshot_service import ScreenshotService
        
        # 创建截图服务
        service = ScreenshotService(str(session_dir))
        
        print(f"\n{'='*60}")
        print(f"📸 开始截图")
        print(f"{'='*60}")
        
        results = []
        start_time = time.time()
        
        for i, site in enumerate(KEY_SITES, 1):
            print(f"\n[{i}/{len(KEY_SITES)}] 📸 {site['name']}")
            print(f"         URL: {site['url']}")
            
            site_start = time.time()
            
            try:
                result = await service.take_screenshot(site['url'], {"headless": True})
                elapsed = time.time() - site_start
                
                if result.get("success"):
                    filename = result.get("filename", "")
                    print(f"         ✅ 成功 ({elapsed:.1f}s) - {filename}")
                    results.append({"name": site['name'], "success": True, "elapsed": elapsed, "filename": filename})
                else:
                    error = result.get("error", "未知错误")
                    print(f"         ❌ 失败 ({elapsed:.1f}s) - {error}")
                    results.append({"name": site['name'], "success": False, "elapsed": elapsed, "error": error})
                    
            except Exception as e:
                elapsed = time.time() - site_start
                print(f"         ❌ 异常 ({elapsed:.1f}s) - {str(e)}")
                results.append({"name": site['name'], "success": False, "elapsed": elapsed, "error": str(e)})
            
            # 进度显示
            success_count = sum(1 for r in results if r.get("success"))
            print(f"         📊 进度: {success_count}/{i} 成功")
            
            # 间隔
            if i < len(KEY_SITES):
                await asyncio.sleep(1)
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r.get("success"))
        
        # 生成简单报告
        print(f"\n{'='*60}")
        print(f"📊 快速截图完成")
        print(f"{'='*60}")
        print(f"总计: {len(results)} 个网站")
        print(f"成功: {success_count} 个 ({success_count/len(results)*100:.1f}%)")
        print(f"失败: {len(results) - success_count} 个")
        print(f"耗时: {total_time:.1f}s ({total_time/60:.1f}分钟)")
        print(f"平均: {total_time/len(results):.1f}s/网站")
        
        # 成功列表
        successful = [r for r in results if r.get("success")]
        if successful:
            print(f"\n✅ 成功截图:")
            for r in successful:
                print(f"   • {r['name']} - {r['filename']}")
        
        # 失败列表
        failed = [r for r in results if not r.get("success")]
        if failed:
            print(f"\n❌ 失败截图:")
            for r in failed:
                print(f"   • {r['name']} - {r.get('error', '未知错误')}")
        
        # 保存简单报告
        import json
        report_file = session_dir / f"report_{session_time}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "session_time": session_time,
                "total": len(results),
                "success": success_count,
                "failed": len(results) - success_count,
                "success_rate": success_count/len(results)*100,
                "total_time": total_time,
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 报告已保存: {report_file}")
        print(f"📁 截图目录: {session_dir}")
        
        if success_count == len(results):
            print(f"\n🎉 完美! 所有网站截图成功!")
        elif success_count > 0:
            print(f"\n✅ 不错! {success_count}/{len(results)} 网站截图成功")
        else:
            print(f"\n❌ 需要检查配置，所有截图都失败了")
            
    except Exception as e:
        print(f"❌ 截图服务初始化失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    try:
        await quick_batch_screenshot()
    except KeyboardInterrupt:
        print(f"\n⏹️ 用户中断")
    except Exception as e:
        print(f"\n❌ 运行失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())