"""端到端冒烟测试，覆盖优化后的关键路径。"""
import os
import sqlite3
import tempfile
import pytest

from agent.preset_schemas import PRESET_SCHEMAS, get_preset
from agent.schema_gen import SchemaGenerator
from agent.judge import JudgeEngine
from db.store import DataStore


@pytest.fixture
def tmp_store():
    path = tempfile.mktemp(suffix=".db")
    s = DataStore(db_path=path)
    yield s
    for ext in ["", "-wal", "-shm"]:
        try:
            os.remove(path + ext)
        except OSError:
            pass


class TestPresetSchemas:
    def test_all_presets_executable(self):
        """所有预置 schema 都能在 SQLite 内存数据库执行。"""
        for domain, sql in PRESET_SCHEMAS.items():
            conn = sqlite3.connect(":memory:")
            conn.executescript(sql)
            conn.close()

    def test_all_domains_have_preset(self):
        from config import DOMAINS
        for d in DOMAINS:
            assert get_preset(d), f"领域 '{d}' 缺少预置 schema"


class TestSchemaGeneratorWithPreset:
    def test_preset_hit_no_llm(self, tmp_store):
        """命中预置时，即使没有 llm 也能返回。"""
        gen = SchemaGenerator(llm=None, store=tmp_store)
        sql = gen.generate("学生管理系统")
        assert "CREATE TABLE" in sql.upper()

    def test_cache_used(self, tmp_store):
        """非预置领域，缓存命中后无需 llm。"""
        tmp_store.cache_schema("假领域", "CREATE TABLE t (id INTEGER); INSERT INTO t VALUES (1);")
        gen = SchemaGenerator(llm=None, store=tmp_store)
        sql = gen.generate("假领域")
        assert "CREATE TABLE" in sql


class TestJudgeFastPath:
    def test_correct_no_llm(self):
        """开关关闭时，结果一致直接 correct，不调 LLM。"""
        schema = "CREATE TABLE t(id INTEGER, name TEXT); INSERT INTO t VALUES (1,'a'),(2,'b');"
        engine = JudgeEngine(llm=None, enable_semantic=False)
        result = engine.judge(schema, "查询所有", "SELECT * FROM t",
                              "SELECT id, name FROM t")
        assert result["verdict"] == "correct"
        assert result["layer"] == 2

    def test_wrong_result(self):
        schema = "CREATE TABLE t(id INTEGER); INSERT INTO t VALUES (1),(2);"
        engine = JudgeEngine(llm=None, enable_semantic=False)
        result = engine.judge(schema, "查询所有", "SELECT * FROM t",
                              "SELECT * FROM t WHERE id=1")
        assert result["verdict"] == "wrong"


class TestQuestionBank:
    def test_pick_random_returns_none_when_empty(self, tmp_store):
        assert tmp_store.pick_random_question("X", "easy", "basic_select") is None

    def test_save_and_pick(self, tmp_store):
        tmp_store.save_question("X", "easy", "SELECT", "Q1", "SELECT 1",
                                question_type="basic_select")
        got = tmp_store.pick_random_question("X", "easy", "basic_select")
        assert got["question_text"] == "Q1"

    def test_wrong_questions(self, tmp_store):
        qid = tmp_store.save_question("X", "easy", "SELECT", "Q1", "SELECT 1",
                                      question_type="basic_select")
        tmp_store.save_history(qid, "WRONG", "wrong", "syntax")
        wrongs = tmp_store.get_wrong_questions()
        assert len(wrongs) == 1
        assert wrongs[0]["question_id"] == qid
