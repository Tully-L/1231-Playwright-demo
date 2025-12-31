const express = require('express');
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const app = express();
app.use(express.json());

// 配置
const CONFIG = {
  PORT: process.env.PORT || 3000,
  SCREENSHOT_DIR: path.join(__dirname, 'screenshots'),
  TIMEOUT: 120000, // 2分钟超时
  VIEWPORT: { width: 1920, height: 1080 },
  // 常见弹窗关闭文本
  POPUP_TEXTS: [
    'Accept', 'Accept all', 'Allow all', 'I agree', 'Got it', 'Close',
    'Reject all', 'Deny all', 'Allow selection', '同意', '接受', '关闭'
  ]
};

// 确保截图目录存在
if (!fs.existsSync(CONFIG.SCREENSHOT_DIR)) {
  fs.mkdirSync(CONFIG.SCREENSHOT_DIR, { recursive: true });
}

// 生成唯一文件名
function generateFilename(url) {
  const timestamp = Date.now();
  const hash = crypto.createHash('md5').update(url).digest('hex').substring(0, 8);
  return `screenshot_${timestamp}_${hash}.png`;
}

// 关闭弹窗函数
async function closePopups(page) {
  try {
    await page.waitForTimeout(2000);
    
    for (const text of CONFIG.POPUP_TEXTS) {
      try {
        const selectors = [
          `button:has-text("${text}")`,
          `a:has-text("${text}")`,
          `div[role="button"]:has-text("${text}")`,
          `span:has-text("${text}")`
        ];
        
        for (const selector of selectors) {
          const element = await page.$(selector);
          if (element) {
            await element.click({ timeout: 3000 });
            console.log(`✅ 关闭弹窗: ${text}`);
            await page.waitForTimeout(1000);
            return true;
          }
        }
      } catch (e) {
        // 忽略单个选择器错误
      }
    }
    
    return false;
  } catch (error) {
    console.log(`⚠️ 弹窗处理异常: ${error.message}`);
    return false;
  }
}

// 核心截图函数
async function takeScreenshot(url, options = {}) {
  let browser = null;
  let context = null;
  let page = null;
  
  try {
    browser = await chromium.launch({
      headless: options.headless !== false,
      args: [
        '--no-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        '--ignore-certificate-errors',
        '--disable-popup-blocking'
      ]
    });
    
    context = await browser.newContext({
      viewport: CONFIG.VIEWPORT,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      locale: 'en-US',
      timezoneId: 'America/New_York',
      ignoreHTTPSErrors: true
    });
    
    await context.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
      Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
      window.chrome = { runtime: {} };
    });
    
    page = await context.newPage();
    
    console.log(`🔄 正在访问: ${url}`);
    await page.goto(url, {
      waitUntil: 'domcontentloaded',
      timeout: CONFIG.TIMEOUT
    });
    
    await closePopups(page);
    
    try {
      await page.waitForLoadState('networkidle', { timeout: 15000 });
    } catch (e) {
      console.log('⚠️ 网络未完全稳定，继续截图');
    }
    
    // 滚动页面触发懒加载
    await page.evaluate(() => {
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
    });
    
    const filename = generateFilename(url);
    const screenshotPath = path.join(CONFIG.SCREENSHOT_DIR, filename);
    
    await page.screenshot({
      path: screenshotPath,
      fullPage: true,
      animations: 'disabled'
    });
    
    console.log(`✅ 截图成功: ${screenshotPath}`);
    
    return {
      success: true,
      filename: filename,
      path: screenshotPath,
      url: url,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error(`❌ 截图失败: ${error.message}`);
    return {
      success: false,
      error: error.message,
      url: url,
      timestamp: new Date().toISOString()
    };
  } finally {
    try {
      if (page) await page.close();
      if (context) await context.close();
      if (browser) await browser.close();
    } catch (e) {
      console.error('资源清理异常:', e.message);
    }
  }
}

// API 路由
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'screenshot-api',
    timestamp: new Date().toISOString()
  });
});

app.post('/screenshot', async (req, res) => {
  const { url, options = {} } = req.body;
  
  if (!url) {
    return res.status(400).json({
      success: false,
      error: 'URL参数必填'
    });
  }
  
  try {
    new URL(url);
  } catch (e) {
    return res.status(400).json({
      success: false,
      error: 'URL格式无效'
    });
  }
  
  console.log(`📸 收到截图请求: ${url}`);
  
  const result = await takeScreenshot(url, options);
  
  if (result.success) {
    res.json({
      success: true,
      data: {
        filename: result.filename,
        path: result.path,
        url: result.url,
        timestamp: result.timestamp
      }
    });
  } else {
    res.status(500).json({
      success: false,
      error: result.error,
      url: result.url,
      timestamp: result.timestamp
    });
  }
});

app.post('/screenshot/batch', async (req, res) => {
  const { urls, options = {} } = req.body;
  
  if (!Array.isArray(urls) || urls.length === 0) {
    return res.status(400).json({
      success: false,
      error: 'urls参数必须是非空数组'
    });
  }
  
  if (urls.length > 10) {
    return res.status(400).json({
      success: false,
      error: '单次批量请求最多支持10个URL'
    });
  }
  
  console.log(`📸 收到批量截图请求: ${urls.length} 个URL`);
  
  const results = [];
  
  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    console.log(`[${i + 1}/${urls.length}] 处理: ${url}`);
    
    try {
      new URL(url);
      const result = await takeScreenshot(url, options);
      results.push(result);
    } catch (e) {
      results.push({
        success: false,
        error: 'URL格式无效',
        url: url,
        timestamp: new Date().toISOString()
      });
    }
    
    if (i < urls.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
  
  const successCount = results.filter(r => r.success).length;
  
  res.json({
    success: true,
    summary: {
      total: urls.length,
      success: successCount,
      failed: urls.length - successCount
    },
    results: results
  });
});

app.get('/screenshot/:filename', (req, res) => {
  const { filename } = req.params;
  const filePath = path.join(CONFIG.SCREENSHOT_DIR, filename);
  
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({
      success: false,
      error: '截图文件不存在'
    });
  }
  
  res.sendFile(filePath);
});

app.get('/screenshots', (req, res) => {
  try {
    const files = fs.readdirSync(CONFIG.SCREENSHOT_DIR)
      .filter(file => file.endsWith('.png'))
      .map(file => {
        const filePath = path.join(CONFIG.SCREENSHOT_DIR, file);
        const stats = fs.statSync(filePath);
        return {
          filename: file,
          size: stats.size,
          created: stats.birthtime,
          modified: stats.mtime
        };
      })
      .sort((a, b) => b.created - a.created);
    
    res.json({
      success: true,
      count: files.length,
      files: files
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.listen(CONFIG.PORT, () => {
  console.log('🚀 截图服务已启动');
  console.log(`📡 服务地址: http://localhost:${CONFIG.PORT}`);
  console.log(`📁 截图目录: ${CONFIG.SCREENSHOT_DIR}`);
  console.log('\n📋 API接口:');
  console.log(`  GET  /health                    - 健康检查`);
  console.log(`  POST /screenshot                - 单个URL截图`);
  console.log(`  POST /screenshot/batch          - 批量URL截图`);
  console.log(`  GET  /screenshot/:filename      - 获取截图文件`);
  console.log(`  GET  /screenshots               - 列出所有截图`);
});

module.exports = app;