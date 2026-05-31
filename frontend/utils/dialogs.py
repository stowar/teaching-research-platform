import streamlit as st

@st.dialog("确认操作", width="small")  # width: small/medium/large
def confirm_dialog():
    st.write("确定要执行这个操作吗？")
    if st.button("确定", type="primary"):
        st.success("操作成功！")
        st.rerun()  # 关闭弹窗
    if st.button("取消"):
        st.rerun()


@st.dialog("通知详情", width="medium")
def notice_detail_dialog(title, content, time):
    st.header(title)
    st.info(content)
    st.caption(f"发布时间：{time}")
    if st.button("关闭"):
        st.rerun()
