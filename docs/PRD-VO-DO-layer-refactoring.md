# PRD：后端分层架构重构 — VO/DO 层引入

## Problem Statement

当前后端代码从数据库到 API 响应的全链路都使用原始 `dict` 传递数据，导致以下问题：

1. **密码哈希泄露**：`login_service` 和 `register_service` 直接返回 `SELECT *` 的原始 dict，包含 `password` 字段，在 HTTP 响应中暴露密码哈希。
2. **响应格式不一致**：有的接口返回 `{"code": 200, "msg": "...", "data": ...}`，有的返回 `{"msg": "...", "access_token": ..., "user": ...}`，有的嵌套层级完全不同。前端需要针对每个接口做不同的解析逻辑。
3. **零类型安全**：所有层都用 `dict` 传数据，靠字符串 key 取值（`user["id"]`、`post["title"]`），IDE 无自动补全，字段拼写错误只能在运行时发现。
4. **数据库变更直接暴露**：给 `posts` 表加一列，API 响应就自动多一个字段。无法控制对外契约。
5. **Pydantic 模型形同虚设**：`UserResponse`、`PostResponse` 已定义但只用了 2 个接口，`from_attributes=True` 在该项目（raw pymysql）中永远不触发。

## Solution

引入 **DO（Data Object）/ VO（View Object）** 双层模型，严格执行分层访问规则：

```
┌─────────────────────────────────────────────────┐
│  API 层                                          │
│  只能 import: core/vo, services/                 │
│  职责: 绑定路由, 调用 service, 返回 VO            │
├─────────────────────────────────────────────────┤
│  Service 层                                      │
│  只能 import: model/ (DO), core/vo (VO), db/     │
│  职责: 业务逻辑, DO→VO 转换, 统一返回 VO           │
├─────────────────────────────────────────────────┤
│  DB 层                                           │
│  只能 import: model/ (DO)                        │
│  职责: SQL 执行, 返回 DO 对象                     │
└─────────────────────────────────────────────────┘
```

**核心规则**：
- **DO（model/）**：对应数据库表行，包含所有字段（含敏感字段如 password、status）。只有 DB 层和 Service 层可以 import。
- **VO（core/vo/）**：对外的返回模型，精心选择字段，格式化日期/枚举。只有 API 层和 Service 层可以 import。
- **API 层绝不 import model/ 中的 DO 类**。这是硬约束，违反则架构失效。
- **Request Schema（PostCreate、UserLogin 等）** 保留在 `model/` 作为"输入 DTO"，API 层可 import 它们（它们不是 DO）。

## User Stories

1. As a 后端开发者, I want 所有 API 响应有统一的 `ApiResponse[T]` 信封格式, so that 前端只需写一次响应解析逻辑。
2. As a 后端开发者, I want 密码哈希在任何情况下都不会出现在 HTTP 响应中, so that 不会因疏忽造成安全漏洞。
3. As a 后端开发者, I want Service 层返回强类型的 VO 对象而非 dict, so that IDE 可以自动补全字段名并在编译时捕获拼写错误。
4. As a 后端开发者, I want 数据库新增字段不会自动暴露到 API, so that 我可以安全地重构数据库而不影响前端。
5. As a 后端开发者, I want DO 和 VO 的转换逻辑集中在 Service 层, so that 转换规则可测试、可复用。
6. As a 前端开发者, I want 每个接口的返回结构是稳定的、可预期的, so that 不需要逐个接口调试响应格式。
7. As a 测试开发者, I want 可以单独测试 VO 序列化和 DO→VO 转换逻辑, so that 数据转换的正确性有保障。
8. As a 新加入的开发者, I want 通过看 VO 定义就能理解每个接口返回什么, so that 不需要深入 DB 层查字段。

## Implementation Decisions

### 1. 目录结构

```
backend/
  core/
    vo/                          # 新增：View Objects
      __init__.py                # 导出所有 VO，提供 response() 快捷函数
      common.py                  # ApiResponse[T], PageVO[T]
      user.py                    # UserVO, LoginVO
      community.py               # PostVO, CommentVO, NotificationVO, CategoryVO, PostListVO
      sentiment.py               # SentimentResultVO
  model/                         # 重定位为 DO + Request Schema
    __init__.py
    user.py                      # UserDO + UserCreate, UserUpdate, UserUpdatePassword, UserLogin
    community.py                 # PostDO, CommentDO, NotificationDO, CategoryDO + PostCreate, PostUpdate, CommentCreate
```

### 2. 统一响应信封

所有接口返回统一包装为泛型 `ApiResponse[T]`：

```python
# core/vo/common.py
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    msg: str = "ok"
    data: Optional[T] = None

class PageVO(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
```

### 3. DO 定义示例

DO 必须包含 DB 表的所有字段，不做任何裁剪：

