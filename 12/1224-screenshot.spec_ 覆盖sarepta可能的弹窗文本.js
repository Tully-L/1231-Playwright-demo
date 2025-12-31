const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// ========== 核心配置（针对sarepta网站优化） ==========
const SCREENSHOT_DIR = path.resolve('E:/25_wjsz/work/1218-AI巡检/screenshot-service/screenshots/1224-cookie_test-pipeline_sites');
const CONFIG = {
  PAGE_LOAD_TIMEOUT: 80000,      
  POPUP_WAIT_TIMEOUT: 15000,     // 延长弹窗等待时间
  GLOBAL_TEST_TIMEOUT: 150000,   
  NETWORK_IDLE_TIMEOUT: 15000,   
  // 覆盖sarepta可能的弹窗文本（包含常见英文关键词）
  POPUP_TEXT_LIST: [
    'Allow all', 'Accept', 'I agree', 'Accept all', 'Deny', 'Deny all',
    'Allow selection', 'Close', 'Reject all', 'Got it'
  ],
  // 兼容各类弹窗按钮标签
  POPUP_CONTAINER_TAGS: ['button', 'a', 'div', 'span']
};

// ========== 仅保留sarepta单个网站 ==========
const WEBSITES = {
  sarepta: { url: 'https://www.sarepta.com/products-pipeline/pipelinel'}
};

// ========== 初始化截图目录 ==========
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  console.log(`✅ 截图目录已创建：${SCREENSHOT_DIR}`);
}

// ========== 核心：增强版弹窗关闭函数 ==========
async function closeCookiePopup(page) {
  let closed = false;

  // 等待页面完全加载+额外延迟，确保弹窗渲染
  await page.waitForLoadState('load');
  await page.waitForTimeout(2000);

  // 步骤1：检测iframe中的弹窗（sarepta可能把弹窗放在iframe）
  const frames = page.frames();
  for (const frame of frames) {
    if (await tryClosePopupInFrame(frame)) {
      console.log(`✅ 从iframe中关闭了Cookie弹窗`);
      closed = true;
      break;
    }
  }

  // 步骤2：检测主页面弹窗
  if (!closed) {
    if (await tryClosePopupInFrame(page.mainFrame())) {
      console.log(`✅ 从主页面关闭了Cookie弹窗`);
      closed = true;
    }
  }

  // 步骤3：兜底：暴力匹配所有可点击元素
  if (!closed) {
    console.log(`ℹ️ 常规方式未找到弹窗，尝试暴力匹配...`);
    const allClickableElements = await page.$('*[onclick], *[role="button"], button, a');
    for (const elem of allClickableElements) {
      try {
        const text = await elem.textContent();
        if (text && CONFIG.POPUP_TEXT_LIST.some(key => text.toLowerCase().includes(key.toLowerCase()))) {
          await elem.click({ timeout: 3000 });
          console.log(`✅ 暴力匹配到弹窗按钮："${text.trim()}"`);
          closed = true;
          break;
        }
      } catch (e) { /* 忽略单个元素错误 */ }
    }
  }

  if (!closed) {
    console.log(`ℹ️ sarepta网站未检测到可关闭的Cookie弹窗`);
  }
  return closed;
}

// 辅助函数：在指定frame中尝试关闭弹窗
async function tryClosePopupInFrame(frame) {
  for (const tag of CONFIG.POPUP_CONTAINER_TAGS) {
    for (const text of CONFIG.POPUP_TEXT_LIST) {
      const selector = `${tag}:has-text("${text}")`;
      try {
        const elem = await frame.waitForSelector(selector, {
          state: 'visible',
          timeout: 1000
        });
        await elem.click({ timeout: 3000 });
        return true;
      } catch (e) { /* 单个选择器失败，继续 */ }
    }
  }
  return false;
}

// ========== 单网站截图逻辑 ==========
Object.entries(WEBSITES).forEach(([siteKey, siteInfo]) => {
  test(`截图：${siteKey.toUpperCase()}`, async ({ page }, testInfo) => {
    // 设置超时
    testInfo.setTimeout(CONFIG.GLOBAL_TEST_TIMEOUT);
    page.setDefaultTimeout(CONFIG.PAGE_LOAD_TIMEOUT);
    
    // 模拟真实浏览器请求头
    await page.setExtraHTTPHeaders({
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'
    });

    try {
      console.log(`\n====================================`);
      console.log(`开始处理：${siteKey.toUpperCase()}`);
      console.log(`目标网址：${siteInfo.url}`);

      // 1. 导航到目标网站（等待所有资源加载）
      await page.goto(siteInfo.url, {
        waitUntil: 'load',
        timeout: CONFIG.PAGE_LOAD_TIMEOUT,
        referer: 'https://www.google.com'
      });
      console.log(`ℹ️ ${siteKey.toUpperCase()} - 页面完全加载完成`);

      // 2. 关闭Cookie弹窗（核心增强逻辑）
      await closeCookiePopup(page);

      // 3. 等待页面稳定
      try {
        await page.waitForLoadState('networkidle', { timeout: CONFIG.NETWORK_IDLE_TIMEOUT });
        console.log(`ℹ️ ${siteKey.toUpperCase()} - 页面网络已稳定`);
      } catch (networkErr) {
        console.log(`ℹ️ ${siteKey.toUpperCase()} - 网络未稳定（超时），继续截图`);
      }
      await page.waitForTimeout(3000);

      // 4. 生成截图
      const screenshotPath = path.join(SCREENSHOT_DIR, `${siteKey}-pipeline.png`);
      await page.screenshot({
        path: screenshotPath,
        fullPage: true,  // 截取完整页面
        omitBackground: false
      });

      console.log(`✅ ${siteKey.toUpperCase()} - 截图成功`);
      console.log(`✅ 保存路径：${screenshotPath}`);

    } catch (err) {
      const errorMsg = `❌ ${siteKey.toUpperCase()} - 处理失败：${err.message}`;
      console.error(errorMsg);
      expect(false, errorMsg).toBe(true);
    }
  });
});