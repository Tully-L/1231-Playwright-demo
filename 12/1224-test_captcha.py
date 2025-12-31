#!/usr/bin/env python3
import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# 核心配置
TARGET_SITES = [
    {"key": "wavelifesciences", "url": "https://wavelifesciences.com/pipeline/research-and-development/"},
    {"key": "silencetherapeutics", "url": "https://silence-therapeutics.com/our-pipeline/default.aspx"}
]
# 修复路径问题，增加容错
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if __file__ else os.getcwd()
SCREENSHOT_DIR = os.path.join(BASE_DIR, "../screenshots/playwright_cloudflare")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Playwright 反检测配置（核心绕Cloudflare）
PLAYWRIGHT_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "viewport": {"width": 1920, "height": 1080},
    "timeout": 120000,  # 页面加载超时（2分钟，给足Cloudflare验证时间）
    "wait_until": "networkidle"
}

def bypass_cloudflare_and_screenshot(site_key, site_url):
    """
    直接使用Playwright绕过Cloudflare并截图
    :param site_key: 网站标识
    :param site_url: 目标URL
    :return: 截图是否成功
    """
    try:
        with sync_playwright() as p:
            # 启动浏览器，添加反检测参数（核心！）
            browser = p.chromium.launch(
                headless=False,  # 调试时用False，生产可改为True（注意：headless模式易被检测）
                args=[
                    "--no-sandbox",  # 禁用沙箱（Linux环境必需）
                    "--disable-blink-features=AutomationControlled",  # 禁用自动化检测
                    "--disable-dev-shm-usage",  # 解决内存不足问题
                    "--start-maximized",  # 最大化窗口
                    "--disable-web-security",  # 放宽跨域限制
                    "--disable-features=VizDisplayCompositor"  # 避免渲染问题
                ]
            )
            
            # 创建浏览器上下文，模拟真实用户环境
            context = browser.new_context(
                viewport=PLAYWRIGHT_CONFIG["viewport"],
                user_agent=PLAYWRIGHT_CONFIG["user_agent"],
                locale="en-US",  # 设置语言环境
                timezone_id="America/New_York",  # 设置时区（模拟真实用户）
                geolocation={"latitude": 40.7128, "longitude": -74.0060},  # 模拟地理位置（纽约）
                permissions=["geolocation"]  # 授予权限
            )
            
            # 禁用webdriver特征（关键反检测步骤）
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]  # 模拟插件数量
                });
            """)
            
            # 新建页面
            page = context.new_page()
            
            # 监听Cloudflare验证相关日志（便于调试）
            page.on("console", lambda msg: print(f"📝 页面日志: {msg.text}") if msg.type == "log" else None)
            
            print(f"🔄 正在访问 {site_key}，等待Cloudflare验证...")
            # 访问目标URL，自动等待Cloudflare验证完成
            page.goto(
                site_url,
                wait_until=PLAYWRIGHT_CONFIG["wait_until"],
                timeout=PLAYWRIGHT_CONFIG["timeout"]
            )
            
            # 额外等待：确保Cloudflare验证完全完成，页面渲染完毕
            # 检测是否还有Cloudflare验证元素
            try:
                # 等待Cloudflare验证框消失（最多10秒）
                page.wait_for_selector("#challenge-running", state="hidden", timeout=10000)
                page.wait_for_selector(".cf-browser-verification", state="hidden", timeout=10000)
            except PlaywrightTimeoutError:
                print(f"⚠️ {site_key} 未检测到Cloudflare验证框，继续执行")
            
            # 等待页面完全渲染
            time.sleep(3)
            
            # 生成截图
            screenshot_filename = f"{site_key}_{int(time.time())}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
            page.screenshot(path=screenshot_path, full_page=True)
            
            # 优雅关闭资源
            page.close()
            context.close()
            browser.close()
            
            print(f"✅ {site_key} 截图完成: {screenshot_path}")
            return True
            
    except PlaywrightTimeoutError:
        print(f"❌ {site_key} 超时：Cloudflare验证或页面加载超过 {PLAYWRIGHT_CONFIG['timeout']/1000} 秒")
        return False
    except Exception as e:
        print(f"❌ {site_key} 执行失败: {str(e)}")
        return False

# 主执行逻辑
if __name__ == "__main__":
    print("🚀 开始使用Playwright绕过Cloudflare并截图")
    success_count = 0
    fail_count = 0
    
    for site in TARGET_SITES:
        print(f"\n🔍 处理 {site['key']}")
        result = bypass_cloudflare_and_screenshot(site["key"], site["url"])
        if result:
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n🏁 执行完成 | 成功: {success_count} | 失败: {fail_count}")
    print(f"📁 截图保存目录: {os.path.abspath(SCREENSHOT_DIR)}")