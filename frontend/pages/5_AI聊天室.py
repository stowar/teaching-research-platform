from config import init_global_app, check_login_state,global_back_home_button,global_button
from components.ai_chat_local import local_chat
from utils.api_client import api_request
init_global_app()

import streamlit as st

check_login_state()

st.html("<style>html,body,.stApp,.stMain{height:100vh;overflow:hidden!important;}</style>")

st.set_page_config(
    page_title="AI聊天机器人",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📚"
)


if "session_name" not in st.session_state:
    st.session_state.session_name = {}
if "session_data" not in st.session_state:
    st.session_state.session_data = {}
if "session_count" not in st.session_state:
    st.session_state.session_count = 0
if "session_chage" not in st.session_state:
    st.session_state.session_change = "session_name"

def get_session(name=None):

    return session_name

def create_session(name=None, option="chat"):
    """创建会话"""

    # 1.创建会话名称
    if name is None:
        st.session_state.session_count += 1
        session_name = f"session_{st.session_state.session_count}"
    else:
        session_name = name

    # todo:2.创建会话数据
    if option == "chat":
        # 2.1 todo:通过api获取数据
        session_data = {
            "code": 200,
            "msg": "创建成功",
            "session_name": session_name,
            "data": [
                {"role": "system", "content": "你是一个AI助手，请按照我的要求回答我的问题"}
            ]
        }
        st.session_state.session_data = session_data
        st.session_state.session_name[session_name] = session_data

col = st.columns([0.8, 4, 2])
# 1.会话框
with col[0]:
    # 新建会话
    with st.container(horizontal=True,horizontal_alignment="left",gap="small"):
        st.markdown('<div style="font-size:20px; font-weight:600; margin-top:3px">新建会话</div>',
                    unsafe_allow_html=True)
        # todo:弹窗获取名字
        name = "装饰器"

        st.button("➕",type="tertiary", on_click=create_session, args=(name,), help="新建会话")

    # 会话数据
    with st.container(height=436,border=False,gap="small",horizontal_alignment="left"):
        if st.session_state.session_name:
            for session_name in st.session_state.session_name:
                st.button(session_name, key=f"{session_name}",use_container_width=True,)

    if st.button("返回首页", use_container_width=True,type="primary"):
        st.switch_page("app.py")


with col[1]:
    # 会话框
    with st.container(border=True):

        local_chat(st.session_state.prompt, container_params={"height": 450, "border": False})
        user_input = st.chat_input("试试问问我吧!")
    if user_input:
        st.session_state.prompt = user_input
        st.rerun()

with col[2]:
    st.markdown('<div style="font-size:20px; font-weight:600; margin-top:3px">游戏规则</div>',unsafe_allow_html=True)
    with st.container(border=True, height=520):
        st.markdown("""""")

# st.info("这里是AI聊天室，你可以继续开发")

global_button()