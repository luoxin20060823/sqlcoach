"""考试模式 Tab — 限时连续多题，自动判分。

核心规则：
- 题数与限时（分钟）由用户配置
- 难度均分（easy/medium/hard 轮询），分数按难度加权 1/2/3，总分恒为 100
- 题间可自由切换（上一题 / 下一题），编辑器保留各题答案
- 不设单题提交；最后一题处显示"提交试卷"
- 倒计时结束自动提交（streamlit-autorefresh 每秒触发 rerun 检查）
- 提交后展示得分 + 复盘，每题可生成详细解析
"""
import sqlite3
import time
import math
import pandas as pd
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
    _HAS_AUTOREFRESH = True
except ImportError:  # pragma: no cover
    _HAS_AUTOREFRESH = False

from agent.judge import JudgeEngine
from agent.preset_schemas import get_preset
from agent.question_gen import QuestionGenerator
from config import DOMAINS
from ui.sql_editor import sql_editor


# 难度分值权重（用于把 100 分平均按难度加权分配到每题）
DIFFICULTY_WEIGHT = {"easy": 1, "medium": 2, "hard": 3}
DIFFICULTY_SEQUENCE = ["easy", "medium", "hard"]


def render_exam_tab(llm_client, store):
    st.subheader("考试模式")

    state = st.session_state.setdefault("exam", {})
    phase = state.get("phase", "setup")  # setup → running → finished

    if phase == "setup":
        _render_setup(llm_client, store)
    elif phase == "running":
        _render_running(store)
    elif phase == "finished":
        _render_finished(llm_client, store)


# ---------------- SETUP ----------------
def _render_setup(llm_client, store):
    st.caption(
        "限时考试。难度均分，分数按难度加权（初级=1、中级=2、高级=3），总分 100 分。"
        "答题过程可来回切换题目，最后一题处提交，超时自动交卷。"
    )

    # 历史考试记录
    runs = store.get_challenge_runs(limit=5)
    if runs:
        df = pd.DataFrame(runs)
        df["分数"] = df.apply(lambda r: f"{r['correct_count']}/{r['question_count']}", axis=1)
        df["用时"] = df["duration_seconds"].apply(_fmt_duration)
        st.markdown("**最近 5 次考试**")
        st.dataframe(
            df[["schema_name", "difficulty", "分数", "用时", "finished_at"]]
              .rename(columns={
                  "schema_name": "领域", "difficulty": "难度", "finished_at": "时间",
              }),
            use_container_width=True, hide_index=True,
        )

    st.markdown("---")
    st.markdown("### 配置考试")

    col1, col2 = st.columns(2)
    with col1:
        schema_name = st.selectbox("领域", DOMAINS, key="exam_schema")
    with col2:
        question_count = st.number_input(
            "题数", min_value=3, max_value=30, value=6, step=1,
            help="建议为 3 的倍数，便于难度均分；非 3 的倍数也可，会按 easy/medium/hard 顺序补齐",
        )

    col3, col4 = st.columns(2)
    with col3:
        time_limit_min = st.number_input(
            "限制时间（分钟）",
            min_value=1, max_value=120, value=10, step=1,
        )
    with col4:
        # 显示分数预估
        difficulties = _allocate_difficulties(int(question_count))
        scores = _compute_scores(difficulties)
        easy_n = difficulties.count("easy")
        med_n = difficulties.count("medium")
        hard_n = difficulties.count("hard")
        st.markdown(
            f"<div style='padding-top:24px;font-size:13px;color:#6b7280'>"
            f"难度分布：初级 {easy_n} · 中级 {med_n} · 高级 {hard_n}<br>"
            f"分数：每初级 {scores[0] if easy_n else 0} 分，"
            f"每中级 {scores[easy_n] if med_n else 0} 分，"
            f"每高级 {scores[easy_n + med_n] if hard_n else 0} 分</div>",
            unsafe_allow_html=True,
        )

    schema_sql = get_preset(schema_name) or store.get_cached_schema(schema_name)
    if not schema_sql:
        st.warning("该领域 schema 不在预置库或缓存中，请先到主界面生成数据库。")
        return

    if st.button("开始考试", type="primary"):
        if not llm_client:
            st.error("请先配置 API Key 才能生成题目。")
            return
        _start_exam(llm_client, store, schema_name, int(question_count),
                    int(time_limit_min) * 60, schema_sql)


def _allocate_difficulties(count: int) -> list:
    """返回长度为 count 的难度列表，按 easy/medium/hard 轮询分配。"""
    return [DIFFICULTY_SEQUENCE[i % 3] for i in range(count)]


