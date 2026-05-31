from config import init_global_app, check_login_state, global_back_home_button, global_button
init_global_app()
check_login_state()

import streamlit as st
from utils.api_client import api_request

# 权限校验：只有管理员能访问
if st.session_state.current_user.get("role") != "admin":
    st.error("您没有权限访问该页面")
    st.stop()

st.title("用户管理")

# 搜索和筛选
col1, col2 = st.columns([3, 1])
with col1:
    search_keyword = st.text_input("搜索用户（输入用户ID精确查询，留空查询全部）")
with col2:
    status_filter = st.selectbox("状态筛选", ["全部", "正常", "禁用"])

# 区分ID精确查询和列表查询
users = []
if search_keyword.strip():
    # 按ID精确查询
    try:
        user_id = int(search_keyword.strip())
        result = api_request("GET", f"/admin/{user_id}")
        if result and result.get("code") == 200:
            data = result.get("data")
            if isinstance(data, list):
                users = data
            elif isinstance(data, dict):
                users = [data]
    except ValueError:
        st.warning("用户ID必须是数字")
else:
    # 查询全部，带状态筛选
    params = {}
    if status_filter != "全部":
        params["status"] = 1 if status_filter == "正常" else 0
    result = api_request("GET", "/admin/", params=params if params else None)
    if result and result.get("code") == 200:
        data = result.get("data")
        if isinstance(data, list):
            users = data

# 展示用户列表
st.subheader(f"用户列表（共 {len(users)} 人）")
if users:
    # 准备展示数据
    display_data = []
    for u in users:
        display_data.append({
            "ID": u.get("id"),
            "手机号": u.get("phone"),
            "姓名": u.get("name"),
            "学校": u.get("school"),
            "职称": u.get("title"),
            "角色": u.get("role"),
            "状态": "正常" if u.get("status") == 1 else "禁用",
            "注册时间": u.get("create_time"),
        })
    st.dataframe(display_data, hide_index=True, use_container_width=True)
else:
    st.info("没有找到符合条件的用户")

st.divider()

# 操作用户
st.subheader("操作用户")
if users:
    # 提供下拉选择，避免手动输入ID
    user_options = {f"{u.get('id')} - {u.get('name')} ({u.get('phone')})": u for u in users}
    selected = st.selectbox("选择要操作用户", list(user_options.keys()))
    target_user = user_options[selected]
    target_id = target_user.get("id")

    tab_edit, tab_status = st.tabs(["编辑信息", "禁用/启用"])

    with tab_edit:
        with st.form("edit_user_form"):
            name = st.text_input("姓名", value=target_user.get("name", ""))
            school = st.text_input("学校", value=target_user.get("school", ""))
            title = st.text_input("职称", value=target_user.get("title", ""))
            submit = st.form_submit_button("保存修改", use_container_width=True)

        if submit:
            update_result = api_request("PUT", f"/admin/{target_id}", data={
                "name": name, "school": school, "title": title
            })
            if update_result and update_result.get("code") == 200:
                st.success("用户信息修改成功")
                st.rerun()
            else:
                st.error("修改失败")

    with tab_status:
        current_status = target_user.get("status")
        if current_status == 1:
            st.write(f"当前状态：**正常**")
            if target_user.get("role") == "admin":
                st.warning("管理员账号不能被禁用")
            else:
                if st.button("禁用该用户", use_container_width=True, type="primary"):
                    # 二次确认
                    if st.checkbox("我确认要禁用此用户", key="confirm_disable"):
                        toggle_result = api_request("DELETE", f"/admin/{target_id}")
                        if toggle_result and toggle_result.get("code") == 200:
                            st.success("用户已禁用")
                            st.rerun()
                        else:
                            st.error("操作失败")
        else:
            st.write(f"当前状态：**已禁用**")
            if st.button("启用该用户", use_container_width=True, type="primary"):
                if st.checkbox("我确认要启用此用户", key="confirm_enable"):
                    toggle_result = api_request("PUT", f"/admin/enable/{target_id}")
                    if toggle_result and toggle_result.get("code") == 200:
                        st.success("用户已启用")
                        st.rerun()
                    else:
                        st.error("操作失败")
else:
    st.info("请先查询出用户再进行操作")

global_back_home_button()
global_button()
