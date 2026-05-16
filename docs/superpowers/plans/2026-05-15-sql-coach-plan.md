# SQL随身教练 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建基于 DeepSeek-V4-Pro 的 SQL 辅助学习桌面应用（Streamlit + SQLite + Electron）

**Architecture:** 5 个 Python Agent 模块通过统一 LLM 客户端调用 DeepSeek API，Streamlit 提供 3-Tab 前端界面，SQLite 持久化题库与用户数据，Electron 套壳发布为桌面应用。

**Tech Stack:** Python 3.10+, Streamlit 1.31+, OpenAI SDK, SQLite3, Plotly 5.0+, Electron

---

### Task 1: 项目初始化与目录结构

**Files:**
- Create: `requirements.txt`
- Create: `agent/__init__.py`
- Create: `db/__init__.py`
- Create: `ui/__init__.py`
- Create: `prompts/__init__.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
streamlit>=1.31
openai>=1.0
plotly>=5.0
pandas>=2.0
```

Write to `requirements.txt` at project root.

- [ ] **Step 2: 创建所有子目录和 __init__.py**

```bash
mkdir -p agent db ui prompts
touch agent/__init__.py db/__init__.py ui/__init__.py prompts/__init__.py
```

Run: `mkdir -p agent db ui prompts`

- [ ] **Step 3: 创建虚拟环境并安装依赖**

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Run: `python -m venv venv && source venv/Scripts/activate && pip install -r requirements.txt`

- [ ] **Step 4: 验证安装**

```bash
python -c "import streamlit; import openai; import plotly; import pandas; import sqlite3; print('OK')"
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add requirements.txt agent/__init__.py db/__init__.py ui/__init__.py prompts/__init__.py
git commit -m "feat: initialize project structure and dependencies"
```

---

### Task 2: 配置管理与 LLM 客户端封装

**Files:**
- Create: `config.py`
- Create: `agent/llm.py`
- Test: `tests/test_llm.py`

- [ ] **Step 1: 创建配置模块 config.py**

```python
"""SQL Coach 配置管理"""
import os

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "sql_coach.db")

# 难度映射
DIFFICULTY_MAP = {
    "easy": "初级 - 单表 SELECT、WHERE、ORDER BY",
    "medium": "中级 - JOIN、GROUP BY、HAVING、聚合函数",
    "hard": "高级 - 子查询、窗口函数、CTE"
}

# 知识领域
DOMAINS = ["学生管理系统", "电商订单系统", "图书管理系统", "企业人事系统"]

# 知识点维度
KNOWLEDGE_POINTS = ["SELECT", "WHERE", "JOIN", "GROUP BY", "子查询", "窗口函数"]
```

Write to `config.py`.

- [ ] **Step 2: 创建 LLM 客户端封装 agent/llm.py**

```python
"""DeepSeek LLM 客户端封装"""
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


class LLMClient:
    """统一 LLM 调用封装，所有 Agent 模块共用"""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = base_url or DEEPSEEK_BASE_URL
        self.model = model or DEEPSEEK_MODEL
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self._client

    def chat(self, system_prompt: str, user_message: str,
             temperature: float = 0.1, max_tokens: int = 4096) -> str:
        """发送 Chat Completion 请求，返回文本响应"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def chat_json(self, system_prompt: str, user_message: str,
                  temperature: float = 0.1) -> str:
        """发送请求并强制 JSON 格式输出"""
        full_system = f"{system_prompt}\n\n请严格按照JSON格式输出，不要包含其他内容。"
        return self.chat(full_system, user_message, temperature)
```

Write to `agent/llm.py`.

- [ ] **Step 3: 编写测试 tests/test_llm.py**

```python
"""LLM 客户端单元测试"""
import pytest
from unittest.mock import patch, MagicMock
from agent.llm import LLMClient


class TestLLMClient:
    def test_init_defaults(self):
        client = LLMClient(api_key="sk-test")
        assert client.model == "deepseek-chat"
        assert client.base_url == "https://api.deepseek.com"

    @patch("agent.llm.OpenAI")
    def test_chat_returns_content(self, mock_openai):
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "SELECT * FROM students;"
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        client = LLMClient(api_key="sk-test")
        client._client = mock_openai.return_value

        result = client.chat("You are a SQL expert.", "查询所有学生")
        assert result == "SELECT * FROM students;"

    @patch("agent.llm.OpenAI")
    def test_chat_json_appends_json_instruction(self, mock_openai):
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = '{"sql": "SELECT 1"}'
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        client = LLMClient(api_key="sk-test")
        client._client = mock_openai.return_value

        result = client.chat_json("You are helpful.", "Give me JSON")
        assert result == '{"sql": "SELECT 1"}'
```

Write to `tests/test_llm.py`.

- [ ] **Step 4: 运行测试**

```bash
pytest tests/test_llm.py -v
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add config.py agent/llm.py tests/test_llm.py
git commit -m "feat: add LLM client wrapper with DeepSeek API support"
```

---

### Task 3: Prompt 模板

**Files:**
- Create: `prompts/templates.py`
- Test: `tests/test_prompts.py`

- [ ] **Step 1: 创建 Prompt 模板 prompts/templates.py**

