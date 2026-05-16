"""Streamlit 练习 Tab — SQL 编辑器 + 运行 → 提交 → 查看解析"""
import threading
import sqlite3
import pandas as pd
import streamlit as st

from config import QUESTION_TYPES, load_settings
from ui.sql_editor import sql_editor


def render_practice_tab(llm_client, store, full_schema_sql, schema_display, current_question):
    st.subheader("SQL 练习")

    if not full_schema_sql:
        st.info("请先在侧边栏选择领域并点击「生成数据库」，再点击「生成题目」。")
        return

    with st.expander("查看当前数据库结构", expanded=False):
        st.code(full_schema_sql, language="sql")

    current_q = current_question or st.session_state.get("last_question")
    if current_q:
        st.markdown("### 当前题目")
        difficulty_labels = {"easy": "初级", "medium": "中级", "hard": "高级"}
        diff = st.session_state.get("current_difficulty", "easy")
        qtype = current_q.get("question_type", "")
        qtype_label = QUESTION_TYPES.get(qtype, qtype) if qtype else ""
        st.markdown(f"**难度**: {difficulty_labels.get(diff, diff)}")
        if qtype_label:
            st.markdown(f"**类型**: {qtype_label}")
        st.markdown(f"**知识点**: {current_q.get('knowledge_point', '')}")
        st.markdown(f"> {current_q.get('question', '')}")

    _display_verdict()

    finished = st.session_state.get("question_finished", False)
    gave_up = st.session_state.get("show_answer", False)
    if finished or gave_up:
        _render_post_answer_actions()

    _render_sql_editor(llm_client, store, full_schema_sql, current_q)


def _render_sql_editor(llm_client, store, full_schema_sql, current_q):
    st.markdown("### SQL 编辑器")

    last_sql = st.session_state.get("last_user_sql", "")
    user_sql = sql_editor(value=last_sql, key="sql_input", height=200,
                          placeholder="例如: SELECT * FROM students WHERE age > 18")

    col1, col2, col3, col4, col5 = st.columns([0.8, 0.8, 0.8, 1.0, 2.0])
    with col1:
        run_btn = st.button("运行", use_container_width=True)
    with col2:
        # 提交按钮：只要 SQL 非空就可点（不强制先点运行）
        run_error = st.session_state.get("run_error", "")
        can_submit = bool(user_sql.strip())
        submit_btn = st.button(
            "提交答案",
            type="primary" if can_submit and not run_error else "secondary",
            disabled=not can_submit,
            use_container_width=True,
        )
    with col3:
        hint_btn = st.button("提示", use_container_width=True)
    with col4:
        # 「查看答案」/「隐藏答案」切换：show_answer 决定按钮文案
        showing_answer = bool(st.session_state.get("show_answer"))
        toggle_label = "隐藏答案" if showing_answer else "查看答案"
        toggle_answer_btn = st.button(toggle_label, use_container_width=True)

    _display_hints()

    if run_btn and user_sql.strip():
        _handle_run_sql(full_schema_sql, user_sql)
    elif run_btn:
        st.warning("请输入 SQL 语句。")

    _display_run_result()

    if submit_btn:
        _handle_submission(llm_client, store, full_schema_sql, current_q, user_sql)

    if hint_btn and current_q and llm_client:
        _request_hint(llm_client, full_schema_sql, current_q)

    if toggle_answer_btn:
        if showing_answer:
            _hide_answer()
        else:
            _handle_show_answer(store, current_q)


def _handle_run_sql(full_schema_sql, user_sql):
    """仅在内存数据库执行用户 SQL 并展示结果，不计入答题记录。"""
    st.session_state["last_user_sql"] = user_sql
    st.session_state.pop("run_result_columns", None)
    st.session_state.pop("run_result_rows", None)
    st.session_state.pop("run_error", None)

    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(full_schema_sql)
        cursor = conn.execute(user_sql)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description] if cursor.description else []
        conn.close()
        st.session_state["run_result_columns"] = cols
        st.session_state["run_result_rows"] = [tuple(r) for r in rows]
        st.session_state["has_run_sql"] = True
        st.session_state["run_error"] = ""
    except sqlite3.Error as e:
        st.session_state["has_run_sql"] = True
        st.session_state["run_error"] = str(e)
    except Exception as e:
        st.session_state["has_run_sql"] = True
        st.session_state["run_error"] = f"执行错误: {str(e)}"


