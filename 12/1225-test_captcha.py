#!/usr/bin/env python3
import os
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ===================== 核心配置 =====================
TARGET_SITES = [
    {"key": "wavelifesciences", "url": "https://wavelifesciences.com/pipeline/research-and-development/"},
    {"key": "silencetherapeutics", "url": "https://silence-therapeutics.com/our-pipeline/default.aspx"}
]

# 绝对路径配置（避免所有路径问题）
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if __file__ else os.getcwd()
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots_playwright")
USER_DATA_DIR = os.path.join(BASE_DIR, "playwright_user_data")

# 创建必要目录（自动创建，无需手动操作）
for dir_path in [SCREENSHOT_DIR, USER_DATA_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, mode=0o755, exist_ok=True)

# 稳定的 Playwright 配置
PLAYWRIGHT_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "viewport": {"width": 1920, "height": 1080},
    "timeout": 300000,  # 5分钟超时
    "slow_mo": 100      # 慢速执行，模拟真人操作
}

# ===================== 核心工具函数 =====================
def inject_anti_detection_scripts(page):
    """注入反检测脚本，移除自动化特征"""
    anti_detect_js = """
    // 彻底移除webdriver属性（核心反检测）
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    
    // 模拟真实浏览器指纹
    Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
    Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: ''},
            {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''}
        ]
    });
    
    // 隐藏自动化痕迹
    window.chrome = {runtime: {}};
    window.navigator.languages = ['en-US', 'en'];
    window.navigator.plugins.length = 2;
    """
    page.add_init_script(anti_detect_js)

def handle_cloudflare_verification(page, site_key):
    """处理Cloudflare人机验证"""
    try:
        # 检测并等待验证框
        verification_selectors = [
            ".cf-browser-verification",
            "#challenge-form",
            "div[class*='cf-challenge']",
            "div[id*='challenge']",
            "iframe[src*='challenges.cloudflare.com']"
        ]
        
        # 等待验证框出现（10秒）
        try:
            page.wait_for_selector(
                ", ".join(verification_selectors),
                state="visible",
                timeout=10000
            )
            print(f"⚠️ [{site_key}] 检测到Cloudflare验证，正在等待自动完成...")
            
            # 等待验证框消失（最多90秒）
            page.wait_for_selector(
                ", ".join(verification_selectors),
                state="hidden",
                timeout=90000
            )
            print(f"✅ [{site_key}] Cloudflare自动验证完成")
        except PlaywrightTimeoutError:
            print(f"ℹ️ [{site_key}] 未检测到Cloudflare验证框或验证已完成")
        
        # 模拟真人操作：随机滚动+停留
        page.mouse.wheel(0, random.randint(100, 400))
        time.sleep(random.uniform(1, 2))
        page.mouse.move(random.randint(100, 800), random.randint(200, 600))
        time.sleep(random.uniform(1, 2))
        
        return True
    except Exception as e:
        print(f"⚠️ [{site_key}] 验证处理异常: {str(e)}")
        # 预留20秒手动验证时间
        print(f"⚠️ [{site_key}] 请手动完成Cloudflare验证（20秒内）...")
        time.sleep(20)
        return True

# ===================== 核心截图函数 =====================
def take_screenshot_with_cloudflare_bypass(site_key, site_url):
    """
    最终稳定版：绕过Cloudflare并截图（修复PNG quality参数错误）
    """
    context = None
    page = None
    try:
        with sync_playwright() as p:
            # 1. 正确使用 launch_persistent_context（直接在chromium上调用）
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,  # 正确的用户数据目录配置
                headless=False,  # 调试用False，生产可改为True
                slow_mo=PLAYWRIGHT_CONFIG["slow_mo"],
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--start-maximized",
                    "--disable-web-security",
                    "--ignore-certificate-errors",
                    "--disable-popup-blocking",
                    "--disable-extensions",
                    "--disable-notifications"
                ],
                viewport=PLAYWRIGHT_CONFIG["viewport"],
                user_agent=PLAYWRIGHT_CONFIG["user_agent"],
                locale="en-US",
                timezone_id="America/New_York",
                permissions=["geolocation"],
                accept_downloads=False,
                bypass_csp=True,  # 绕过内容安全策略
                no_viewport=True  # 配合start-maximized
            )
            
            # 2. 创建新页面
            page = context.new_page()
            
            # 3. 注入反检测脚本
            inject_anti_detection_scripts(page)
            
            # 4. 访问目标URL
            print(f"🔄 [{site_key}] 正在访问: {site_url}")
            page.goto(
                site_url,
                wait_until="domcontentloaded",
                timeout=PLAYWRIGHT_CONFIG["timeout"]
            )
            
            # 5. 处理Cloudflare验证
            handle_cloudflare_verification(page, site_key)
            
            # 6. 等待页面完全加载
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # 7. 生成截图（全屏）- 修复PNG quality参数错误！
            screenshot_filename = f"{site_key}_{int(time.time())}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
            # 关键修复：移除quality参数（PNG不支持），保留核心配置
            page.screenshot(
                path=screenshot_path,
                full_page=True,
                scale="device"  # 仅保留支持PNG的参数
            )
            
            print(f"✅ [{site_key}] 截图成功！")
            print(f"📸 截图路径: {os.path.abspath(screenshot_path)}")
            
            return True
            
    except PlaywrightTimeoutError:
        print(f"❌ [{site_key}] 执行超时：页面加载/验证超过 {PLAYWRIGHT_CONFIG['timeout']/1000} 秒")
        return False
    except Exception as e:
        print(f"❌ [{site_key}] 执行失败: {str(e)}")
        return False
    finally:
        # 确保资源总是被释放（关键！）
        try:
            if page:
                page.close()
        except:
            pass
        try:
            if context:
                context.close()
        except:
            pass

# ===================== 主执行逻辑 =====================
if __name__ == "__main__":
    # 打印启动信息
    print("="*60)
    print("🚀 Playwright Cloudflare 截图工具 | 最终稳定版")
    print(f"📁 截图保存目录: {os.path.abspath(SCREENSHOT_DIR)}")
    print(f"📁 用户数据目录: {os.path.abspath(USER_DATA_DIR)}")
    print("="*60)
    
    # 初始化统计
    success_count = 0
    total_sites = len(TARGET_SITES)
    
    # 遍历处理每个网站
    for idx, site in enumerate(TARGET_SITES, 1):
        print(f"\n[{idx}/{total_sites}] 开始处理: {site['key']}")
        print(f"🔗 目标URL: {site['url']}")
        
        # 执行截图
        is_success = take_screenshot_with_cloudflare_bypass(site["key"], site["url"])
        
        # 更新统计
        if is_success:
            success_count += 1
        
        # 网站间添加随机延迟
        if idx < total_sites:
            delay = random.randint(5, 10)
            print(f"\n⏳ 等待 {delay} 秒后处理下一个网站...")
            time.sleep(delay)
    
    # 打印最终统计结果
    print("\n" + "="*60)
    print("🏁 所有网站处理完成 | 最终统计")
    print(f"✅ 成功截图: {success_count} / {total_sites}")
    print(f"❌ 处理失败: {total_sites - success_count} / {total_sites}")
    if total_sites > 0:
        success_rate = (success_count / total_sites) * 100
        print(f"📊 成功率: {success_rate:.1f}%")
    print(f"📁 所有截图保存在: {os.path.abspath(SCREENSHOT_DIR)}")
    print("="*60)