```python
"""5 个 Agent 模块的 Prompt 模板"""

SCHEMA_GEN_SYSTEM = """你是一个数据库设计专家。根据用户指定的业务领域，生成一个合理的SQLite数据库Schema。
要求：
1. 设计3-4个互相关联的表
2. 每个表包含4-8个字段，包含主键和外键
3. 为每个表生成10-15条有意义的示例数据
4. 使用中文作为字段注释

输出格式：纯SQL语句（CREATE TABLE + INSERT），不要包含其他内容。"""

SCHEMA_GEN_USER = """请为"{domain}"领域生成数据库Schema和示例数据。"""

QUESTION_GEN_SYSTEM = """你是一个SQL教学专家。根据提供的数据库Schema和难度等级，生成一道SQL查询题目。

要求：
1. 题目描述必须清晰明确
2. 标准答案SQL必须是可执行的
3. 难度严格匹配指定等级
4. 标注题目考察的知识点

输出JSON格式：
{{
  "question": "题目描述（自然语言）",
  "difficulty": "easy|medium|hard",
  "knowledge_point": "SELECT|WHERE|JOIN|GROUP BY|子查询|窗口函数",
  "answer_sql": "标准答案SQL语句"
}}"""

QUESTION_GEN_USER = """数据库Schema：
{schema}

难度：{difficulty}（{difficulty_desc}）

请生成一道SQL查询题目。"""

JUDGE_SEMANTIC_SYSTEM = """你是一个SQL逻辑审查专家。对比学生的SQL和标准答案，判断学生SQL是否正确。

即使执行结果相同，也要审查SQL逻辑是否真的正确。注意以下场景：
- 学生用WHERE 1=1代替正确条件，碰巧数据全部满足
- 学生用具体的值代替关联条件，碰巧值相等
- 学生遗漏了关键条件，但当前数据未暴露问题

输出JSON格式：
{{
  "verdict": "correct|flawed|wrong",
  "is_coincidence": true|false,
  "error_type": "syntax|join_logic|aggregation|subquery|where_condition|window_function|equivalent",
  "analysis": "详细分析（中文）",
  "suggestion": "修改建议（中文，如正确则为空）"
}}"""

JUDGE_SEMANTIC_USER = """数据库Schema：
{schema}

题目：{question}

标准答案SQL：
{answer_sql}

学生提交SQL：
{user_sql}

执行结果对比：{exec_result}

请审查学生SQL是否正确。"""

TUTOR_SYSTEM = """你是一个耐心细致的SQL学习导师。针对学生做错的SQL题目，提供清晰的解析和指导。

要求：
1. 用通俗易懂的语言解释错误原因
2. 如果学生SQL只是写法不同但逻辑正确，肯定学生并说明两种写法的区别
3. 如果学生答对了，可以提一些SQL优化建议
4. 鼓励学生继续练习"""

TUTOR_USER = """数据库Schema：
{schema}

题目：{question}

标准答案：{answer_sql}

我的答案：{user_sql}

判题结果：{verdict}
分析：{analysis}

请帮我解析这道题。"""

ANALYZER_SYSTEM = """你是一个SQL学习分析师。根据学生的答题历史数据，分析其SQL能力并给出改进建议。

要求：
1. 识别学生的强项和弱项
2. 按知识维度（SELECT/WHERE/JOIN/GROUP BY/子查询/窗口函数）分析正确率
3. 给出针对性的学习建议
4. 语言鼓励、积极向上

输出JSON格式：
{{
  "summary": "总体评价（中文）",
  "strengths": ["强项1", "强项2"],
  "weaknesses": ["弱项1", "弱项2"],
  "dimension_scores": {{
    "SELECT": 0.0-1.0,
    "WHERE": 0.0-1.0,
    "JOIN": 0.0-1.0,
    "GROUP BY": 0.0-1.0,
    "子查询": 0.0-1.0,
    "窗口函数": 0.0-1.0
  }},
  "suggestions": ["建议1", "建议2", "建议3"],
  "next_difficulty": "easy|medium|hard"
}}"""

ANALYZER_USER = """学生答题历史：
{history_json}

请分析学生的SQL能力并给出建议。"""
```

Write to `prompts/templates.py`.

- [ ] **Step 2: 编写测试 tests/test_prompts.py**

```python
"""Prompt 模板测试"""
from prompts.templates import (
    SCHEMA_GEN_SYSTEM, SCHEMA_GEN_USER,
    QUESTION_GEN_SYSTEM, QUESTION_GEN_USER,
    JUDGE_SEMANTIC_SYSTEM, JUDGE_SEMANTIC_USER,
    TUTOR_SYSTEM, TUTOR_USER,
    ANALYZER_SYSTEM, ANALYZER_USER
)


class TestPromptTemplates:
    def test_schema_gen_format(self):
        prompt = SCHEMA_GEN_USER.format(domain="学生管理系统")
        assert "学生管理系统" in prompt
        assert len(prompt) > 0

    def test_question_gen_format(self):
        prompt = QUESTION_GEN_USER.format(
            schema="students(id, name)",
            difficulty="easy",
            difficulty_desc="初级"
        )
        assert "students" in prompt
        assert "easy" in prompt

    def test_judge_format(self):
        prompt = JUDGE_SEMANTIC_USER.format(
            schema="students(id, name)",
            question="查询所有学生",
            answer_sql="SELECT * FROM students",
            user_sql="SELECT * FROM students",
            exec_result="结果相同"
        )
        assert "查询所有学生" in prompt

    def test_tutor_format(self):
        prompt = TUTOR_USER.format(
            schema="students(id, name)",
            question="查询所有学生",
            answer_sql="SELECT * FROM students",
            user_sql="SELECT * FROM students",
            verdict="correct",
            analysis="正确"
        )
        assert "students" in prompt

    def test_analyzer_format(self):
        prompt = ANALYZER_USER.format(history_json='[{"verdict": "correct"}]')
        assert "correct" in prompt
```

Write to `tests/test_prompts.py`.

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_prompts.py -v
```

Expected: 5 tests PASS

- [ ] **Step 4: Commit**

```bash
git add prompts/templates.py tests/test_prompts.py
git commit -m "feat: add 5 prompt templates for all agent modules"
```

---

### Task 4: 数据库存储层

**Files:**
- Create: `db/store.py`
- Test: `tests/test_store.py`

- [ ] **Step 1: 创建数据存储模块 db/store.py**

```python
"""SQLite 数据存储管理"""
import sqlite3
import os
from config import DB_PATH


