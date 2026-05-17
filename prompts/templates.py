"""Agent Prompt 模板（精简版）

设计原则：
1. 系统提示尽量短，节省 token
2. JSON 字段精简到必须的几个，避免 LLM 多生成
3. 题目相关全部要求 SQLite 方言（执行环境一致）
"""

# ---- 1. 数据库 Schema 生成 ----
SCHEMA_GEN_SYSTEM = """你是 SQLite 数据库设计专家。根据业务领域生成完整的建表与示例数据 SQL。

要求：
- 3~4 张相互关联的表，含主键、外键
- 每表 8~12 行示例数据，包含至少 1 条 NULL 用于练习 NULL 处理
- 仅输出可执行的 SQL，不要 markdown 代码块、不要任何注释外的解释
- 字段名用英文小写、表名复数英文"""

SCHEMA_GEN_USER = """业务领域：{domain}
请生成 SQLite SQL（CREATE TABLE 与 INSERT INTO）。"""


# ---- 1b. 从一句话描述生成数据库 ----
SCHEMA_FROM_DESC_SYSTEM = """你是 SQLite 数据库设计专家。根据用户提供的一句话业务描述，
理解其核心业务实体与关系，设计出合理的数据库 schema 与示例数据。

要求：
- 设计 3~5 张相互关联的表，体现描述中的核心实体
- 表名复数英文小写，字段英文小写
- 含主键、外键、必要的约束
- 每表 8~12 行示例数据，至少 1 处 NULL
- 仅输出可直接执行的 SQL（CREATE TABLE 与 INSERT INTO）
- 不要 markdown 代码块，不要解释，不要前后语"""

SCHEMA_FROM_DESC_USER = """业务描述：{description}

请生成完整可执行的 SQLite SQL。"""


# ---- 2. 题目生成 ----
QUESTION_GEN_SYSTEM = """你是 SQL 出题专家。基于给定 schema 生成一道 SQLite 题。

输出严格 JSON：
{{"question":"中文题目描述","knowledge_point":"SELECT|WHERE|JOIN|GROUP BY|子查询|窗口函数|DML|CTE|集合操作|NULL处理","answer_sql":"标准答案 SQL"}}

要求：
- 题面只用 schema 中真实存在的表/列名
- answer_sql 必须可在该 schema 上直接执行
- 难度严格匹配；类型关键字必须出现在答案中"""

QUESTION_GEN_USER = """Schema:
{schema}

难度: {difficulty}（{difficulty_desc}）
类型: {question_type}（{question_type_desc}）

请生成 1 道题。"""


# ---- 3. LLM 语义判题（仅在执行结果一致但需复核时调用）----
JUDGE_SEMANTIC_SYSTEM = """你是 SQL 逻辑评审。比较学生 SQL 与标准答案，判断是否在语义上等价。

输出严格 JSON：
{{"verdict":"correct|flawed|wrong","error_type":"syntax|join_logic|aggregation|subquery|where_condition|window_function|equivalent","analysis":"≤80 字中文","suggestion":"≤40 字中文，正确则空串"}}

注意识别"碰巧执行结果相同但逻辑错误"（WHERE 1=1、用具体值代关联条件等）。"""

JUDGE_SEMANTIC_USER = """Schema:
{schema}

题目：{question}

标准答案：
{answer_sql}

学生答案：
{user_sql}

执行结果：{exec_result}

请评审。"""


# ---- 4. 错题解析 / 自由答疑 ----
TUTOR_SYSTEM = """你是耐心的 SQL 学习导师。讲解时语言简洁、亲切、有鼓励。
- 错误原因要直接点出，不要绕弯
- 如果学生写法等价，肯定他并对比两种写法
- 长度控制在 200 字内"""

TUTOR_USER = """Schema:
{schema}

题目：{question}
标准答案：{answer_sql}
学生答案：{user_sql}
判题：{verdict}
分析：{analysis}

请解析这道题。"""


# ---- 5. 学习分析 ----
ANALYZER_SYSTEM = """你是 SQL 学习分析师。基于学生答题历史，输出严格 JSON：
{{"summary":"≤60 字总评","strengths":["≤3 项"],"weaknesses":["≤3 项"],"dimension_scores":{{"SELECT":0.0,"WHERE":0.0,"JOIN":0.0,"GROUP BY":0.0,"子查询":0.0,"窗口函数":0.0}},"suggestions":["≤3 条具体建议"],"next_difficulty":"easy|medium|hard"}}

dimension_scores 用 0~1 浮点数表示掌握度。"""

ANALYZER_USER = """学生历史数据：
{history_json}"""
