"""错题复习 Tab — 列出做错或放弃过的题，重新作答"""
import sqlite3
import pandas as pd
import streamlit as st
from agent.judge import JudgeEngine
from ui.sql_editor import sql_editor


def render_review_tab(llm_client, store):
    st.subheader("错题复习")
    wrong = store.get_wrong_questions(limit=100)
    if not wrong:
        st.info("还没有错题或放弃记录。继续做题吧。")
        return

    st.caption(f"共 {len(wrong)} 道待复习题。点列表中任意一题，重新作答。")

    verdict_label = {"wrong": "错误", "flawed": "瑕疵", "skipped": "看答案"}
    df = pd.DataFrame([
        {
            "id": w["question_id"],
            "领域": w["schema_name"],
            "难度": w["difficulty"],
            "题目": (w["question_text"][:50] + "...") if len(w["question_text"] or "") > 50 else w["question_text"],
            "结果": verdict_label.get(w["verdict"], w["verdict"]),
            "上次时间": w.get("last_attempt", ""),
        }
        for w in wrong
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    options = [f"#{w['question_id']} [{w['difficulty']}] {w['question_text'][:30]}" for w in wrong]
    pick = st.selectbox("选择一道题重新作答", options)
    if not pick:
        return
    qid = int(pick.split("#", 1)[1].split(" ", 1)[0])
    q = store.get_question(qid)
    if not q:
        st.error("题目已不存在。")
        return

    st.markdown(
        f"**领域**: {q['schema_name']} ｜ **难度**: {q['difficulty']} ｜ "
        f"**知识点**: {q['knowledge_point']}"
    )
    st.markdown(f"> {q['question_text']}")

    schema_sql = _resolve_schema_sql(store, q["schema_name"])
    if not schema_sql:
        st.warning(
            f"该题所属领域 '{q['schema_name']}' 的 schema 不在本地缓存，"
            "请先在主界面生成或加载该数据库。"
        )
        return

    with st.expander("数据库结构", expanded=False):
        st.code(schema_sql, language="sql")

    sql_input = sql_editor(
        value="",
        key=f"review_sql_{qid}",
        height=160,
        placeholder="重新作答这道题...",
    )

    c1, c2, c3 = st.columns([1, 1, 4])
    with c1:
        run_btn = st.button("运行", key=f"run_{qid}", use_container_width=True)
    with c2:
        submit_btn = st.button("判定", key=f"submit_{qid}", type="primary", use_container_width=True)
    with c3:
        show_answer = st.checkbox("查看标准答案", key=f"show_ans_{qid}")

    if run_btn and sql_input.strip():
        _run_sql(schema_sql, sql_input, qid)
    if submit_btn and sql_input.strip():
        _judge(schema_sql, q, sql_input, llm_client, store)

    _render_run_result(qid)

    if show_answer:
        st.markdown("### 标准答案")
        st.code(q["answer_sql"], language="sql")

    res_key = f"review_result_{qid}"
    if st.session_state.get(res_key):
        result = st.session_state[res_key]
        labels = {"correct": "这次对了", "wrong": "仍然错误",
                  "flawed": "结果对但逻辑有瑕疵"}
        st.markdown(f"## {labels.get(result['verdict'], result['verdict'])}")
        if result.get("analysis"):
            st.markdown(f"**分析**: {result['analysis']}")
        # 答错时不显示「建议」
        if result.get("suggestion") and result["verdict"] not in ("wrong", "flawed"):
            st.markdown(f"**建议**: {result['suggestion']}")


def _resolve_schema_sql(store, domain: str) -> str:
    from agent.preset_schemas import get_preset
    preset = get_preset(domain)
    if preset:
        return preset
    return store.get_cached_schema(domain) or ""


def _run_sql(schema_sql, sql, qid):
    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_sql)
        cur = conn.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        st.session_state[f"review_run_{qid}"] = {"cols": cols, "rows": rows, "error": ""}
    except Exception as e:
        st.session_state[f"review_run_{qid}"] = {"cols": [], "rows": [], "error": str(e)}


def _render_run_result(qid):
    info = st.session_state.get(f"review_run_{qid}")
    if not info:
        return
    if info["error"]:
        st.error(f"执行错误：{info['error']}")
        return
    if info["rows"]:
        df = pd.DataFrame(info["rows"], columns=info["cols"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"共 {len(info['rows'])} 行")
    else:
        st.info("空结果集（0 行）。")


def _judge(schema_sql, question, user_sql, llm_client, store):
    from config import load_settings
    settings = load_settings()
    judge = JudgeEngine(
        llm=llm_client if settings.get("enable_semantic_judge") else None,
        enable_semantic=settings.get("enable_semantic_judge", False),
    )
    result = judge.judge(
        schema_sql,
        question["question_text"],
        question["answer_sql"],
        user_sql,
    )
    store.save_history(question["id"], user_sql, result["verdict"], result.get("error_type", ""))
    st.session_state[f"review_result_{question['id']}"] = result
    st.session_state["stats"] = store.get_stats()
