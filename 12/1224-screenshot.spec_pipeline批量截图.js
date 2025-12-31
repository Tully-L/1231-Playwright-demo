const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// ========== 核心配置 ==========
// 截图保存目录（请确认路径存在或修改为你的实际路径）
const SCREENSHOT_DIR = path.resolve('E:/25_wjsz/work/1218-AI巡检/screenshot-service/screenshots/pipeline_sites');
// 超时配置（毫秒）
const CONFIG = {
  PAGE_LOAD_TIMEOUT: 80000,      // 页面加载超时（延长至80秒，适配国外网站）
  POPUP_WAIT_TIMEOUT: 10000,     // 弹窗等待超时
  GLOBAL_TEST_TIMEOUT: 150000,   // 单个用例总超时（150秒）
  NETWORK_IDLE_TIMEOUT: 15000,   // 网络空闲等待超时
  POPUP_SELECTOR: 'button:has-text("Accept")' // 通用弹窗关闭选择器
};

// ========== 完整网站列表（包含你提供的所有网址） ==========
const WEBSITES = {
  alnylam: { url: 'https://www.alnylam.com/alnylam-rnai-pipeline' },
  arrowheadpharma: { url: 'https://arrowheadpharma.com/pipeline/' },
  ionis: { url: 'https://ionis.com/pipeline/independent?_format=json' },
  wavelifesciences: { url: 'https://wavelifesciences.com/pipeline/research-and-development/' },
  silencetherapeutics: { url: 'https://silence-therapeutics.com/our-pipeline/default.aspx' },
  aviditybiosciences: { url: 'https://www.aviditybiosciences.com/pipeline/pipeline-overview' },
  lilly: { url: 'https://www.lilly.com/innovation/clinical-development-pipeline' },
  novonordisk: { url: 'https://www.novonordisk.com/science-and-technology/r-d-pipeline.html' },
  novartis: { url: 'https://www.novartis.com/research-development/novartis-pipeline' },
  regeneron: { url: 'https://www.regeneron.com/science/investigational-pipeline' },
  dynetx: { url: 'https://www.dyne-tx.com/pipeline/' },
  denalitherapeutics: { url: 'https://www.denalitherapeutics.com/pipeline' },
  adarx: { url: 'https://www.adarx.com/pipeline/' },
  ribolia: { url: 'https://www.ribolia.com/pipeline' },
  intelliatx: { url: 'https://www.intelliatx.com/pipeline/' },
  beamtx: { url: 'https://beamtx.com/pipeline/' },
  astrazeneca: { url: 'https://www.astrazeneca.com/our-therapy-areas/pipeline.html' },
  roche: { url: 'https://www.roche.com/solutions/pipeline' },
  atalantatx: { url: 'https://www.atalantatx.com/pipeline/' },
  sarepta: { url: 'https://www.sarepta.com/products-pipeline/pipelinel' },
  ronatherapeutics: { url: 'https://www.ronatherapeutics.com/pipeline' },
  crisprtx: { url: 'https://crisprtx.com/pipeline' },
  olixpharma: { url: 'https://olixpharma.com/rnd/rnd03.php' },
  entradatx: { url: 'https://www.entradatx.com/pipeline' },
  pepgen: { url: 'https://www.pepgen.com/pipeline/' },
  tangramtx: { url: 'https://tangramtx.com/pipeline/' },
  switchthera: { url: 'https://www.switchthera.com/our-science/' },
  arobiotx: { url: 'https://www.arobiotx.com/pipeline' },
  sirnaomics: { url: 'https://www.sirnaomics.com/cn/science-pipeline/pipeline/' },
  sanegenebio: { url: 'https://www.sanegenebio.com/pipeline/' },
  siriusrna: { url: 'https://www.siriusrna.com/pipeline/index.html#pipeline' },
  synerk: { url: 'https://synerk.cn/productinfo/883480.html' },
  aligos: { url: 'https://aligos.com/science/scientific-overview/' },
  arbutusbio: { url: 'https://www.arbutusbio.com/pipeline/' },
  proqr: { url: 'https://www.proqr.com/pipeline' },
  metagenomi: { url: 'https://metagenomi.co/pipeline' },
  camp4tx: { url: 'https://www.camp4tx.com/pipeline/' },
  minatx: { url: 'https://minatx.com/pipeline/' },
  ractigen: { url: 'https://www.ractigen.com/pipeline/' },
  judobio: { url: 'https://judo.bio/pipeline/' },
  rigerna: { url: 'https://www.rigerna.com/page/cpgx/' },
  siranbio: { url: 'https://www.siranbio.com/page/cpgx/' },
  visirna: { url: 'https://www.visirna.com/pages/client/pplinea?version=v1' },
  hygieiapharma: { url: 'https://www.hygieiapharma.com/Pipeline/3.html' },
  bebettermed: { url: 'http://www.bebettermed.com/goods-2-view.html#rd_4' },
  bebettermedcn: { url: 'http://www.bebettermed.cn/goods-2-view.html#rd_4' },
  apellis: { url: 'https://apellis.com/our-science/our-pipeline/' },
  biogen: { url: 'https://www.biogen.com/science-and-innovation/pipeline.html' },
  amgenpipeline: { url: 'https://www.amgenpipeline.com/' },
  jnj: { url: 'https://www.investor.jnj.com/pipeline/development-pipeline/default.aspx' },
  takeda: { url: 'https://www.takeda.com/science/pipeline/' },
  gsk: { url: 'https://www.gsk.com/en-gb/innovation/pipeline/' },
  sanofi: { url: 'https://www.sanofi.com/en/our-science/our-pipeline' },
  abbvie: { url: 'https://www.abbvie.com/science/pipeline.html' },
  merck: { url: 'https://www.merck.com/research/product-pipeline/' },
  gilead: { url: 'https://www.gilead.com/science/pipeline' },
  boehringer: { url: 'https://www.boehringer-ingelheim.com/science-innovation/human-health-innovation/clinical-pipeline' },
  pfizer: { url: 'https://www.pfizer.com/science/drug-product-pipeline' },
  csl: { url: 'https://www.csl.com/research-and-development/product-pipeline' },
  bms: { url: 'https://www.bms.com/researchers-and-partners/in-the-pipeline.html' },
  bayer: { url: 'https://www.bayer.com/en/pharma/development-pipeline' }
};