```python
# model/user.py — UserDO
class UserDO(BaseModel):
    """数据库 users 表的完整映射，包含所有列（含密码）"""
    id: int
    phone: str
    password: str              # ← 存在于 DO 中
    name: Optional[str]
    school: Optional[str]
    title: Optional[str]
    role: str
    status: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True  # 兼容 dict 转换（model_validate）
```

### 4. VO 定义示例

VO 只包含需要返回给客户端的字段，不含密码等敏感字段：

```python
# core/vo/user.py
class UserVO(BaseModel):
    """用户信息 VO — 不含密码、不含 status"""
    id: int
    phone: str
    name: Optional[str]
    school: Optional[str]
    title: Optional[str]
    role: str
    role_label: str              # ← 格式化后的角色名 "管理员"/"教师"
    create_time: str             # ← 格式化后的时间字符串

class LoginVO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserVO
```

### 5. DB 层改造

DB 函数返回 DO 对象而非原始 dict：

```python
# db/user_db.py (改造后)
def get_user_by_id(user_id: int) -> Optional[UserDO]:
    raw = execute_one("SELECT * FROM users WHERE id = %s", (user_id,))
    if raw is None:
        return None
    return UserDO.model_validate(raw)   # dict → DO

def get_user_by_phone(phone: str) -> Optional[UserDO]:
    raw = execute_one("SELECT * FROM users WHERE phone = %s", (phone,))
    if raw is None:
        return None
    return UserDO.model_validate(raw)
```

### 6. Service 层改造

Service 层接收 DO，返回 VO。DO→VO 转换在 Service 层完成：

```python
# services/auth.py (改造后)
from backend.core.vo.user import UserVO, LoginVO
from backend.core.vo.common import ApiResponse

def login_service(phone: str, password: str) -> ApiResponse[LoginVO]:
    user_do = user_db.get_user_by_phone(phone)       # ← DO 对象
    if not user_do:
        raise BusinessException("用户不存在", code=400)

    if not verify_password(password, user_do.password):  # ← 类型安全访问
        raise BusinessException("密码错误", code=401)

    access_token = create_access_token(user_do.id)
    return ApiResponse(
        msg="登录成功",
        data=LoginVO(
            access_token=access_token,
            user=_to_user_vo(user_do),               # ← DO→VO 转换
        )
    )

def _to_user_vo(u: UserDO) -> UserVO:
    """DO→VO 转换（Service 层内部复用）"""
    return UserVO(
        id=u.id, phone=u.phone, name=u.name,
        school=u.school, title=u.title, role=u.role,
        role_label="管理员" if u.role == "admin" else "教师",
        create_time=u.create_time.strftime("%Y-%m-%d %H:%M"),
    )
```

### 7. API 层改造

API 层不再 import DO，改为声明 `response_model`：

```python
# api/v1/auth.py (改造后)
from backend.core.vo.user import LoginVO
from backend.core.vo.common import ApiResponse

@router.post("/login", response_model=ApiResponse[LoginVO])
def login(login_data: UserLogin):
    return auth_service.login_service(login_data.phone, login_data.password)
    # 返回的是 ApiResponse Pydantic 对象，FastAPI 自动序列化
```

### 8. 现有 Request Schema 的处理

`PostCreate`、`PostUpdate`、`UserLogin`、`UserCreate`、`CommentCreate`、`UserUpdatePassword` 等**请求模型**保持放在 `model/` 中。它们不是 DO（不含 password 之外的全量 DB 字段），也不是 VO（不作为返回值）。它们是 API 输入契约，API 层可以 import 它们。

命名约定：请求模型保持现有命名（`XxxCreate`、`XxxUpdate`），DO 加 `DO` 后缀，VO 加 `VO` 后缀。这是临时过渡策略 —— 目的是让 DO 和 VO 在 import 时一眼可辨，避免混淆。

### 9. 安全约束实现

`UserVO` **不包含** `password` 字段。即使开发者误把 `UserDO` 传给 API 响应，Pydantic 的 `response_model` 校验也会在序列化时过滤掉未定义的字段。双重保障：

- 代码层面：Service 层只返回 VO，VO 不含 password → 编译时安全
- 运行时层面：`response_model` 做字段白名单过滤 → 运行时兜底

### 10. 迁移策略

分 3 个阶段迁移，每阶段可独立上线：

| 阶段 | 范围 | 工作量 | 风险 |
|------|------|--------|------|
| Phase 1 | 新 `core/vo/` 目录 + `ApiResponse` + `common.py`，改造 `auth` 模块（登录/注册） | 2 个 Service, 2 个 API | 低 — auth 最简单，适合验证方案 |
| Phase 2 | 社区模块：PostVO、CommentVO、NotificationVO、CategoryVO + 全部社区 Service 改造 | 11 个 Service, 15 个 API | 中 — 涉及最多端点 |
| Phase 3 | 用户模块：UserVO + admin 模块 + sentiment 模块 | 6 个 Service, 7 个 API | 低 — 收尾工作 |

