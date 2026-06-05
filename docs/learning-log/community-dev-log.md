# 教研社区模块开发学习日志

> 本文件记录从零开发教研社区（Teaching Research Community）模块的完整教学过程。
> 参与者：stowar（学员）+ Claude Code（教学助手）
> 开始日期：2026-06-06

---

## 阶段 0：理解数据模型（✅ 已完成）

### 核心概念
教研社区 = 教师版的贴吧/论坛。核心数据关系：

```
users ──1:N──► posts ──N:1──► categories
                │
        ┌───────┴───────┐
        │               │
    comments        likes
        │
   notifications
```

### 5 张表的分工

| 表名 | 作用 | 核心字段 |
|---|---|---|
| **categories** | 帖子分类 | 教案分享、课堂管理、考试命题... |
| **posts** | 帖子本身 | 标题、内容、作者、分类、浏览量、点赞数 |
| **comments** | 评论/回复 | 内容、作者、属于哪个帖子、回复了哪条评论 |
| **likes** | 谁点赞了谁 | 用户ID + 帖子ID（联合唯一，防止重复点赞） |
| **notifications** | 通知消息 | 谁收到了、谁触发的、什么类型、已读未读 |

### 关键设计决策

**1. 为什么 posts 要有 like_count / comment_count 冗余字段？**
- 避免列表页频繁 JOIN COUNT
- 列表有 20 条帖子，无冗余要查 40 次 COUNT
- 有冗余字段，列表页直接读 posts 表一行数据
- 代价：点赞/评论时多一步更新计数
- 这叫**反规范化（Denormalization）**，以空间换时间

**2. comments.parent_id 是什么？**
- **NULL**：直接回复帖子（顶层评论）
- **有值**：回复了某条评论（楼中楼）
- 不是"评论人 ID"，不是"匿名标记"

### 学员问答记录

**Q1：为什么 posts 表里要有 like_count 和 comment_count？**
> 学员答：解耦，让调用资源没那么频繁。
> 评价：方向正确，核心思路是避免频繁 JOIN/COUNT。

**Q2：comments.parent_id 是什么意思？**
> 学员答：评论人的 id，匿名回答为 NULL。
> 评价：错误。parent_id 是"回复了哪条评论"的 ID，不是评论人 ID。
> 修正：NULL = 回复帖子本身；有值 = 回复某条评论（楼中楼）。

---

## 阶段 1：写建表 SQL（✅ 已完成）

### 最终正确的建表语句

```sql
-- 分类表
CREATE TABLE categories (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    name VARCHAR(50) NOT NULL COMMENT '分类名称',
    description VARCHAR(200) DEFAULT NULL COMMENT '分类描述',
    sort_order INT(11) DEFAULT 0 COMMENT '排序权重',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子分类表';

-- 帖子表
CREATE TABLE posts (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '帖子ID',
    user_id INT(11) NOT NULL COMMENT '作者ID',
    category_id INT(11) NOT NULL COMMENT '分类ID',
    title VARCHAR(200) NOT NULL COMMENT '帖子标题',
    content TEXT NOT NULL COMMENT '帖子内容',
    view_count INT(11) NOT NULL DEFAULT 0 COMMENT '浏览量',
    like_count INT(11) NOT NULL DEFAULT 0 COMMENT '点赞数',
    comment_count INT(11) NOT NULL DEFAULT 0 COMMENT '评论数',
    is_pinned TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否置顶：1是 0否',
    is_essence TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否精华：1是 0否',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态：1正常 0隐藏 2删除',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    update_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='帖子表';

-- 评论表
CREATE TABLE comments (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '评论ID',
    post_id INT(11) NOT NULL COMMENT '所属帖子ID',
    user_id INT(11) NOT NULL COMMENT '评论者ID',
    parent_id INT(11) DEFAULT NULL COMMENT '回复的评论ID，NULL表示直接回复帖子',
    content TEXT NOT NULL COMMENT '评论内容',
    status TINYINT(1) NOT NULL DEFAULT 1 COMMENT '状态：1正常 0隐藏',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

-- 点赞表
CREATE TABLE likes (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '点赞ID',
    post_id INT(11) NOT NULL COMMENT '帖子ID',
    user_id INT(11) NOT NULL COMMENT '用户ID',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    UNIQUE KEY uk_post_user (post_id, user_id),
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='点赞记录表';

-- 通知表
CREATE TABLE notifications (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '通知ID',
    user_id INT(11) NOT NULL COMMENT '接收者ID',
    sender_id INT(11) NOT NULL COMMENT '触发者ID',
    type VARCHAR(20) NOT NULL COMMENT '类型：comment/like/reply',
    post_id INT(11) NOT NULL COMMENT '关联帖子ID',
    comment_id INT(11) DEFAULT NULL COMMENT '关联评论ID',
    content VARCHAR(200) NOT NULL COMMENT '通知摘要',
    is_read TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已读：1是 0否',
    create_time DATETIME NOT NULL COMMENT '创建时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='通知表';

-- 种子数据
INSERT INTO categories (name, description, sort_order, create_time) VALUES
('教案分享', '分享优秀教案与教学设计', 1, NOW()),
('课堂管理', '课堂纪律、学生互动技巧', 2, NOW()),
('考试命题', '试题设计、试卷分析', 3, NOW()),
('教学反思', '课后反思与改进记录', 4, NOW()),
('职业英语', '职场英语教学内容交流', 5, NOW()),
('AI工具', 'AI辅助教学工具与经验', 6, NOW());
```

