import streamlit as st

# 检查登录状态，未登录自动跳转到登录页
if not st.session_state.token:
    st.warning("请先登录！")
    st.switch_page("pages/login.py")
    st.stop()

# 首页业务逻辑
st.title(f"欢迎回来，{st.session_state.current_user['name']}")
st.write("这是职业院校英语虚拟教研社区系统")
st.write(f"您的角色：{'管理员' if st.session_state.current_user['role'] == 'admin' else '教师'}")