// ========== 初始化：创建截图目录 ==========
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  console.log(`✅ 截图目录已创建：${SCREENSHOT_DIR}`);
}

// ========== 批量截图核心逻辑 ==========
Object.entries(WEBSITES).forEach(([siteKey, siteInfo]) => {
  test(`截图：${siteKey.toUpperCase()} (${siteKey})`, async ({ page }, testInfo) => {
    // 1. 设置超时和页面配置
    testInfo.setTimeout(CONFIG.GLOBAL_TEST_TIMEOUT);
    page.setDefaultTimeout(CONFIG.PAGE_LOAD_TIMEOUT);
    
    // 模拟真实浏览器（降低反爬概率）
    await page.setExtraHTTPHeaders({
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'
    });

    try {
      console.log(`\n====================================`);
      console.log(`开始处理：${siteKey.toUpperCase()}`);
      console.log(`目标网址：${siteInfo.url}`);

      // 2. 导航到目标网站（仅等待DOM加载完成）
      await page.goto(siteInfo.url, {
        waitUntil: 'domcontentloaded',
        timeout: CONFIG.PAGE_LOAD_TIMEOUT,
        referer: 'https://www.google.com'
      });
      console.log(`ℹ️ ${siteKey.toUpperCase()} - 页面DOM加载完成`);

      // 3. 处理Cookie/隐私弹窗（通用容错）
      try {
        await page.waitForSelector(CONFIG.POPUP_SELECTOR, {
          state: 'visible',
          timeout: CONFIG.POPUP_WAIT_TIMEOUT
        });
        await page.click(CONFIG.POPUP_SELECTOR, { timeout: 5000 });
        console.log(`✅ ${siteKey.toUpperCase()} - 关闭Cookie弹窗`);
      } catch (popupErr) {
        console.log(`ℹ️ ${siteKey.toUpperCase()} - 未检测到Cookie弹窗，跳过`);
      }

      // 4. 等待页面稳定（容错：网络空闲超时则跳过）
      try {
        await page.waitForLoadState('networkidle', { timeout: CONFIG.NETWORK_IDLE_TIMEOUT });
        console.log(`ℹ️ ${siteKey.toUpperCase()} - 页面网络已稳定`);
      } catch (networkErr) {
        console.log(`ℹ️ ${siteKey.toUpperCase()} - 网络未稳定（超时），继续截图`);
      }
      // 额外延迟确保动态内容渲染
      await page.waitForTimeout(3000);

      // 5. 截图（核心：移除PNG不支持的quality参数）
      const screenshotPath = path.join(SCREENSHOT_DIR, `${siteKey}-pipeline.png`);
      await page.screenshot({
        path: screenshotPath,
        fullPage: true,  // 截取完整页面（含滚动内容）
        omitBackground: false
      });

      // 6. 成功日志
      console.log(`✅ ${siteKey.toUpperCase()} - 截图成功`);
      console.log(`✅ 保存路径：${screenshotPath}`);

    } catch (err) {
      // 异常处理：记录错误但不中断其他用例
      const errorMsg = `❌ ${siteKey.toUpperCase()} - 处理失败：${err.message}`;
      console.error(errorMsg);
      // 标记测试失败（不影响批量执行）
      expect(false, errorMsg).toBe(true);
    }
  });
});