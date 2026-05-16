"""三层 SQL 判题引擎

性能优化：
- 默认快速路径：语法 → 执行结果对比，结果一致直接 correct，不调 LLM
- LLM 语义复核做成开关（settings.enable_semantic_judge），默认关闭
- LLM 调用统一走 json_mode，max_tokens 收紧到 768
"""
import sqlite3
import json
import re
from agent.llm import LLMClient, LLMError
from prompts.templates import JUDGE_SEMANTIC_SYSTEM, JUDGE_SEMANTIC_USER
from config import load_settings


class JudgeEngine:
    """三层判题：语法 → 执行 → (可选) LLM 语义"""

    ERROR_TYPES = [
        "syntax", "join_logic", "aggregation", "subquery",
        "where_condition", "window_function", "equivalent",
    ]

    def __init__(self, llm: LLMClient = None, enable_semantic: bool = None):
        self.llm = llm
        settings = load_settings()
        # 显式传 enable_semantic 优先；否则从配置读
        if enable_semantic is None:
            enable_semantic = settings.get("enable_semantic_judge", False)
        self.enable_semantic = bool(enable_semantic)
        self.max_tokens = int(settings.get("max_tokens_judge", 768))

    def judge(self, schema_sql: str, question: str, answer_sql: str,
              user_sql: str) -> dict:
        """完整判题流程

        返回: {verdict, error_type, analysis, suggestion, layer}
        layer: 1=语法 2=执行 3=语义
        """
        # 第1层：语法
        ok, err = self._check_syntax(user_sql)
        if not ok:
            return {
                "verdict": "wrong",
                "error_type": "syntax",
                "analysis": f"SQL 语法错误：{err}",
                "suggestion": "检查关键字、括号、分号是否正确。",
                "layer": 1,
            }

        # 第2层：执行结果对比
        match, info = self._compare_execution(schema_sql, answer_sql, user_sql)
        if not match and info != "execution_error":
            # 结果不一致 → 直接判错（不再花时间调 LLM）
            return {
                "verdict": "wrong",
                "error_type": "",
                "analysis": f"查询结果与标准答案不一致。\n{info}",
                "suggestion": "对比预期与实际行数、字段值，定位差异。",
                "layer": 2,
            }
        if not match and info == "execution_error":
            return {
                "verdict": "wrong",
                "error_type": "syntax",
                "analysis": "SQL 在该数据库上执行失败。",
                "suggestion": "检查表名、列名是否拼写正确。",
                "layer": 2,
            }

        # 第3层：可选 LLM 语义复核
        if self.enable_semantic and self.llm is not None:
            try:
                return self._semantic_check(
                    schema_sql, question, answer_sql, user_sql, "结果完全相同"
                )
            except LLMError:
                pass  # 失败回退到判对

        # 默认：执行结果一致即判对
        return {
            "verdict": "correct",
            "error_type": "equivalent",
            "analysis": "",
            "suggestion": "",
            "layer": 2,
        }

    # ---- 内部 ----
    def _check_syntax(self, sql: str) -> tuple:
        try:
            conn = sqlite3.connect(":memory:")
            conn.execute(f"EXPLAIN {sql}")
            conn.close()
            return True, ""
        except sqlite3.Error as e:
            msg = str(e)
            if "no such table" in msg or "no such column" in msg:
                return True, ""
            return False, msg

    def _compare_execution(self, schema_sql: str, answer_sql: str,
                           user_sql: str) -> tuple:
        try:
            conn = sqlite3.connect(":memory:")
            conn.executescript(schema_sql)

            cur = conn.execute(answer_sql)
            ans_rows = [tuple(r) for r in cur.fetchall()]

            cur = conn.execute(user_sql)
            user_rows = [tuple(r) for r in cur.fetchall()]
            conn.close()

            ans_sorted = sorted(ans_rows, key=lambda r: tuple(str(x) for x in r))
            user_sorted = sorted(user_rows, key=lambda r: tuple(str(x) for x in r))
            if ans_sorted == user_sorted:
                return True, "结果完全相同"
            preview_a = ans_sorted[:3]
            preview_u = user_sorted[:3]
            return False, (
                f"预期 {len(ans_rows)} 行，得到 {len(user_rows)} 行。\n"
                f"预期前 3 行: {preview_a}\n实际前 3 行: {preview_u}"
            )
        except sqlite3.Error:
            return False, "execution_error"
        except Exception as e:
            return False, f"执行错误: {str(e)}"

    def _semantic_check(self, schema_sql: str, question: str, answer_sql: str,
                        user_sql: str, exec_result: str) -> dict:
        response = self.llm.chat_json(
            system_prompt=JUDGE_SEMANTIC_SYSTEM,
            user_message=JUDGE_SEMANTIC_USER.format(
                schema=schema_sql,
                question=question,
                answer_sql=answer_sql,
                user_sql=user_sql,
                exec_result=exec_result,
            ),
            temperature=0.0,
            max_tokens=self.max_tokens,
        )
        result = self._parse_json(response)
        result["layer"] = 3
        return result

    def _parse_json(self, response: str) -> dict:
        text = (response or "").strip()
        m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if m:
            text = m.group(1)
        else:
            s, e = text.find('{'), text.rfind('}')
            if s != -1 and e > s:
                text = text[s:e + 1]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "verdict": "correct",
                "error_type": "equivalent",
                "analysis": "",
                "suggestion": "",
            }
