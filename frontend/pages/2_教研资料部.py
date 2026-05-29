from config import init_global_app, check_login_state,global_back_home_button,global_button
init_global_app()

import streamlit as st

# 这里写你的教研资料业务逻辑（上传、搜索、下载等）
st.info("这里是教研资料部的业务逻辑，你可以继续开发")
global_back_home_button()
global_button()