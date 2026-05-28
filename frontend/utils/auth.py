import streamlit as st

def init_session_state():
    """初始化全局状态"""
    if "token" not in st.session_state:
        st.session_state.token = None
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "page" not in st.session_state:
        st.session_state.page = "login"

def check_login():
    """所有需要登录的页面，第一行就调用这个函数，未登录自动跳转到登录页"""
    if not st.session_state.token:
        st.warning("请先登录！")
        st.switch_page("pages/login.py")  # 自动跳转到登录页
        st.stop()  # 停止当前页面的后续执行