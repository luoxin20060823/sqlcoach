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

                CREATE INDEX IF NOT EXISTS idx_qb_lookup
                    ON question_bank(schema_name, difficulty, question_type);
                CREATE INDEX IF NOT EXISTS idx_uh_qid
                    ON user_history(question_id);
            """)
            # 兼容旧表
            for stmt in [
                "ALTER TABLE question_bank ADD COLUMN question_type TEXT NOT NULL DEFAULT ''",
                "ALTER TABLE question_bank ADD COLUMN schema_hash TEXT",
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

    def get_wrong_questions(self, limit: int = 50) -> list:
        """获取最近做错的题（去重，每题只取最近一次）。"""
        with self._get_conn() as conn:
            rows = conn.execute(
                """SELECT qb.id AS question_id,
                          qb.schema_name, qb.difficulty, qb.knowledge_point,
                          qb.question_text, qb.answer_sql, qb.question_type,
                          MAX(uh.created_at) AS last_attempt,
                          uh.user_sql, uh.verdict, uh.error_type
                   FROM user_history uh
                   JOIN question_bank qb ON uh.question_id = qb.id
                   WHERE uh.verdict IN ('wrong', 'flawed')
                   GROUP BY qb.id
                   ORDER BY last_attempt DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_stats(self) -> dict:
        with self._get_conn() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM user_history"
            ).fetchone()[0]
            correct = conn.execute(
                "SELECT COUNT(*) FROM user_history WHERE verdict = 'correct'"
            ).fetchone()[0]
            return {
                "total": total,
                "correct": correct,
                "accuracy": correct / total if total > 0 else 0.0,
            }

    def get_dimension_stats(self) -> dict:
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT qb.knowledge_point,
                       COUNT(*) AS total,
                       SUM(CASE WHEN uh.verdict = 'correct' THEN 1 ELSE 0 END) AS correct
                FROM user_history uh
                JOIN question_bank qb ON uh.question_id = qb.id
                GROUP BY qb.knowledge_point
            """).fetchall()
            result = {}
            for r in rows:
                result[r["knowledge_point"]] = {
                    "total": r["total"],
                    "correct": r["correct"] or 0,
                    "accuracy": (r["correct"] or 0) / r["total"] if r["total"] > 0 else 0.0,
                }
            return result
