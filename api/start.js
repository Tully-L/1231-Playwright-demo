#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');

console.log('🚀 启动截图API服务...\n');

// 检查依赖
if (!fs.existsSync('node_modules')) {
  console.log('📦 正在安装依赖...');
  const install = spawn('npm', ['install'], { stdio: 'inherit' });
  
  install.on('close', (code) => {
    if (code === 0) {
      console.log('✅ 依赖安装完成\n');
      startService();
    } else {
      console.error('❌ 依赖安装失败');
      process.exit(1);
    }
  });
} else {
  startService();
}

function startService() {
  console.log('🌐 启动截图API服务...');
  
  const service = spawn('node', ['screenshot-api.js'], {
    stdio: 'inherit',
    cwd: __dirname
  });
  
  service.on('error', (err) => {
    console.error('❌ 服务启动失败:', err.message);
    process.exit(1);
  });
  
  service.on('close', (code) => {
    console.log(`\n📴 服务已停止 (退出码: ${code})`);
  });
  
  // 优雅关闭
  process.on('SIGINT', () => {
    console.log('\n🛑 正在关闭服务...');
    service.kill('SIGINT');
  });
}