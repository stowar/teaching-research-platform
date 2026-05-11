# -*- coding: utf-8 -*-
# @Time    : 2026/5/11 20:49
import requests
from backend.core.config import settings

BASE_URL = "http://localhost:8000" + settings.API_V1_STR

def health_check():
    """测试后端连接"""
    try:
        response = requests.get(BASE_URL + "/health")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    print(health_check())