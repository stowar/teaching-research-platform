from config import init_global_app, global_button
init_global_app()

import streamlit as st
from utils.api_client import api_request

st.title("注册")

cols = st.columns([1, 2, 1])
with cols[1]:
    with st.form("register_form"):
        phone = st.text_input("手机号", max_chars=11)
        password = st.text_input("密码", type="password")
        current_password = st.text_input("确认密码", type="password")
        name = st.text_input("姓名")
        school = st.text_input("学校")
        title = st.text_input("职称")
        submit = st.form_submit_button("注册", use_container_width=True)

    if submit:
        if not phone or not password:
            st.warning("手机号和密码不能为空")
        elif password != current_password:
            st.warning("两次输入的密码不一致")
        else:
            result = api_request("POST", "/auth/register", data={
                "phone": phone, "password": password, "name": name,
                "school": school, "title": title
            })
            if result and result.get("code") == 200:
                st.success("注册成功！")
                st.balloons()
                st.switch_page("pages/login.py")
            elif result:
                st.error(result.get("msg", "注册失败"))
            else:
                st.error("网络错误，请稍后重试")

    if st.button("已有账号？点击登录", use_container_width=True):
        st.switch_page("pages/login.py")
    if st.button("返回首页", use_container_width=True, type="primary"):
        st.switch_page("app.py")
    global_button()
