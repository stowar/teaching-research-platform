import streamlit as st
import requests
from dotenv import load_dotenv
from urllib.parse import urljoin


# 加载环境变量
load_dotenv()
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
BACKEND_URL = urljoin(BASE_URL, API_PREFIX.lstrip('/'))

# 初始化全局状态
if "token" not in st.session_state:
    st.session_state.token = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

st.set_page_config(
    page_title="职业院校英语虚拟教研社区",
    page_icon="📚",
    layout="wide"
)

# 统一API请求封装（自带请求拦截器）
def api_request(method, endpoint, data=None, params=None):
    """
    统一API请求函数，自动添加Token请求头，统一处理响应错误
    """
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    url = f"{BACKEND_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, json=data)

        # 统一响应处理
        result = response.json()

        # 401未登录：清除状态跳转到登录页
        if response.status_code == 401:
            st.session_state.token = None
            st.session_state.current_user = None
            st.session_state.page = "login"
            st.error("登录已过期，请重新登录")
            st.rerun()

        # 403无权限
        elif response.status_code == 403:
            st.error("您没有权限访问该页面")
            return None

        # 其他错误
        elif response.status_code != 200:
            st.error(f"请求失败：{result.get('msg', '未知错误')}")
            return None

        return result

    except Exception as e:
        st.error(f"网络错误：{str(e)}")
        return None


if st.session_state.token:
    with st.sidebar:
        st.title("📚 虚拟教研社区")
        st.divider()
        st.write(f"👋 欢迎，{st.session_state.current_user['name']}")
        st.write(f"角色：{'管理员' if st.session_state.current_user['role'] == 'admin' else '教师'}")
        st.divider()

        # 退出登录按钮
        if st.button("退出登录", use_container_width=True, type="primary"):
            st.session_state.token = None
            st.session_state.current_user = None
            st.switch_page("pages/login.py")
            st.stop()

# def main():
#     if st.session_state.page == "login":
#         show_login_page()
#     elif st.session_state.page == "home":
#         show_home_page()
#     elif st.session_state.page == "profile":
#         show_profile_page()
#     elif st.session_state.page == "user_management":
#         # 权限校验：只有管理员能访问
#         if st.session_state.current_user and st.session_state.current_user["role"] == "admin":
#             show_user_management_page()
#         else:
#             st.error("您没有权限访问该页面")
#             st.session_state.page = "home"
#             st.rerun()


