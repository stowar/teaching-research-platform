from config import init_global_app, global_back_home_button, global_button
init_global_app()

import streamlit as st

st.title("关于项目")
with st.container(border=True):
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except FileNotFoundError:
        st.info("README.md 未找到")

global_back_home_button()
global_button()
