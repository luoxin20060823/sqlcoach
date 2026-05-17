"""SQLite 数据存储管理"""
import sqlite3
import os
import hashlib
from config import DB_PATH


class DataStore:
    """题库 + 答题记录 + Schema 缓存的持久化存储"""

    def __init__(self, db_path: str = ""):
        self.db_path = db_path or DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_tables()

    # ---- 内部 ----
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
                    schema_hash TEXT,
                    difficulty TEXT NOT NULL,
                    question_type TEXT NOT NULL DEFAULT '',
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

                CREATE TABLE IF NOT EXISTS schema_cache (
                    domain TEXT PRIMARY KEY,
                    sql_text TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS challenge_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schema_name TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    question_count INTEGER NOT NULL,
                    correct_count INTEGER NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    total_score INTEGER NOT NULL DEFAULT 0,
                    time_limit_seconds INTEGER NOT NULL DEFAULT 0,
                    finished_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_qb_lookup
                    ON question_bank(schema_name, difficulty, question_type);
                CREATE INDEX IF NOT EXISTS idx_uh_qid
                    ON user_history(question_id);
                CREATE INDEX IF NOT EXISTS idx_cr_finished
                    ON challenge_runs(finished_at DESC);
            """)
            # 兼容旧表
            for stmt in [
                "ALTER TABLE question_bank ADD COLUMN question_type TEXT NOT NULL DEFAULT ''",
                "ALTER TABLE question_bank ADD COLUMN schema_hash TEXT",
                "ALTER TABLE challenge_runs ADD COLUMN total_score INTEGER NOT NULL DEFAULT 0",
                "ALTER TABLE challenge_runs ADD COLUMN time_limit_seconds INTEGER NOT NULL DEFAULT 0",
            ]:
                try:
                    conn.execute(stmt)
                except Exception:
                    pass

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.md5((text or "").encode("utf-8")).hexdigest()

    # ---- Schema 缓存 ----
    def cache_schema(self, domain: str, sql_text: str):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO schema_cache(domain, sql_text, updated_at) "
                "VALUES (?, ?, CURRENT_TIMESTAMP) "
                "ON CONFLICT(domain) DO UPDATE SET sql_text=excluded.sql_text, updated_at=CURRENT_TIMESTAMP",
                (domain, sql_text),
            )

    def get_cached_schema(self, domain: str) -> str:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT sql_text FROM schema_cache WHERE domain = ?", (domain,)
            ).fetchone()
            return row["sql_text"] if row else ""

    def clear_cached_schema(self, domain: str = ""):
        with self._get_conn() as conn:
            if domain:
                conn.execute("DELETE FROM schema_cache WHERE domain = ?", (domain,))
            else:
                conn.execute("DELETE FROM schema_cache")

    # ---- 题库 ----
    def save_question(self, schema_name: str, difficulty: str,
                      knowledge_point: str, question_text: str,
                      answer_sql: str, question_type: str = "",
                      schema_sql: str = "") -> int:
        schema_hash = self._hash(schema_sql) if schema_sql else ""
        with self._get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO question_bank "
                "(schema_name, schema_hash, difficulty, knowledge_point, "
                " question_text, answer_sql, question_type) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (schema_name, schema_hash, difficulty, knowledge_point,
                 question_text, answer_sql, question_type),
            )
            return cur.lastrowid

    def get_question(self, question_id: int) -> dict:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM question_bank WHERE id = ?", (question_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_questions_by_schema(self, schema_name: str) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM question_bank WHERE schema_name = ? "
                "ORDER BY difficulty, id",
                (schema_name,),
            ).fetchall()
            return [dict(r) for r in rows]

    def pick_random_question(self, schema_name: str, difficulty: str,
                             question_type: str) -> dict:
        """从题库中随机抽一道（同 schema/难度/类型）。"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM question_bank "
                "WHERE schema_name = ? AND difficulty = ? AND question_type = ? "
                "ORDER BY RANDOM() LIMIT 1",
                (schema_name, difficulty, question_type),
            ).fetchone()
            return dict(row) if row else None

    def count_questions(self, schema_name: str = "") -> int:
        with self._get_conn() as conn:
            if schema_name:
                row = conn.execute(
                    "SELECT COUNT(*) AS c FROM question_bank WHERE schema_name = ?",
                    (schema_name,),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT COUNT(*) AS c FROM question_bank"
                ).fetchone()
            return row["c"] if row else 0

    # ---- 答题记录 ----
    def save_history(self, question_id: int, user_sql: str,
                     verdict: str, error_type: str = "") -> int:
        with self._get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO user_history (question_id, user_sql, verdict, error_type) "
                "VALUES (?, ?, ?, ?)",
                (question_id, user_sql, verdict, error_type),
            )
            return cur.lastrowid

    def get_user_history(self, limit: int = 100) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                """SELECT uh.*, qb.question_text, qb.difficulty,
                          qb.knowledge_point, qb.answer_sql, qb.schema_name,
                          qb.question_type
                   FROM user_history uh
                   LEFT JOIN question_bank qb ON uh.question_id = qb.id
                   ORDER BY uh.created_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_first_attempts(self, limit: int = 100) -> list:
        """每题只取第一次提交（排除 skipped/查看答案），按时间倒序。

        用于答题历史展示：避免同一题多次提交反复出现。
        """
        with self._get_conn() as conn:
            rows = conn.execute(
                """WITH first_per_q AS (
                       SELECT uh.*,
                              ROW_NUMBER() OVER (
                                  PARTITION BY question_id ORDER BY id
                              ) AS rn
                       FROM user_history uh
                       WHERE verdict != 'skipped' AND question_id IS NOT NULL
                   )
                   SELECT fpq.*, qb.question_text, qb.difficulty,
                          qb.knowledge_point, qb.answer_sql, qb.schema_name,
                          qb.question_type
                   FROM first_per_q fpq
                   LEFT JOIN question_bank qb ON fpq.question_id = qb.id
                   WHERE fpq.rn = 1
                   ORDER BY fpq.created_at DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_wrong_questions(self, limit: int = 50) -> list:
        """获取最近未完整做对的题（含 wrong / flawed / skipped）。

        每题只保留最近一次记录。skipped（放弃 / 直接看答案）也算需要复习。
        """
        with self._get_conn() as conn:
            rows = conn.execute(
                """SELECT qb.id AS question_id,
                          qb.schema_name, qb.difficulty, qb.knowledge_point,
                          qb.question_text, qb.answer_sql, qb.question_type,
                          MAX(uh.created_at) AS last_attempt,
                          uh.user_sql, uh.verdict, uh.error_type
                   FROM user_history uh
                   JOIN question_bank qb ON uh.question_id = qb.id
                   WHERE uh.verdict IN ('wrong', 'flawed', 'skipped')
                   GROUP BY qb.id
                   ORDER BY last_attempt DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        """统计：每道题只算一次，且只看第一次提交的判定。

        - 排除 skipped（查看答案）记录
        - 同一题多次提交，只取最早一次的 verdict
        - 第一次答错则永远不计为正确
        """
        with self._get_conn() as conn:
            row = conn.execute("""
                WITH first_attempts AS (
                    SELECT question_id, verdict,
                           ROW_NUMBER() OVER (
                               PARTITION BY question_id ORDER BY id
                           ) AS rn
                    FROM user_history
                    WHERE verdict != 'skipped' AND question_id IS NOT NULL
                )
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN verdict = 'correct' THEN 1 ELSE 0 END) AS correct
                FROM first_attempts
                WHERE rn = 1
            """).fetchone()
            total = row["total"] or 0
            correct = row["correct"] or 0
            return {
                "total": total,
                "correct": correct,
                "accuracy": correct / total if total > 0 else 0.0,
            }

    def get_dimension_stats(self) -> dict:
        """按知识维度统计；同样按题去重 + 第一次为准。"""
        with self._get_conn() as conn:
            rows = conn.execute("""
                WITH first_attempts AS (
                    SELECT question_id, verdict,
                           ROW_NUMBER() OVER (
                               PARTITION BY question_id ORDER BY id
                           ) AS rn
                    FROM user_history
                    WHERE verdict != 'skipped' AND question_id IS NOT NULL
                )
                SELECT qb.knowledge_point,
                       COUNT(*) AS total,
                       SUM(CASE WHEN fa.verdict = 'correct' THEN 1 ELSE 0 END) AS correct
                FROM first_attempts fa
                JOIN question_bank qb ON fa.question_id = qb.id
                WHERE fa.rn = 1
                GROUP BY qb.knowledge_point
            """).fetchall()
            result = {}
            for r in rows:
                total = r["total"] or 0
                correct = r["correct"] or 0
                result[r["knowledge_point"]] = {
                    "total": total,
                    "correct": correct,
                    "accuracy": correct / total if total > 0 else 0.0,
                }
            return result

    # ---- 挑战记录 ----
    def save_challenge_run(self, schema_name: str, difficulty: str,
                           question_count: int, correct_count: int,
                           duration_seconds: int) -> int:
        with self._get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO challenge_runs "
                "(schema_name, difficulty, question_count, correct_count, duration_seconds) "
                "VALUES (?, ?, ?, ?, ?)",
                (schema_name, difficulty, question_count, correct_count, duration_seconds),
            )
            return cur.lastrowid

    def save_exam_run(self, schema_name: str, question_count: int,
                      correct_count: int, total_score: int,
                      duration_seconds: int, time_limit_seconds: int) -> int:
        """保存考试记录（difficulty 字段填 'mixed'）。"""
        with self._get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO challenge_runs "
                "(schema_name, difficulty, question_count, correct_count, "
                " duration_seconds, total_score, time_limit_seconds) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (schema_name, "mixed", question_count, correct_count,
                 duration_seconds, total_score, time_limit_seconds),
            )
            return cur.lastrowid

    def get_exam_runs(self, limit: int = 20) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM challenge_runs WHERE difficulty = 'mixed' "
                "ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_challenge_runs(self, limit: int = 20) -> list:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM challenge_runs ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_best_challenge(self, schema_name: str, difficulty: str,
                           question_count: int) -> dict:
        """同条件下的最高分（正确数高 + 用时短）。"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM challenge_runs "
                "WHERE schema_name = ? AND difficulty = ? AND question_count = ? "
                "ORDER BY correct_count DESC, duration_seconds ASC LIMIT 1",
                (schema_name, difficulty, question_count),
            ).fetchone()
            return dict(row) if row else None
