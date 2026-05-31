from config import init_global_app, check_login_state, global_back_home_button, global_button, save_login_state
init_global_app()
check_login_state()

import streamlit as st
from utils.api_client import api_request

st.title("个人中心")

# 选项卡：查看信息 / 修改信息 / 修改密码
tab1, tab2, tab3 = st.tabs(["个人信息", "修改信息", "修改密码"])

# 获取当前用户信息，优先使用 session_state 中的最新数据
if not st.session_state.get("current_user"):
    st.session_state.current_user = {}
user = st.session_state.current_user

with tab1:
    st.subheader("我的信息")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:2rem 1rem;">
            <div style="font-size:4rem; margin-bottom:0.5rem;">👤</div>
            <div style="font-size:1.5rem; font-weight:700;">{user.get('name') or '未命名'}</div>
            <div style="color:#666; margin-top:0.3rem;">{user.get('school') or ''}</div>
            <div style="margin-top:0.5rem;">
                <span style="background:#2563eb; color:white; padding:0.2rem 0.8rem; border-radius:12px; font-size:0.85rem;">
                    {user.get('title') or '教师'}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("**手机号：** " + (user.get('phone') or '-'))
        st.markdown("**学校：** " + (user.get('school') or '-'))
        st.markdown("**职称：** " + (user.get('title') or '-'))
        st.markdown("**角色：** " + ("管理员" if user.get('role') == "admin" else "普通用户"))
        st.markdown("**注册时间：** " + str(user.get('create_time') or '-'))
        st.markdown("**更新时间：** " + str(user.get('update_time') or '-'))

with tab2:
    st.subheader("修改个人信息")
    with st.form("update_profile_form"):
        name = st.text_input("姓名", value=user.get("name", ""))
        school = st.text_input("学校", value=user.get("school", ""))
        title = st.text_input("职称", value=user.get("title", ""))
        submit = st.form_submit_button("保存修改", use_container_width=True)

    if submit:
        result = api_request("PUT", "/users/me", data={"name": name, "school": school, "title": title})
        if result and result.get("code") == 200:
            updated_user = result.get("data")
            if updated_user:
                # 统一保存登录状态（同步 session_state + URL query params）
                save_login_state(st.session_state.token, updated_user)
                st.session_state.current_user = updated_user
            st.success("信息修改成功")
            st.rerun()
        else:
            error_msg = result.get("msg", "修改失败，请稍后重试") if result else "修改失败，请稍后重试"
            st.error(error_msg)

with tab3:
    st.subheader("修改密码")
    with st.form("change_password_form"):
        old_password = st.text_input("原密码", type="password")
        new_password = st.text_input("新密码", type="password")
        confirm_password = st.text_input("确认新密码", type="password")
        submit = st.form_submit_button("修改密码", use_container_width=True)

    if submit:
        if not old_password or not new_password:
            st.warning("请填写完整")
        elif new_password != confirm_password:
            st.warning("两次输入的新密码不一致")
        else:
            result = api_request("PUT", "/users/password", data={
                "old_password": old_password,
                "new_password": new_password
            })
            if result and result.get("code") == 200:
                st.success("密码修改成功，请重新登录")
                st.session_state.token = None
                st.session_state.current_user = None
                st.query_params.clear()
                st.switch_page("pages/login.py")
            elif result:
                st.error(result.get("msg", "修改失败"))
            else:
                st.error("网络错误")

global_back_home_button()
global_button()