class DataStore:
    """管理题库和用户答题记录的持久化存储"""

    def __init__(self, db_path: str = ""):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_tables()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_tables(self):
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS question_bank (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schema_name TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    knowledge_point TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    answer_sql TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS user_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER,
                    user_sql TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    error_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_id) REFERENCES question_bank(id)
                );
            """)

    def save_question(self, schema_name: str, difficulty: str,
                      knowledge_point: str, question_text: str,
                      answer_sql: str) -> int:
        """保存题目到题库，返回题目ID"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO question_bank (schema_name, difficulty, knowledge_point, question_text, answer_sql) VALUES (?, ?, ?, ?, ?)",
                (schema_name, difficulty, knowledge_point, question_text, answer_sql)
            )
            return cursor.lastrowid

    def get_question(self, question_id: int) -> dict:
        """根据ID获取题目"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM question_bank WHERE id = ?", (question_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_questions_by_schema(self, schema_name: str) -> list[dict]:
        """获取指定数据库的所有题目"""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM question_bank WHERE schema_name = ? ORDER BY difficulty, id",
                (schema_name,)
            ).fetchall()
            return [dict(r) for r in rows]

    def save_history(self, question_id: int, user_sql: str,
                     verdict: str, error_type: str = "") -> int:
        """保存答题记录"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "INSERT INTO user_history (question_id, user_sql, verdict, error_type) VALUES (?, ?, ?, ?)",
                (question_id, user_sql, verdict, error_type)
            )
            return cursor.lastrowid

    def get_user_history(self, limit: int = 100) -> list[dict]:
        """获取最近的答题记录"""
        with self._get_conn() as conn:
            rows = conn.execute(
                """SELECT uh.*, qb.question_text, qb.difficulty, qb.knowledge_point, qb.answer_sql
                   FROM user_history uh
                   LEFT JOIN question_bank qb ON uh.question_id = qb.id
                   ORDER BY uh.created_at DESC LIMIT ?""",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        """获取答题统计"""
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM user_history").fetchone()[0]
            correct = conn.execute(
                "SELECT COUNT(*) FROM user_history WHERE verdict = 'correct'"
            ).fetchone()[0]
            return {
                "total": total,
                "correct": correct,
                "accuracy": correct / total if total > 0 else 0.0
            }

    def get_dimension_stats(self) -> dict:
        """按知识维度统计正确率"""
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT qb.knowledge_point,
                       COUNT(*) as total,
                       SUM(CASE WHEN uh.verdict = 'correct' THEN 1 ELSE 0 END) as correct
                FROM user_history uh
                JOIN question_bank qb ON uh.question_id = qb.id
                GROUP BY qb.knowledge_point
            """).fetchall()
            result = {}
            for r in rows:
                result[r["knowledge_point"]] = {
                    "total": r["total"],
                    "correct": r["correct"],
                    "accuracy": r["correct"] / r["total"] if r["total"] > 0 else 0.0
                }
            return result
```

Write to `db/store.py`.

- [ ] **Step 2: 编写测试 tests/test_store.py**

```python
"""数据库存储层测试"""
import pytest
import os
import tempfile
from db.store import DataStore


@pytest.fixture
def store():
    tmp = tempfile.mktemp(suffix=".db")
    s = DataStore(db_path=tmp)
    yield s
    os.remove(tmp)


class TestDataStore:
    def test_init_creates_tables(self, store):
        conn = store._get_conn()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t["name"] for t in tables]
        assert "question_bank" in table_names
        assert "user_history" in table_names

    def test_save_and_get_question(self, store):
        qid = store.save_question(
            "test_schema", "easy", "SELECT",
            "查询所有用户", "SELECT * FROM users"
        )
        question = store.get_question(qid)
        assert question["question_text"] == "查询所有用户"
        assert question["answer_sql"] == "SELECT * FROM users"
        assert question["difficulty"] == "easy"

    def test_save_and_get_history(self, store):
        qid = store.save_question("db1", "medium", "JOIN", "Q1", "SELECT 1")
        hid = store.save_history(qid, "SELECT 1", "correct", "")
        history = store.get_user_history()
        assert len(history) == 1
        assert history[0]["verdict"] == "correct"

    def test_get_stats_empty(self, store):
        stats = store.get_stats()
        assert stats["total"] == 0
        assert stats["accuracy"] == 0.0

    def test_get_stats_with_data(self, store):
        qid = store.save_question("db1", "easy", "SELECT", "Q1", "SELECT 1")
        store.save_history(qid, "SELECT 1", "correct")
        store.save_history(qid, "WRONG", "wrong", "syntax")
        stats = store.get_stats()
        assert stats["total"] == 2
        assert stats["correct"] == 1
        assert stats["accuracy"] == 0.5

    def test_dimension_stats(self, store):
        qid1 = store.save_question("db1", "easy", "SELECT", "Q1", "SELECT 1")
        qid2 = store.save_question("db1", "medium", "JOIN", "Q2", "SELECT * FROM a JOIN b")
        store.save_history(qid1, "SELECT 1", "correct")
        store.save_history(qid2, "SELECT * FROM a JOIN b", "wrong", "join_logic")

        dims = store.get_dimension_stats()
        assert dims["SELECT"]["accuracy"] == 1.0
        assert dims["JOIN"]["accuracy"] == 0.0
```

Write to `tests/test_store.py`.

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_store.py -v
```

Expected: 6 tests PASS

- [ ] **Step 4: Commit**

```bash
git add db/store.py tests/test_store.py
git commit -m "feat: add SQLite data store with question bank and history"
```

---

### Task 5: Schema 与数据生成模块

**Files:**
- Create: `agent/schema_gen.py`

- [ ] **Step 1: 编写 Schema 生成器 agent/schema_gen.py**

```python
"""数据库 Schema 与实例数据生成模块"""
import json
from agent.llm import LLMClient
from prompts.templates import SCHEMA_GEN_SYSTEM, SCHEMA_GEN_USER


class SchemaGenerator:
    """调用 LLM 生成 SQLite 数据库 Schema 和示例数据"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, domain: str) -> str:
        """生成完整 SQL（CREATE TABLE + INSERT），返回 SQL 文本"""
        response = self.llm.chat(
            system_prompt=SCHEMA_GEN_SYSTEM,
            user_message=SCHEMA_GEN_USER.format(domain=domain)
        )
        return response.strip()

    def parse_schema(self, sql_text: str) -> dict:
        """解析生成的 SQL，提取 Schema 信息为字典"""
        tables = []
        current_table = None
        for line in sql_text.split("\n"):
            line_upper = line.strip().upper()
            if line_upper.startswith("CREATE TABLE"):
                parts = line.strip().split()
                if len(parts) >= 3:
                    name = parts[2].split("(")[0].strip("`\"'")
                    current_table = {"name": name, "columns": []}
                    tables.append(current_table)
            elif current_table and line.strip() and not line_upper.startswith("INSERT"):
                col = line.strip().lstrip(",").split()[0].strip("`\"'")
                if col and not col.upper().startswith(("PRIMARY", "FOREIGN", "CONSTRAINT", ")")):
                    current_table["columns"].append(col)
        return {"tables": tables, "raw_sql": sql_text}
```

Write to `agent/schema_gen.py`.

- [ ] **Step 2: 手动验证**

```bash
python -c "
from agent.llm import LLMClient
from agent.schema_gen import SchemaGenerator
# 需要设置 DEEPSEEK_API_KEY 环境变量
import os
if os.environ.get('DEEPSEEK_API_KEY'):
    llm = LLMClient()
    gen = SchemaGenerator(llm)
    sql = gen.generate('学生管理系统')
    print(sql[:500])
    # 验证包含 CREATE TABLE 和 INSERT
    assert 'CREATE TABLE' in sql.upper()
    assert 'INSERT' in sql.upper()
    print('Schema generation OK')
else:
    print('SKIP: DEEPSEEK_API_KEY not set')
"
```

- [ ] **Step 3: Commit**

```bash
git add agent/schema_gen.py
git commit -m "feat: add schema and data generation agent"
```

---

### Task 6: 题目生成模块

**Files:**
- Create: `agent/question_gen.py`

- [ ] **Step 1: 编写题目生成器 agent/question_gen.py**

```python
"""SQL 题目生成模块"""
import json
from agent.llm import LLMClient
from prompts.templates import QUESTION_GEN_SYSTEM, QUESTION_GEN_USER
from config import DIFFICULTY_MAP


class QuestionGenerator:
    """调用 LLM 生成不同难度的 SQL 题目"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, schema: str, difficulty: str) -> dict:
        """
        生成一道 SQL 题目
        参数: schema - 数据库 DDL（CREATE TABLE 语句）
              difficulty - easy / medium / hard
        返回: {"question", "difficulty", "knowledge_point", "answer_sql"}
        """
        response = self.llm.chat_json(
            system_prompt=QUESTION_GEN_SYSTEM,
            user_message=QUESTION_GEN_USER.format(
                schema=schema,
                difficulty=difficulty,
                difficulty_desc=DIFFICULTY_MAP.get(difficulty, "")
            )
        )
        return self._parse_response(response)

    def generate_batch(self, schema: str, difficulty: str, count: int = 3) -> list[dict]:
        """批量生成多道题目"""
        questions = []
        for _ in range(count):
            q = self.generate(schema, difficulty)
            if q:
                questions.append(q)
        return questions

    def _parse_response(self, response: str) -> dict:
        """解析 LLM 返回的 JSON"""
        try:
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1])
            return json.loads(response)
        except json.JSONDecodeError:
            return None
```

Write to `agent/question_gen.py`.

- [ ] **Step 2: 手动验证**

```bash
python -c "
import os, json
if os.environ.get('DEEPSEEK_API_KEY'):
    from agent.llm import LLMClient
    from agent.question_gen import QuestionGenerator
    llm = LLMClient()
    gen = QuestionGenerator(llm)
    schema = 'CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);'
    q = gen.generate(schema, 'easy')
    print(json.dumps(q, ensure_ascii=False, indent=2))
    assert 'question' in q
    assert 'answer_sql' in q
    print('Question generation OK')
else:
    print('SKIP: DEEPSEEK_API_KEY not set')
"
```

- [ ] **Step 3: Commit**

```bash
git add agent/question_gen.py
git commit -m "feat: add question generation agent"
```

---

### Task 7: 三层判题引擎

**Files:**
- Create: `agent/judge.py`
- Test: `tests/test_judge.py`

- [ ] **Step 1: 编写判题引擎 agent/judge.py**

```python
"""三层 SQL 判题引擎"""
import sqlite3
import json
from agent.llm import LLMClient
from prompts.templates import JUDGE_SEMANTIC_SYSTEM, JUDGE_SEMANTIC_USER


class JudgeEngine:
    """三层判题：语法检查 → 执行对比 → LLM 语义验证"""

    ERROR_TYPES = [
        "syntax", "join_logic", "aggregation", "subquery",
        "where_condition", "window_function", "equivalent"
    ]

    def __init__(self, llm: LLMClient = None):
        self.llm = llm

    def judge(self, schema_sql: str, question: str, answer_sql: str,
              user_sql: str) -> dict:
        """
        完整判题流程
        返回: {"verdict", "error_type", "analysis", "suggestion", "layer"}
        """
        # 第1层：语法检查
        syntax_ok, syntax_error = self._check_syntax(user_sql)
        if not syntax_ok:
            return {
                "verdict": "wrong",
                "error_type": "syntax",
                "analysis": f"SQL语法错误：{syntax_error}",
                "suggestion": "请检查SQL语句的语法，确保关键字、括号使用正确。",
                "layer": 1
            }

        # 第2层：执行结果对比
        exec_match, exec_info = self._compare_execution(schema_sql, answer_sql, user_sql)
        if not exec_match and exec_info != "execution_error":
            return {
                "verdict": "wrong",
                "error_type": "",
                "analysis": f"查询结果与标准答案不一致。\n{exec_info}",
                "suggestion": "",
                "layer": 2
            }

        # 第3层：LLM 语义验证
        if self.llm:
            return self._semantic_check(schema_sql, question, answer_sql,
                                        user_sql, "结果相同" if exec_match else exec_info)
        else:
            # 无 LLM 时，结果相同即判对
            verdict = "correct" if exec_match else "wrong"
            return {
                "verdict": verdict,
                "error_type": "",
                "analysis": "",
                "suggestion": "",
                "layer": 2
            }

    def _check_syntax(self, sql: str) -> tuple:
        """第1层：用 SQLite EXPLAIN 检查语法"""
        try:
            conn = sqlite3.connect(":memory:")
            conn.execute(f"EXPLAIN {sql}")
            conn.close()
            return True, ""
        except sqlite3.Error as e:
            return False, str(e)

    def _compare_execution(self, schema_sql: str, answer_sql: str,
                           user_sql: str) -> tuple:
        """第2层：在临时内存数据库中执行并对比结果"""
        try:
            conn = sqlite3.connect(":memory:")
            conn.executescript(schema_sql)

            cursor = conn.execute(answer_sql)
            answer_rows = [tuple(row) for row in cursor.fetchall()]

            cursor = conn.execute(user_sql)
            user_rows = [tuple(row) for row in cursor.fetchall()]
            conn.close()

            # 排序后比较（忽略列顺序和行顺序）
            answer_sorted = sorted(answer_rows)
            user_sorted = sorted(user_rows)

            if answer_sorted == user_sorted:
                return True, "结果完全相同"
            else:
                return False, f"预期{len(answer_rows)}行，得到{len(user_rows)}行。\n预期: {answer_sorted[:5]}\n实际: {user_sorted[:5]}"
        except sqlite3.Error as e:
            return False, "execution_error"
        except Exception as e:
            return False, f"执行错误: {str(e)}"

    def _semantic_check(self, schema_sql: str, question: str, answer_sql: str,
                        user_sql: str, exec_result: str) -> dict:
        """第3层：LLM 语义验证"""
        response = self.llm.chat_json(
            system_prompt=JUDGE_SEMANTIC_SYSTEM,
            user_message=JUDGE_SEMANTIC_USER.format(
                schema=schema_sql,
                question=question,
                answer_sql=answer_sql,
                user_sql=user_sql,
                exec_result=exec_result
            )
        )
        try:
            result = json.loads(response.strip().lstrip("```json").rstrip("```").strip())
            result["layer"] = 3
            return result
        except json.JSONDecodeError:
            return {
                "verdict": "correct",
                "error_type": "",
                "analysis": response,
                "suggestion": "",
                "layer": 3
            }
```

Write to `agent/judge.py`.

- [ ] **Step 2: 编写测试 tests/test_judge.py**

```python
"""判题引擎测试"""
import pytest
from agent.judge import JudgeEngine


class TestSyntaxCheck:
    def test_valid_sql(self):
        engine = JudgeEngine()
        ok, err = engine._check_syntax("SELECT * FROM students")
        assert ok is True

    def test_invalid_sql(self):
        engine = JudgeEngine()
        ok, err = engine._check_syntax("SELEC * FROM students")
        assert ok is False

    def test_missing_from(self):
        engine = JudgeEngine()
        ok, err = engine._check_syntax("SELECT * students")
        assert ok is False


SCHEMA = """
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
INSERT INTO students VALUES (1, '张三', 20);
INSERT INTO students VALUES (2, '李四', 22);
INSERT INTO students VALUES (3, '王五', 20);
"""


class TestExecutionCompare:
    def test_same_result(self):
        engine = JudgeEngine()
        ok, info = engine._compare_execution(
            SCHEMA,
            "SELECT * FROM students WHERE age = 20",
            "SELECT id, name, age FROM students WHERE age = 20"
        )
        assert ok is True

    def test_different_result(self):
        engine = JudgeEngine()
        ok, info = engine._compare_execution(
            SCHEMA,
            "SELECT * FROM students WHERE age = 20",
            "SELECT * FROM students WHERE age = 22"
        )
        assert ok is False

    def test_invalid_sql_execution(self):
        engine = JudgeEngine()
        ok, info = engine._compare_execution(
            SCHEMA,
            "SELECT * FROM students",
            "SELECT * FROM nonexistent"
        )
        assert ok is False


class TestFullJudge:
    def test_judge_syntax_error(self):
        engine = JudgeEngine()
        result = engine.judge(
            SCHEMA, "test", "SELECT * FROM students",
            "SELEC * FROM students"
        )
        assert result["verdict"] == "wrong"
        assert result["error_type"] == "syntax"
        assert result["layer"] == 1

    def test_judge_execution_match_without_llm(self):
        engine = JudgeEngine()
        result = engine.judge(
            SCHEMA, "test",
            "SELECT * FROM students WHERE name = '张三'",
            "SELECT * FROM students WHERE name = '张三'"
        )
        assert result["verdict"] == "correct"
```

Write to `tests/test_judge.py`.

- [ ] **Step 3: 运行测试**

```bash
pytest tests/test_judge.py -v
```

Expected: 6 tests PASS

- [ ] **Step 4: Commit**

```bash
git add agent/judge.py tests/test_judge.py
git commit -m "feat: add three-layer SQL judge engine"
```

---

### Task 8: 答疑导师模块

**Files:**
- Create: `agent/tutor.py`

- [ ] **Step 1: 编写答疑模块 agent/tutor.py**

```python
"""SQL 答疑导师模块"""
from agent.llm import LLMClient
from prompts.templates import TUTOR_SYSTEM, TUTOR_USER


class Tutor:
    """错题解析 + 自由答疑"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def explain(self, schema: str, question: str, answer_sql: str,
                user_sql: str, verdict: str, analysis: str) -> str:
        """根据判题结果生成错题解析"""
        return self.llm.chat(
            system_prompt=TUTOR_SYSTEM,
            user_message=TUTOR_USER.format(
                schema=schema,
                question=question,
                answer_sql=answer_sql,
                user_sql=user_sql,
                verdict=verdict,
                analysis=analysis
            )
        )

    def answer_question(self, schema: str, user_question: str) -> str:
        """自由答疑：回答用户的 SQL 相关问题"""
        return self.llm.chat(
            system_prompt=TUTOR_SYSTEM,
            user_message=f"""数据库Schema：
{schema}

学生提问：{user_question}

请用通俗易懂的方式解答。如果涉及SQL，请给出示例。"""
        )