### Review 记录

**posts 表初稿问题（已全部修正）：**
1. 缺少 `id` 主键自增字段
2. `author_id` → 改为 `user_id`
3. 缺少 `comment_count` 冗余字段
4. 缺少 `is_pinned`、`is_essence`、`status`
5. 缺少 `create_time`、`update_time`
6. 末尾逗号语法错误
7. 缺少引擎和字符集声明

**likes 表初稿问题（已修正）：**
1. COMMENT 复制错误（"评论ID"→"点赞ID"，"评论者ID"→"用户ID"）

**notifications 表初稿问题（已修正）：**
1. 缺少 `comment_id INT(11) DEFAULT NULL` 字段
2. 多了 `status` 字段（不影响功能，保留）

### 验证结果
✅ SQL 运行成功，5 张表全部建表完成。

---

## 阶段 2：DB 层 — 写 Python SQL 函数（✅ 已完成）

### 学习要点

项目使用裸 SQL + pymysql，DB 层的三个工具函数（`db/connection.py`）：
```python
execute_query(sql, params) → 返回列表（多条结果）
execute_one(sql, params)  → 返回字典（单条结果）
execute_update(sql, params) → 返回影响行数（INSERT/UPDATE/DELETE）
```

### 完成函数清单

| 函数 | 作用 | 状态 |
|---|---|---|
| `get_post_list(category_id, sort, keyword, page, page_size)` | 分页列表 + 筛选 + 排序 + 搜索 | ✅ |
| `get_post_by_id(post_id)` | 单条查询 | ✅ |
| `create_post(post_data)` | 创建帖子 | ✅ |
| `update_post(post_id, update_data)` | 动态编辑帖子（只改传入字段） | ✅ |
| `delete_post(post_id)` | 软删除（status=2） | ✅ |
| `increment_view_count(post_id)` | 浏览量 +1 | ✅ |
| `update_post_counters(post_id, delta_likes, delta_comments)` | 点赞/评论计数增量 | ✅ |

### Review 记录

**`get_post_list` — 关键词搜索 params 数量不匹配（已修正）**
- Bug：SQL 有两个 `%s`（title LIKE + content LIKE），但 params 只 append 了一个
- 修正：`params.extend([keyword, keyword])`

**`create_post` — 缺少 create_time 字段（已修正）**
- posts 表 create_time 是 NOT NULL 的
- 修正：追加 `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`

**`update_post` — 多余 return 0（已修正）**
- Bug：category_id 判断块内有一个 `return 0`，导致后面逻辑全部跳过
- 修正：删除该行

**code review 最终发现：**
1. ✅ SQL 写法稳，view_count + 1 用 SQL 算术避免并发覆盖
2. ✅ update_post 动态拼接正确（is not None + update_fields/params 分离）
3. ❌ 第 2-3 行有无用 import（UserCreate, get_password_hash，从 user_db.py 复制时带入）
4. ❌ get_post_by_id 未过滤 status，被删的帖子还能查出来

---

## 阶段 3：Model 层 — Pydantic 请求/响应模型（🔄 进行中）

### 学习要点

Pydantic Model 层的两个职责：
| 方向 | 模型类型 | 例子 |
|---|---|---|
| 前端 → 后端 | 请求模型（Create/Update） | PostCreate、PostUpdate |
| 后端 → 前端 | 响应模型（Response） | PostResponse |

参考已掌握的 `model/user.py`：Field() 做约束，Optional 标记可选字段，`class Config: from_attributes = True` 让 Pydantic 能读数据库字典。

### 完成情况
✅ PostCreate、PostUpdate、PostResponse 三个模型全部正确，一次通过。

---

## 阶段 4：Service 层 — 业务逻辑（✅ 已完成）

### 学习要点

Service 层的位置：
```
API 层 → Service 层（校验+组装）→ DB 层（SQL）
```

### 完成函数清单

