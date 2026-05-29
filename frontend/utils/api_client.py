# -*- coding: utf-8 -*-
# @Time    : 2026/5/11 20:49
import requests
import streamlit as st
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
BACKEND_URL = urljoin(BASE_URL, API_PREFIX.lstrip('/'))

def health_check():
    """测试后端连接"""
    try:
        response = requests.get(BASE_URL + "/health")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 统一API请求封装（自带请求拦截器）
def api_request(method, endpoint, data=None, params=None):
    """
    统一API请求函数，自动添加Token请求头，统一处理响应错误
    """
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    url = f"{BACKEND_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, json=data)

        # 统一响应处理
        result = response.json()

        # 401未登录：清除状态跳转到登录页
        if response.status_code == 401:
            st.session_state.token = None
            st.session_state.current_user = None
            st.session_state.page = "login"
            st.error("登录已过期，请重新登录")
            st.rerun()

        # 403无权限
        elif response.status_code == 403:
            st.error("您没有权限访问该页面")
            return None

        # 其他错误
        elif response.status_code != 200:
            st.error(f"请求失败：{result.get('msg', '未知错误')}")
            return None

        return result

    except Exception as e:
        st.error(f"网络错误：{str(e)}")
        return None

if __name__ == '__main__':
    print(health_check())