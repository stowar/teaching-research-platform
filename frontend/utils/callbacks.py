import streamlit as st

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