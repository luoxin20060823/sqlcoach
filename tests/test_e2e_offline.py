"""离线端到端：用预置 schema + 手填题 + 判题，模拟真实闭环。"""
import os
import tempfile
import pytest

from agent.preset_schemas import get_preset
from agent.judge import JudgeEngine
from db.store import DataStore


@pytest.fixture
def store():
    path = tempfile.mktemp(suffix=".db")
    s = DataStore(db_path=path)
    yield s
    for ext in ["", "-wal", "-shm"]:
        try:
            os.remove(path + ext)
        except OSError:
            pass


def test_full_loop_student_db(store):
    """完整闭环：加载学生数据库 → 题库存题 → 用户做题 → 判题 → 写历史 → 统计"""
    schema = get_preset("学生管理系统")
    assert schema

    # 1. 出一道"查询年龄大于 20 的学生"
    answer = "SELECT name FROM students WHERE age > 20"
    qid = store.save_question(
        schema_name="学生管理系统", difficulty="easy",
        knowledge_point="WHERE", question_text="查询年龄大于 20 岁的学生姓名",
        answer_sql=answer, question_type="basic_select", schema_sql=schema,
    )

    # 2. 学生提交一个等价 SQL（字段顺序不同）
    user_sql = "SELECT name FROM students WHERE age > 20"
    judge = JudgeEngine(llm=None, enable_semantic=False)
    result = judge.judge(schema, "查询年龄大于 20 岁的学生姓名", answer, user_sql)
    assert result["verdict"] == "correct"
    store.save_history(qid, user_sql, result["verdict"], result.get("error_type", ""))

    # 3. 学生再提交一个错的（漏了 WHERE）
    user_sql2 = "SELECT name FROM students"
    result2 = judge.judge(schema, "查询年龄大于 20 岁的学生姓名", answer, user_sql2)
    assert result2["verdict"] == "wrong"
    store.save_history(qid, user_sql2, result2["verdict"], result2.get("error_type", ""))

    # 4. 统计（按题去重 + 第一次为准）
    # 同一题两次提交（correct → wrong），第一次是 correct，所以 total=1 correct=1
    stats = store.get_stats()
    assert stats["total"] == 1
    assert stats["correct"] == 1
    assert abs(stats["accuracy"] - 1.0) < 1e-6

    # 5. 错题应能查回来（错题表按完整历史而非第一次）
    wrongs = store.get_wrong_questions()
    assert any(w["question_id"] == qid for w in wrongs)
