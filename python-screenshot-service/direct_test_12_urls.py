#!/usr/bin/env python3
"""
直接测试12文件夹URL - 不通过API，直接调用截图服务
"""
import asyncio
import sys
import os
import time
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 从12文件夹中提取的关键URL
KEY_URLS = [
    {
        "name": "Wave Life Sciences",
        "url": "https://wavelifesciences.com/pipeline/research-and-development/",
        "note": "12文件夹Python代码成功抓取的网站"
    },
    {
        "name": "Silence Therapeutics",
        "url": "https://silence-therapeutics.com/our-pipeline/default.aspx",
        "note": "可能有Cloudflare保护"
    },
    {
        "name": "Alnylam",
        "url": "https://www.alnylam.com/alnylam-rnai-pipeline",
        "note": "RNAi领域知名公司"
    },
    {
        "name": "Arrowhead Pharma",
        "url": "https://arrowheadpharma.com/pipeline/",
        "note": "RNAi治疗公司"
    },
    {
        "name": "CRISPR Therapeutics",
        "url": "https://crisprtx.com/pipeline",
        "note": "基因编辑公司"
    }
]

async def test_single_url(service, url_info, index, total):
    """测试单个URL"""
    name = url_info["name"]
    url = url_info["url"]
    note = url_info["note"]
    
    print(f"[{index}/{total}] 📸 {name}")
    print(f"         URL: {url}")
    print(f"         备注: {note}")
    
    start_time = time.time()
    
    try:
        # 直接调用截图服务
        result = await service.take_screenshot(url, {"headless": True})
        elapsed = time.time() - start_time
        
        if result.get("success"):
            filename = result.get("filename", "")
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
            error = result.get("error", "未知错误")
            print(f"         ❌ 失败 ({elapsed:.1f}s) - {error}")
            return {
                "name": name,
                "url": url,
                "success": False,
                "error": error,
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

async def test_basic_functionality():
    """先测试基本功能"""
    print("🧪 测试基本功能\n")
    
    try:
        from screenshot_service import ScreenshotService
        
        # 创建服务实例
        service = ScreenshotService("./screenshots")
        print("✅ 截图服务实例创建成功")
        
        # 测试简单URL
        print("\n📸 测试简单URL...")
        simple_result = await service.take_screenshot("https://httpbin.org/html")
        
        if simple_result.get("success"):
            print(f"✅ 简单URL测试成功: {simple_result.get('filename')}")
            return service
        else:
            print(f"❌ 简单URL测试失败: {simple_result.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_12_folder_urls():
    """测试12文件夹中的URL"""
    print("🚀 直接测试12文件夹中的URL")
    print("🎯 不通过API，直接调用截图服务\n")
    
    # 先测试基本功能
    service = await test_basic_functionality()
    
    if not service:
        print("❌ 基本功能测试失败，无法继续")
        return
    
    print("\n" + "="*60)
    print("📸 开始测试关键URL")
    print("="*60)
    
    results = []
    
    for i, url_info in enumerate(KEY_URLS, 1):
        result = await test_single_url(service, url_info, i, len(KEY_URLS))
        results.append(result)
        
        print()  # 空行分隔
        
        # 每个URL测试后等待2秒
        if i < len(KEY_URLS):
            print("⏳ 等待 2 秒...\n")
            await asyncio.sleep(2)
    
    # 生成报告
    generate_report(results)

def generate_report(results):
    """生成测试报告"""
    total = len(results)
    success_count = sum(1 for r in results if r.get("success"))
    failed_count = total - success_count
    
    total_time = sum(r.get("elapsed", 0) for r in results)
    avg_time = total_time / total if total > 0 else 0
    
    print("="*80)
    print("📊 直接测试报告")
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
    import json
    report_file = f"direct_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "test_type": "direct_screenshot_service",
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
    print(f"\n💡 结果分析:")
    if success_count == total:
        print(f"   🎉 所有网站截图成功！Python反检测方案完全有效")
        print(f"   📈 成功率: 100% - 可以放心使用")
    elif success_count > total * 0.7:
        print(f"   ✅ 大部分网站截图成功，方案基本有效")
        print(f"   📈 成功率: {success_count/total*100:.1f}% - 表现良好")
    elif success_count > 0:
        print(f"   ⚠️ 部分网站截图成功，需要优化")
        print(f"   📈 成功率: {success_count/total*100:.1f}% - 有改进空间")
    else:
        print(f"   ❌ 所有网站截图失败，需要检查配置")
        print(f"   🔧 建议检查网络连接和依赖安装")
    
    if success_count > 0:
        print(f"\n🚀 下一步:")
        print(f"   • 脚本测试成功，可以修复API接口")
        print(f"   • 运行完整测试: python test_all_urls_direct.py")

async def main():
    try:
        await test_12_folder_urls()
    except KeyboardInterrupt:
        print(f"\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())