```

Write to `agent/tutor.py`.

- [ ] **Step 2: Commit**

```bash
git add agent/tutor.py
git commit -m "feat: add tutor module for error explanation and Q&A"
```

---

### Task 9: 评分分析模块

**Files:**
- Create: `agent/analyzer.py`

- [ ] **Step 1: 编写分析模块 agent/analyzer.py**

```python
"""学习分析与评分模块"""
import json
from agent.llm import LLMClient
from prompts.templates import ANALYZER_SYSTEM, ANALYZER_USER
from config import KNOWLEDGE_POINTS


class Analyzer:
    """累计成绩分析与改进建议"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def analyze(self, history: list[dict], dimension_stats: dict) -> dict:
        """
        分析学生答题数据，返回分析结果
        参数: history - 答题记录列表
              dimension_stats - 按知识维度的统计数据
        返回: {"summary", "strengths", "weaknesses", "dimension_scores", "suggestions", "next_difficulty"}
        """
        history_json = json.dumps({
            "total_questions": len(history),
            "recent_20": [
                {
                    "question": h.get("question_text", ""),
                    "difficulty": h.get("difficulty", ""),
                    "knowledge_point": h.get("knowledge_point", ""),
                    "verdict": h.get("verdict", ""),
                    "error_type": h.get("error_type", "")
                }
                for h in history[-20:]
            ],
            "dimension_stats": dimension_stats
        }, ensure_ascii=False)

        response = self.llm.chat_json(
            system_prompt=ANALYZER_SYSTEM,
            user_message=ANALYZER_USER.format(history_json=history_json)
        )
        try:
            response = response.strip().lstrip("```json").rstrip("```").strip()
            return json.loads(response)
        except json.JSONDecodeError:
            return self._fallback_analysis(history, dimension_stats)

    def _fallback_analysis(self, history: list[dict],
                           dimension_stats: dict) -> dict:
        """LLM 解析失败时的回落分析"""
        accuracy = sum(1 for h in history if h.get("verdict") == "correct") / max(len(history), 1)
        scores = {}
        for kp in KNOWLEDGE_POINTS:
            dim = dimension_stats.get(kp, {"accuracy": 0.0})
            scores[kp] = dim["accuracy"]

        weaknesses = [kp for kp, v in scores.items() if v < 0.6]
        strengths = [kp for kp, v in scores.items() if v >= 0.8]

        if accuracy < 0.5:
            next_diff = "easy"
        elif accuracy < 0.8:
            next_diff = "medium"
        else:
            next_diff = "hard"

        return {
            "summary": f"你已完成{len(history)}道题，正确率{accuracy:.0%}。",
            "strengths": strengths or ["暂无足够数据"],
            "weaknesses": weaknesses or ["暂无足够数据"],
            "dimension_scores": scores,
            "suggestions": ["继续加油！"],
            "next_difficulty": next_diff
        }
```

Write to `agent/analyzer.py`.

- [ ] **Step 2: 编写单元验证脚本**

```bash
python -c "
from agent.analyzer import Analyzer
a = Analyzer(None)
result = a._fallback_analysis(
    [{'verdict': 'correct'}, {'verdict': 'wrong'}, {'verdict': 'correct'}],
    {'SELECT': {'accuracy': 1.0}, 'JOIN': {'accuracy': 0.0}}
)
assert result['dimension_scores']['SELECT'] == 1.0
assert result['dimension_scores']['JOIN'] == 0.0
print('Fallback analysis OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add agent/analyzer.py
git commit -m "feat: add scoring and analysis module"
```

---

### Task 10: Streamlit UI — 练习 Tab

**Files:**
- Create: `ui/practice.py`

- [ ] **Step 1: 编写练习 Tab ui/practice.py**

```python
"""Streamlit 练习 Tab — 对话式答题界面"""
import streamlit as st


def render_practice_tab(llm_client, store, current_schema, current_question):
    """渲染练习Tab的完整界面"""
    st.subheader("📝 SQL 练习")

    if not current_schema:
        st.info("👈 请先在侧边栏选择学习领域并生成数据库，然后点击"生成题目"开始练习。")
        return

    # 显示 Schema 浏览按钮
    with st.expander("📋 查看当前数据库结构", expanded=False):
        st.code(current_schema, language="sql")

    # 显示当前题目
    if current_question:
        st.markdown("### 🤖 当前题目")
        difficulty_labels = {"easy": "🟢 初级", "medium": "🟡 中级", "hard": "🔴 高级"}
        diff = st.session_state.get("current_difficulty", "easy")
        st.markdown(f"**难度**: {difficulty_labels.get(diff, diff)}")
        st.markdown(f"**知识点**: {current_question.get('knowledge_point', '')}")
        st.markdown(f"> {current_question.get('question', '')}")

    # 答题区
    st.markdown("### ✍️ 提交你的答案")
    user_sql = st.text_area(
        "SQL 语句",
        placeholder="请输入你的 SQL 语句...\n例如: SELECT * FROM students WHERE age > 18",
        height=150,
        key="sql_input"
    )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        submit = st.button("✅ 提交答案", type="primary", use_container_width=True)
    with col2:
        if st.button("💡 我需要提示", use_container_width=True):
            if current_question and llm_client:
                with st.spinner("生成提示..."):
                    from agent.tutor import Tutor
                    tutor = Tutor(llm_client)
                    hint = tutor.answer_question(
                        current_schema,
                        f"针对题目'{current_question.get('question', '')}'，请给出一个提示（不要直接给出答案），引导我思考解题思路。"
                    )
                    st.session_state["current_hint"] = hint

    if "current_hint" in st.session_state:
        with st.expander("💡 提示", expanded=True):
            st.markdown(st.session_state["current_hint"])

    # 处理提交
    if submit and user_sql.strip():
        _handle_submission(llm_client, store, current_schema, current_question, user_sql)
    elif submit:
        st.warning("请输入 SQL 语句。")


def _handle_submission(llm_client, store, current_schema, current_question, user_sql):
    """处理用户提交的SQL答案"""
    from agent.judge import JudgeEngine
    from agent.tutor import Tutor

    with st.spinner("正在判题..."):
        judge = JudgeEngine(llm_client)
        result = judge.judge(
            current_schema,
            current_question.get("question", ""),
            current_question.get("answer_sql", ""),
            user_sql
        )

    # 保存记录
    qid = st.session_state.get("current_question_id")
    if qid:
        store.save_history(qid, user_sql, result["verdict"],
                           result.get("error_type", ""))

    # 清除提示
    if "current_hint" in st.session_state:
        del st.session_state["current_hint"]

    # 显示结果
    verdict_icons = {
        "correct": "✅ 正确！",
        "flawed": "⚠️ 结果正确但逻辑有瑕疵",
        "wrong": "❌ 错误"
    }
    st.markdown(f"## {verdict_icons.get(result['verdict'], result['verdict'])}")

    if result.get("analysis"):
        st.markdown(f"**分析**: {result['analysis']}")

    if result.get("suggestion"):
        st.markdown(f"**建议**: {result['suggestion']}")

    # 错题自动解析
    if result["verdict"] != "correct":
        with st.spinner("🤖 生成详细解析..."):
            tutor = Tutor(llm_client)
            explanation = tutor.explain(
                current_schema,
                current_question.get("question", ""),
                current_question.get("answer_sql", ""),
                user_sql,
                result["verdict"],
                result.get("analysis", "")
            )
        st.markdown("### 📖 详细解析")
        st.markdown(explanation)

    # 刷新统计
    st.session_state["stats"] = store.get_stats()
    st.rerun()
```

Write to `ui/practice.py`.

- [ ] **Step 2: Commit**

```bash
git add ui/practice.py
git commit -m "feat: add practice tab with chat-based SQL answering"
```

---

### Task 11: Streamlit UI — 分析报告与数据浏览 Tab

**Files:**
- Create: `ui/report.py`
- Create: `ui/browser.py`

- [ ] **Step 1: 编写分析报告 Tab ui/report.py**

```python
"""Streamlit 分析报告 Tab — 雷达图 + 历史 + 建议"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import KNOWLEDGE_POINTS


