# -*- coding: utf-8 -*-
# @Time    : 2025/5/11 19:40

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "虚拟教研社区系统"
    API_V1_STR: str = "/api/v1"

    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD","123456")
    DB_NAME: str = os.getenv("DB_NAME", "teaching_research")

    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-it-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # 豆包API配置
    DOUBAO_API_KEY: str = os.getenv("DOUBAO_API_KEY", "")

    # 文件上传配置
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB


settings = Settings()