import asyncio
import os
import hashlib
import time
from datetime import datetime
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

class ScreenshotService:
    def __init__(self, screenshot_dir: str):
        self.base_screenshot_dir = screenshot_dir
        # 创建基于时间的子目录
        self.session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.screenshot_dir = os.path.join(screenshot_dir, f"session_{self.session_time}")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        print(f"📁 截图将保存到: {self.screenshot_dir}")
        
        self.config = {
            "timeout": 120000,  # 2分钟超时
            "viewport": {"width": 1920, "height": 1080},
            "popup_texts": [
                'Accept', 'Accept all', 'Allow all', 'I agree', 'Got it', 'Close',
                'Reject all', 'Deny all', 'Allow selection', '同意', '接受', '关闭',
                'OK', 'Continue', 'Agree and continue', 'Accept cookies'
            ]
        }
    
    def generate_filename(self, url: str) -> str:
        """生成唯一文件名"""
        timestamp = int(time.time() * 1000)
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        # 添加域名信息使文件名更有意义
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '').replace('.', '_')
            return f"{domain}_{timestamp}_{url_hash}.png"
        except:
            return f"screenshot_{timestamp}_{url_hash}.png"
    
    async def close_popups(self, page):
        """关闭弹窗"""
        try:
            await page.wait_for_timeout(2000)
            
            for text in self.config["popup_texts"]:
                try:
                    # 多种选择器策略
                    selectors = [
                        f'button:has-text("{text}")',
                        f'a:has-text("{text}")',
                        f'div[role="button"]:has-text("{text}")',
                        f'span:has-text("{text}")',
                        f'[data-testid*="accept"]',
                        f'[id*="accept"]',
                        f'[class*="accept"]',
                        f'[class*="cookie"]',
                        f'[class*="consent"]'
                    ]
                    
                    for selector in selectors:
                        try:
                            element = await page.query_selector(selector)
                            if element:
                                await element.click(timeout=3000)
                                print(f"✅ 关闭弹窗: {text}")
                                await page.wait_for_timeout(1000)
                                return True
                        except:
                            continue
                            
                except Exception as e:
                    continue
            
            return False
        except Exception as error:
            print(f"⚠️ 弹窗处理异常: {error}")
            return False
    
    async def handle_lazy_loading(self, page):
        """处理懒加载"""
        try:
            await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        let totalHeight = 0;
                        const distance = 100;
                        const timer = setInterval(() => {
                            const scrollHeight = document.body.scrollHeight;
                            window.scrollBy(0, distance);
                            totalHeight += distance;
                            
                            if (totalHeight >= scrollHeight) {
                                clearInterval(timer);
                                window.scrollTo(0, 0);
                                setTimeout(resolve, 1000);
                            }
                        }, 100);
                    });
                }
            """)
        except Exception as e:
            print(f"⚠️ 懒加载处理异常: {e}")
    
    async def take_screenshot(self, url: str, options: dict = None) -> dict:
        """核心截图函数"""
        if options is None:
            options = {}
        
        playwright = None
        browser = None
        context = None
        page = None
        
        print(f"🔄 开始截图: {url}")
        
        try:
            playwright = await async_playwright().start()
            print("✅ Playwright已启动")
            
            # 启动浏览器，使用stealth模式
            browser = await playwright.chromium.launch(
                headless=options.get('headless', True),
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--ignore-certificate-errors',
                    '--disable-popup-blocking',
                    '--disable-extensions',
                    '--no-first-run',
                    '--disable-default-apps',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            print("✅ 浏览器已启动")
            
            # 创建上下文
            context = await browser.new_context(
                viewport=self.config["viewport"],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                ignore_https_errors=True,
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            # 添加反检测脚本
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                window.chrome = {
                    runtime: {},
                };
                
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' }),
                    }),
                });
            """)
            
            page = await context.new_page()
            print("✅ 页面已创建")
            
            # 应用stealth插件
            try:
                await stealth_async(page)
                print("✅ Stealth插件已应用")
            except Exception as e:
                print(f"⚠️ Stealth插件应用失败: {e}")
            
            print(f"🔄 正在访问: {url}")
            
            # 访问页面
            await page.goto(url, wait_until='domcontentloaded', timeout=self.config["timeout"])
            
            # 关闭弹窗
            await self.close_popups(page)
            
            # 等待网络稳定
            try:
                await page.wait_for_load_state('networkidle', timeout=15000)
            except:
                print('⚠️ 网络未完全稳定，继续截图')
            
            # 处理懒加载
            await self.handle_lazy_loading(page)
            
            # 生成截图
            filename = self.generate_filename(url)
            screenshot_path = os.path.join(self.screenshot_dir, filename)
            
            await page.screenshot(
                path=screenshot_path,
                full_page=True,
                animations='disabled'
            )
            
            print(f"✅ 截图成功: {screenshot_path}")
            
            return {
                "success": True,
                "filename": filename,
                "path": screenshot_path,
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as error:
            error_msg = str(error)
            print(f"❌ 截图失败: {error_msg}")
            print(f"   错误类型: {type(error).__name__}")
            
            # 详细错误信息
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": error_msg,
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            # 清理资源
            try:
                if page:
                    await page.close()
                if context:
                    await context.close()
                if browser:
                    await browser.close()
                if playwright:
                    await playwright.stop()
            except Exception as e:
                print(f'资源清理异常: {e}')