def render_report_tab(llm_client, store):
    """渲染分析报告Tab"""
    st.subheader("📊 学习分析报告")

    stats = store.get_stats()
    if stats["total"] == 0:
        st.info("还没有答题记录，先去练习吧！")
        return

    # 总体统计卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总答题数", stats["total"])
    with col2:
        st.metric("正确数", stats["correct"])
    with col3:
        st.metric("正确率", f"{stats['accuracy']:.0%}")

    # 雷达图
    dim_stats = store.get_dimension_stats()
    st.markdown("### 🎯 能力雷达图")

    fig = _build_radar_chart(dim_stats)
    st.plotly_chart(fig, use_container_width=True)

    # 答题历史
    st.markdown("### 📝 答题历史")
    history = store.get_user_history(limit=50)
    if history:
        df = pd.DataFrame(history)
        df["结果"] = df["verdict"].map({
            "correct": "✅", "flawed": "⚠️", "wrong": "❌"
        })
        st.dataframe(
            df[["question_text", "difficulty", "knowledge_point", "结果"]].tail(20),
            use_container_width=True,
            hide_index=True
        )

    # LLM 分析建议
    if llm_client:
        st.markdown("### 💡 智能分析建议")
        if st.button("🔄 生成/刷新分析", type="primary"):
            with st.spinner("正在分析..."):
                from agent.analyzer import Analyzer
                analyzer = Analyzer(llm_client)
                analysis = analyzer.analyze(history, dim_stats)

                st.markdown(f"**总评**: {analysis.get('summary', '')}")

                col_s, col_w = st.columns(2)
                with col_s:
                    st.markdown("**强项**:")
                    for s in analysis.get("strengths", []):
                        st.markdown(f"- ✅ {s}")
                with col_w:
                    st.markdown("**弱项**:")
                    for w in analysis.get("weaknesses", []):
                        st.markdown(f"- ⚠️ {w}")

                st.markdown("**改进建议**:")
                for sug in analysis.get("suggestions", []):
                    st.markdown(f"- 💡 {sug}")

                next_diff = analysis.get("next_difficulty", "easy")
                diff_labels = {"easy": "初级", "medium": "中级", "hard": "高级"}
                st.info(f"📌 建议下次练习难度: **{diff_labels.get(next_diff, next_diff)}**")

    # 错误分布
    st.markdown("### 🔍 错误类型分布")
    error_data = _count_error_types(history)
    if error_data:
        fig2 = px.pie(
            names=list(error_data.keys()),
            values=list(error_data.values()),
            title="错误分类统计"
        )
        st.plotly_chart(fig2, use_container_width=True)


