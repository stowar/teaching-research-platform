# 虚拟教研社区

专为职业院校英语教师打造的教研协作平台。发帖沉淀讨论、资料分类检索、AI 辅助教研、学生评价情感分析——让教研从碎片化聊天里走出来。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + Pinia + Vue Router + markdown-it |
| 后端 | FastAPI + Pydantic + JWT + bcrypt |
| 数据库 | MySQL + pymysql + PooledDB 连接池 |
| AI 对话 | DeepSeek API + 自研人格状态机 + Function Calling 工具链 |
| 情感分析 | PyTorch BiGRU + Self-Attention + 六层温度缩放后处理 |
| 部署 | 阿里云 ECS + Nginx + Supervisor |

## 功能模块

- **教研社区** — 帖子 CRUD、Markdown 编辑、分类筛选、搜索分页、点赞、嵌套评论、通知系统
- **AI 聊天室** — 多会话隔离、三维度人格状态机（语气/投入度/关注度）、三层记忆检索（L1投入度→查询范围/L2分级/L3时间衰减+召回加成）、7 个 Function Calling 工具、裁切总结、每日配额、安全模式。投入度和关注度实行双重保险——AI 自主判断 + 代码强制兜底
- **情感分析** — BiGRU + Self-Attention 推理、六层温度校准、注意力可视化（共振图 + 热力词）
- **个人中心** — 消息通知、我的帖子、资料编辑
- **管理后台** — 用户管理、角色权限、启用/禁用

## 架构

```
backend/
  schema/          ← 数据定义（DO / VO / Request 三层）
  domain/          ← 服务接口（Domain 层，API 只依赖此层）
  services/        ← 业务逻辑
  db/              ← 数据访问（裸 SQL）
  api/v1/          ← RESTful 端点
  Agent/           ← AI 教研助手引擎（人格 + Provider + 工具 + 规则）
  ml/sentiment/    ← 情感分析引擎（模型 + 推理 + 训练 + 温度体系）
```

**开发理念**：先定义形状再写代码（DO → VO → Domain → DB → Service → API）。所有代码围着数据走，不是围着框架走。详见 [设计哲学](docs/exhibition/设计哲学.md)。

## 快速开始

```bash
# 1. 后端
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload --host localhost --port 8000

# 2. 前端
cd frontend-vue
npm install
npm run dev
```

## 环境变量

复制 `backend/.env.example` 为 `backend/.env`：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=teaching_research
SECRET_KEY=your_secret_key
API_KEY=your_deepseek_api_key    # AI 聊天室所需
AI_BASE_URL=https://api.deepseek.com
```

## 数据库

```bash
mysql -u root -p teaching_research < docs/database/create_tables.sql
```

## 相关项目

- [XiaoBai](https://github.com/stowar/XiaoBai) — AI 虚拟伴侣，人格系统 + 记忆系统 + 主动消息调度。教研平台 AI 聊天室的前身。
- [Hotel_Emotion_Predict](https://github.com/stowar/Hotel_Emotion_Predict) — 第一个全栈 AI 项目，酒店评论情感分析。教研平台情感分析模型的起点。

## License

MIT
