"""学习分析与评分模块"""
import json
import re
from agent.llm import LLMClient
from prompts.templates import ANALYZER_SYSTEM, ANALYZER_USER
from config import KNOWLEDGE_POINTS


class Analyzer:
    """累计成绩分析与改进建议"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def analyze(self, history: list, dimension_stats: dict) -> dict:
        """分析学生答题数据，返回 {summary, strengths, weaknesses,
                                  dimension_scores, suggestions, next_difficulty}
        """
        history_json = json.dumps({
            "total_questions": len(history),
            "recent_30": [
                {
                    "question": h.get("question_text", ""),
                    "difficulty": h.get("difficulty", ""),
                    "knowledge_point": h.get("knowledge_point", ""),
                    "verdict": h.get("verdict", ""),
                    "error_type": h.get("error_type", ""),
                }
                for h in history[-30:]
            ],
            "dimension_stats": dimension_stats,
        }, ensure_ascii=False)

        try:
            response = self.llm.chat_json(
                system_prompt=ANALYZER_SYSTEM,
                user_message=ANALYZER_USER.format(history_json=history_json),
                temperature=0.3,
                max_tokens=1024,
            )
            return self._parse_json(response) or self._fallback(history, dimension_stats)
        except Exception:
            return self._fallback(history, dimension_stats)

    @staticmethod
    def _parse_json(response: str) -> dict:
        if not response:
            return None
        text = response.strip()
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
            return None

    def _fallback(self, history: list, dimension_stats: dict) -> dict:
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
            "summary": f"已完成 {len(history)} 道题，正确率 {accuracy:.0%}。",
            "strengths": strengths or ["暂无足够数据"],
            "weaknesses": weaknesses or ["暂无足够数据"],
            "dimension_scores": scores,
            "suggestions": ["针对薄弱维度多做练习，再回头复习错题。"],
            "next_difficulty": next_diff,
        }