# def show_login_page():
#     st.title("职业院校英语虚拟教研社区")
#     st.subheader("登录")
#
#     with st.form("login_form"):
#         phone = st.text_input("手机号", max_chars=11)
#         password = st.text_input("密码", type="password")
#         submit = st.form_submit_button("登录", use_container_width=True)
#
#     if submit:
#         if not phone or not password:
#             st.warning("请输入手机号和密码")
#             return
#
#         # 调用登录接口
#         result = api_request("POST", "/auth/login", data={"phone": phone, "password": password})
#
#         if result and result["code"] == 200:
#             # 保存Token和用户信息到全局状态
#             st.session_state.token = result["access_token"]
#             st.session_state.current_user = result["user"]
#             st.session_state.page = "home"
#             st.success("登录成功")
#             st.rerun()
#
#
# def show_home_page():
#     # 侧边栏导航
#     with st.sidebar:
#         st.title("导航菜单")
#         if st.button("首页", use_container_width=True):
#             st.session_state.page = "home"
#             st.rerun()
#         if st.button("个人中心", use_container_width=True):
#             st.session_state.page = "profile"
#             st.rerun()
#
#         # 管理员专属菜单
#         if st.session_state.current_user and st.session_state.current_user["role"] == "admin":
#             st.divider()
#             if st.button("用户管理", use_container_width=True):
#                 st.session_state.page = "user_management"
#                 st.rerun()
#
#         st.divider()
#         if st.button("退出登录", use_container_width=True, type="primary"):
#             st.session_state.token = None
#             st.session_state.current_user = None
#             st.session_state.page = "login"
#             st.success("已退出登录")
#             st.rerun()
#
#     # 首页内容
#     st.title(f"欢迎回来，{st.session_state.current_user['name']}")
#     st.write("这是职业院校英语虚拟教研社区系统")
#     st.write(f"您的角色：{'管理员' if st.session_state.current_user['role'] == 'admin' else '教师'}")
#
#
# def show_profile_page():
#     # 侧边栏导航（复用首页的导航逻辑）
#     with st.sidebar:
#         st.title("导航菜单")
#         if st.button("首页", use_container_width=True):
#             st.session_state.page = "home"
#             st.rerun()
#         if st.button("个人中心", use_container_width=True):
#             st.session_state.page = "profile"
#             st.rerun()
#         if st.session_state.current_user["role"] == "admin":
#             st.divider()
#             if st.button("用户管理", use_container_width=True):
#                 st.session_state.page = "user_management"
#                 st.rerun()
#         st.divider()
#         if st.button("退出登录", use_container_width=True, type="primary"):
#             st.session_state.token = None
#             st.session_state.current_user = None
#             st.session_state.page = "login"
#             st.rerun()
#
#     st.title("个人中心")
#
#     # 选项卡：查看信息 / 修改信息 / 修改密码
#     tab1, tab2, tab3 = st.tabs(["个人信息", "修改信息", "修改密码"])
#
#     with tab1:
#         st.subheader("我的信息")
#         st.write(f"手机号：{st.session_state.current_user['phone']}")
#         st.write(f"姓名：{st.session_state.current_user['name']}")
#         st.write(f"学校：{st.session_state.current_user['school']}")
#         st.write(f"职称：{st.session_state.current_user['title']}")
#         st.write(f"注册时间：{st.session_state.current_user['create_time']}")
#
#     with tab2:
#         st.subheader("修改个人信息")
#         with st.form("update_profile_form"):
#             name = st.text_input("姓名", value=st.session_state.current_user["name"])
#             school = st.text_input("学校", value=st.session_state.current_user["school"])
#             title = st.text_input("职称", value=st.session_state.current_user["title"])
#             submit = st.form_submit_button("保存修改", use_container_width=True)
#
#         if submit:
#             result = api_request("PUT", "/auth/profile", data={
#                 "name": name,
#                 "school": school,
#                 "title": title
#             })
#
#             if result and result["code"] == 200:
#                 # 更新全局状态中的用户信息
#                 st.session_state.current_user = result["data"]
#                 st.success("信息修改成功")
#                 st.rerun()
#
#     with tab3:
#         st.subheader("修改密码")
#         with st.form("change_password_form"):
#             old_password = st.text_input("原密码", type="password")
#             new_password = st.text_input("新密码", type="password")
#             confirm_password = st.text_input("确认新密码", type="password")
#             submit = st.form_submit_button("修改密码", use_container_width=True)
#
#         if submit:
#             if new_password != confirm_password:
#                 st.warning("两次输入的新密码不一致")
#                 return
#
#             result = api_request("PUT", "/auth/password", data={
#                 "old_password": old_password,
#                 "new_password": new_password
#             })
#
#             if result and result["code"] == 200:
#                 st.success("密码修改成功，请重新登录")
#                 # 清除状态跳转到登录页
#                 st.session_state.token = None
#                 st.session_state.current_user = None
#                 st.session_state.page = "login"
#                 st.rerun()
#
#
# def show_user_management_page():
#     # 侧边栏导航
#     with st.sidebar:
#         st.title("导航菜单")
#         if st.button("首页", use_container_width=True):
#             st.session_state.page = "home"
#             st.rerun()
#         if st.button("个人中心", use_container_width=True):
#             st.session_state.page = "profile"
#             st.rerun()
#         st.divider()
#         if st.button("用户管理", use_container_width=True):
#             st.session_state.page = "user_management"
#             st.rerun()
#         st.divider()
#         if st.button("退出登录", use_container_width=True, type="primary"):
#             st.session_state.token = None
#             st.session_state.current_user = None
#             st.session_state.page = "login"
#             st.rerun()
#
#     st.title("用户管理")
#
#     # 搜索和筛选
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         search_keyword = st.text_input("搜索用户（手机号/姓名）")
#     with col2:
#         status_filter = st.selectbox("状态筛选", ["全部", "正常", "禁用"])
#
#     # 获取用户列表
#     params = {}
#     if search_keyword:
#         params["keyword"] = search_keyword
#     if status_filter != "全部":
#         params["status"] = 1 if status_filter == "正常" else 0
#
#     result = api_request("GET", "/admin/users", params=params)
#
#     if result and result["code"] == 200:
#         users = result["data"]
#
#         # 用户列表表格
#         if users:
#             st.dataframe(
#                 users,
#                 column_config={
#                     "id": "ID",
#                     "phone": "手机号",
#                     "name": "姓名",
#                     "school": "学校",
#                     "title": "职称",
#                     "role": "角色",
#                     "status": st.column_config.SelectboxColumn(
#                         "状态",
#                         options=[0, 1],
#                         format_func=lambda x: "禁用" if x == 0 else "正常"
#                     ),
#                     "create_time": "注册时间"
#                 },
#                 use_container_width=True,
#                 hide_index=True
#             )
#
#             # 编辑和禁用用户
#             st.subheader("操作用户")
#             user_id = st.number_input("输入要操作的用户ID", min_value=1, step=1)
#             action = st.radio("操作类型", ["编辑信息", "禁用/启用用户"])
#
#             if action == "编辑信息":
#                 # 获取用户详情
#                 user_result = api_request("GET", f"/admin/users/{user_id}")
#                 if user_result and user_result["code"] == 200:
#                     user = user_result["data"]
#                     with st.form("edit_user_form"):
#                         name = st.text_input("姓名", value=user["name"])
#                         school = st.text_input("学校", value=user["school"])
#                         title = st.text_input("职称", value=user["title"])
#                         role = st.selectbox("角色", ["teacher", "admin"], index=0 if user["role"] == "teacher" else 1)
#                         submit = st.form_submit_button("保存修改", use_container_width=True)
#
#                     if submit:
#                         update_result = api_request("PUT", f"/admin/users/{user_id}", data={
#                             "name": name,
#                             "school": school,
#                             "title": title,
#                             "role": role
#                         })
#                         if update_result and update_result["code"] == 200:
#                             st.success("用户信息修改成功")
#                             st.rerun()
#
#             elif action == "禁用/启用用户":
#                 if st.button("执行操作", use_container_width=True, type="primary"):
#                     toggle_result = api_request("PUT", f"/admin/users/{user_id}/toggle")
#                     if toggle_result and toggle_result["code"] == 200:
#                         st.success("用户状态修改成功")
#                         st.rerun()
#
#         else:
#             st.info("没有找到符合条件的用户")


# if __name__ == "__main__":
#     main()

