# -*- coding: utf-8 -*-
# @ Time    2026/5/11 20:05

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查接口
@app.get(f"{settings.API_V1_STR}/health", tags=["系统"])
def health_check():
    return {"status": "ok", "message": "系统运行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="localhost", port=8000, reload=True)