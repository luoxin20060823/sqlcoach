"""挑战模式 Tab — 一次性出 N 道题，限时通关。

特点：
- 题目并发预生成（QuestionGenerator.generate_batch）
- 不能使用提示 / 不能查看答案
- 每题给出对错但不显示标准答案，避免泄题
- 全部完成后给出总分 + 用时 + 复盘
- 挑战记录单独存表，不污染主统计
"""
import sqlite3
import time
import pandas as pd
import streamlit as st

from agent.judge import JudgeEngine
from agent.preset_schemas import get_preset
from agent.question_gen import QuestionGenerator
from config import DOMAINS, load_settings
from ui.sql_editor import sql_editor


def render_challenge_tab(llm_client, store):
    st.subheader("挑战模式")

    state = st.session_state.setdefault("challenge", {})
    phase = state.get("phase", "setup")  # setup -> running -> finished

    if phase == "setup":
        _render_setup(llm_client, store)
    elif phase == "running":
        _render_running(store)
    elif phase == "finished":
        _render_finished(store)


# ---------------- SETUP ----------------
def _render_setup(llm_client, store):
    st.caption("一次性挑战 N 道连续题。挑战中无法查看答案、无提示，结束后看总分。")

    # 历史最佳
    runs = store.get_challenge_runs(limit=5)
    if runs:
        df = pd.DataFrame(runs)
        df["分数"] = df.apply(lambda r: f"{r['correct_count']}/{r['question_count']}", axis=1)
        df["用时"] = df["duration_seconds"].apply(_fmt_duration)
        st.markdown("**最近 5 次挑战**")
        st.dataframe(
            df[["schema_name", "difficulty", "分数", "用时", "finished_at"]]
              .rename(columns={
                  "schema_name": "领域", "difficulty": "难度", "finished_at": "时间",
              }),
            use_container_width=True, hide_index=True,
        )

    st.markdown("---")
    st.markdown("### 配置挑战")
    col1, col2, col3 = st.columns(3)
    with col1:
        schema_name = st.selectbox("领域", DOMAINS, key="challenge_schema")
    with col2:
        difficulty = st.selectbox(
            "难度", ["easy", "medium", "hard"], key="challenge_difficulty",
            format_func=lambda x: {"easy": "初级", "medium": "中级", "hard": "高级"}[x],
        )
    with col3:
        count = st.selectbox("题数", [3, 5, 10], index=1, key="challenge_count")

    best = store.get_best_challenge(schema_name, difficulty, count)
    if best:
        st.info(
            f"该条件最佳成绩：{best['correct_count']}/{best['question_count']}，"
            f"用时 {_fmt_duration(best['duration_seconds'])}"
        )

    schema_sql = get_preset(schema_name) or store.get_cached_schema(schema_name)
    if not schema_sql:
        st.warning("该领域 schema 不在预置库或缓存中。请先到主界面生成数据库。")
        return

    if st.button("开始挑战", type="primary", use_container_width=False):
        if not llm_client:
            st.error("请先配置 API Key 才能生成题目。")
            return
        _start_challenge(llm_client, store, schema_name, difficulty, count, schema_sql)


def _start_challenge(llm_client, store, schema_name, difficulty, count, schema_sql):
    qgen = QuestionGenerator(llm_client, store=store)
    with st.spinner(f"正在并发生成 {count} 道题..."):
        questions = qgen.generate_batch(schema_sql, difficulty, count=count)

    # 并发生成可能少几道，至少要 max(count-1, 3) 才开打，否则提示重试
    if len(questions) < max(3, count - 1):
        st.error(f"题目生成失败（仅 {len(questions)}/{count}），请重试。")
        return

    # 持久化到题库
    saved = []
    for q in questions:
        qid = store.save_question(
            schema_name=schema_name,
            difficulty=difficulty,
            knowledge_point=q.get("knowledge_point", ""),
            question_text=q.get("question", ""),
            answer_sql=q.get("answer_sql", ""),
            question_type=q.get("question_type", ""),
            schema_sql=schema_sql,
        )
        q["__qid"] = qid
        saved.append(q)

    st.session_state["challenge"] = {
        "phase": "running",
        "schema_name": schema_name,
        "difficulty": difficulty,
        "schema_sql": schema_sql,
        "questions": saved,
        "current_index": 0,
        "results": [],          # [{verdict, user_sql, time_used}]
        "started_at": time.time(),
        "current_started_at": time.time(),
    }
    st.rerun()