def _compute_scores(difficulties: list) -> list:
    """根据难度权重，把总分 100 平均加权分给每题（保留两位小数后修正最后一题，使总分 = 100）。"""
    weights = [DIFFICULTY_WEIGHT[d] for d in difficulties]
    total_weight = sum(weights) or 1
    scores = [round(w * 100 / total_weight, 2) for w in weights]
    # 修正小数误差
    diff = round(100 - sum(scores), 2)
    if scores:
        scores[-1] = round(scores[-1] + diff, 2)
    return scores


def _start_exam(llm_client, store, schema_name, count, time_limit_sec, schema_sql):
    qgen = QuestionGenerator(llm_client, store=store)
    difficulties = _allocate_difficulties(count)
    scores = _compute_scores(difficulties)

    # 按难度分组并发生成（一次性 chat_many）
    with st.spinner(f"正在为 {count} 道题并发生成..."):
        # generate_batch 接受单一 difficulty，所以分批
        questions = []
        for diff_label in DIFFICULTY_SEQUENCE:
            n = difficulties.count(diff_label)
            if n <= 0:
                continue
            batch = qgen.generate_batch(schema_sql, diff_label, count=n)
            questions.extend([(diff_label, q) for q in batch])

    # 至少要 max(count - 1, 3) 才开考
    if len(questions) < max(3, count - 1):
        st.error(f"题目生成失败（仅 {len(questions)}/{count}），请重试。")
        return

    # 重新按 difficulties 顺序排，分数与位置对齐
    bucket = {"easy": [], "medium": [], "hard": []}
    for d, q in questions:
        bucket[d].append(q)
    ordered = []
    for d in difficulties:
        if bucket[d]:
            ordered.append((d, bucket[d].pop(0)))
    if len(ordered) != len(difficulties):
        # 若某档生成数量不够，截断分数列表对齐
        difficulties = [d for d, _ in ordered]
        scores = _compute_scores(difficulties)

    # 持久化题目（关联到 schema_name）
    saved = []
    for (d, q), s in zip(ordered, scores):
        qid = store.save_question(
            schema_name=schema_name,
            difficulty=d,
            knowledge_point=q.get("knowledge_point", ""),
            question_text=q.get("question", ""),
            answer_sql=q.get("answer_sql", ""),
            question_type=q.get("question_type", ""),
            schema_sql=schema_sql,
        )
        q["__qid"] = qid
        q["difficulty"] = d
        q["score"] = s
        saved.append(q)

    st.session_state["exam"] = {
        "phase": "running",
        "schema_name": schema_name,
        "schema_sql": schema_sql,
        "questions": saved,
        "current_index": 0,
        "answers": ["" for _ in saved],     # 每题保留的 SQL
        "started_at": time.time(),
        "deadline": time.time() + time_limit_sec,
        "time_limit_sec": time_limit_sec,
    }
    st.rerun()


