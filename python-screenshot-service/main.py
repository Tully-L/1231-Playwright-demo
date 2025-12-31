from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import asyncio
import os
import hashlib
import time
from datetime import datetime
from screenshot_service import ScreenshotService

app = FastAPI(title="Python Screenshot Service", version="1.0.0")

# 配置
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 初始化截图服务
screenshot_service = ScreenshotService(SCREENSHOT_DIR)

class ScreenshotRequest(BaseModel):
    url: HttpUrl
    options: Optional[dict] = {}

class BatchScreenshotRequest(BaseModel):
    urls: List[HttpUrl]
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
    return {
        "status": "ok",
        "service": "python-screenshot-stealth",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/screenshot", response_model=ScreenshotResponse)
async def take_screenshot(request: ScreenshotRequest):
    """单个URL截图"""
    url = str(request.url)
    print(f"📸 收到截图请求: {url}")
    
    try:
        result = await screenshot_service.take_screenshot(url, request.options)
        print(f"📋 截图服务返回: {result}")
        
        # 直接返回结果，不进行额外处理
        if result.get("success"):
            return ScreenshotResponse(
                success=True,
                filename=result.get("filename"),
                path=result.get("path"),
                url=url,
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                error=None
            )
        else:
            return ScreenshotResponse(
                success=False,
                filename=None,
                path=None,
                url=url,
                timestamp=result.get("timestamp", datetime.now().isoformat()),
                error=result.get("error", "未知错误")
            )
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ API异常: {error_msg}")
        import traceback
        traceback.print_exc()
        
        return ScreenshotResponse(
            success=False,
            filename=None,
            path=None,
            url=url,
            timestamp=datetime.now().isoformat(),
            error=error_msg
        )

@app.post("/screenshot/batch")
async def take_batch_screenshots(request: BatchScreenshotRequest):
    """批量URL截图"""
    urls = [str(url) for url in request.urls]
    
    if len(urls) > 10:
        raise HTTPException(status_code=400, detail="单次批量请求最多支持10个URL")
    
    print(f"📸 收到批量截图请求: {len(urls)} 个URL")
    
    results = []
    for i, url in enumerate(urls):
        print(f"[{i + 1}/{len(urls)}] 处理: {url}")
        
        try:
            result = await screenshot_service.take_screenshot(url, request.options)
            results.append(ScreenshotResponse(**result))
        except Exception as e:
            results.append(ScreenshotResponse(
                success=False,
                url=url,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            ))
        
        # 批量请求间隔
        if i < len(urls) - 1:
            await asyncio.sleep(2)
    
    success_count = sum(1 for r in results if r.success)
    
    return {
        "success": True,
        "summary": {
            "total": len(urls),
            "success": success_count,
            "failed": len(urls) - success_count
        },
        "results": results
    }

@app.get("/screenshots")
async def list_screenshots():
    """获取截图列表"""
    try:
        files = []
        for filename in os.listdir(SCREENSHOT_DIR):
            if filename.endswith('.png'):
                filepath = os.path.join(SCREENSHOT_DIR, filename)
                stat = os.stat(filepath)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        files.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "success": True,
            "count": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)