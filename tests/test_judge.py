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
