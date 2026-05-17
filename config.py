"""SQL Coach 配置管理"""
import os
import json

# DeepSeek API 配置
# DeepSeek 官方仅提供 deepseek-chat（V3）和 deepseek-reasoner（R1），
# 这里默认用 deepseek-chat，速度快且足以应对结构化输出。
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# 性能与体验开关（可在 UI 侧边栏调整，存在 user_config.json 中持久化）
DEFAULT_SETTINGS = {
    # 是否启用 LLM 语义判题（关闭后只比对执行结果，速度快 5~10 倍）
    "enable_semantic_judge": False,
    # 答对后是否再调一次 LLM 给优化建议（关闭后省一次 5~10s 的等待）
    "enable_auto_optimization": False,
    # 是否在做题时静默预取下一题
    "prefetch_next_question": True,
    # 题库复用：同 schema+难度+类型 优先从历史题库抽题，没库存再生成
    "reuse_question_bank": True,
    # 一次只调用 1 个 LLM 请求生成的最大 token 上限（越小越快）
    "max_tokens_question": 1024,
    "max_tokens_judge": 768,
    "max_tokens_explain": 1024,
    "max_tokens_schema": 3072,
    # API 请求超时（秒）
    "request_timeout": 30,
    # UI 主题：default / classic（一键回滚到原生 UI）
    "theme_version": "default",
}

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "sql_coach.db")

# API Key + 用户偏好的本地持久化
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "data", "user_config.json")


def _read_config() -> dict:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f) or {}
    except Exception:
        pass
    return {}


def _write_config(cfg: dict):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_api_key() -> str:
    return _read_config().get("api_key", "")


def save_api_key(api_key: str):
    cfg = _read_config()
    cfg["api_key"] = api_key
    _write_config(cfg)


def clear_api_key():
    cfg = _read_config()
    cfg.pop("api_key", None)
    _write_config(cfg)


def load_settings() -> dict:
    cfg = _read_config()
    settings = dict(DEFAULT_SETTINGS)
    settings.update(cfg.get("settings", {}))
    return settings


def save_settings(settings: dict):
    cfg = _read_config()
    cfg["settings"] = settings
    _write_config(cfg)


# 难度映射
DIFFICULTY_MAP = {
    "easy": "初级 - 单表 SELECT、WHERE、ORDER BY",
    "medium": "中级 - JOIN、GROUP BY、HAVING、聚合函数",
    "hard": "高级 - 子查询、窗口函数、CTE"
}

# 题目类型
QUESTION_TYPES = {
    "basic_select": "基础查询 - SELECT + FROM + WHERE 条件过滤",
    "order_limit": "排序分页 - ORDER BY + LIMIT + OFFSET",
    "aggregation": "聚合统计 - COUNT/SUM/AVG/MAX/MIN + GROUP BY + HAVING",
    "join_inner": "内连接 - INNER JOIN 多表关联查询",
    "join_outer": "外连接 - LEFT/RIGHT JOIN 含空值处理",
    "subquery_scalar": "标量子查询 - SELECT 中使用子查询作为值",
    "subquery_in": "IN/NOT IN子查询 - WHERE 中使用子查询集合",
    "subquery_exists": "EXISTS子查询 - 相关子查询关联外层查询",
    "union": "集合操作 - UNION/INTERSECT/EXCEPT 合并结果集",
    "window_func": "窗口函数 - ROW_NUMBER/RANK/LAG/LEAD + PARTITION BY",
    "cte": "CTE公用表表达式 - WITH 子句递归或非递归",
    "dml_update": "数据修改 - UPDATE/DELETE 条件更新删除",
    "case_when": "条件表达式 - CASE WHEN 分类转换",
    "like_regex": "模糊匹配 - LIKE/BETWEEN/IN 模式匹配",
    "null_handle": "NULL处理 - IS NULL/COALESCE/IFNULL 空值处理",
}

# 知识领域
DOMAINS = [
    "学生管理系统",
    "电商订单系统",
    "图书管理系统",
    "企业人事系统",
    "医院挂号系统",
    "银行交易系统",
    "餐厅外卖系统",
    "博客社交系统",
]

# 知识点维度
KNOWLEDGE_POINTS = [
    "SELECT", "WHERE", "JOIN", "GROUP BY", "子查询",
    "窗口函数", "DML", "CTE", "集合操作", "NULL处理"
]
