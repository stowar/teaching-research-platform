# PRD: 教研社区（Teaching Research Community）API 与数据库设计

## Problem Statement

虚拟教研社区的"教研社区"模块目前是一个占位页面（CommunityView.vue），仅显示"功能开发中"。用户需要一个完整的教师交流社区，支持发帖讨论、互助答疑、分享教学经验。用户疑问"只是 CRUD 吗？"——答案是否定的。一个社区模块不仅需要基础的增删改查，还需要分页筛选、点赞互动、消息通知、搜索检索、管理员置顶/加精等能力。

## Solution

构建一套完整的教研社区后端 API 与数据库体系，涵盖帖子（Post）、评论（Comment）、分类（Category）、点赞（Like）四个核心实体。提供教师发帖、回帖、点赞、浏览、搜索的全流程能力。消息通知数据为后续"消息中心"模块奠基。前端 CommunityView.vue 从占位页升级为真实可用的社区首页（帖子列表 + 分类筛选 + 发帖入口）。

## User Stories

1. 作为一名教师，我想在社区发布教学问题或经验分享帖，以便与其他教师交流探讨。
2. 作为一名教师，我想浏览社区中的帖子列表，以便发现感兴趣的教学话题。
3. 作为一名教师，我想按分类（如"教案分享"、"课堂管理"、"考试命题"）筛选帖子，以便快速找到相关内容。
4. 作为一名教师，我想对感兴趣的帖子进行点赞，以便表达对作者观点的认同。
5. 作为一名教师，我想在帖子下方发表评论进行答疑或讨论，以便形成深度交流。
6. 作为一名教师，我想查看自己发布过的所有帖子，以便管理自己的内容。
7. 作为一名教师，我想搜索帖子标题或内容中的关键词，以便快速定位历史讨论。
8. 作为一名教师，我想在消息中心收到有人回复我帖子或点赞的通知，以便及时参与互动。
9. 作为社区管理员，我想将优质帖子置顶或加精，以便让更多教师看到优质内容。
10. 作为社区管理员，我想删除违规帖子或评论，以便维护社区秩序。
11. 作为一名访客（未登录），我想浏览公开帖子列表，以便了解社区氛围（部分内容可开放）。
12. 作为一名教师，我想编辑或删除自己发布的帖子/评论，以便修正错误或撤回内容。
13. 作为一名教师，我想查看帖子的浏览量，以便了解话题的热度。
14. 作为一名教师，我想按"最新发布"或"最热讨论"排序帖子，以便发现不同维度下的优质内容。
15. 作为系统，我想记录用户的点赞行为防止重复点赞，以便保证数据一致性。

## Implementation Decisions

### 1. 数据库表设计（MySQL，utf8mb4）

遵循现有项目的裸 SQL + pymysql 模式，不使用 ORM。

#### 1.1 categories（分类表）
- `id` INT PK AI
- `name` VARCHAR(50) NOT NULL（如：教案分享、课堂管理、考试命题、教学反思）
- `description` VARCHAR(200) 可选
- `sort_order` INT DEFAULT 0（排序权重）
- `create_time` DATETIME

#### 1.2 posts（帖子表）

- `id` INT PK AI
- `user_id` INT NOT NULL FK → users.id（作者）
- `category_id` INT NOT NULL FK → categories.id
- `title` VARCHAR(200) NOT NULL
- `content` TEXT NOT NULL（帖子正文）
- `view_count` INT DEFAULT 0（浏览量）
- `like_count` INT DEFAULT 0（点赞数，冗余字段加速列表查询）
- `comment_count` INT DEFAULT 0（评论数，冗余字段加速列表查询）
- `is_pinned` TINYINT(1) DEFAULT 0（是否置顶）
- `is_essence` TINYINT(1) DEFAULT 0（是否精华）
- `status` TINYINT(1) DEFAULT 1（1正常 0隐藏 2删除）
- `create_time` DATETIME
- `update_time` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

#### 1.3 comments（评论表）
- `id` INT PK AI
- `post_id` INT NOT NULL FK → posts.id
- `user_id` INT NOT NULL FK → users.id
- `parent_id` INT DEFAULT NULL（楼中楼回复，指向另一 comment.id）
- `content` TEXT NOT NULL
- `status` TINYINT(1) DEFAULT 1（1正常 0隐藏）
- `create_time` DATETIME

#### 1.4 likes（点赞表）
- `id` INT PK AI
- `post_id` INT NOT NULL FK → posts.id
- `user_id` INT NOT NULL FK → users.id
- `create_time` DATETIME
- UNIQUE(`post_id`, `user_id`) 防止重复点赞

#### 1.5 notifications（通知表，为消息中心奠基）
- `id` INT PK AI
- `user_id` INT NOT NULL FK → users.id（接收者）
- `sender_id` INT NOT NULL FK → users.id（触发者）
- `type` VARCHAR(20) NOT NULL（'comment' / 'like' / 'reply'）
- `post_id` INT FK → posts.id
- `comment_id` INT FK → comments.id（可选）
- `content` VARCHAR(200)（通知摘要，如"张三回复了你的帖子《xxx》"）
- `is_read` TINYINT(1) DEFAULT 0
- `create_time` DATETIME

### 2. 后端架构（遵循现有三层架构）

