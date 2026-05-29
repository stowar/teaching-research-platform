from config import init_global_app, check_login_state,global_back_home_button,global_button
init_global_app()
check_login_state()

import streamlit as st

import streamlit as st
import pandas as pd
from utils.api_client import api_request


# 权限校验：只有管理员能访问
if st.session_state.current_user["role"] != "admin":
    st.error("您没有权限访问该页面")
    st.stop()

st.title("用户管理")

# 搜索和筛选
col1, col2 = st.columns([3, 1])
with col1:
    search_keyword = st.text_input("搜索用户(id)")
with col2:
    status_filter = st.selectbox("状态筛选", ["全部", "正常", "禁用"])

# 获取回应
params = {}
if search_keyword:
    params["keyword"] = search_keyword
if status_filter != "全部":
    params["status"] = 1 if status_filter == "正常" else 0

result = api_request("GET", f"/admin/{search_keyword}", params=params)

if result["code"] == 200:
    users = result["data"]

    # 获取用户列表
    st.subheader("用户列表")
    if users:
        df = pd.DataFrame(columns=['ID', '手机号', '姓名', '学校', '职称', '角色', '状态', '注册时间', '更新时间'])
        for user in users:
            df.loc[len(df)] = (user["id"], user["phone"], user["name"], user["school"], user["title"], user["role"], user["status"], user["create_time"], user["update_time"])
        df.index = df.index + 1
        st.dataframe(df)

    # 编辑和禁用用户
    st.subheader("操作用户")
    user_id = st.number_input("输入要操作的用户ID", min_value=1, step=1)
    action = st.radio("操作类型", ["编辑信息", "禁用/启用用户"])

    if action == "编辑信息":
        user_result = api_request("GET", f"/admin/{user_id}")
        if user_result and user_result["code"] == 200:
            users = user_result["data"]
            for user in users: pass
            with st.form("edit_user_form"):
                name = st.text_input("姓名", value=user["name"])
                school = st.text_input("学校", value=user["school"])
                title = st.text_input("职称", value=user["title"])

                submit = st.form_submit_button("保存修改", use_container_width=True)

            if submit:
                update_result = api_request("PUT", f"/admin/{user_id}", data={
                    "name": name,
                    "school": school,
                    "title": title
                })

                if update_result and update_result["code"] == 200:
                    st.success("用户信息修改成功")
                    st.rerun()

    elif action == "禁用/启用用户":
        if st.button("执行操作", use_container_width=True, type="primary"):
            toggle_result = api_request("PUT", f"/admin/users/{user_id}/toggle")
            if toggle_result and toggle_result["code"] == 200:
                st.success("用户状态修改成功")
                st.rerun()
else:
    st.info("没有找到符合条件的用户")

global_back_home_button()
global_button()