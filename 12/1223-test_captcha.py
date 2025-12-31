#!/usr/bin/env python3
import os
import time
from curl_cffi import requests as cffi_requests
from playwright.sync_api import sync_playwright

# 核心配置（仅保留必要项）
TARGET_SITES = [
    {"key": "wavelifesciences", "url": "https://wavelifesciences.com/pipeline/research-and-development/"},
    {"key": "silencetherapeutics", "url": "https://silence-therapeutics.com/our-pipeline/default.aspx"}
]
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "../screenshots/curl_cffi_v124")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Chrome 124 核心绕过配置
CONFIG = {
    "impersonate": "chrome124",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    },
    "timeout": 60,
    "allow_redirects": True
}

def bypass_cloudflare(url):
    """极简curl_cffi绕过：直接调用cffi_requests.get"""
    # 按要求简化调用：直接用cffi_requests.get(url)
    resp = cffi_requests.get(
        url,
        impersonate=CONFIG["impersonate"],
        headers=CONFIG["headers"],
        timeout=CONFIG["timeout"],
        allow_redirects=CONFIG["allow_redirects"]
    )
    # 解析Cookie（极简版）
    cookies = [{"name": k, "value": v, "domain": url.split("//")[1].split("/")[0], "path": "/"} 
               for k, v in resp.cookies.get_dict().items()]
    return {"success": resp.status_code == 200 and "cloudflare" not in resp.text.lower(), 
            "cookies": cookies, "url": resp.url}

def screenshot(url, cookies, key):
    """极简截图：仅核心逻辑"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        if cookies:
            context.add_cookies(cookies)
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=120000)
        time.sleep(2)
        # 生成截图
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{key}_{int(time.time())}.png")
        page.screenshot(path=screenshot_path, full_page=True)
        browser.close()
        print(f"✅ {key} 截图完成: {screenshot_path}")

# 主执行逻辑（极简）
if __name__ == "__main__":
    print("🚀 开始Chrome 124绕过Cloudflare")
    for site in TARGET_SITES:
        print(f"\n🔍 处理 {site['key']}")
        bypass_result = bypass_cloudflare(site["url"])
        if bypass_result["success"]:
            screenshot(bypass_result["url"], bypass_result["cookies"], site["key"])
        else:
            print(f"❌ {site['key']} 绕过失败")
    print("\n🏁 执行完成")