- `backend/db/community_db.py` — 数据层：帖子/评论/点赞/通知/分类的增删改查 SQL
- `backend/services/community.py` — 业务层：发帖校验、点赞去重、通知生成、置顶权限校验
- `backend/api/v1/community.py` — 路由层：FastAPI Router，定义 RESTful 接口
- `backend/model/community.py` — Pydantic 模型：请求/响应 Schema

### 3. API 接口设计

#### 3.1 分类
- `GET /api/v1/community/categories` — 获取所有分类列表

#### 3.2 帖子
- `GET /api/v1/community/posts` — 帖子列表（分页 + 分类筛选 + 排序）
  - Query: `page`, `page_size`, `category_id`, `sort`('new'|'hot'), `keyword`
- `GET /api/v1/community/posts/{post_id}` — 帖子详情（含评论列表 + 作者信息）
- `POST /api/v1/community/posts` — 发布帖子（需登录）
- `PUT /api/v1/community/posts/{post_id}` — 编辑自己的帖子（需登录 + 作者本人）
- `DELETE /api/v1/community/posts/{post_id}` — 删除自己的帖子（软删除，status=2）

#### 3.3 评论
- `GET /api/v1/community/posts/{post_id}/comments` — 获取帖子的评论列表（分页）
- `POST /api/v1/community/posts/{post_id}/comments` — 发表评论（需登录）
- `DELETE /api/v1/community/comments/{comment_id}` — 删除评论（作者本人或管理员）

#### 3.4 点赞
- `POST /api/v1/community/posts/{post_id}/like` — 点赞/取消点赞（toggle，需登录）
- `GET /api/v1/community/posts/{post_id}/like` — 查询当前用户是否已点赞

#### 3.5 管理
- `PUT /api/v1/community/posts/{post_id}/pin` — 置顶/取消置顶（管理员）
- `PUT /api/v1/community/posts/{post_id}/essence` — 加精/取消加精（管理员）

### 4. 业务规则

- **软删除**：帖子/评论采用 status 字段软删除，保留数据可追溯。
- **点赞幂等**：同一用户对同一帖子只能点赞一次，再次点击则取消点赞。通过 likes 表的 UNIQUE 索引 + 业务层 try/except 实现。
- **冗余计数**：posts.like_count / comment_count 为冗余字段，由业务层在点赞/评论时同步更新，避免列表页频繁 JOIN COUNT。
- **通知触发**：发表评论时，如果 parent_id 为 NULL（直接回复帖子），则给帖子作者发通知；如果 parent_id 不为 NULL（回复评论），则给被回复的评论作者发通知。点赞时给帖子作者发通知。
- **浏览量**：帖子详情页每次 GET 时 view_count + 1（简单实现，后续可加 Redis 防刷）。

### 5. 前端对应改动

- `CommunityView.vue` 从占位页升级为真实社区首页：分类 Tab + 帖子列表卡片 + 发帖按钮 + 排序切换（最新/最热）。
- 新增 `PostDetailView.vue`：帖子详情 + 评论列表 + 发表评论输入框 + 点赞按钮。
- 新增 `PostCreateView.vue`：发帖表单（标题、分类选择、富文本/textarea 内容）。
- 路由注册：`/community/:post_id` 帖子详情，`/community/create` 发帖页。

### 6. 排序策略

- **最新（new）**：按 create_time DESC
- **最热（hot）**：综合 comment_count * 3 + like_count * 2 + view_count * 0.5，按分值 DESC

## Testing Decisions

- **测试分层**：沿用现有项目无单元测试的现状，优先通过 FastAPI TestClient 做接口级验收测试。
- **关键验收点**：
  1. 点赞 toggle 的幂等性（连续两次点赞后状态正确，计数正确）
  2. 分页边界（最后一页、空列表）
  3. 权限边界（普通用户不能置顶，不能删除他人帖子）
  4. 评论通知触发（发表评论后通知表是否有正确记录）
- **手工测试脚本**：在 `backend/tests/test_community.py` 中提供基于 `TestClient` 的端到端测试，覆盖发帖→评论→点赞→列表查询全链路。

## Out of Scope

1. **富文本编辑器**：帖子 content 使用纯文本 textarea，不引入 Markdown/Quill 编辑器（后续迭代）。
2. **图片/文件上传**：帖子不支持附件上传（后续迭代）。
3. **实时消息推送**：通知仅写入数据库，前端通过轮询或进入页面时查询，不引入 WebSocket（后续迭代）。
4. **全文搜索**：keyword 搜索仅基于 MySQL LIKE '%keyword%'，不引入 Elasticsearch（后续迭代）。
5. **消息中心 UI**：notifications 表为 MessagesView 奠基，但本 PRD 不实现消息中心前端页面。

## Further Notes

- 本模块的数据库表建表 SQL 应追加到 `docs/database/create_tables.sql`，并通过 `scripts/init_db.py` 执行。
- 分类数据（categories）需要预设种子数据，建议初始分类：教案分享、课堂管理、考试命题、教学反思、职业英语、AI工具。
- 前端帖子列表卡片应复用现有的 Design Token 和动画体系（slide-up-enter、hover-lift 等）。
- 帖子详情页的 attention 热力图组件如有需要，可参考 SentimentView.vue 的 heatmap 实现。
