from config import init_global_app, save_login_state, global_button
init_global_app()

import streamlit as st
from datetime import datetime

# ========== 首页专用样式（鲜明配色 + 对称布局） ==========
st.markdown("""
<style>
/* 顶部欢迎区：深蓝紫渐变，有冲击力 */
.hero-banner {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 30%, #4f46e5 70%, #7c3aed 100%);
    border-radius: 18px;
    padding: 2.5rem 2rem;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 12px 40px rgba(79, 70, 229, 0.35);
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -30%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-banner h1 {
    margin: 0;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.hero-banner p {
    margin: 0.6rem 0 0 0;
    opacity: 0.85;
    font-size: 1.1rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    font-size: 0.85rem;
    margin-top: 0.8rem;
    border: 1px solid rgba(255,255,255,0.15);
}

/* 分区标题 */
.section-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #0f172a;
    margin: 1.5rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* 功能卡片：鲜明左边框 + hover 动效 */
.feature-card {
    background: white;
    border-radius: 14px;
    border: 2px solid #e2e8f0;
    padding: 1.5rem 1rem;
    text-align: center;
    margin-bottom: 0.6rem;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.feature-card:hover {
    border-color: #c7d2fe;
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(79, 70, 229, 0.12);
}
.feature-card .accent-bar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    border-radius: 14px 14px 0 0;
}
.feature-icon {
    font-size: 2.2rem;
    margin-bottom: 0.4rem;
}
.feature-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.25rem;
}
.feature-desc {
    font-size: 0.82rem;
    color: #64748b;
    line-height: 1.4;
}

/* 小组件容器：深色标题栏 + 鲜明边框 */
.widget-box {
    background: white;
    border-radius: 14px;
    border: 2px solid #e2e8f0;
    padding: 0;
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
}
.widget-header {
    background: #f8fafc;
    padding: 0.9rem 1.2rem;
    border-bottom: 2px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.widget-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    flex: 1;
}
.widget-badge {
    background: #e0e7ff;
    color: #4338ca;
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-weight: 700;
}
.widget-body {
    padding: 1rem 1.2rem;
    flex: 1;
}

/* 通知项：琥珀色鲜明标记 */
.notice-item {
    padding: 1rem 1.2rem;
    margin-bottom: 1.2rem;
    border-radius: 12px;
    background: #ffffff;
    border-left: 6px solid #64748b; /* 柔和灰蓝，完全不刺眼 */
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    line-height: 1.5;
    font-size: 0.95rem;
}
.notice-item:hover {
    transform: translateX(4px);
    box-shadow: 0 4px 12px rgba(100, 116, 139, 0.12);
    border-left-color: #475569;
}

.notice-title {
    font-weight: 700;
    color: #7c2d12;
    font-size: 0.95rem;
}
.notice-content {
    font-size: 0.85rem;
    color: #9a3412;
    margin-top: 0.2rem;
    line-height: 1.4;
}
.notice-meta {
    font-size: 0.75rem;
    color: #c2410c;
    margin-top: 0.35rem;
    font-weight: 600;
}
.notice-tag {
    display: inline-block;
    font-size: 0.7rem;
    padding: 0.1rem 0.5rem;
    border-radius: 4px;
    margin-left: 0.4rem;
    font-weight: 700;
}
.tag-urgent { background: #fee2e2; color: #991b1b; }
.tag-normal { background: #dbeafe; color: #1e40af; }
.tag-activity { background: #d1fae5; color: #065f46; }

/* 备忘录项：翠绿色鲜明标记 */
.memo-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.65rem 0.8rem;
    margin-bottom: 0.5rem;
    border-radius: 10px;
    background: #f0fdf4;
    border-left: 4px solid #10b981;
    transition: all 0.2s;
}
.memo-item:hover {
    background: #dcfce7;
}
.memo-done {
    opacity: 0.55;
    text-decoration: line-through;
    background: #f8fafc;
    border-left-color: #94a3b8;
}

/* 底部操作栏 */
.action-bar {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border-radius: 14px;
    padding: 1rem;
    margin-top: 2rem;
    border: 2px solid #e2e8f0;
}

/* 未登录页 Hero */
.landing-hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #4f46e5 100%);
    border-radius: 20px;
    padding: 5rem 2rem;
    text-align: center;
    color: white;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(15, 23, 42, 0.3);
}
.landing-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -30%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(124, 58, 237, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 70% 50%, rgba(6, 182, 212, 0.2) 0%, transparent 50%);
}
.landing-hero h1 {
    font-size: 3.2rem;
    margin-bottom: 1rem;
    position: relative;
    z-index: 1;
    font-weight: 800;
    letter-spacing: -1px;
}
.landing-hero p {
    font-size: 1.25rem;
    opacity: 0.8;
    margin-bottom: 2rem;
    position: relative;
    z-index: 1;
}
.landing-slogan {
    display: inline-block;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    padding: 0.5rem 1.5rem;
    border-radius: 30px;
    font-size: 1rem;
    border: 1px solid rgba(255,255,255,0.2);
    position: relative;
    z-index: 1;
}

/* 亮点卡片 */
.highlight-card {
    background: white;
    border-radius: 16px;
    border: 2px solid #e2e8f0;
    padding: 2.5rem 1.5rem;
    text-align: center;
    transition: all 0.3s;
}
.highlight-card:hover {
    border-color: #c7d2fe;
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(79, 70, 229, 0.1);
}
</style>
""", unsafe_allow_html=True)

