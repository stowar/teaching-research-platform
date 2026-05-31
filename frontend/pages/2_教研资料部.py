from config import init_global_app, check_login_state,global_back_home_button,global_button
init_global_app()

import streamlit as st

st.info("📚 教研资料模块正在全力开发中，未来将支持教案共享、教学资源下载与备课模板管理功能")
# 再和底部按钮加个间距
st.markdown("<br><br>", unsafe_allow_html=True)
global_back_home_button()
global_button()