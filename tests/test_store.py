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
    try:
        os.remove(tmp)
        os.remove(tmp + "-wal")
    except (PermissionError, OSError):
        pass
    try:
        os.remove(tmp + "-shm")
    except (PermissionError, OSError):
        pass


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
        """同一题两次提交（先对后错）按"第一次为准 + 去重"算 total=1, correct=1。"""
        qid = store.save_question("db1", "easy", "SELECT", "Q1", "SELECT 1")
        store.save_history(qid, "SELECT 1", "correct")
        store.save_history(qid, "WRONG", "wrong", "syntax")
        stats = store.get_stats()
        assert stats["total"] == 1
        assert stats["correct"] == 1
        assert stats["accuracy"] == 1.0

    def test_get_stats_first_attempt_locks_in(self, store):
        """第一次答错则永远不计为正确，即使后来答对。"""
        qid = store.save_question("db1", "easy", "SELECT", "Q1", "SELECT 1")
        store.save_history(qid, "WRONG", "wrong", "syntax")
        store.save_history(qid, "SELECT 1", "correct")
        stats = store.get_stats()
        assert stats["total"] == 1
        assert stats["correct"] == 0

    def test_get_stats_skipped_excluded(self, store):
        """查看答案（skipped）不计入总题数。"""
        qid = store.save_question("db1", "easy", "SELECT", "Q1", "SELECT 1")
        store.save_history(qid, "（已查看答案）", "skipped")
        stats = store.get_stats()
        assert stats["total"] == 0
        assert stats["correct"] == 0

    def test_get_stats_multiple_questions(self, store):
        """两道不同题，各算一次。"""
        qid1 = store.save_question("db1", "easy", "SELECT", "Q1", "SELECT 1")
        qid2 = store.save_question("db1", "easy", "SELECT", "Q2", "SELECT 2")
        store.save_history(qid1, "SELECT 1", "correct")
        store.save_history(qid2, "WRONG", "wrong", "syntax")
        stats = store.get_stats()
        assert stats["total"] == 2
        assert stats["correct"] == 1

    def test_dimension_stats(self, store):
        qid1 = store.save_question("db1", "easy", "SELECT", "Q1", "SELECT 1")
        qid2 = store.save_question("db1", "medium", "JOIN", "Q2", "SELECT * FROM a JOIN b")
        store.save_history(qid1, "SELECT 1", "correct")
        store.save_history(qid2, "SELECT * FROM a JOIN b", "wrong", "join_logic")

        dims = store.get_dimension_stats()
        assert dims["SELECT"]["accuracy"] == 1.0
        assert dims["JOIN"]["accuracy"] == 0.0
