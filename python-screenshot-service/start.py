#!/usr/bin/env python3
"""
启动脚本 - 启动Python截图服务
"""
import uvicorn
import os
import sys

def main():
    print("🚀 启动 Python Screenshot Service")
    print("📡 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("📁 截图目录: ./screenshots")
    print("\n📋 API接口:")
    print("  GET  /health                    - 健康检查")
    print("  POST /screenshot                - 单个URL截图")
    print("  POST /screenshot/batch          - 批量URL截图")
    print("  GET  /screenshots               - 列出所有截图")
    print("\n按 Ctrl+C 停止服务\n")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()