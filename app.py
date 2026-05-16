"""SQL随身教练 — Streamlit 主入口"""
import sqlite3
import streamlit as st

from agent.llm import LLMClient
from agent.schema_gen import SchemaGenerator
from agent.question_gen import QuestionGenerator
from db.store import DataStore
from ui.practice import render_practice_tab
from ui.report import render_report_tab
from ui.browser import render_browser_tab
from ui.review import render_review_tab
from ui.chat import render_chat_tab
from config import (
    DOMAINS, QUESTION_TYPES,
    load_api_key, save_api_key, clear_api_key,
    load_settings, save_settings, DEFAULT_SETTINGS,
)

st.set_page_config(
    page_title="SQL随身教练",
    layout="wide",
)


def init_session_state():
    saved_key = load_api_key()
    settings = load_settings()
    defaults = {
        "api_key": saved_key,
        "llm_client": None,
        "store": DataStore(),
        "current_schema": "",
        "current_schema_sql": "",
        "current_data": {},
        "current_question": None,
        "current_question_id": None,
        "current_difficulty": "easy",
        "current_question_type": "random",
        "current_domain": DOMAINS[0],
        "stats": {"total": 0, "correct": 0, "accuracy": 0.0},
        "hint_level": 0,
        "hints": [],
        "trigger_new_question": False,
        "remember_key": bool(saved_key),
        "settings": settings,
        "prefetched_question": None,
        "review_question_id": None,
        "chat_history": [],
        "custom_domain": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    if saved_key and st.session_state.get("llm_client") is None:
        try:
            st.session_state["llm_client"] = LLMClient(api_key=saved_key)
        except Exception:
            pass


def sidebar():
    with st.sidebar:
        st.title("SQL随身教练")

        # 学习进度
        st.markdown("### 学习进度")
        stats = st.session_state.get("stats", {})
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("总题", stats.get("total", 0))
        with c2:
            st.metric("正确", stats.get("correct", 0))
        with c3:
            st.metric("正确率", f"{stats.get('accuracy', 0):.0%}")

        st.divider()

        # 学习设置
        st.markdown("### 学习设置")
        domain_choices = list(DOMAINS) + ["自定义领域..."]
        cur_domain = st.session_state["current_domain"]
        idx = domain_choices.index(cur_domain) if cur_domain in domain_choices else 0
        domain_pick = st.selectbox("知识领域", domain_choices, index=idx)
        if domain_pick == "自定义领域...":
            custom = st.text_input("输入自定义领域", value=st.session_state.get("custom_domain", ""))
            st.session_state["custom_domain"] = custom
            st.session_state["current_domain"] = custom or DOMAINS[0]
        else:
            st.session_state["current_domain"] = domain_pick

        difficulty = st.selectbox(
            "难度", ["easy", "medium", "hard"],
            index=["easy", "medium", "hard"].index(st.session_state["current_difficulty"]),
            format_func=lambda x: {"easy": "初级", "medium": "中级", "hard": "高级"}[x],
        )
        st.session_state["current_difficulty"] = difficulty

        type_keys = ["random"] + list(QUESTION_TYPES.keys())
        type_labels = dict([("random", "随机出题")] + list(QUESTION_TYPES.items()))
        cur_type = st.session_state.get("current_question_type", "random")
        if cur_type not in type_keys:
            cur_type = "random"
        question_type = st.selectbox(
            "题目类型", type_keys, index=type_keys.index(cur_type),
            format_func=lambda x: type_labels.get(x, x),
        )
        st.session_state["current_question_type"] = question_type

        st.divider()

        # 操作
        st.markdown("### 操作")
        if st.button("生成数据库", type="primary", use_container_width=True):
            _generate_schema(force_llm=False)

        if st.button("生成题目", type="primary", use_container_width=True):
            _generate_question()

        if st.button("刷新统计", use_container_width=True):
            st.session_state["stats"] = st.session_state["store"].get_stats()
            st.rerun()

        st.divider()

        # 高级设置
        with st.expander("高级设置", expanded=False):
            # API Key
            st.markdown("**API 设置**")
            api_key = st.text_input(
                "DeepSeek API Key",
                type="password",
                value=st.session_state["api_key"],
                placeholder="sk-...",
            )
            if api_key != st.session_state["api_key"]:
                st.session_state["api_key"] = api_key
                if api_key:
                    st.session_state["llm_client"] = LLMClient(api_key=api_key)
                else:
                    st.session_state["llm_client"] = None

            remember = st.checkbox(
                "记住 API Key（保存到本地）",
                value=st.session_state.get("remember_key", False),
            )
            if remember != st.session_state.get("remember_key"):
                st.session_state["remember_key"] = remember
                if remember and api_key:
                    save_api_key(api_key)
                    st.success("API Key 已保存。")
                elif not remember:
                    clear_api_key()
                    st.info("已清除本地 API Key。")

            st.markdown("---")

            # LLM 重生成
            st.markdown("**数据库重生成**")
            if st.button("LLM 重新生成数据库", use_container_width=True,
                         help="跳过预置/缓存，重新调 LLM 生成数据库（耗时较长）"):
                _generate_schema(force_llm=True)

            st.markdown("---")

            # 性能 / 体验开关
            st.markdown("**性能 / 体验**")
            settings = dict(st.session_state.get("settings", DEFAULT_SETTINGS))
            settings["enable_semantic_judge"] = st.checkbox(
                "LLM 语义判题（更严格，但慢）",
                value=settings.get("enable_semantic_judge", False),
            )
            settings["enable_auto_optimization"] = st.checkbox(
                "答对后自动调 LLM 给优化建议",
                value=settings.get("enable_auto_optimization", False),
            )
            settings["prefetch_next_question"] = st.checkbox(
                "做题时静默预取下一题",
                value=settings.get("prefetch_next_question", True),
            )
            settings["reuse_question_bank"] = st.checkbox(
                "题库复用（同条件先抽老题）",
                value=settings.get("reuse_question_bank", True),
            )
            if st.button("保存设置", use_container_width=True):
                save_settings(settings)
                st.session_state["settings"] = settings
                if st.session_state["api_key"]:
                    st.session_state["llm_client"] = LLMClient(api_key=st.session_state["api_key"])
                st.success("已保存。")


def _load_schema_into_state(sql: str):
    st.session_state["current_schema_sql"] = sql

    lines = []
    for line in sql.split("\n"):
        u = line.strip().upper()
        if u.startswith("CREATE TABLE") or (
                lines and not u.startswith("INSERT")):
            lines.append(line)
        elif u.startswith("INSERT"):
            break
    st.session_state["current_schema"] = "\n".join(lines)

    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(sql)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        data = {}
        for t in tables:
            cols = [d[1] for d in conn.execute(f"PRAGMA table_info([{t[0]}])").fetchall()]
            rows = conn.execute(f"SELECT * FROM [{t[0]}]").fetchall()
            data[t[0]] = [dict(zip(cols, r)) for r in rows]
        st.session_state["current_data"] = data
        conn.close()
    except Exception:
        st.session_state["current_data"] = {}


def _generate_schema(force_llm: bool = False):
    domain = st.session_state["current_domain"]
    if not domain:
        st.error("请先选择或填写一个领域。")
        return
    llm = st.session_state.get("llm_client")
    store = st.session_state["store"]

    gen = SchemaGenerator(llm=llm, store=store)

    if not force_llm:
        from agent.preset_schemas import get_preset
        preset = get_preset(domain)
        if preset:
            _load_schema_into_state(preset)
            st.success(f"已加载内置 '{domain}' 数据库。")
            st.rerun()
            return
        cached = store.get_cached_schema(domain)
        if cached:
            _load_schema_into_state(cached)
            st.success(f"已加载缓存的 '{domain}' 数据库。")
            st.rerun()
            return

    if not llm:
        st.error("自定义领域需要调 LLM 生成，请先设置 API Key。")
        return

    with st.spinner(f"正在为 '{domain}' 调用 LLM 生成数据库..."):
        sql = gen.generate(domain, force_llm=force_llm)
    if not sql:
        st.error("生成失败，请检查 API Key 或重试。")
        return
    _load_schema_into_state(sql)
    st.success(f"'{domain}' 数据库已生成。")
    st.rerun()


def _clear_question_state():
    for key in [
        "last_result", "last_explanation", "last_explanation_error",
        "last_optimization", "show_answer", "question_finished",
        "last_user_sql", "last_question",
        "run_result_columns", "run_result_rows", "run_error", "has_run_sql",
        "_skipped_recorded",
    ]:
        st.session_state.pop(key, None)
    st.session_state["hint_level"] = 0
    st.session_state["hints"] = []


def _generate_question():
    llm = st.session_state.get("llm_client")
    schema = st.session_state.get("current_schema_sql")
    if not schema:
        st.error("请先生成数据库。")
        return

    _clear_question_state()
    domain = st.session_state["current_domain"]
    difficulty = st.session_state["current_difficulty"]
    qtype = st.session_state.get("current_question_type", "random")

    prefetched = st.session_state.get("prefetched_question")
    if prefetched and prefetched.get("__domain") == domain \
            and prefetched.get("__difficulty") == difficulty \
            and prefetched.get("__qtype") == qtype:
        question = prefetched
        st.session_state["prefetched_question"] = None
    else:
        if not llm:
            st.error("请先输入 API Key（或开启题库复用并已有题目）。")
        store = st.session_state["store"]
        qgen = QuestionGenerator(llm, store=store)
        with st.spinner("正在生成题目..."):
            question = qgen.generate(schema, difficulty, qtype, schema_name=domain)

    if not question:
        st.error("题目生成失败，请重试或检查网络。")
        return

    store = st.session_state["store"]
    if question.get("_reused"):
        with store._get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM question_bank WHERE schema_name=? AND question_text=? "
                "ORDER BY id DESC LIMIT 1",
                (domain, question.get("question", "")),
            ).fetchone()
            qid = row["id"] if row else None
    else:
        qid = store.save_question(
            schema_name=domain,
            difficulty=difficulty,
            knowledge_point=question.get("knowledge_point", ""),
            question_text=question.get("question", ""),
            answer_sql=question.get("answer_sql", ""),
            question_type=question.get("question_type", qtype),
            schema_sql=schema,
        )

    st.session_state["current_question"] = question
    st.session_state["current_question_id"] = qid
    st.session_state["last_question"] = question
    st.success("题目已生成。" + ("（复用题库）" if question.get("_reused") else ""))
    st.rerun()


def main():
    init_session_state()

    if st.session_state.get("trigger_new_question"):
        st.session_state["trigger_new_question"] = False
        _generate_question()

    sidebar()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "练习", "分析报告", "数据浏览", "错题复习", "自由答疑",
    ])

    with tab1:
        render_practice_tab(
            st.session_state.get("llm_client"),
            st.session_state["store"],
            st.session_state.get("current_schema_sql", ""),
            st.session_state.get("current_schema", ""),
            st.session_state.get("current_question"),
        )

    with tab2:
        render_report_tab(
            st.session_state.get("llm_client"),
            st.session_state["store"],
        )

    with tab3:
        render_browser_tab(
            st.session_state.get("current_schema_sql", ""),
            st.session_state.get("current_data", {}),
        )

    with tab4:
        render_review_tab(
            st.session_state.get("llm_client"),
            st.session_state["store"],
        )

    with tab5:
        render_chat_tab(
            st.session_state.get("llm_client"),
            st.session_state.get("current_schema_sql", ""),
        )


if __name__ == "__main__":
    main()
