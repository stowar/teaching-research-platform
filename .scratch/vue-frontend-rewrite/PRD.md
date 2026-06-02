Status: ready-for-agent

# Vue 前端重构 PRD

## Problem Statement

当前项目使用 Streamlit 作为前端框架。随着功能扩展（教研社区、教研资料部、AI聊天室、用户管理、消息中心等），Streamlit 的局限性日益明显：

- 无客户端路由，页面切换依赖 `st.switch_page()`，体验不流畅
- 组件复用困难，所有 UI 通过 Python 字符串拼接 HTML/CSS 实现，维护成本高
- 状态管理局限于 `st.session_state`，难以跨页面共享复杂状态
- 样式注入依赖 `unsafe_allow_html=True`，存在安全风险且难以调试
- 性能瓶颈明显，每次交互触发全页重渲染

需要一个现代化的前端架构来支撑后续功能迭代。

## Solution

用 Vue 3 + Vite 重构整个前端，完整复刻现有 Streamlit 前端的所有页面和功能。重构后的前端具备：

- 客户端路由（Vue Router），实现无刷新页面切换
- 组件化开发，复用 UI 组件（通知卡片、备忘录、功能网格等）
- 组合式 API（Composition API）管理状态
- 原生 CSS/SCSS 样式系统，替代字符串注入
- 与现有 FastAPI 后端通过统一 API client 对接，保持 API 契约不变

## User Stories

1. 作为教师用户，我希望能通过流畅的页面导航访问各功能模块，以便提升使用体验。
2. 作为教师用户，我希望首页展示欢迎信息、活动通知和备忘录，以便快速了解教研动态和管理个人任务。
3. 作为教师用户，我希望在教研社区发帖讨论、互助答疑、分享教学经验，以便与同行协作。
4. 作为教师用户，我希望在教研资料部浏览和下载教案课件、真题题库，以便获取教学资源。
5. 作为教师用户，我希望使用 AI 聊天室进行智能教研助手对话和 RAG 深度检索，以便提升教研效率。
6. 作为教师用户，我希望在个人中心查看和编辑个人信息，以便管理账户资料。
7. 作为教师用户，我希望在消息中心接收互动交流通知和推送，以便及时获取重要信息。
8. 作为管理员，我希望在用户管理页面进行账号权限、信息审核、状态管理，以便维护平台秩序。
9. 作为访客，我希望在未登录状态下看到平台介绍和注册/登录入口，以便了解平台并加入。
10. 作为教师用户，我希望登录状态在页面刷新后保持，以便无需重复登录。
11. 作为教师用户，我希望在操作失败时看到清晰的错误提示（如 401 登录过期、403 无权限），以便理解问题原因。
12. 作为开发者，我希望前端代码采用组件化结构，以便后续维护和扩展功能。

## Implementation Decisions

- 使用 Vue 3 + Vite 作为构建工具，保持与现有 `frontend-vue` 脚手架一致
- 引入 Vue Router 实现客户端路由，路由结构映射现有 Streamlit 页面（`/`, `/login`, `/register`, `/community`, `/resources`, `/profile`, `/admin/users`, `/ai-chat`, `/messages`, `/about`）
- 引入 Pinia 进行全局状态管理（用户认证状态、用户信息）
- 将 `frontend/utils/api_client.py` 中的 API 请求逻辑迁移为 JavaScript 模块，保持与后端 `/api/v1` 的接口契约不变
- 首页功能拆分为独立组件：`HeroBanner`, `NoticeWidget`, `MemoWidget`, `FeatureGrid`
- 复用现有的后端认证机制（JWT Bearer Token），将 token 存储于 `localStorage` 并在 Axios 拦截器中注入
- 响应式布局采用 CSS Grid + Flexbox，替代 Streamlit 的 `st.columns()`
- 样式系统迁移为 scoped CSS + 全局变量，替代内联 `<style>` 字符串注入

## Testing Decisions

- **API 集成 seam**：使用 Vitest + MSW 模拟后端 API，验证 API client 的请求/响应处理（包括 401/403 错误处理、Token 注入）
- **页面路由 seam**：使用 Vue Test Utils + Vue Router 进行组件挂载测试，验证各页面在路由切换下的正确渲染
- **关键组件 seam**：使用 Vue Test Utils 验证独立组件的 props、事件和渲染行为（如 `MemoWidget` 的增删改、`NoticeWidget` 的列表渲染）
- **E2E 可选**：关键用户流程（登录→首页→进入功能页→注销）使用 Playwright 验证端到端

## Out of Scope

- 后端 API 的修改或新增接口（保持现有契约不变）
- AI 聊天室的后端 RAG 逻辑优化
- 移动端适配（当前重构聚焦桌面端功能对等）
- 设计系统的完全重建（复刻现有视觉风格，而非重新设计）

## Further Notes

- 重构期间 `frontend/`（Streamlit）保持可用，直到 Vue 前端功能完全对等后再切换
- 开发计划可参照根目录 `开发计划 .md` 中的功能优先级
- 考虑逐步引入 Element Plus 或 Ant Design Vue 等组件库来加速开发，但第一阶段以原生组件复刻为主以保持视觉一致性
