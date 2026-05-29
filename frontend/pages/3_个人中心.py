from config import init_global_app, check_login_state,global_back_home_button,global_button
init_global_app()
check_login_state()

import streamlit as st

import streamlit as st
import pandas as pd
from utils.api_client import api_request


st.title("个人中心")

# 选项卡：查看信息 / 修改信息 / 修改密码
tab1, tab2, tab3 = st.tabs(["个人信息", "修改信息", "修改密码"])

with tab1:
    st.subheader("我的信息")
    user_info = {
        "信息项": ["手机号", "姓名", "学校", "职称", "注册时间", "更新时间"],
        "内容": [
            st.session_state.current_user['phone'],
            st.session_state.current_user['name'],
            st.session_state.current_user['school'],
            st.session_state.current_user['title'],
            st.session_state.current_user['create_time'],
            st.session_state.current_user['update_time']
        ]
    }
    df = pd.DataFrame(user_info)
    st.dataframe(df,hide_index=True)


with tab2:
    st.subheader("修改个人信息")
    with st.form("update_profile_form"):
        name = st.text_input("姓名", value=st.session_state.current_user["name"])
        school = st.text_input("学校", value=st.session_state.current_user["school"])
        title = st.text_input("职称", value=st.session_state.current_user["title"])
        submit = st.form_submit_button("保存修改", use_container_width=True)

    if submit:
        result = api_request("PUT", "/auth/me", data={
            "name": name,
            "school": school,
            "title": title
        })

        if result and result["code"] == 200:
            st.session_state.current_user = result["data"]
            st.success("信息修改成功")
            st.rerun()

with tab3:
    st.subheader("修改密码")
    with st.form("change_password_form"):
        old_password = st.text_input("原密码", type="password")
        new_password = st.text_input("新密码", type="password")
        confirm_password = st.text_input("确认新密码", type="password")
        submit = st.form_submit_button("修改密码", use_container_width=True)

    if submit:
        if new_password != confirm_password:
            st.warning("两次输入的新密码不一致")

        result = api_request("PUT", "/auth/password", data={
            "old_password": old_password,
            "new_password": new_password
        })

        if result and result["code"] == 200:
            st.success("密码修改成功，请重新登录")
            st.session_state.token = None
            st.session_state.current_user = None
            st.switch_page("pages/login.py")

global_back_home_button()
global_button()