import os

import streamlit as st
import json
import time
from datetime import datetime, date


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(BASE_DIR, "static", "style.css")


class _DateTimeEncoder(json.JSONEncoder):
    """处理 datetime/date 对象的 JSON 序列化器"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def _safe_json_dumps(data):
    """安全地将数据序列化为 JSON 字符串，兼容 datetime 类型"""
    try:
        return json.dumps(data, ensure_ascii=False, cls=_DateTimeEncoder)
    except (TypeError, ValueError):
        # 兜底：将所有值转为字符串后再序列化
        return json.dumps({k: str(v) for k, v in data.items()}, ensure_ascii=False)

def init_global_app():
    """
    全局初始化入口，必须是每个页面的第一行可执行代码
    功能：1. 统一页面配置 2. 同步登录状态 3. 全局路由守卫 4.加载static/style.css中的全局样式
    """
    # 1. 全局统一页面配置（所有页面自动生效）
    st.set_page_config(
        page_title="虚拟教研社区",
        layout="wide",
        initial_sidebar_state="collapsed",
        page_icon="📚"
    )
    # 2. 强制初始化所有全局状态（确保所有页面键名完全一致）
    st.session_state.token = st.session_state.get("token", None)
    st.session_state.current_user = st.session_state.get("current_user", None)
    st.session_state.page = st.session_state.get("page", "home")
    st.session_state.prompt = st.session_state.get("prompt", "")

    # 3. 从URL自动恢复登录状态（刷新/切换页面都不丢失）
    params = st.query_params
    if "token" in params and st.session_state.token is None:
        st.session_state.token = params["token"]
    if "current_user" in params and st.session_state.current_user is None:
        try:
            st.session_state.current_user = json.loads(params["current_user"])
        except:
            pass

    # 如果session中有登录状态但URL没有参数，自动补全
    if st.session_state.token is not None and "token" not in params:
        st.query_params["token"] = st.session_state.token
        try:
            st.query_params["current_user"] = _safe_json_dumps(st.session_state.current_user)
        except Exception:
            pass

    # markdown注入
    try:
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"全局样式文件未找到: {CSS_PATH}")


def check_login_state():
    # 只有登录页和注册页允许未登录访问
    if not st.session_state.token:
        st.warning("请先登录！")
        time.sleep(1)
        st.switch_page("app.py")
        st.stop()

def save_login_state(token, user):
    """全局统一保存登录状态，登录成功后调用"""
    st.session_state.token = token
    st.session_state.current_user = user
    st.query_params["token"] = token
    try:
        st.query_params["current_user"] = _safe_json_dumps(user)
    except Exception:
        pass

def global_back_home_button():
    """全局统一返回首页，用于退出登录、切换用户等操作"""
    col = st.columns([1, 2, 1])
    with col[1]:
        if st.button("返回首页",use_container_width=True,type="primary"):
            st.switch_page("app.py")

def global_button():
    st.markdown("<p style='text-align: center; color: #999; margin-top: 3rem;'>© 2026 虚拟教研社区 版权所有</p>",
                unsafe_allow_html=True)