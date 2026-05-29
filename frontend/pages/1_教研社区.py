from config import init_global_app, check_login_state,global_back_home_button,global_button
init_global_app()

import streamlit as st

# 这里写你的教研社区业务逻辑（接入RAG等,发布文章,查看文章...）
st.info("这里是教研社区的业务逻辑，你可以继续开发")
global_back_home_button()
global_button()