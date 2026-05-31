from config import init_global_app, check_login_state,global_back_home_button,global_button
init_global_app()

import streamlit as st

st.info("这里是消息区域,未来教师之间可以相互沟通交流")
st.markdown("<br><br>", unsafe_allow_html=True)
global_back_home_button()
global_button()