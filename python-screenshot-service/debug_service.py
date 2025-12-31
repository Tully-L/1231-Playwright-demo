#!/usr/bin/env python3
"""
调试版服务 - 详细日志输出
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import asyncio
import os
import sys
import traceback
from datetime import datetime
from screenshot_service import ScreenshotService

# 添加详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Debug Screenshot Service", version="1.0.0")

# 配置
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 初始化截图服务
screenshot_service = ScreenshotService(SCREENSHOT_DIR)

class ScreenshotRequest(BaseModel):
    url: HttpUrl
    options: Optional[dict] = {}

class ScreenshotResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    path: Optional[str] = None
    url: str
    timestamp: str
    error: Optional[str] = None

@app.get("/health")
async def health_check():
    logger.info("健康检查请求")
    return {
        "status": "ok",
        "service": "debug-screenshot-service",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/screenshot", response_model=ScreenshotResponse)
async def take_screenshot(request: ScreenshotRequest):
    """单个URL截图 - 调试版"""
    url = str(request.url)
    logger.info(f"📸 收到截图请求: {url}")
    logger.info(f"📋 请求选项: {request.options}")
    
    try:
        logger.info("🔄 开始调用截图服务...")
        
        # 直接调用服务
        result = await screenshot_service.take_screenshot(url, request.options)
        
        logger.info(f"📋 截图服务返回类型: {type(result)}")
        logger.info(f"📋 截图服务返回内容: {result}")
        
        # 检查结果
        if not isinstance(result, dict):
            error_msg = f"截图服务返回类型错误: {type(result)}"
            logger.error(error_msg)
            return ScreenshotResponse(
                success=False,
                filename=None,
                path=None,
                url=url,
                timestamp=datetime.now().isoformat(),
                error=error_msg
            )
        
        success = result.get("success", False)
        logger.info(f"📊 截图结果: success={success}")
        
        if success:
            filename = result.get("filename")
            path = result.get("path")
            timestamp = result.get("timestamp", datetime.now().isoformat())
            
            logger.info(f"✅ 截图成功: {filename}")
            
            return ScreenshotResponse(
                success=True,
                filename=filename,
                path=path,
                url=url,
                timestamp=timestamp,
                error=None
            )
        else:
            error = result.get("error", "未知错误")
            timestamp = result.get("timestamp", datetime.now().isoformat())
            
            logger.error(f"❌ 截图失败: {error}")
            
            return ScreenshotResponse(
                success=False,
                filename=None,
                path=None,
                url=url,
                timestamp=timestamp,
                error=error
            )
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ API异常: {error_msg}")
        logger.error(f"异常类型: {type(e).__name__}")
        logger.error("异常堆栈:")
        logger.error(traceback.format_exc())
        
        return ScreenshotResponse(
            success=False,
            filename=None,
            path=None,
            url=url,
            timestamp=datetime.now().isoformat(),
            error=f"API异常: {error_msg}"
        )

@app.get("/test-direct")
async def test_direct():
    """直接测试截图服务"""
    logger.info("🧪 直接测试截图服务")
    
    try:
        result = await screenshot_service.take_screenshot("https://httpbin.org/html")
        logger.info(f"直接测试结果: {result}")
        return {"direct_test": result}
    except Exception as e:
        logger.error(f"直接测试失败: {e}")
        logger.error(traceback.format_exc())
        return {"direct_test": {"success": False, "error": str(e)}}

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动调试版截图服务")
    print("📡 服务地址: http://localhost:8001")
    print("🔍 详细日志已启用")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")