| 函数 | 作用 | 关键逻辑 |
|---|---|---|
| `create_post_service(post_data, user)` | 创建帖子 | user_id 从 JWT 注入 |
| `get_post_list_service(category_id, sort, keyword, page, page_size)` | 帖子列表 | content 裁切 100 字摘要 |
| `get_post_detail_service(post_id)` | 帖子详情 | 浏览量 +1 + 帖子不存在抛 404 |
| `update_post_service(post_id, update_data, user)` | 编辑帖子 | 校验作者本人 → 403 |
| `delete_post_service(post_id, user)` | 删除帖子 | 作者本人或管理员 → 403 |

### Review 记录

**权限校验理解纠正：**
- 学员原先在 `update_post_service` 里校验 `post_id != update_data.id`（PostUpdate 没有 id 字段）
- 正确逻辑：先查原帖，然后比对 `post["user_id"] != user["id"]`
- `user` 来自 JWT 自动注入（`Depends(get_current_user)`），不是前端传的

**get_post_detail_service 初次返回格式不统一：**
- 原先直接返回 `post` 对象，其他 Service 函数统一返回 `{code, msg, data}`
- 已修正为统一格式

---

## 阶段 5：API 路由层（✅ 已完成）

### 完成接口清单

| 方法 | 路径 | 认证 | 说明 |
|---|---|---|---|
| GET | `/posts` | 无需 | 帖子分页列表（筛选+排序+搜索） |
| GET | `/posts/{post_id}` | 无需 | 帖子详情（浏览量+1） |
| POST | `/posts` | JWT | 发布帖子 |
| PUT | `/posts/{post_id}` | JWT | 编辑帖子（仅作者本人） |
| DELETE | `/posts/{post_id}` | JWT | 删除帖子（作者或管理员） |

---

## 阶段 6：注册路由 + 测试（✅ 已完成）

### 注册
`backend/main.py` 已追加 `from backend.api.v1.community import router as community_router` 和 `app.include_router(community_router, ...)`

### 测试结果

| # | 测试项 | 状态 | 结果 |
|---|---|---|---|
| 1 | 登录后发帖 | 200 | `{"code": 200, "msg": "发布成功"}` |
| 2 | 帖子列表 | 200 | 返回 2 条帖子（含作者名 + 摘要） |
| 3 | 帖子详情 | 200 | 浏览量 +1 |
| 4 | 编辑帖子 | 200 | 仅修改标题生效 |
| 5 | 删除帖子 | 200 | 软删除（status=2） |
| 6 | 删除后列表过滤 | 200 | 已删帖子不出现在列表 ✅ |

### Bug 修复记录

**jwt.py Python 3.7 兼容性：**
- `int | None` → `Optional[int]`（需 import typing.Optional）

**PostCreate 无 user_id 字段：**
- Service 层直接传 `user["id"]` 给 DB 层，不挂到 Pydantic 模型上
- DB 层 `create_post(post_data, user_id)` 单独接收 user_id 参数

---

---

## 阶段 7：前端社区首页 + 帖子详情 + 发帖（✅ 已完成）

### 新增文件

| 文件 | 说明 |
|---|---|
| `CommunityView.vue` | 帖子列表 + 分类Tab + 排序 + 搜索 + 分页 |
| `PostDetailView.vue` | 帖子详情 + 评论列表 + 点赞toggle + 发表评论 |
| `PostCreateView.vue` | 发帖表单（标题/分类/内容） |

### 路由新增

| 路径 | 页面 | 认证 |
|---|---|---|
| `/community` | 社区首页（帖子列表） | 需登录 |
| `/community/create` | 发帖 | 需登录 |
| `/community/:postId` | 帖子详情 | 公开 |

### 后端新增端点

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/categories` | 分类列表 |
| GET/POST | `/posts/{id}/comments` | 评论列表 + 发表评论 |
| DELETE | `/comments/{id}` | 删除评论 |
| GET/POST | `/posts/{id}/like` | 点赞状态 + toggle |

### 构建结果
✅ 全部编译通过，零报错。新增 CommunityView.css (6.57kB) + PostDetailView.css (6.73kB) + PostCreateView.css (2.99kB)

### 性能优化
- 连接池 `PooledDB` 已启用（`connection.py`）
- posts 表索引已添加

---

## 后端开发完整流程总结

```
阶段 0: 理解业务 → 画数据关系图 → 确定表结构
阶段 1: 写建表 SQL → 种子数据 → init_db.py 验证
阶段 2: DB 层 → SQL 封装成函数（execute_query/one/update）
阶段 3: Model 层 → Pydantic 请求/响应校验
阶段 4: Service 层 → 权限校验 + 业务组装 + 统一返回格式
阶段 5: API 层 → FastAPI Router + Depends 注入 + try/except
阶段 6: 注册路由 + TestClient 端到端测试
阶段 7: 前端页面 → script setup + template + scoped style
```

**任何时候做新模块，套这个模板。**

---

*本日志由 Claude Code 在教学过程中实时维护。*
