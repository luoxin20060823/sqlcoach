# SQL随身教练 — 设计规格文档

## 项目概述

基于大模型 Agent 的 SQL 辅助学习系统，提供数据库模式生成、SQL 题目出题、自动判题、错题解析、学习分析等完整学习闭环。

**交付物**：可运行的桌面 Demo + 技术报告/PPT

---

## 技术架构

```
Electron 桌面壳（加载 localhost）
    ↓
Streamlit 前端（3 Tab: 练习/分析报告/数据浏览）
    ↓
LLM Agent 引擎（Python，5 个模块）
    ↓
SQLite 数据库（题库 + 用户进度）
    ↓
DeepSeek-V4-Pro API（统一 LLM，用户提供 API Key）
```

### 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | Streamlit ≥1.31 | Chat 对话 + SQL 编辑器 + 图表 |
| 后端 | Python ≥3.10 | Agent 核心逻辑 |
| LLM | DeepSeek-V4-Pro | OpenAI SDK 兼容调用 |
| 数据库 | sqlite3 | Python 内置，零配置 |
| 图表 | plotly | 雷达图 + 进度可视化 |
| 桌面壳 | Electron | 加载 localhost Streamlit |

### 项目文件结构

```
sql-coach/
├── app.py              # Streamlit 主入口
├── agent/
│   ├── schema_gen.py   # Schema & 数据生成
│   ├── question_gen.py # 题目生成
│   ├── judge.py        # 三层判题引擎
│   ├── tutor.py        # 答疑导师
│   └── analyzer.py     # 评分分析
├── db/
│   └── store.py        # SQLite 管理
├── ui/
│   ├── practice.py     # 练习 Tab
│   ├── report.py       # 分析报告 Tab
│   └── browser.py      # 数据浏览 Tab
├── prompts/
│   └── templates.py    # 5 个 Prompt 模板
├── electron/
│   └── main.js         # Electron 启动脚本
├── requirements.txt
└── README.md
```

---

## 核心功能（学习闭环）

1. **Schema & 数据生成**：LLM 根据选择的知识领域自动生成 SQLite 数据库和实例数据
2. **题目生成**：LLM 基于当前数据库，按难度（初级/中级/高级）生成 SQL 题目，附带标准答案
3. **用户答题**：Streamlit Chat 界面，支持 SQL 代码输入和对话交互
4. **判题与答疑**：三层校验机制，错题自动触发解析
5. **评分分析**：累计正确率、知识维度雷达图、LLM 改进建议

---

## LLM Agent 设计

### 5 个 Prompt 模板，对应 5 个功能模块

| Prompt | 模块 | 职责 |
|--------|------|------|
| Prompt 1 | schema_gen.py | 生成 CREATE TABLE + INSERT 语句 |
| Prompt 2 | question_gen.py | 按难度生成题目 + 标准答案（JSON） |
| Prompt 3 | judge.py | 三层判题：语法→执行→语义验证 |
| Prompt 4 | tutor.py | 错题解析 + 自由答疑 |
| Prompt 5 | analyzer.py | 弱项分析 + 学习建议 |

### 统一 LLM 调用

```python
from openai import OpenAI

client = OpenAI(
    api_key="用户提供的 API Key",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    temperature=0.1  # SQL 任务低温度保证准确
)
```

---

## 三层判题机制

### 第 1 层：语法检查
- 使用 SQLite EXPLAIN 检查 SQL 是否可解析
- 失败 → 直接反馈语法错误

### 第 2 层：执行结果对比
- 分别执行标准答案 SQL 和用户 SQL
- 比较结果集（忽略列顺序）
- 结果不同 → 触发解析流程

### 第 3 层：LLM 语义验证（防"歪打正着"）
- 即使结果相同，LLM 也审查 SQL 逻辑
- 判决类型：
  - `correct`：逻辑等价/正确
  - `flawed`：逻辑有瑕疵（依赖数据巧合）
  - `wrong`：逻辑错误（碰巧结果对）→ 判错 + 解析

### 错误分类体系

- 语法错误、JOIN 逻辑错误、聚合/分组错误、子查询错误、WHERE 条件错误、窗口函数错误、逻辑等价但写法不同

---

## 界面设计

### Streamlit 布局

```
┌──────────────────────────────────────┐
│  🏠 SQL随身教练                       │
├────────┬─────────────────────────────┤
│ 侧边栏  │ [练习] [分析报告] [数据浏览]  │
│        │                             │
│ 学习进度│ 🤖 题目展示                  │
│ ✅ 12  │ 🧑 SQL编辑器                 │
│ ❌ 5   │ ✅/❌ 判题结果                │
│ 📈 70% │ 💡 解析/提示                  │
│        │                             │
│ ⚙️设置 │ [SQL输入框]  [发送]           │
│ 难度   │                             │
│ 领域   │                             │
│ 模型   │                             │
└────────┴─────────────────────────────┘
```

### 三个 Tab

1. **练习**：对话式答题，Chat 消息 + SQL 代码编辑
2. **分析报告**：雷达图 + 历史记录表 + LLM 改进建议
3. **数据浏览**：查看当前数据库表结构和数据概览

---

## 数据库设计

### SQLite 表结构

```sql
-- 存储已生成的题库（持久化复用）
CREATE TABLE question_bank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schema_name TEXT,          -- 所属数据库名
    difficulty TEXT,           -- easy / medium / hard
    knowledge_point TEXT,      -- SELECT / JOIN / GROUP BY / subquery / window
    question_text TEXT,        -- 题目描述
    answer_sql TEXT,           -- 标准答案
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 存储用户答题记录
CREATE TABLE user_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
    user_sql TEXT,             -- 用户提交的 SQL
    verdict TEXT,              -- correct / flawed / wrong
    error_type TEXT,           -- 错误分类
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES question_bank(id)
);
```

---

## 依赖清单

```
streamlit>=1.31
openai>=1.0
plotly>=5.0
pandas>=2.0
```

---

## 开发阶段预估

| 阶段 | 内容 | 产出 |
|------|------|------|
| P1 | LLM 调用封装 + Prompt 模板 | 5 个模块可独立调 LLM |
| P2 | Schema/数据生成 + 题目生成 | 能自动建库出题 |
| P3 | 判题引擎 + 答疑模块 | 三层判题 + 错题解析 |
| P4 | Streamlit UI | 3 Tab 完整界面 |
| P5 | 评分分析 + 雷达图 | 报告 Tab |
| P6 | Electron 包装 | 可双击运行的桌面软件 |
| P7 | 报告/PPT | 技术文档 |
