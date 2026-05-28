import streamlit as st
from app import api_request


st.title("职业院校英语虚拟教研社区")
st.subheader("登录")

with st.form("login_form"):
    phone = st.text_input("手机号", max_chars=11)
    password = st.text_input("密码", type="password")
    submit = st.form_submit_button("登录", use_container_width=True)

if submit:
    if not phone or not password:
        st.warning("请输入手机号和密码")

    result = api_request("POST", "/auth/login", data={"phone": phone, "password": password})

    if result and result["code"] == 200:
        # 保存登录状态
        st.session_state.token = result["access_token"]
        st.session_state.current_user = result["user"]
        st.success("登录成功！正在跳转...")
        st.switch_page("pages/1_首页.py")