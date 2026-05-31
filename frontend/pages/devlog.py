from config import init_global_app, global_back_home_button, global_button
init_global_app()

import streamlit as st

st.title("开发日志")
with st.container(border=True):
    try:
        with open("dev_log.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.info("dev_log.md 未找到")

global_back_home_button()
global_button()
