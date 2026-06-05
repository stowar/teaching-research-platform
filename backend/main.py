# -*- coding: utf-8 -*-
# @ Time    2026/5/11 20:05

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.api.v1.auth import router as auth_router
from backend.api.v1.users import router_user as users_router
from backend.api.v1.admin import router_admin as admin_router
from backend.api.v1.sentiment import router as sentiment_router
from backend.api.v1.community import router as community_router



app = FastAPI(title=settings.PROJECT_NAME)

# 注册认证路由
app.include_router(auth_router,prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(sentiment_router, prefix=settings.API_V1_STR)
app.include_router(community_router, prefix=settings.API_V1_STR)

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

@app.get("/")
def root():
    return {"message": "教研管理系统API服务运行中"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="localhost", port=8000, reload=True)