# ---------------- RUNNING ----------------
def _render_running(store):
    state = st.session_state["exam"]
    questions = state["questions"]
    idx = state["current_index"]
    total = len(questions)
    q = questions[idx]

    # 倒计时（每秒自动刷新）
    if _HAS_AUTOREFRESH:
        st_autorefresh(interval=1000, key="exam_timer_tick")

    remaining = max(0, int(state["deadline"] - time.time()))
    if remaining <= 0:
        st.warning("考试时间已到，自动提交。")
        _finalize_exam(store)
        return

    # 顶部状态栏：题号 + 倒计时
    top_col1, top_col2, top_col3 = st.columns([2, 2, 2])
    with top_col1:
        st.metric("当前题号", f"{idx + 1} / {total}")
    with top_col2:
        st.metric("本题分值", f"{q.get('score', 0)} 分")
    with top_col3:
        # 倒计时高亮：≤60s 红色
        color = "#dc2626" if remaining <= 60 else "#3b82f6"
        st.markdown(
            f"<div style='font-size:14px;color:#6b7280'>剩余时间</div>"
            f"<div style='font-size:32px;font-weight:bold;color:{color};line-height:1'>"
            f"{_fmt_duration(remaining)}</div>",
            unsafe_allow_html=True,
        )

    st.progress((idx + 1) / total, text=f"进度 {idx + 1}/{total}")

    # 题目内容
    diff_label = {"easy": "初级", "medium": "中级", "hard": "高级"}.get(
        q.get("difficulty", ""), q.get("difficulty", "")
    )
    st.markdown(f"### 第 {idx + 1} 题（{diff_label}，{q.get('score', 0)} 分）")
    st.markdown(f"**知识点**: {q.get('knowledge_point', '')}")
    st.markdown(f"> {q.get('question', '')}")

    with st.expander("数据库结构", expanded=False):
        st.code(state["schema_sql"], language="sql")

    # SQL 编辑器：使用题号作为 key，保留每题答案
    saved_answer = state["answers"][idx]
    sql_input = sql_editor(
        value=saved_answer,
        key=f"exam_q_editor_{idx}",
        height=160,
        placeholder="输入 SQL 作答；可点上一题/下一题切换，本题答案会被保留",
    )
    # 实时同步到 state（用户输入后下一次 rerun 时记录）
    state["answers"][idx] = sql_input

    # 操作按钮：运行 / 上一题 / 下一题 / 提交
    btn_cols = st.columns([1, 1, 1, 1, 2])
    with btn_cols[0]:
        run_btn = st.button("运行", key=f"exam_run_{idx}", use_container_width=True)
    with btn_cols[1]:
        prev_btn = st.button("上一题", key=f"exam_prev_{idx}",
                              disabled=idx == 0, use_container_width=True)
    with btn_cols[2]:
        next_btn = st.button("下一题", key=f"exam_next_{idx}",
                              disabled=idx >= total - 1, use_container_width=True)
    with btn_cols[3]:
        if idx == total - 1:
            submit_btn = st.button("提交试卷", key=f"exam_submit_{idx}",
                                    type="primary", use_container_width=True)
        else:
            submit_btn = False
    with btn_cols[4]:
        if st.button("放弃考试", key=f"exam_abort_{idx}",
                      help="不计入历史"):
            st.session_state["exam"] = {"phase": "setup"}
            st.rerun()

    if run_btn and sql_input.strip():
        _run_sql(state["schema_sql"], sql_input, idx)
    _render_run_result(idx)

    if prev_btn:
        state["current_index"] = max(0, idx - 1)
        st.rerun()
    if next_btn:
        state["current_index"] = min(total - 1, idx + 1)
        st.rerun()
    if submit_btn:
        _finalize_exam(store)


def _finalize_exam(store):
    """判卷：对每道题用 JudgeEngine 快速判，累计得分，写入考试历史。"""
    state = st.session_state["exam"]
    judge = JudgeEngine(llm=None, enable_semantic=False)

    results = []
    total_score = 0.0
    correct_cnt = 0
    for q, user_sql in zip(state["questions"], state["answers"]):
        if not user_sql.strip():
            results.append({
                "verdict": "wrong",
                "user_sql": "",
                "analysis": "未作答。",
                "score_obtained": 0.0,
            })
            continue
        try:
            r = judge.judge(state["schema_sql"], q["question"],
                            q["answer_sql"], user_sql)
        except Exception as e:
            r = {"verdict": "wrong", "analysis": f"判题异常：{e}",
                 "error_type": "syntax"}
        score_got = q["score"] if r["verdict"] == "correct" else 0.0
        if r["verdict"] == "correct":
            correct_cnt += 1
        total_score += score_got
        results.append({
            "verdict": r["verdict"],
            "user_sql": user_sql,
            "analysis": r.get("analysis", ""),
            "score_obtained": round(score_got, 2),
        })

    duration = int(time.time() - state["started_at"])
    # 记录到 challenge_runs（沿用旧表）
    store.save_challenge_run(
        schema_name=state["schema_name"],
        difficulty="exam",
        question_count=len(state["questions"]),
        correct_count=correct_cnt,
        duration_seconds=duration,
    )

    state["phase"] = "finished"
    state["results"] = results
    state["total_score"] = round(total_score, 2)
    state["correct_count"] = correct_cnt
    state["duration"] = duration
    st.rerun()


