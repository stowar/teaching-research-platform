import time
import ollama
import streamlit as st

# 初始化ollama客户端
client = ollama.Client(host="http://localhost:11434")

# todo:待优化:通过加载对话数据(填充对话框,加强模型模型上下文)

# 初始化消息记录
if "message" not in st.session_state:
    st.session_state["message"] = []

def local_chat(prompt=None, container_params=None):
    """
    本地聊天函数
    :param prompt:
    :param container_params:
    :return:
    """
    default_params = {
        "gap": "small",
    }
    final_params = {**(container_params or {})}
    with st.container(**final_params):
        # 判断:用户输入了内容
        if prompt:
            # 将用户提问添加到历史记录中
            st.session_state["message"].append({"role":"user","content":prompt})
            # 渲染历史消息
            for message in st.session_state["message"]:
                st.chat_message(message['role']).markdown(message['content'])

            with st.spinner("正在思考..."):
                time.sleep(1)
                response = client.chat(
                    model="deepseek-r1:7b",
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                # 从response里面取出message和content两个key
                response = response["message"]["content"]
                # 将AI回答记录到历史记录中
                st.session_state["message"].append({"role":"assistant","content":response})
                # 渲染AI回答
                st.chat_message("assistant").markdown(response)

        st.session_state.prompt = None


