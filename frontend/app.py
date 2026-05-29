from config import init_global_app, save_login_state,global_back_home_button,global_button
init_global_app()

import streamlit as st
import time
from utils.api_client import api_request


# todo:回调函数区域
def go_to_Home():
    st.session_state.page = "home"

def go_to_login():
    st.session_state.page = "login"

def go_to_register():
    st.session_state.page = "register"

def go_to_about():
    st.session_state.page = "about"

def go_to_devlog():
    st.session_state.page = "devlog"

def go_to_note():
    st.session_state.page = "my_note"

def logout():
    st.session_state.token = None
    st.session_state.current_user = None
    st.query_params.clear()
    st.session_state.page = "home"


# todo:页面区域
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align: center; color: #2E4057; margin-bottom: 0.5rem;'>📚 虚拟教研社区</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #555; margin-bottom: 0.5rem;'>聚师成林，研无止境</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1rem; color: #777; margin-bottom: 2rem;'>专为职业院校英语教师打造的教研协作平台</p>", unsafe_allow_html=True)
    st.divider()
    if st.session_state.token:
        st.success(f"👋 欢迎您，{st.session_state.current_user['name']}（{st.session_state.current_user['role']}）")
        st.divider()

    st.subheader("✨ 平台核心功能")
    col = st.columns(3)
    with col[0]:
        st.info("💬 教研社区:发帖讨论、互助答疑")
    with col[1]:
        st.info("📂 教研资料部:教案、课件、真题库")
    with col[2]:
        st.info("🎓 课程共建:集体备课、协同开发")
    st.divider()

    if st.session_state.token:
        st.subheader("您可以：", anchor=False)
        col = st.columns([1, 2, 1])  # 中间列放按钮，宽屏不分散
        with col[0]:
            st.success("📈 我的教研进度")
            st.progress(75, text="已完成教研任务 75%")
            st.caption("还剩1个任务待完成~")
        with col[1]:
            with st.container(border=True):
                if st.button("**教研社区**", icon="💬", use_container_width=True):
                    st.switch_page("pages/1_教研社区.py")
                if st.button("**教研资料部**", icon="📁", use_container_width=True):
                    st.switch_page("pages/2_教研资料部.py")
                if st.button("**个人中心**", icon="👤", use_container_width=True):
                    st.switch_page("pages/3_个人中心.py")
                if st.session_state.current_user["role"] == "admin":
                    if st.button("**用户管理**", icon="🔐", use_container_width=True):
                        st.switch_page("pages/4_用户管理.py")
                    st.button("**开发日志**", icon="📝", on_click=go_to_devlog, use_container_width=True)

                st.button("**关于作者**", icon="ℹ️", on_click=go_to_about, use_container_width=True)
                st.divider()
                st.button("注销", icon="🔌", on_click=logout, use_container_width=True, type="secondary",key="logout")
        with col[2]:
            st.warning("🔔 最新通知")
            st.markdown("""
            <div style='font-size:0.9rem;'>
            • 新的教研课件已上传<br>
            • 下周教研活动报名开始啦
            </div>
            """, unsafe_allow_html=True)

    else:
        col = st.columns([1, 2, 1])
        with col[1]:
            st.button("**登录**",icon="🔐", on_click=go_to_login, use_container_width=True)
            st.button("**注册**",icon="✏️", on_click=go_to_register, use_container_width=True)
            st.button("**关于作者**",icon="ℹ️", on_click=go_to_about, use_container_width=True)


elif st.session_state.page == "login":
    with st.form("login_form"):
        st.subheader("登录", text_alignment="center")
        phone = st.text_input("手机号", max_chars=11)
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录", use_container_width=True)

    if submit:
        if not phone or not password:
            st.warning("请输入手机号和密码")

        result = api_request("POST", "/auth/login", data={"phone": phone, "password": password})

        if result and result["code"] == 200:
            st.balloons()
            # 登录成功同时保存到URL参数（刷新不丢失）
            save_login_state(result["access_token"], result["user"])

            st.success("登录成功！正在跳转到首页...")
            time.sleep(1)
            go_to_Home()
            st.rerun()

    col = st.columns([1, 2, 1])
    with col[1]:
        st.button("**返回首页**", on_click=go_to_Home, use_container_width=True)



elif st.session_state.page == "register":
    with st.form("register_form"):
        st.subheader("注册", text_alignment="center")
        phone = st.text_input("手机号", max_chars=11)
        password = st.text_input("密码", type="password")
        current_password = st.text_input("确认密码", type="password")
        if password != current_password:
            st.warning("两次输入的密码不一致")
        name = st.text_input("姓名")
        school = st.text_input("学校")
        title = st.text_input("职称")

        submit = st.form_submit_button("注册", use_container_width=True)

        if submit:
            result = api_request("POST", "/auth/register", data={"phone": phone, "password": password, "name": name, "school": school, "title": title})
            st.balloons()
            if result and result["code"] == 200:
                st.success("注册成功！正在跳转到登录页面...")
                time.sleep(1)
                go_to_login()
                st.rerun()

    col = st.columns([1, 2, 1])
    with col[1]:
        st.button("**返回首页**", on_click=go_to_Home, use_container_width=True)

if st.session_state.page == "about":
    st.title("关于项目", text_alignment="center")
    with st.container(border=True):
        with open ("README.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    st.button("**返回首页**", on_click=go_to_Home, use_container_width=True)

if st.session_state.page == "devlog":
    st.title("开发日志", text_alignment="center")
    with st.container(border=True):
        with open ("dev_log.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    st.button("**返回首页**", on_click=go_to_Home, use_container_width=True)

if st.session_state.page == "my_note":
    st.title("教研任务", text_alignment="center")


global_button()