每个 Phase 完成后可 deploy 到服务器验证。

## Testing Decisions

### 测试边界

- **VO 序列化测试**：构造 VO 对象，验证 `.model_dump()` 输出符合预期（字段名、类型、缺失敏感字段）。
- **DO→VO 转换测试**：构造 DO，调用 `_to_xxx_vo()` 转换函数，验证字段映射正确、角色/时间等派生字段格式化正确。
- **API 契约测试**：发 HTTP 请求，断言响应 JSON 的 key 集合与 VO 定义一致，不包含多余字段。
- **不测试 DB 层 SQL**：保持现状，DB 函数本身不引入新逻辑。

### 参考现有测试

项目当前无自动化测试。本次重构以 **手动验证 + 前端联调** 为主。每个 Phase 完成后，启动 dev server，从前端页面验证关键流程（登录 → 发帖 → 查看通知）。

### 好测试的标准

- 测试对外行为（API 返回什么字段），不测试实现细节（DO 有几个字段）。
- 每个 VO 至少一个序列化测试。
- 每个 `_to_xxx_vo()` 转换函数至少一个映射正确性测试。

## Out of Scope

1. **不引入 ORM**：继续使用 pymysql + raw SQL，DO 通过 `model_validate(dict)` 构造。
2. **不改造前端**：VO 的字段名保持与现有 dict key 一致（如 `author_name` 而非 `author`），前端无需改动。
3. **不引入 Repository 模式**：DB 层保持现有结构，仅在返回值类型上做改造。
4. **不引入依赖注入容器**：继续使用 FastAPI 的 `Depends()`。
5. **不动 sentiment 预测模块的数学逻辑**：仅包装返回值为 VO。
6. **不增加新的第三方依赖**：仅使用 Pydantic（已有）和 Python 标准库。

## Further Notes

### 与你原始方案的对照评估

你提出的方案（core 加 VO 层 + model 做 DO 层 + API 不碰 model）在架构上是**正确且成熟的分层模式**，常见于 Java Spring（DTO/VO/DO 三层）和 Go 项目。具体评价：

**值得做的理由**：
- 密码哈希泄露是真实的安全隐患，当前 `login_service` 返回的 `user` 对象包含 `password` 字段。VO 层可以从**结构上**杜绝此类问题。
- 响应格式统一后，前端只需一个拦截器处理 `ApiResponse`，不再逐接口适配。
- Pydantic 泛型 `ApiResponse[T]` 配合 `response_model` 能自动生成 OpenAPI 文档，Swagger UI 会显示每个接口的精确返回结构。

**需要警惕的点**：
- 你的项目规模（~25 个端点、6 种实体）用 DO/VO 分层不会太沉重，但要避免过度抽象。**不要**引入 Builder、Mapper、Factory 等设计模式 —— 一个简单的 `_to_xxx_vo()` 函数就够了。
- DO 目前通过 `model_validate(dict)` 从 raw dict 构造，这一步本质上是把运行时 dict 校验转为 Pydantic 校验。**如果某天你换上 SQLAlchemy ORM**，`from_attributes = True` 就能直接生效，DO 定义不需要改。
- 最大的成本不是写代码，而是**记住规则**（哪些层能 import 什么）。建议在 `__init__.py` 里用 `__all__` 明确导出，并在 code review 时检查 import 语句。

**我的建议**：按 Phase 1 → 2 → 3 的顺序推进。Phase 1 做完后先在前端验证登录和注册流程正常，确认方案可行再继续。如果中途觉得 DO 层收益不够明显（因为你的 DB 表结构已经很稳定），可以只保留 VO 层 + `_to_vo()` 转换函数，DB 层继续返回 dict —— 但 API 不碰 model 的规则仍然有效。

### 当前已知的需要修复的密码泄露点

| 文件 | 函数 | 问题 |
|------|------|------|
| `services/auth.py:29` | `login_service` | `"user": user` — user 是 DB dict，含 `password` |
| `services/auth.py:44` | `register_service` | `"data": new_user` — new_user 是 DB dict，含 `password` |
| `services/users.py:13` | `update_current_user_info_service` | `"data": r_updated_user` — DB dict，含 `password` |
| `services/admin.py` | 多个函数 | 返回 raw DB user dict，含 `password` |
| `core/deps.py:31` | `get_current_user` | 返回的 dict 含 `password`，`GET /users/me` 通过 `response_model=UserResponse` 过滤了，但其他不声明 response_model 的接口如果拿到 current_user 直接返回就泄露 |
