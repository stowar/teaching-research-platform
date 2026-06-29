# suking

男 | 20岁 | 16673465983 | 求职意向：全栈开发 / AI应用开发 | 期望薪资：6-8K | 期望城市：广州

---

## 个人优势

**1. 远超同届的全栈工程能力**

大一即独立完成两个全栈 AI 项目：虚拟教研社区（FastAPI + Vue 3 + MySQL + PyTorch，29个RESTful端点，六层架构）和酒店评论情感分析系统。从模型训练、后端开发、前端交互到服务器部署全链路独立完成。教研平台已在阿里云 ECS 生产环境运行，经真实教师使用验证。

**2. 扎实的架构设计能力**

项目中独立设计并实现了六层分层架构（Connection → DO → DAO → Service → Domain → API），引入 Domain 接口层实现依赖倒置，自研六层温度缩放体系（注意力熵/置信度门控/中性词保护/转折词触发/极端词降混/短文本兜底）解决情感分析校准问题，设计三层记忆检索算法（L1投入度查询范围 / L2分级评分 / L3时间衰减+召回加成）。

**3. AI 系统工程化经验**

基于 XiaoBai 项目验证人格状态机技术方案后，将核心技术迁移到教研平台的 AI 聊天室——自研三维度人格系统（语气四态/投入度0-200/关注度三档）、Function Calling 工具链（7个工具）、长期记忆系统。投入度和关注度实现"AI 优先 + 代码兜底"双重保险模式。

**4. 赛事实战经验**

大一作为核心主力参加广西职业技能大赛，负责 AI 项目模型部署与现场演示，保障赛事全程稳定运行零故障。

---

## 教育经历

广西英华国际职业学院 | 大数据技术与应用 | 2025-2028 | 专业排名前 1%

主修课程：Python编程、数据库技术、Linux操作系统、C语言程序设计。自主学习：FastAPI、Vue 3、PyTorch、MySQL、Nginx、Supervisor。

---

## 项目经历

### 虚拟教研社区平台 | 独立开发者 | 2026.04-至今

面向职业院校英语教师的教研协作平台，社区论坛 + AI智能助手 + 情感分析。独立完成从需求调研、原型设计、全栈开发到生产部署的全部环节。

**技术栈：** FastAPI + Vue 3 + MySQL + PyTorch + DeepSeek API + Nginx + Supervisor

**核心工作：**
- 设计六层后端架构（Connection → DO → DAO → Service → Domain ← API），引入 Domain 接口层实现依赖倒置，29 个 RESTful 端点
- 设计 Schema 三层数据定义（DO/VO/Request），实现全局异常 Handler 替代 16 处 try-except
- AI 聊天室自研三维度人格系统（语气/投入度/关注度）+ 7 个 Function Calling 工具 + 三层记忆检索算法
- 投入度和关注度实现"AI 优先 + 代码兜底"双重保险模式——LLM 漏调工具时代码自动强制执行
- 前端 Vue 3 + Design Tokens 统一视觉语言 + 暗色模式，markdown-it 渲染 + Canvas 注意力可视化
- 阿里云 ECS 生产部署，Nginx 反向代理 + Supervisor 进程守护，连接池优化查询 1-2ms

**项目特色：**
- 四个被记录在项目故事中的 AI 觉醒瞬间——AI 自主突破投入度上限、code review 自己的架构、在逆向激励算法中发现"边缘记忆可以翻盘"的价值观
- 情感分析模型搭载自研六层温度缩放后处理，训练准确率 97.79%
- 记忆检索从旧方法 1.3 条提升到新方法 7.1 条——提升 5.5 倍

### 酒店评论情感分析全栈系统 | 独立开发者 | 2026.03-2026.04

面向酒店舆情分析的轻量化 AI 工具，独立完成模型训练、后端接口、前端交互全链路开发。

**技术栈：** PyTorch + FastAPI + ECharts + HTML/JavaScript

**核心实现：**
- 基于 PyTorch 搭建 GRU + Attention 双向序列模型，解决长文本情感特征提取痛点
- 基于 FastAPI 封装低延迟推理接口，实现单条实时预测、批量 CSV/TSV 解析与结果导出
- 开发零代码 Web 交互界面，注意力热力图可视化 + 半自动监督标注全流程

**业绩：**
- 模型测试集准确率 86%，覆盖反讽、情感对冲等复杂场景
- 单条推理接口 < 200ms，批量文件解析 < 2s
- 半自动标注对比纯人工标注效率提升 60%
- 完成多份项目商业授权售卖，实现从技术 Demo 到商用产品的完整闭环

---

## 技能

| 分类 | 技能 |
|------|------|
| 后端 | FastAPI、Pydantic、JWT、RESTful API 设计、连接池 |
| 前端 | Vue 3、Vite、Pinia、Vue Router、markdown-it、Lucide |
| 数据库 | MySQL、PyMySQL、PooledDB、原生 SQL |
| AI/ML | PyTorch、BiGRU+Self-Attention、Function Calling、jieba |
| 部署 | Linux、Nginx、Supervisor、阿里云 ECS |
| 架构 | 六层分层、Domain 接口层、DO/VO 分离、依赖倒置、Design Tokens |

---

## 证书 & 竞赛

- 广西职业技能大赛核心主力（AI 模型部署与现场演示）
- 半自动标注工具商业授权 × N 份