def _display_run_result():
    cols = st.session_state.get("run_result_columns")
    rows = st.session_state.get("run_result_rows")
    error = st.session_state.get("run_error", "")

    if error:
        st.error(f"SQL 执行错误：{error}")
        return
    if cols is None and rows is None:
        return

    st.markdown("### 查询结果")
    if rows is not None and len(rows) > 0:
        df = pd.DataFrame(rows, columns=cols)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"共 {len(rows)} 行")
    elif rows is not None and len(rows) == 0:
        st.info("查询返回空结果集（0 行）。")
    else:
        st.caption("查询已执行，无返回数据。")


def _display_verdict():
    result = st.session_state.get("last_result")
    if not result:
        return
    st.divider()
    labels = {
        "correct": "正确",
        "flawed": "结果正确但逻辑有瑕疵",
        "wrong": "错误",
        "skipped": "已查看答案",
    }
    st.markdown(f"## {labels.get(result['verdict'], result['verdict'])}")

    if result.get("analysis"):
        st.markdown(f"**分析**: {result['analysis']}")
    # 答错（wrong / flawed）时不再显示「建议」字段，避免提前剧透解题方向
    if result.get("suggestion") and result["verdict"] not in ("wrong", "flawed"):
        st.markdown(f"**建议**: {result['suggestion']}")

    if st.session_state.get("show_answer"):
        current_q = st.session_state.get("last_question") or {}
        ans_sql = current_q.get("answer_sql", "")
        if ans_sql:
            st.markdown("### 标准答案")
            st.code(ans_sql, language="sql")

    optimization = st.session_state.get("last_optimization")
    if optimization:
        st.markdown("### 优化建议")
        st.markdown(optimization)

    # 解析按钮：所有判题结果都允许查看解析（包括答对）
    if not st.session_state.get("last_explanation"):
        if st.button("查看解析", type="secondary"):
            _generate_explanation()

    explanation = st.session_state.get("last_explanation")
    if explanation:
        st.markdown("### 详细解析")
        st.markdown(explanation)
    if explanation is None and st.session_state.get("last_explanation_error"):
        st.warning(st.session_state["last_explanation_error"])

    st.divider()


def _generate_explanation():
    from agent.tutor import Tutor
    llm = st.session_state.get("llm_client")
    schema = st.session_state.get("current_schema_sql", "")
    current_q = st.session_state.get("last_question") or {}
    user_sql = st.session_state.get("last_user_sql", "")
    result = st.session_state.get("last_result", {})
    if not llm:
        st.warning("请先设置 API Key。")
        return
    # 仅在非正确答案时同时展示标准答案，正确时只显示解析即可
    if result.get("verdict") != "correct":
        st.session_state["show_answer"] = True
    with st.spinner("生成详细解析..."):
        try:
            tutor = Tutor(llm)
            explanation = tutor.explain(
                schema, current_q.get("question", ""),
                current_q.get("answer_sql", ""),
                user_sql, result.get("verdict", "wrong"),
                result.get("analysis", ""),
            )
            st.session_state["last_explanation"] = explanation
            st.session_state["last_explanation_error"] = None
        except Exception as e:
            st.session_state["last_explanation"] = None
            st.session_state["last_explanation_error"] = f"解析生成失败：{e}"
    st.rerun()


def _handle_submission(llm_client, store, full_schema_sql, current_question, user_sql):
    from agent.judge import JudgeEngine
    settings = load_settings()

    for key in ["last_result", "last_explanation", "last_explanation_error",
                "last_optimization", "show_answer"]:
        st.session_state.pop(key, None)

    st.session_state["last_user_sql"] = user_sql
    st.session_state["last_question"] = current_question

    try:
        judge = JudgeEngine(
            llm=llm_client if settings.get("enable_semantic_judge") else None,
            enable_semantic=settings.get("enable_semantic_judge", False),
        )
        result = judge.judge(
            full_schema_sql,
            current_question.get("question", ""),
            current_question.get("answer_sql", ""),
            user_sql,
        )
    except Exception as e:
        st.error(f"判题过程出错：{e}")
        return

    qid = st.session_state.get("current_question_id")
    if qid:
        store.save_history(qid, user_sql, result["verdict"],
                           result.get("error_type", ""))

    st.session_state["hint_level"] = 0
    st.session_state["hints"] = []
    st.session_state["last_result"] = result
    st.session_state["question_finished"] = True

    if result["verdict"] == "correct" and settings.get("enable_auto_optimization") and llm_client:
        _generate_optimization(llm_client, full_schema_sql, current_question, user_sql)

    if settings.get("prefetch_next_question") and llm_client:
        _prefetch_next_question_async(llm_client, store, full_schema_sql)

    st.session_state["stats"] = store.get_stats()
    st.rerun()