# ---------------- FINISHED ----------------
def _render_finished(llm_client, store):
    state = st.session_state["exam"]
    total_q = len(state["questions"])
    score = state["total_score"]
    correct = state["correct_count"]
    duration = state["duration"]

    # 评级
    if score >= 90:
        rating, color = "A+", "#16a34a"
    elif score >= 80:
        rating, color = "A", "#3b82f6"
    elif score >= 70:
        rating, color = "B", "#0891b2"
    elif score >= 60:
        rating, color = "C", "#f59e0b"
    else:
        rating, color = "D", "#dc2626"

    st.markdown("### 考试完成")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("得分", f"{score} / 100")
    with c2:
        st.metric("正确题数", f"{correct} / {total_q}")
    with c3:
        st.metric("用时", _fmt_duration(duration))
    with c4:
        st.markdown(
            f"<div style='font-size:14px;color:#6b7280'>评级</div>"
            f"<div style='font-size:48px;font-weight:bold;color:{color};line-height:1'>{rating}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    review_header_col1, review_header_col2 = st.columns([3, 2])
    with review_header_col1:
        st.markdown("### 复盘")
    with review_header_col2:
        all_done = all(r.get("explanation") for r in state["results"])
        if not all_done and llm_client:
            if st.button("一键生成全部解析", use_container_width=True,
                         help="并发请求 LLM，约 5~15 秒"):
                _explain_all(llm_client, state)

    diff_label_map = {"easy": "初级", "medium": "中级", "hard": "高级"}
    for i, (q, r) in enumerate(zip(state["questions"], state["results"]), 1):
        verdict_label = {"correct": "正确", "wrong": "错误",
                         "flawed": "瑕疵"}.get(r["verdict"], r["verdict"])
        diff = diff_label_map.get(q.get("difficulty", ""), "")
        score_line = f"{r['score_obtained']}/{q.get('score', 0)} 分"
        with st.expander(
            f"第 {i} 题（{diff}） — {verdict_label} — {score_line}",
            expanded=(r["verdict"] != "correct"),
        ):
            st.markdown(f"**题目**: {q['question']}")
            st.markdown(f"**知识点**: {q.get('knowledge_point', '')}")
            if r.get("analysis"):
                st.markdown(f"**判题分析**: {r['analysis']}")
            st.markdown("**你的答案**:")
            st.code(r["user_sql"] or "（未作答）", language="sql")
            st.markdown("**标准答案**:")
            st.code(q["answer_sql"], language="sql")

            explanation = r.get("explanation")
            if explanation:
                st.markdown("**详细解析**")
                st.markdown(explanation)
            elif llm_client:
                if st.button("生成详细解析", key=f"exam_explain_{i}"):
                    _explain_one(llm_client, state, i - 1)

    st.markdown("---")
    if st.button("再考一次", type="primary"):
        st.session_state["exam"] = {"phase": "setup"}
        st.rerun()


def _explain_one(llm_client, state, idx: int):
    from agent.tutor import Tutor
    q = state["questions"][idx]
    r = state["results"][idx]
    with st.spinner("生成详细解析..."):
        try:
            tutor = Tutor(llm_client)
            explanation = tutor.explain(
                schema=state["schema_sql"],
                question=q.get("question", ""),
                answer_sql=q.get("answer_sql", ""),
                user_sql=r.get("user_sql", "") or "（未作答）",
                verdict=r.get("verdict", "wrong"),
                analysis=r.get("analysis", ""),
            )
            r["explanation"] = explanation
        except Exception as e:
            r["explanation"] = f"解析生成失败：{e}"
    st.rerun()


def _explain_all(llm_client, state):
    from prompts.templates import TUTOR_SYSTEM, TUTOR_USER

    pending = [
        (i, q, r) for i, (q, r) in enumerate(zip(state["questions"], state["results"]))
        if not r.get("explanation")
    ]
    if not pending:
        return

    requests = []
    for _, q, r in pending:
        requests.append({
            "system_prompt": TUTOR_SYSTEM,
            "user_message": TUTOR_USER.format(
                schema=state["schema_sql"],
                question=q.get("question", ""),
                answer_sql=q.get("answer_sql", ""),
                user_sql=r.get("user_sql", "") or "（未作答）",
                verdict=r.get("verdict", "wrong"),
                analysis=r.get("analysis", ""),
            ),
            "temperature": 0.3,
            "max_tokens": 1024,
        })

    with st.spinner(f"并发生成 {len(pending)} 道题的解析..."):
        def _worker(req):
            return llm_client.chat(
                req["system_prompt"], req["user_message"],
                temperature=req["temperature"],
                max_tokens=req["max_tokens"],
            )

        try:
            responses = llm_client.chat_many(requests, worker=_worker, max_workers=4)
            for (i, _, r), resp in zip(pending, responses):
                r["explanation"] = resp or "（解析生成失败，请单独重试）"
        except Exception as e:
            st.error(f"批量生成失败：{e}")
    st.rerun()


# ---------------- 工具 ----------------
def _fmt_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def _run_sql(schema_sql, sql, idx):
    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_sql)
        cur = conn.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        st.session_state[f"exam_run_result_{idx}"] = {
            "cols": cols, "rows": rows, "error": "",
        }
    except Exception as e:
        st.session_state[f"exam_run_result_{idx}"] = {
            "cols": [], "rows": [], "error": str(e),
        }


def _render_run_result(idx):
    info = st.session_state.get(f"exam_run_result_{idx}")
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
