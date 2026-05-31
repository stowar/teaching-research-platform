import os

import streamlit as st
from utils.dialogs import notice_detail_dialog


class CardComponent:
    """
    卡片组件类（面向对象封装）
    包含：功能卡片 normal_card + 通知卡片 activity_card
    统一管理样式、计数器、交互逻辑
    """
    def __init__(self):
        # 初始化（兜底）
        self.init_count()

    def init_count(self):
        # 核心修复：独立初始化方法，随时调用
        if "card_count" not in st.session_state:
            st.session_state.card_count = 0

    def _get_key(self):
        """私有方法：自动生成唯一按钮key"""
        self.init_count()
        st.session_state.card_count += 1
        return f"card_{st.session_state.card_count}"


    def normal_card(self, title: str, content: str, btn_text: str, page: str = None, on_click = None) -> bool:
        """
        通用功能卡片
        :param title: 标题
        :param content: 描述
        :param btn_text: 按钮文字
        :param page: 跳转页面路径
        :param on_click: 回调函数/打开弹窗
        """
        with st.container(border=True):
            key = self._get_key()
            st.markdown(f"### {title}", text_alignment="center")
            st.caption(f"{content}", text_alignment="center")

            if on_click is not None:
                st.button(f"进入{btn_text}", use_container_width=True, key=key, on_click=on_click)
            else:
                if st.button(f"进入{btn_text}", use_container_width=True):
                    st.switch_page(f"./{page}")

    def activity_card(self, title: str, content: str, time: str):
        """
        通知卡片（点击打开详情弹窗）
        """
        with st.container(border=True):
            key = self._get_key()
            st.markdown(f"**📢 {title}**")  # 标题加图标，更美观
            st.caption(f"ℹ️ {content}")  # 内容加图标
            st.caption(f"📅 {time}")  # 时间用小号文案，更协调

            st.button("查看详情",on_click=notice_detail_dialog, args=(title,content,time),key=key)


card = CardComponent()