def _generate_optimization(llm_client, full_schema_sql, current_q, user_sql):
    from agent.tutor import Tutor
    try:
        tutor = Tutor(llm_client)
        opt = tutor.answer_question(
            full_schema_sql,
            f"学生 SQL：\n```sql\n{user_sql}\n```\n标准答案：\n```sql\n{current_q.get('answer_sql', '')}\n```\n"
            f"请用 1~2 句话给优化建议；没有空间则说『已经很好了』。最多 60 字。",
        )
        st.session_state["last_optimization"] = opt
    except Exception:
        st.session_state["last_optimization"] = "答得很好，继续保持。"


def _prefetch_next_question_async(llm_client, store, full_schema_sql):
    from agent.question_gen import QuestionGenerator
    domain = st.session_state.get("current_domain", "")
    difficulty = st.session_state.get("current_difficulty", "easy")
    qtype = st.session_state.get("current_question_type", "random")

    state = st.session_state

    def _worker():
        try:
            qgen = QuestionGenerator(llm_client, store=store)
            q = qgen.generate(full_schema_sql, difficulty, qtype, schema_name=domain)
            if q:
                q["__domain"] = domain
                q["__difficulty"] = difficulty
                q["__qtype"] = qtype
                state["prefetched_question"] = q
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()


def _handle_show_answer(store, current_q):
    """查看答案：进入"已查看答案"状态，标准答案显示出来。

    需求：查看答案不计入总题数（统计中已排除 skipped）。
    同一题首次查看时记一条 skipped 历史，再次查看不重复写入。
    """
    qid = st.session_state.get("current_question_id")
    if qid and current_q and not st.session_state.get("_skipped_recorded"):
        store.save_history(qid, "（已查看答案）", "skipped", "")
        st.session_state["_skipped_recorded"] = True

    if current_q:
        st.session_state["last_question"] = current_q

    st.session_state["show_answer"] = True
    # 仅当尚未提交过判题结果时，标记为「已查看答案」并填一个占位 result
    # 已经有 last_result（用户先提交过 wrong）时不要覆盖原始判定
    if not st.session_state.get("last_result"):
        st.session_state["last_result"] = {
            "verdict": "skipped",
            "analysis": "你选择了直接查看答案。",
            "suggestion": "仔细学习标准答案，理解思路后可以再做一次。",
            "layer": 0,
        }
    st.session_state["question_finished"] = True
    st.session_state["stats"] = store.get_stats()
    st.rerun()


def _hide_answer():
    """隐藏答案：仅切回 show_answer=False，不改写历史。"""
    st.session_state["show_answer"] = False
    st.rerun()


def _render_post_answer_actions():
    st.markdown("---")
    if st.button("下一题", type="primary", use_container_width=False):
        for key in [
            "last_result", "last_explanation", "last_explanation_error",
            "show_answer", "question_finished", "last_user_sql",
            "last_question", "last_optimization",
            "run_result_columns", "run_result_rows", "run_error",
            "has_run_sql", "_skipped_recorded",
        ]:
            st.session_state.pop(key, None)
        st.session_state["hint_level"] = 0
        st.session_state["hints"] = []
        st.session_state["trigger_new_question"] = True
        st.rerun()


def _display_hints():
    hints = st.session_state.get("hints", [])
    if not hints:
        return
    with st.expander(f"提示（共 {len(hints)} 层）", expanded=True):
        for i, h in enumerate(hints, 1):
            level_label = {1: "方向", 2: "引导", 3: "具体"}.get(i, f"第{i}层")
            st.markdown(f"**{level_label}**: {h}")


def _request_hint(llm_client, full_schema_sql, current_question):
    """生成一层提示并立即刷新页面显示。"""
    from agent.tutor import Tutor
    hint_level = st.session_state.get("hint_level", 0) + 1
    st.session_state["hint_level"] = hint_level
    level_prompts = {
        1: f"针对题目'{current_question.get('question', '')}'，给一个高层思路（涉及哪些表/关键字），不要给 SQL。1~2 句。",
        2: f"针对题目'{current_question.get('question', '')}'，给具体引导（如何 JOIN/聚合）。仍不要完整 SQL。2~3 句。",
        3: f"针对题目'{current_question.get('question', '')}'，给关键 SQL 片段，但不完整。3~4 句。",
    }
    prompt = level_prompts.get(hint_level, level_prompts[3])
    with st.spinner(f"生成第 {hint_level} 层提示..."):
        try:
            tutor = Tutor(llm_client)
            hint = tutor.answer_question(full_schema_sql, prompt)
            st.session_state.setdefault("hints", []).append(hint)
        except Exception as e:
            st.session_state.setdefault("hints", []).append(f"（提示生成失败：{e}）")
    # 关键：生成完后立即刷新，否则当前帧已经渲染过 _display_hints
    st.rerun()