# ---------------- RUNNING ----------------
def _render_running(store):
    state = st.session_state["challenge"]
    questions = state["questions"]
    idx = state["current_index"]
    total = len(questions)
    q = questions[idx]

    # 进度
    st.progress(idx / total, text=f"第 {idx + 1} / {total} 题")
    elapsed_total = int(time.time() - state["started_at"])
    st.caption(f"已用时：{_fmt_duration(elapsed_total)}")

    # 本题
    st.markdown(f"### 第 {idx + 1} 题")
    st.markdown(f"**知识点**: {q.get('knowledge_point', '')}")
    st.markdown(f"> {q.get('question', '')}")

    with st.expander("数据库结构", expanded=False):
        st.code(state["schema_sql"], language="sql")

    sql_input = sql_editor(
        value="",
        key=f"challenge_q_{idx}",
        height=160,
        placeholder="作答这道题，提交后无法修改",
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        run_btn = st.button("运行", key=f"ch_run_{idx}", use_container_width=True)
    with col2:
        submit_btn = st.button("提交", key=f"ch_submit_{idx}", type="primary",
                                use_container_width=True,
                                disabled=not bool(sql_input.strip()))
    with col3:
        if st.button("放弃挑战", key=f"ch_abort_{idx}"):
            _abort_challenge()

    if run_btn and sql_input.strip():
        _run_sql(state["schema_sql"], sql_input, idx)
    _render_run_result(idx)

    if submit_btn:
        _submit_current(state, store, sql_input)


def _submit_current(state, store, sql_input):
    settings = load_settings()
    judge = JudgeEngine(llm=None, enable_semantic=False)  # 挑战模式只走快速判定
    q = state["questions"][state["current_index"]]
    result = judge.judge(state["schema_sql"], q["question"],
                         q["answer_sql"], sql_input)

    time_used = int(time.time() - state["current_started_at"])
    state["results"].append({
        "verdict": result["verdict"],
        "user_sql": sql_input,
        "time_used": time_used,
        "analysis": result.get("analysis", ""),
    })

    state["current_index"] += 1
    state["current_started_at"] = time.time()

    # 全部做完 → 进入 finished 阶段
    if state["current_index"] >= len(state["questions"]):
        _finalize_challenge(state, store)
    st.rerun()


def _abort_challenge():
    """放弃当前挑战，返回 setup 阶段（不计入历史）。"""
    st.session_state["challenge"] = {"phase": "setup"}
    st.rerun()


def _finalize_challenge(state, store):
    duration = int(time.time() - state["started_at"])
    correct = sum(1 for r in state["results"] if r["verdict"] == "correct")
    store.save_challenge_run(
        schema_name=state["schema_name"],
        difficulty=state["difficulty"],
        question_count=len(state["questions"]),
        correct_count=correct,
        duration_seconds=duration,
    )
    state["phase"] = "finished"
    state["duration"] = duration
    state["correct"] = correct


# ---------------- FINISHED ----------------
def _render_finished(store):
    state = st.session_state["challenge"]
    total = len(state["questions"])
    correct = state["correct"]
    duration = state["duration"]
    accuracy = correct / total if total else 0

    # 评级
    if accuracy >= 0.9:
        rating, color = "S", "#16a34a"
    elif accuracy >= 0.7:
        rating, color = "A", "#3b82f6"
    elif accuracy >= 0.5:
        rating, color = "B", "#f59e0b"
    else:
        rating, color = "C", "#dc2626"

    st.markdown(f"### 挑战完成")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("得分", f"{correct} / {total}")
    with c2:
        st.metric("正确率", f"{accuracy:.0%}")
    with c3:
        st.metric("用时", _fmt_duration(duration))
    with c4:
        st.markdown(
            f"<div style='font-size:14px;color:#6b7280'>评级</div>"
            f"<div style='font-size:48px;font-weight:bold;color:{color};line-height:1'>{rating}</div>",
            unsafe_allow_html=True,
        )

    # 历史最佳
    best = store.get_best_challenge(
        state["schema_name"], state["difficulty"], total,
    )
    if best:
        if best["correct_count"] == correct and best["duration_seconds"] == duration:
            st.success("新的最佳成绩！")
        else:
            st.caption(
                f"该条件最佳成绩：{best['correct_count']}/{best['question_count']}，"
                f"用时 {_fmt_duration(best['duration_seconds'])}"
            )

    st.markdown("---")
    st.markdown("### 复盘")
    for i, (q, r) in enumerate(zip(state["questions"], state["results"]), 1):
        verdict_label = {"correct": "正确", "wrong": "错误",
                         "flawed": "瑕疵"}.get(r["verdict"], r["verdict"])
        with st.expander(
            f"第 {i} 题 — {verdict_label} — 用时 {_fmt_duration(r['time_used'])}",
            expanded=(r["verdict"] != "correct"),
        ):
            st.markdown(f"**题目**: {q['question']}")
            st.markdown(f"**知识点**: {q.get('knowledge_point', '')}")
            if r.get("analysis"):
                st.markdown(f"**分析**: {r['analysis']}")
            st.markdown("**你的答案**:")
            st.code(r["user_sql"] or "（未作答）", language="sql")
            st.markdown("**标准答案**:")
            st.code(q["answer_sql"], language="sql")

    st.markdown("---")
    if st.button("再来一次", type="primary"):
        st.session_state["challenge"] = {"phase": "setup"}
        st.rerun()


# ---------------- 工具 ----------------
def _fmt_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


def _run_sql(schema_sql, sql, idx):
    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_sql)
        cur = conn.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        st.session_state[f"ch_run_result_{idx}"] = {
            "cols": cols, "rows": rows, "error": ""
        }
    except Exception as e:
        st.session_state[f"ch_run_result_{idx}"] = {
            "cols": [], "rows": [], "error": str(e)
        }


def _render_run_result(idx):
    info = st.session_state.get(f"ch_run_result_{idx}")
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
