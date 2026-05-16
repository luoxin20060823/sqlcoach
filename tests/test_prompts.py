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
            difficulty_desc="初级",
            question_type="basic_select",
            question_type_desc="基础查询"
        )
        assert "students" in prompt
        assert "basic_select" in prompt
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
