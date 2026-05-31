from config import init_global_app, save_login_state, global_button, global_back_home_button
init_global_app()

import streamlit as st
import time
from utils.api_client import api_request

st.title("登录")

col = st.columns([2, 1.9, 2])
with col[1]:
    with st.form("login_form"):
        phone = st.text_input("手机号", max_chars=11)
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录", use_container_width=True)

    if submit:
        if not phone or not password:
            st.warning("请输入手机号和密码")
        else:
            result = api_request("POST", "/auth/login", data={"phone": phone, "password": password})
            if result and result.get("code") == 200:
                save_login_state(result["access_token"], result["user"])
                st.balloons()
                st.success("登录成功！正在跳转...")
                time.sleep(0.5)
                st.switch_page("app.py")
            elif result:
                st.error(result.get("msg", "登录失败"))
            else:
                st.error("网络错误，请稍后重试")

    if st.button("还没有账号？点击注册", use_container_width=True):
        st.switch_page("pages/register.py")
    if st.button("返回首页", use_container_width=True,type="primary"):
        st.switch_page("app.py")

global_button()