# ========== 状态初始化 ==========
if "memo_items" not in st.session_state:
    st.session_state.memo_items = [
        {"id": 1, "text": "准备下周英语研讨会PPT", "done": False},
        {"id": 2, "text": "提交期中考试分析报告", "done": False},
        {"id": 3, "text": "参加新教材培训会议", "done": True},
    ]
if "memo_next_id" not in st.session_state:
    st.session_state.memo_next_id = 4

# 活动通知数据（示例 — 后续可接后端接口）
NOTICES = [
    {"title": "高中英语阅读教学研讨会", "content": "本周五下午2:00在教学楼A301开展，请各备课组准时参加", "time": "2026-06-05 14:00", "tag": "活动", "tag_class": "tag-activity"},
    {"title": "期中考试质量分析会", "content": "各备课组请准备好质量分析材料，周一上午交教务处", "time": "2026-06-08 09:00", "tag": "紧急", "tag_class": "tag-urgent"},
    {"title": "人教版新教材培训", "content": "新教材使用培训，请全体英语教师参加", "time": "2026-06-10 08:30", "tag": "培训", "tag_class": "tag-normal"},
]

# ========== 已登录首页 ==========
if st.session_state.token:
    user = st.session_state.current_user or {}
    user_name = user.get('name') or '教师'
    user_role = user.get('role') or 'user'
    user_school = user.get('school') or '虚拟教研社区'

    # --- 顶部欢迎区（对称居中） ---
    role_label = "🔐 管理员" if user_role == "admin" else "👤 教师用户"
    st.markdown(f"""
    <div class="hero-banner">
        <div style="font-size:3.5rem; margin-bottom:0.5rem;">👋</div>
        <h1>欢迎回来，{user_name}老师</h1>
        <p style="opacity:0.8;">{user_school}</p>
        <div class="hero-badge">{role_label}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- 左右分栏小组件（对称） ---
    st.markdown('<div class="section-title">📋 工作台</div>', unsafe_allow_html=True)
    left_col, right_col = st.columns(2)

    # 左侧：活动通知
    with left_col:
        urgent_count = len([n for n in NOTICES if n.get('tag') == '紧急'])
        st.markdown(f"""
        <div class="widget-header">
            <span style="font-size:1.2rem;">📢</span>
            <span class="widget-title">活动通知</span>
            <span class="widget-badge">{urgent_count} 条紧急</span>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True, height=518):
            for notice in NOTICES:
                st.markdown(f"""
                <div class="notice-item">
                    <div class="notice-title">
                        {notice['title']}
                        <span class="notice-tag {notice['tag_class']}">{notice['tag']}</span>
                    </div>
                    <div class="notice-content">{notice['content']}</div>
                    <div class="notice-meta">📅 {notice['time']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

    # 右侧：备忘录
    with right_col:
        todo_count = len([i for i in st.session_state.memo_items if not i['done']])
        st.markdown(f"""
        <div class="widget-header">
            <span style="font-size:1.2rem;">📝</span>
            <span class="widget-title">我的备忘录</span>
            <span class="widget-badge">{todo_count} 待办</span>
        </div>
        """, unsafe_allow_html=True)
        with st.container(border=True,height=400):
            for item in st.session_state.memo_items:
                item_id = item['id']
                if item['done']:
                    st.markdown(f'<div class="memo-item memo-done">✅ {item["text"]}</div>', unsafe_allow_html=True)
                else:
                    c1, c2 = st.columns([8, 1])
                    with c1:
                        done = st.checkbox(item['text'], value=item['done'], key=f"memo_{item_id}")
                        if done != item['done']:
                            item['done'] = done
                            st.rerun()
                    with c2:
                        if st.button("➖", key=f"del_memo_{item_id}"):
                            st.session_state.memo_items = [i for i in st.session_state.memo_items if i['id'] != item_id]
                            st.rerun()

        # 添加新任务
        new_task = st.text_input("", placeholder="✏️ 输入新任务后点击添加...", key="memo_input", label_visibility="collapsed")
        c_add, c_clear = st.columns(2)
        with c_add:
            if st.button("➕ 添加任务", use_container_width=True):
                if new_task.strip():
                    st.session_state.memo_items.append({
                        "id": st.session_state.memo_next_id,
                        "text": new_task.strip(),
                        "done": False
                    })
                    st.session_state.memo_next_id += 1
                    st.rerun()
        with c_clear:
            if st.button("🗑️ 清空已完成", use_container_width=True):
                st.session_state.memo_items = [i for i in st.session_state.memo_items if not i['done']]
                st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

    # --- 底部操作栏（对称居中） ---
    st.divider()
    ac1, ac2, ac3 = st.columns([1, 1, 1])
    with ac1:
        if st.button("👤 个人中心", use_container_width=True):
            st.switch_page("pages/3_个人中心.py")
    with ac2:
        if st.button("💬 我的消息", use_container_width=True):
            st.switch_page("pages/6_消息.py")
    with ac3:
        if st.button("🔌 注销登录", use_container_width=True, type="primary"):
            st.session_state.token = None
            st.session_state.current_user = None
            st.query_params.clear()
            st.rerun()

    # --- 核心功能网格（对称 3 列） ---
    st.markdown('<div class="section-title">✨ 核心功能</div>', unsafe_allow_html=True)

    features = [
        ("💬", "教研社区", "发帖讨论、互助答疑、分享教学经验", "pages/1_教研社区.py", "#4f46e5"),
        ("📚", "教研资料部", "教案课件、真题题库一键下载", "pages/2_教研资料部.py", "#7c3aed"),
        ("🤖", "AI聊天室", "智能教研助手，RAG深度检索", "pages/5_AI聊天室.py", "#06b6d4"),
        ("🤝", "集体备课", "课程共建、协同开发、资源共享", "pages/1_教研社区.py", "#10b981"),
        ("💬", "消息中心", "教师互动交流、通知推送", "pages/6_消息.py", "#f59e0b"),
        ("ℹ️", "关于项目", "平台介绍、使用说明、更新记录", "pages/about.py", "#64748b"),
    ]
    if user_role == "admin":
        features.append(("🔐", "用户管理", "账号权限、信息审核、状态管理", "pages/4_用户管理.py", "#ef4444"))

    cols = st.columns(3)
    for idx, (icon, title, desc, page, color) in enumerate(features):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="accent-bar" style="background:{color};"></div>
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"进入 ▶", key=f"feat_{idx}", use_container_width=True):
                st.switch_page(page)



# ========== 未登录首页 ==========
else:
    # Hero Section
    st.markdown("""
    <div class="landing-hero">
        <div style="font-size:4rem; margin-bottom:1rem; position:relative; z-index:1;">🏫</div>
        <h1>虚拟教研社区</h1>
        <p>聚师成林，研无止境</p>
        <div class="landing-slogan">专为职业院校英语教师打造的教研协作平台</div>
    </div>
    """, unsafe_allow_html=True)

    # CTA 按钮（对称居中）
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        lc, rc = st.columns(2)
        with lc:
            if st.button("🔐 立即登录", use_container_width=True, type="primary"):
                st.switch_page("pages/login.py")
        with rc:
            if st.button("📝 注册账号", use_container_width=True):
                st.switch_page("pages/register.py")

    # 核心亮点
    st.markdown('<div style="margin: 3rem 0 1.5rem 0; text-align:center; font-size:1.6rem; font-weight:800; color:#0f172a;">🌟 平台核心亮点</div>', unsafe_allow_html=True)

    highlights = [
        ("💬", "教研交流", "跨校协作、在线研讨、经验分享", "#4f46e5"),
        ("📚", "资源共享", "教案课件、真题题库一键获取", "#7c3aed"),
        ("🤖", "AI赋能", "智能助手、RAG检索、教研提效", "#06b6d4"),
    ]

    hcols = st.columns(3)
    for idx, (icon, title, desc, color) in enumerate(highlights):
        with hcols[idx]:
            st.markdown(f"""
            <div class="highlight-card">
                <div style="font-size:3rem; margin-bottom:0.8rem;">{icon}</div>
                <div style="font-size:1.3rem; font-weight:700; color:#1e293b; margin-bottom:0.5rem;">{title}</div>
                <div style="font-size:0.9rem; color:#64748b; line-height:1.5;">{desc}</div>
                <div style="margin-top:1rem; height:4px; background:{color}; border-radius:2px; width:60%; margin-left:auto; margin-right:auto;"></div>
            </div>
            """, unsafe_allow_html=True)

global_button()