def _build_radar_chart(dim_stats: dict) -> go.Figure:
    """构建雷达图"""
    values = []
    for kp in KNOWLEDGE_POINTS:
        dim = dim_stats.get(kp, {"accuracy": 0.0})
        values.append(dim["accuracy"])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=KNOWLEDGE_POINTS,
        fill="toself",
        name="正确率",
        line_color="#3b82f6",
        fillcolor="rgba(59, 130, 246, 0.3)"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1], tickformat=".0%")),
        height=400
    )
    return fig


def _count_error_types(history: list[dict]) -> dict:
    """统计各类错误数量"""
    counts = {}
    for h in history:
        et = h.get("error_type") or ""
        if et and et != "equivalent":
            label = {
                "syntax": "语法错误", "join_logic": "JOIN错误",
                "aggregation": "聚合错误", "subquery": "子查询错误",
                "where_condition": "WHERE错误", "window_function": "窗口函数错误"
            }.get(et, et)
            counts[label] = counts.get(label, 0) + 1
    return counts
```

Write to `ui/report.py`.

- [ ] **Step 2: 编写数据浏览 Tab ui/browser.py**

```python
"""Streamlit 数据浏览 Tab"""
import streamlit as st


def render_browser_tab(current_schema, current_data):
    """渲染数据浏览Tab — 展示当前数据库的表结构和数据"""
    st.subheader("🗄️ 数据库浏览")

    if not current_schema:
        st.info("还没有生成数据库，请先在侧边栏选择领域并点击"生成数据库"。")
        return

    st.code(current_schema, language="sql")

    if current_data:
        st.markdown("---")
        for table_name, rows in current_data.items():
            st.markdown(f"### 📋 {table_name} ({len(rows)} 行)")
            if rows:
                import pandas as pd
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.caption("（空表）")
```

Write to `ui/browser.py`.

- [ ] **Step 3: Commit**

```bash
git add ui/report.py ui/browser.py
git commit -m "feat: add report tab with radar chart and browser tab"
```

---

### Task 12: Streamlit 主入口与侧边栏

**Files:**
- Create: `app.py`

- [ ] **Step 1: 编写主应用 app.py**

```python
"""SQL随身教练 — Streamlit 主入口"""
import streamlit as st
import sqlite3
from agent.llm import LLMClient
from agent.schema_gen import SchemaGenerator
from agent.question_gen import QuestionGenerator
from db.store import DataStore
from ui.practice import render_practice_tab
from ui.report import render_report_tab
from ui.browser import render_browser_tab
from config import DOMAINS

