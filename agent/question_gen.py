"""SQL 题目生成模块

性能与实用性优化：
- 题库复用：DataStore 中已有同 schema+难度+类型 的题目可直接抽取（设置开启时）
- 并发批量：generate_batch 使用 ThreadPoolExecutor 并发请求
- JSON Mode：使用 OpenAI 兼容的 response_format=json_object
- max_tokens 调到 1024（默认 4096 的 1/4）
"""
import json
import random
import re
import sqlite3
from agent.llm import LLMClient
from prompts.templates import QUESTION_GEN_SYSTEM, QUESTION_GEN_USER
from config import DIFFICULTY_MAP, QUESTION_TYPES, load_settings


class QuestionGenerator:
    """生成 SQL 题目"""

    def __init__(self, llm: LLMClient, store=None):
        self.llm = llm
        self.store = store
        self._settings = load_settings()

    # ---- 单题生成 ----
    def generate(self, schema: str, difficulty: str, question_type: str = "",
                 schema_name: str = "", allow_reuse: bool = True) -> dict:
        """生成一道题。

        优先从题库抽取，再调 LLM；调失败/解析失败时返回 None。
        """
        if not question_type or question_type == "random":
            question_type = random.choice(list(QUESTION_TYPES.keys()))

        # 题库复用（同 schema_name + difficulty + question_type）
        if (allow_reuse
                and self.store is not None and schema_name
                and self._settings.get("reuse_question_bank", True)):
            reused = self.store.pick_random_question(
                schema_name, difficulty, question_type
            )
            if reused:
                return {
                    "question": reused["question_text"],
                    "answer_sql": reused["answer_sql"],
                    "knowledge_point": reused["knowledge_point"],
                    "question_type": reused.get("question_type", question_type),
                    "difficulty": reused.get("difficulty", difficulty),
                    "_reused": True,
                }

        return self._llm_generate(schema, difficulty, question_type)

    def _llm_generate(self, schema: str, difficulty: str, question_type: str) -> dict:
        type_desc = QUESTION_TYPES.get(question_type, question_type)
        max_tokens = int(self._settings.get("max_tokens_question", 1024))
        try:
            response = self.llm.chat_json(
                system_prompt=QUESTION_GEN_SYSTEM,
                user_message=QUESTION_GEN_USER.format(
                    schema=schema,
                    difficulty=difficulty,
                    difficulty_desc=DIFFICULTY_MAP.get(difficulty, ""),
                    question_type=question_type,
                    question_type_desc=type_desc,
                ),
                temperature=0.4,
                max_tokens=max_tokens,
            )
        except Exception:
            return None

        result = self._parse_response(response)
        if not result:
            return None

        # 验证 answer_sql 在该 schema 下是否真的可执行（避免脏题）
        if not self._validate_sql(schema, result.get("answer_sql", "")):
            return None

        result.setdefault("question_type", question_type)
        result.setdefault("difficulty", difficulty)
        return result

    # ---- 并发批量生成 ----
    def generate_batch(self, schema: str, difficulty: str,
                       count: int = 3, question_type: str = "") -> list:
        """并发生成多道题（不走题库复用）。"""
        if not question_type or question_type == "random":
            type_pool = list(QUESTION_TYPES.keys())
            types = [random.choice(type_pool) for _ in range(count)]
        else:
            types = [question_type] * count

        max_tokens = int(self._settings.get("max_tokens_question", 1024))
        requests = []
        for t in types:
            type_desc = QUESTION_TYPES.get(t, t)
            requests.append({
                "system_prompt": QUESTION_GEN_SYSTEM,
                "user_message": QUESTION_GEN_USER.format(
                    schema=schema,
                    difficulty=difficulty,
                    difficulty_desc=DIFFICULTY_MAP.get(difficulty, ""),
                    question_type=t,
                    question_type_desc=type_desc,
                ),
                "temperature": 0.4,
                "max_tokens": max_tokens,
            })

        responses = self.llm.chat_many(requests, max_workers=min(count, 4))

        questions = []
        for resp, t in zip(responses, types):
            if not resp:
                continue
            q = self._parse_response(resp)
            if q and self._validate_sql(schema, q.get("answer_sql", "")):
                q.setdefault("question_type", t)
                q.setdefault("difficulty", difficulty)
                questions.append(q)
        return questions

    # ---- 工具 ----
    @staticmethod
    def get_types() -> dict:
        return QUESTION_TYPES

    def _parse_response(self, response: str) -> dict:
        if not response:
            return None
        text = response.strip()
        # 去掉 ```json 包裹
        m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if m:
            text = m.group(1)
        else:
            start, end = text.find('{'), text.rfind('}')
            if start != -1 and end > start:
                text = text[start:end + 1]
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        if "question" not in data or "answer_sql" not in data:
            return None
        return data

    @staticmethod
    def _validate_sql(schema: str, sql: str) -> bool:
        """在内存数据库中执行 schema + 用户 sql，验证可执行。"""
        if not sql:
            return False
        try:
            conn = sqlite3.connect(":memory:")
            conn.executescript(schema)
            conn.execute(sql)
            conn.close()
            return True
        except Exception:
            return False
