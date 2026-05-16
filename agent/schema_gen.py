"""数据库 Schema 与实例数据生成模块

性能优化：
- 4 个内置领域直接命中本地 PRESET，0 等待
- 自定义领域走 LLM；同一领域第二次会从缓存命中（DataStore.get_cached_schema）
"""
from agent.llm import LLMClient
from agent.preset_schemas import get_preset
from prompts.templates import SCHEMA_GEN_SYSTEM, SCHEMA_GEN_USER
from config import load_settings


class SchemaGenerator:
    """生成 SQLite 数据库 Schema + 示例数据。

    使用顺序：
    1. PRESET 命中 → 直接返回（< 1ms）
    2. DataStore 缓存命中 → 直接返回
    3. 调 LLM 生成
    """

    def __init__(self, llm: LLMClient = None, store=None):
        self.llm = llm
        self.store = store
        self._settings = load_settings()

    def generate(self, domain: str, force_llm: bool = False) -> str:
        """返回完整可执行 SQL。

        force_llm=True 时跳过预置和缓存，强制调 LLM 重新生成。
        """
        if not force_llm:
            # 1. 预置库
            preset = get_preset(domain)
            if preset:
                return preset
            # 2. 历史缓存（同领域之前生成过）
            if self.store is not None:
                cached = self.store.get_cached_schema(domain)
                if cached:
                    return cached

        # 3. LLM 生成
        if self.llm is None:
            return ""
        max_tokens = int(self._settings.get("max_tokens_schema", 3072))
        sql = self.llm.chat(
            system_prompt=SCHEMA_GEN_SYSTEM,
            user_message=SCHEMA_GEN_USER.format(domain=domain),
            temperature=0.3,
            max_tokens=max_tokens,
        ).strip()

        # 去掉 ```sql 包裹
        if sql.startswith("```"):
            lines = sql.split("\n")
            sql = "\n".join(l for l in lines if not l.strip().startswith("```"))
        sql = sql.strip()

        # 写入缓存
        if self.store is not None and sql:
            try:
                self.store.cache_schema(domain, sql)
            except Exception:
                pass
        return sql

    def parse_schema(self, sql_text: str) -> dict:
        """解析生成的 SQL，提取 Schema 信息为字典"""
        tables = []
        current_table = None
        for line in sql_text.split("\n"):
            line_upper = line.strip().upper()
            if line_upper.startswith("CREATE TABLE"):
                parts = line.strip().split()
                if len(parts) >= 3:
                    name = parts[2].split("(")[0].strip("`\"'")
                    current_table = {"name": name, "columns": []}
                    tables.append(current_table)
            elif current_table and line.strip() and not line_upper.startswith("INSERT"):
                col = line.strip().lstrip(",").split()[0].strip("`\"'")
                if col and not col.upper().startswith(("PRIMARY", "FOREIGN", "CONSTRAINT", ")")):
                    current_table["columns"].append(col)
        return {"tables": tables, "raw_sql": sql_text}