st.set_page_config(
    page_title="SQL随身教练",
    page_icon="🏠",
    layout="wide"
)


def init_session_state():
    """初始化所有会话状态"""
    defaults = {
        "api_key": "",
        "llm_client": None,
        "store": DataStore(),
        "current_schema": "",
        "current_schema_sql": "",
        "current_data": {},
        "current_question": None,
        "current_question_id": None,
        "current_difficulty": "easy",
        "current_domain": DOMAINS[0],
        "stats": {"total": 0, "correct": 0, "accuracy": 0.0},
        "current_hint": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def sidebar():
    """侧边栏：设置、进度、操作按钮"""
    with st.sidebar:
        st.title("🏠 SQL随身教练")

        # API Key
        st.markdown("### 🔑 API 设置")
        api_key = st.text_input(
            "DeepSeek API Key",
            type="password",
            value=st.session_state["api_key"],
            placeholder="sk-..."
        )
        if api_key != st.session_state["api_key"]:
            st.session_state["api_key"] = api_key
            if api_key:
                st.session_state["llm_client"] = LLMClient(api_key=api_key)
            else:
                st.session_state["llm_client"] = None

        st.divider()

        # 学习进度
        st.markdown("### 📊 学习进度")
        stats = st.session_state.get("stats", {})
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总题", stats.get("total", 0))
        with col2:
            st.metric("正确", stats.get("correct", 0))
        with col3:
            st.metric("正确率", f"{stats.get('accuracy', 0):.0%}")

        st.divider()

        # 设置
        st.markdown("### ⚙️ 学习设置")

        domain = st.selectbox("知识领域", DOMAINS,
                              index=DOMAINS.index(st.session_state["current_domain"]))
        st.session_state["current_domain"] = domain

        difficulty = st.selectbox("难度", ["easy", "medium", "hard"],
                                  index=["easy", "medium", "hard"].index(
                                      st.session_state["current_difficulty"]),
                                  format_func=lambda x: {"easy": "🟢 初级", "medium": "🟡 中级", "hard": "🔴 高级"}[x])
        st.session_state["current_difficulty"] = difficulty

        st.divider()

        # 操作按钮
        st.markdown("### 🎮 操作")

        if st.button("🗄️ 生成数据库", type="primary", use_container_width=True):
            _generate_schema()

        if st.button("📝 生成题目", type="primary", use_container_width=True):
            _generate_question()

        st.divider()

        # 刷新统计
        if st.button("🔄 刷新统计", use_container_width=True):
            st.session_state["stats"] = st.session_state["store"].get_stats()
            st.rerun()


def _generate_schema():
    """调用 LLM 生成数据库 Schema 和数据"""
    llm = st.session_state.get("llm_client")
    if not llm:
        st.error("请先输入 API Key！")
        return

    domain = st.session_state["current_domain"]
    with st.spinner(f"正在为'{domain}'生成数据库..."):
        gen = SchemaGenerator(llm)
        sql = gen.generate(domain)
        st.session_state["current_schema_sql"] = sql

        # 提取 Schema（仅 CREATE TABLE，用于展示）
        lines = []
        for line in sql.split("\n"):
            if line.strip().upper().startswith("CREATE TABLE") or (
                    lines and not line.strip().upper().startswith("INSERT")):
                lines.append(line)
            elif line.strip().upper().startswith("INSERT"):
                break
        st.session_state["current_schema"] = "\n".join(lines)

        # 在临时数据库中执行，获取数据预览
        try:
            conn = sqlite3.connect(":memory:")
            conn.executescript(sql)
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            data = {}
            for t in tables:
                rows = conn.execute(f"SELECT * FROM [{t[0]}]").fetchall()
                cols = [d[0] for d in conn.execute(f"PRAGMA table_info([{t[0]}])").fetchall()]
                data[t[0]] = [dict(zip(cols, row)) for row in rows]
            st.session_state["current_data"] = data
            conn.close()
        except Exception:
            st.session_state["current_data"] = {}

    st.success(f"'{domain}' 数据库已生成！")
    st.rerun()


def _generate_question():
    """调用 LLM 生成 SQL 题目"""
    llm = st.session_state.get("llm_client")
    schema = st.session_state.get("current_schema_sql")
    if not llm:
        st.error("请先输入 API Key！")
        return
    if not schema:
        st.error("请先生成数据库！")
        return

    difficulty = st.session_state["current_difficulty"]
    with st.spinner("正在生成题目..."):
        qgen = QuestionGenerator(llm)
        question = qgen.generate(schema, difficulty)

        if question:
            # 保存到题库
            qid = st.session_state["store"].save_question(
                schema_name=st.session_state["current_domain"],
                difficulty=difficulty,
                knowledge_point=question.get("knowledge_point", ""),
                question_text=question.get("question", ""),
                answer_sql=question.get("answer_sql", "")
            )
            st.session_state["current_question"] = question
            st.session_state["current_question_id"] = qid
            st.success("题目已生成！")
        else:
            st.error("题目生成失败，请重试。")

    st.rerun()


def main():
    init_session_state()
    sidebar()

    # 主区域 Tabs
    tab1, tab2, tab3 = st.tabs(["📝 练习", "📊 分析报告", "🗄️ 数据浏览"])

    with tab1:
        render_practice_tab(
            st.session_state.get("llm_client"),
            st.session_state["store"],
            st.session_state.get("current_schema", ""),
            st.session_state.get("current_question")
        )

    with tab2:
        render_report_tab(
            st.session_state.get("llm_client"),
            st.session_state["store"]
        )

    with tab3:
        render_browser_tab(
            st.session_state.get("current_schema_sql", ""),
            st.session_state.get("current_data", {})
        )


if __name__ == "__main__":
    main()
```

Write to `app.py`.

- [ ] **Step 2: 启动应用进行手动验证**

```bash
streamlit run app.py
```

手动验证清单：
- [ ] 输入 API Key 后侧边栏正常响应
- [ ] 点击"生成数据库"能生成 Schema 和数据
- [ ] 点击"生成题目"能出题
- [ ] 三个 Tab 可正常切换
- [ ] 数据浏览 Tab 能看到生成的表和数据

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add Streamlit main app with sidebar and 3 tabs"
```

---

### Task 13: Electron 桌面包装

**Files:**
- Create: `electron/main.js`
- Create: `electron/package.json`

- [ ] **Step 1: 创建 Electron 启动脚本 electron/main.js**

```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let streamlitProcess;

function startStreamlit() {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const venvPath = process.platform === 'win32'
        ? path.join(__dirname, '..', 'venv', 'Scripts', 'python.exe')
        : path.join(__dirname, '..', 'venv', 'bin', 'python');

    streamlitProcess = spawn(pythonCmd, [
        '-m', 'streamlit', 'run',
        path.join(__dirname, '..', 'app.py'),
        '--server.headless', 'true',
        '--server.port', '8501',
        '--browser.gatherUsageStats', 'false'
    ], {
        cwd: path.join(__dirname, '..'),
        stdio: 'pipe'
    });

    streamlitProcess.stdout.on('data', (data) => {
        console.log(`Streamlit: ${data}`);
    });

    streamlitProcess.stderr.on('data', (data) => {
        console.error(`Streamlit: ${data}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        title: 'SQL随身教练',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    // 等待 Streamlit 启动后加载
    setTimeout(() => {
        mainWindow.loadURL('http://localhost:8501');
    }, 3000);

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    startStreamlit();
    createWindow();
});

