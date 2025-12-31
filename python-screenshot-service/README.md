# Python Screenshot Service

基于 Playwright + Stealth 的反检测截图服务，专门用于绕过 Cloudflare 等反爬保护。

## 特性

- ✅ **反检测**: 使用 playwright-stealth 绕过 Cloudflare
- ✅ **自动弹窗处理**: 智能识别并关闭各种弹窗
- ✅ **懒加载支持**: 自动滚动触发懒加载内容
- ✅ **批量截图**: 支持批量URL处理
- ✅ **完整截图**: 生成完整页面截图
- ✅ **RESTful API**: 标准HTTP接口

## 快速开始

### 1. 安装依赖

```bash
# 自动安装所有依赖
python install.py

# 或手动安装
pip install -r requirements.txt
playwright install chromium
```

### 2. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

### 3. 测试服务

```bash
python test_service.py
```

## API 接口

### 健康检查
```http
GET /health
```

### 单个URL截图
```http
POST /screenshot
Content-Type: application/json

{
  "url": "https://example.com",
  "options": {
    "headless": true
  }
}
```

### 批量URL截图
```http
POST /screenshot/batch
Content-Type: application/json

{
  "urls": [
    "https://example1.com",
    "https://example2.com"
  ],
  "options": {
    "headless": true
  }
}
```

### 获取截图列表
```http
GET /screenshots
```

## 配置说明

### 反检测特性
- 使用 playwright-stealth 插件
- 自定义 User-Agent 和浏览器指纹
- 禁用自动化检测特征
- 模拟真实用户行为

### 弹窗处理
自动识别并关闭以下类型的弹窗：
- Cookie 同意弹窗
- 隐私政策弹窗  
- 广告弹窗
- 订阅弹窗

### 懒加载处理
- 自动滚动页面
- 触发所有懒加载内容
- 等待内容完全加载

## 与现有服务集成

此服务可以与现有的 Express API 配合使用：

```javascript
// 在 Express API 中调用 Python 服务
const pythonScreenshot = await axios.post('http://localhost:8000/screenshot', {
  url: targetUrl,
  options: { headless: true }
});
```

## 目录结构

```
python-screenshot-service/
├── main.py              # FastAPI 主服务
├── screenshot_service.py # 核心截图逻辑
├── requirements.txt     # Python 依赖
├── install.py          # 安装脚本
├── test_service.py     # 测试脚本
├── screenshots/        # 截图存储目录
└── README.md          # 说明文档
```

## 性能优化

- 异步处理提高并发性能
- 资源自动清理避免内存泄漏
- 批量请求间隔控制
- 超时机制防止卡死

## 故障排除

### 常见问题

1. **Playwright 浏览器未安装**
   ```bash
   playwright install chromium
   ```

2. **Linux 系统依赖缺失**
   ```bash
   playwright install-deps chromium
   ```

3. **端口冲突**
   修改 `main.py` 中的端口号

4. **截图失败**
   检查目标网站是否可访问，增加超时时间