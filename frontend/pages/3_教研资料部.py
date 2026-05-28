import streamlit as st

# 检查登录状态
if not st.session_state.token:
    st.warning("请先登录！")
    st.switch_page("pages/login.py")
    st.stop()

st.title("📚 教研资料部")
st.divider()

# 这里写你的教研资料业务逻辑（上传、搜索、下载等）
st.info("这里是教研资料部的业务逻辑，你可以继续开发")