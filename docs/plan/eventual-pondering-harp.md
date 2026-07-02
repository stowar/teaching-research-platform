# RAG + Agent 两阶段管道架构重构

## Context

当前 `backend/services/ai_chat.py:chat()` 是一个约200行的单体方法：构建巨型 system prompt → 单次 AI 调用 + function calling 循环（11个工具全暴露）→ 返回。问题是：

1. **没有预处理层** — 所有上下文（状态、记忆、时间）都塞进 system prompt，依赖 AI 在对话中自行调用工具获取
2. **没有 RAG 检索** — 记忆检索是 system prompt 构建时的简单关键词匹配，不是独立的检索步骤
3. **工具混杂** — 信息类工具（get_state、get_current_time）和动作类工具（record_memory、adjust_engagement）混在一起，AI 每轮都要判断
4. **Provider 单例 bug** — `get_ai_provider(model)` 忽略后续 model 参数，无法支持不同阶段用不同模型

重构目标：将单体管道拆分为 **预处理层（轻量模型）+ 最终生成层（主模型）**，中间插入 RAG 检索和代码驱动的工具调用。

## 新架构

```
用户输入（原始保留）
    │
    ▼
┌─────────────────────────────────────────┐
│ PHASE 1: 预处理（轻量模型 flash）        │
│                                         │
│ Call 1: 提取关键信息（意图/关键词/实体/  │
│         建议调用的工具）                  │
│         ↓                               │
│ 代码执行: 关键词 → MemoryStore.query()   │
│          建议工具 → 调用对应函数          │
│         ↓                               │
│ Call 2: 整合 原始输入 + 提取信息 +       │
│         检索结果 + 工具结果 → 优化摘要    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ PHASE 2: 提示词组装（prompt_builder）    │
│                                         │
│ Layer 1: 系统指令（行为规则，精简版）     │
│ Layer 2: 状态层（personality status）    │
│ Layer 3: 记忆层（RAG 检索结果）          │
│ Layer 4: 预处理层（Call 2 优化上下文）    │
│ Layer 5: 用户状态（成就/配额/连续天数）   │
│                                         │
│ 上下文窗口: 历史消息（含原始用户输入）    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ PHASE 3: 主模型生成                      │
│                                         │
│ 可用工具（仅5个）:                       │
│   check_memory, record_memory,          │
│   adjust_engagement, adjust_attention,  │
│   unlock_achievement                    │
│                                         │
│ Function calling 循环（max 3轮）         │
│ + 代码强制兜底（engagement/attention）    │
└─────────────────────────────────────────┘
```

## 工具分类

| 阶段 | 工具 | 触发方式 |
|------|------|---------|
| Phase 1（预处理） | get_state, get_current_time, get_silence_timing, calc, translate, set_tone | 轻量 AI 提取 → 代码决定 → 结果注入 prompt |
| Phase 3（主模型） | check_memory, record_memory, adjust_engagement, adjust_attention, unlock_achievement | AI 在 function calling 中自主调用 |

## 文件变更清单

### 新建文件

1. **`backend/Agent/tool_router.py`** — 工具分类常量 + `split_tool_definitions()` + `build_preprocess_tool_hints()`
2. **`backend/Agent/preprocessor.py`** — `PreprocessResult` dataclass + `Preprocessor` 类（`run()`, `_extract()`, `_retrieve()`, `_optimize()`）
3. **`backend/Agent/prompt_builder.py`** — `build_layered_prompt()` + 各层构建函数 + `build_achievement_rules()`（从 rules.py 迁出）
4. **`backend/tests/`** — `conftest.py`, `test_preprocessor.py`, `test_prompt_builder.py`, `test_tool_router.py`, `test_provider.py`

### 修改文件

5. **`backend/Agent/provider.py`** — 修复单例 bug：`_provider` 改为 `_providers: dict`（model → instance）
6. **`backend/Agent/rules.py`** — 移除 `_build_ach_rules()` 和 `_build_user_state()`（迁到 prompt_builder）；保留所有常量和 `TONE_RULES`；`build_system_prompt()` 标记废弃
7. **`backend/core/config.py`** — 新增 `PREPROCESS_MODEL: str = os.getenv("PREPROCESS_MODEL", "deepseek-v4-flash")`
8. **`backend/services/ai_chat.py`** — 重构 `chat()` 为三阶段管道；新增 `_make_preprocess_executor()` 和 `_build_history_summary()`；预处理工具统计移到 Phase 1

### 不改的文件

`personality.py`, `memory.py`, `achievements.py`, `tools.py`, `domain/ai_chat.py`, `schema/vo/ai_chat.py`, `api/v1/ai_chat.py`, `core/deps.py`

## 实施顺序

1. **修复 provider 单例** — 所有模型调用的前提
2. **新增 config** — 一行 `PREPROCESS_MODEL`
3. **创建 tool_router.py** — 无依赖，独立
4. **创建 preprocessor.py** — 依赖 provider 接口 + tool_router
5. **创建 prompt_builder.py** — 依赖 PreprocessResult
6. **修改 rules.py** — 迁出函数，保留常量
7. **重构 ai_chat.py** — 主集成点
8. **添加测试** — 验证管道端到端

## 关键设计决策

- **轻量模型两次调用都是纯 chat()**（不用 function calling），更简单更便宜
- **Call 1 返回 JSON**，解析失败时优雅降级到默认值（不崩管道）
- **Call 2 返回自然语言摘要**，主 AI 作为 prompt 上下文读取
- **原始用户输入完全保留**：存入 DB 后通过 history 传进消息数组，不被任何预处理修改
- **calc/translate 的参数**由 Call 1 从用户输入中提取为 entities，tool_executor 接受 `**kwargs`
- **工具使用统计**（成就追踪）：预处理工具在 Phase 1 执行后立即统计；主模型工具在 function calling 循环中统计（逻辑不变）

## 验证方式

1. 启动后端 `cd backend && python -m uvicorn main:app --reload`
2. 用前端或 curl 发送对话请求，验证：
   - 正常对话返回格式不变（ChatReplyVO 结构完整）
   - AI 状态（tone/engagement/attention）正确更新
   - 记忆检索仍然生效（AI 回复中引用【根据你之前的信息……】）
   - 成就系统正常触发
   - calc/translate 工具仍可用
3. 运行 `pytest backend/tests/ -v` 验证新模块单元测试
