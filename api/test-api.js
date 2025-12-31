const axios = require('axios');

const API_BASE = 'http://localhost:3000';

async function testAPI() {
  console.log('🧪 开始API测试\n');
  
  try {
    // 1. 健康检查
    console.log('📋 健康检查...');
    const health = await axios.get(`${API_BASE}/health`);
    console.log('✅ 服务状态:', health.data);
    
    // 2. 单个URL截图
    console.log('\n📸 单个URL截图测试...');
    const singleResult = await axios.post(`${API_BASE}/screenshot`, {
      url: 'https://wavelifesciences.com/pipeline/research-and-development/',
      options: { headless: true }
    }, { timeout: 180000 });
    console.log('✅ 单个截图结果:', singleResult.data);
    
    // 3. 批量URL截图
    console.log('\n📸 批量URL截图测试...');
    const batchResult = await axios.post(`${API_BASE}/screenshot/batch`, {
      urls: [
        'https://www.alnylam.com/alnylam-rnai-pipeline',
        'https://arrowheadpharma.com/pipeline/'
      ],
      options: { headless: true }
    }, { timeout: 300000 });
    console.log('✅ 批量截图结果:', batchResult.data);
    
    // 4. 获取截图列表
    console.log('\n📋 获取截图列表...');
    const screenshots = await axios.get(`${API_BASE}/screenshots`);
    console.log('✅ 截图列表:', screenshots.data);
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    if (error.response) {
      console.error('📄 错误响应:', error.response.data);
    }
  }
}

// 检查服务
async function checkService() {
  try {
    await axios.get(`${API_BASE}/health`, { timeout: 5000 });
    console.log('✅ 服务已启动\n');
    return true;
  } catch (error) {
    console.log('❌ 服务未启动，请先运行: node start.js');
    return false;
  }
}

async function main() {
  const ready = await checkService();
  if (ready) {
    await testAPI();
  }
}

main().catch(console.error);