app.on('window-all-closed', () => {
    if (streamlitProcess) {
        streamlitProcess.kill();
    }
    app.quit();
});

app.on('before-quit', () => {
    if (streamlitProcess) {
        streamlitProcess.kill();
    }
});
```

Write to `electron/main.js`.

- [ ] **Step 2: 创建 Electron package.json electron/package.json**

```json
{
  "name": "sql-coach",
  "version": "1.0.0",
  "description": "SQL随身教练 - 基于大模型的SQL辅助学习系统",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder"
  },
  "devDependencies": {
    "electron": "^28.0.0",
    "electron-builder": "^24.0.0"
  },
  "build": {
    "appId": "com.sqlcoach.app",
    "productName": "SQL随身教练",
    "directories": {
      "output": "dist"
    }
  }
}
```

Write to `electron/package.json`.

- [ ] **Step 3: 创建启动脚本 run.py（可选：命令行一键启动）**

```python
"""一键启动 SQL 随身教练（无需 Electron 时使用）"""
import os
import sys
import subprocess


def main():
    print("=" * 50)
    print("  🏠 SQL随身教练")
    print("  基于 DeepSeek-V4-Pro 的 SQL 辅助学习系统")
    print("=" * 50)

    # 检查虚拟环境
    if not os.path.exists("venv"):
        print("\n⚠️ 未找到虚拟环境，正在创建...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("✅ 虚拟环境已创建")

    # 启动 Streamlit
    print("\n🚀 正在启动应用...")
    print("📱 浏览器将自动打开 http://localhost:8501")
    print("   如果未自动打开，请手动访问该地址")
    print("\n按 Ctrl+C 退出\n")

    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501"
    ])


if __name__ == "__main__":
    main()
```

Write to `run.py`.

- [ ] **Step 4: Commit**

```bash
git add electron/main.js electron/package.json run.py
git commit -m "feat: add Electron wrapper and one-click launcher"
```

---

### Task 14: 集成测试与收尾

**Files:**
- Create: `README.md`
- Create: `tests/test_integration.py`

- [ ] **Step 1: 编写 README.md**

```markdown
# SQL随身教练

基于 DeepSeek-V4-Pro 大模型的 SQL 辅助学习系统。

## 功能

- 🗄️ 自动生成数据库 Schema 和实例数据
- 📝 按难度分级生成 SQL 题目
- ✅ 三层判题机制（语法→执行→语义）
- 📖 错题解析与答疑
- 📊 学习分析与改进建议

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 启动应用
```bash
streamlit run app.py
```
或
```bash
python run.py
```

3. 在侧边栏输入 DeepSeek API Key
4. 选择领域，生成数据库，开始练习！

## 技术栈

- Python 3.10+ / Streamlit / SQLite
- DeepSeek-V4-Pro API
- Plotly 可视化
- Electron 桌面包装（可选）
```

Write to `README.md`.

- [ ] **Step 2: 运行所有测试**

```bash
pytest tests/ -v
```

Expected: All tests PASS

- [ ] **Step 3: 端到端手动测试清单**

```bash
streamlit run app.py
```

验证：
- [ ] 输入 API Key → 侧边栏进度面板正常
- [ ] 生成数据库 → 4 个领域均可正常生成
- [ ] 生成题目 → 三个难度均可正常出题
- [ ] 提交正确答案 → 判对，显示正确提示
- [ ] 提交错误答案 → 判错，显示解析
- [ ] 分析报告 Tab → 雷达图和统计正确
- [ ] 数据浏览 Tab → 表结构和数据可见
- [ ] 多次答题后 → 答题历史正确记录

- [ ] **Step 4: 最终 Commit**

```bash
git add README.md tests/test_integration.py
git commit -m "feat: add README, integration tests, and final polish"
```

---

## 附录：错误分类映射表

| 错误类型 | 中文名 | 典型表现 |
|---------|--------|---------|
| syntax | 语法错误 | 关键字拼写错误、括号不匹配 |
| join_logic | JOIN逻辑错误 | ON条件错误、漏JOIN表、多余JOIN |
| aggregation | 聚合/分组错误 | 缺少GROUP BY、HAVING误用 |
| subquery | 子查询错误 | 子查询返回多行、相关子查询逻辑错误 |
| where_condition | WHERE条件错误 | 条件遗漏、条件反转、类型不匹配 |
| window_function | 窗口函数错误 | PARTITION BY错误、框架子句误用 |
| equivalent | 逻辑等价 | SQL不同但逻辑正确，写法差异 |
