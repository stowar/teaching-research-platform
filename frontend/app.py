import sys
import os
# 获取项目根目录（自动适配你的电脑，不用手动改路径）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import streamlit as st
from utils.api_client import health_check

st.set_page_config(
    page_title="虚拟教研社区",
    page_icon="📚",
    layout="wide"
)
st.title("📚 虚拟教研社区系统")

# 测试后端连接
result = health_check()
if result["status"] == "ok":
    st.success("后端连接成功")
else:
    st.error("后端连接失败")