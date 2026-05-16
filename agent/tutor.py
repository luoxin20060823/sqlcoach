"""SQL 答疑导师模块"""
from agent.llm import LLMClient
from prompts.templates import TUTOR_SYSTEM, TUTOR_USER
from config import load_settings


class Tutor:
    """错题解析 + 自由答疑（含多轮历史）"""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self._settings = load_settings()

    def explain(self, schema: str, question: str, answer_sql: str,
                user_sql: str, verdict: str, analysis: str) -> str:
        return self.llm.chat(
            system_prompt=TUTOR_SYSTEM,
            user_message=TUTOR_USER.format(
                schema=schema,
                question=question,
                answer_sql=answer_sql,
                user_sql=user_sql,
                verdict=verdict,
                analysis=analysis,
            ),
            temperature=0.3,
            max_tokens=int(self._settings.get("max_tokens_explain", 1024)),
        )

    def answer_question(self, schema: str, user_question: str) -> str:
        """单轮自由答疑。"""
        prompt = (
            f"数据库 Schema：\n{schema}\n\n学生提问：{user_question}\n\n"
            f"请用通俗易懂的方式解答；如涉及 SQL，请给可执行的示例。"
        )
        return self.llm.chat(
            system_prompt=TUTOR_SYSTEM,
            user_message=prompt,
            temperature=0.4,
            max_tokens=int(self._settings.get("max_tokens_explain", 1024)),
        )

    def chat(self, schema: str, history: list, user_message: str) -> str:
        """多轮答疑：history = [{role, content}, ...] OpenAI 格式。"""
        messages = [{"role": "system", "content": TUTOR_SYSTEM}]
        if schema:
            messages.append({
                "role": "system",
                "content": f"当前数据库 Schema 如下，可用于举例：\n{schema}",
            })
        for m in history or []:
            role = m.get("role")
            content = m.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})

        try:
            resp = self.llm.client.chat.completions.create(
                model=self.llm.model,
                messages=messages,
                temperature=0.4,
                max_tokens=int(self._settings.get("max_tokens_explain", 1024)),
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"答疑失败：{e}"
