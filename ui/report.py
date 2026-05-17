"""Streamlit 分析报告 Tab — 雷达图 + 趋势图 + 历史 + 建议 + 导出"""
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from config import KNOWLEDGE_POINTS


def render_report_tab(llm_client, store):
    st.subheader("学习分析报告")

    stats = store.get_stats()
    if stats["total"] == 0:
        st.info("还没有答题记录，先去练习吧。")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("总答题数", stats["total"])
    with c2:
        st.metric("正确数", stats["correct"])
    with c3:
        st.metric("正确率", f"{stats['accuracy']:.0%}")

    history = store.get_user_history(limit=200)
    first_attempts = store.get_first_attempts(limit=200)
    dim_stats = store.get_dimension_stats()

    # 趋势图：每日正确率折线 + 每日做题数柱状（同一行）
    st.markdown("### 答题趋势")
    daily = _daily_aggregate(history)
    if not daily.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(_build_accuracy_trend(daily), use_container_width=True)
        with col_b:
            st.plotly_chart(_build_volume_chart(daily), use_container_width=True)
    else:
        st.caption("数据不足以画趋势图。")

    # 能力维度：雷达图 + 横向条形图
    st.markdown("### 能力维度")
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(_build_radar_chart(dim_stats), use_container_width=True)
    with col_r:
        st.plotly_chart(_build_dimension_bar(dim_stats), use_container_width=True)

    # 答题历史
    st.markdown("### 答题历史（最近 20 条，每题只显示第一次）")
    if first_attempts:
        df = pd.DataFrame(first_attempts)
        df["结果"] = df["verdict"].map({
            "correct": "正确", "flawed": "瑕疵", "wrong": "错误",
        })
        cols = [c for c in ["question_text", "difficulty", "knowledge_point", "结果"]
                if c in df.columns]
        st.dataframe(df[cols].head(20), use_container_width=True, hide_index=True)
    else:
        st.caption("还没有有效的答题记录。")

    # 智能分析
    if llm_client:
        st.markdown("### 智能分析建议")
        if st.button("生成 / 刷新分析", type="primary"):
            with st.spinner("正在分析..."):
                from agent.analyzer import Analyzer
                analyzer = Analyzer(llm_client)
                analysis = analyzer.analyze(history, dim_stats)
                st.session_state["last_analysis"] = analysis
        analysis = st.session_state.get("last_analysis")
        if analysis:
            _render_analysis(analysis)
            _render_export(stats, first_attempts, dim_stats, analysis)


# ----------------- 趋势图 -----------------
def _daily_aggregate(history: list) -> pd.DataFrame:
    """聚合每日做题数与正确数（排除 skipped）。"""
    if not history:
        return pd.DataFrame()
    df = pd.DataFrame(history)
    if "created_at" not in df.columns:
        return pd.DataFrame()
    df = df[df["verdict"] != "skipped"].copy()
    if df.empty:
        return pd.DataFrame()
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    g = df.groupby("date").agg(
        total=("verdict", "count"),
        correct=("verdict", lambda v: (v == "correct").sum()),
    ).reset_index().sort_values("date")
    g["accuracy"] = g["correct"] / g["total"]
    return g


def _build_accuracy_trend(daily: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["accuracy"],
        mode="lines+markers",
        line=dict(color="#3b82f6", width=3),
        marker=dict(size=8, color="#3b82f6"),
        name="每日正确率",
        hovertemplate="%{x}<br>正确率 %{y:.0%}<extra></extra>",
    ))
    fig.update_layout(
        title="每日正确率趋势",
        height=320,
        yaxis=dict(range=[0, 1.05], tickformat=".0%"),
        xaxis_title="日期",
        margin=dict(t=40, b=30, l=30, r=10),
    )
    return fig


def _build_volume_chart(daily: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["date"], y=daily["total"],
        marker_color="#818cf8",
        name="每日做题数",
        hovertemplate="%{x}<br>做题数 %{y}<extra></extra>",
    ))
    fig.update_layout(
        title="每日做题量",
        height=320,
        xaxis_title="日期",
        yaxis_title="做题数",
        margin=dict(t=40, b=30, l=30, r=10),
    )
    return fig


# ----------------- 维度图 -----------------
def _build_dimension_bar(dim_stats: dict) -> go.Figure:
    points, accuracies, totals = [], [], []
    for kp in KNOWLEDGE_POINTS:
        d = dim_stats.get(kp, {"accuracy": 0.0, "total": 0})
        points.append(kp)
        accuracies.append(d["accuracy"])
        totals.append(d["total"])

    colors = [
        "#10b981" if a >= 0.8 else "#f59e0b" if a >= 0.5 else "#ef4444"
        for a in accuracies
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=accuracies,
        y=points,
        orientation="h",
        marker_color=colors,
        text=[f"{a:.0%} ({t} 题)" if t else "无记录" for a, t in zip(accuracies, totals)],
        textposition="outside",
        hovertemplate="%{y}<br>正确率 %{x:.0%}<extra></extra>",
    ))
    fig.update_layout(
        title="知识点掌握度（绿色 ≥80%，橙色 50-80%，红色 <50%）",
        height=400,
        xaxis=dict(range=[0, 1.15], tickformat=".0%"),
        margin=dict(t=40, b=30, l=80, r=20),
    )
    return fig


def _render_analysis(analysis):
    st.markdown(f"**总评**: {analysis.get('summary', '')}")
    cs, cw = st.columns(2)
    with cs:
        st.markdown("**强项**:")
        for s in analysis.get("strengths", []):
            st.markdown(f"- {s}")
    with cw:
        st.markdown("**弱项**:")
        for w in analysis.get("weaknesses", []):
            st.markdown(f"- {w}")
    st.markdown("**改进建议**:")
    for sug in analysis.get("suggestions", []):
        st.markdown(f"- {sug}")
    next_diff = analysis.get("next_difficulty", "easy")
    diff_labels = {"easy": "初级", "medium": "中级", "hard": "高级"}
    st.info(f"建议下次练习难度：{diff_labels.get(next_diff, next_diff)}")


def _render_export(stats, history, dim_stats, analysis):
    md = _build_markdown_report(stats, history, dim_stats, analysis)
    st.download_button(
        "导出 Markdown 报告",
        data=md.encode("utf-8"),
        file_name=f"sql_coach_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown",
        use_container_width=False,
    )


def _build_markdown_report(stats, history, dim_stats, analysis) -> str:
    lines = [
        "# SQL 随身教练 学习报告",
        f"_生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "## 总体统计",
        f"- 总答题数：**{stats['total']}**",
        f"- 正确数：**{stats['correct']}**",
        f"- 正确率：**{stats['accuracy']:.0%}**",
        "",
        "## 维度掌握度",
    ]
    for kp in KNOWLEDGE_POINTS:
        d = dim_stats.get(kp, {"total": 0, "correct": 0, "accuracy": 0.0})
        lines.append(f"- {kp}：{d['correct']}/{d['total']} (正确率 {d['accuracy']:.0%})")
    lines.append("")
    if analysis:
        lines.extend([
            "## 智能分析",
            f"**总评**：{analysis.get('summary', '')}",
            "",
            "**强项**：" + "、".join(analysis.get("strengths", []) or ["—"]),
            "**弱项**：" + "、".join(analysis.get("weaknesses", []) or ["—"]),
            "",
            "### 改进建议",
        ])
        for s in analysis.get("suggestions", []):
            lines.append(f"- {s}")
        lines.append("")
    lines.append("## 最近 20 条记录（每题第一次）")
    lines.append("| 难度 | 知识点 | 结果 | 题目 |")
    lines.append("|---|---|---|---|")
    for h in history[:20]:
        verdict = {"correct": "正确", "flawed": "瑕疵", "wrong": "错误"}.get(
            h.get("verdict", ""), h.get("verdict", "")
        )
        title = (h.get("question_text") or "").replace("|", "\\|").replace("\n", " ")[:60]
        lines.append(
            f"| {h.get('difficulty', '')} | {h.get('knowledge_point', '')} | "
            f"{verdict} | {title} |"
        )
    return "\n".join(lines)


def _build_radar_chart(dim_stats: dict) -> go.Figure:
    values = []
    for kp in KNOWLEDGE_POINTS:
        dim = dim_stats.get(kp, {"accuracy": 0.0})
        values.append(dim["accuracy"])
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=KNOWLEDGE_POINTS,
        fill="toself",
        name="正确率",
        line_color="#3b82f6",
        fillcolor="rgba(59, 130, 246, 0.3)",
    ))
    fig.update_layout(
        title="能力雷达图",
        polar=dict(radialaxis=dict(range=[0, 1], tickformat=".0%")),
        height=400,
        margin=dict(t=40, b=20, l=20, r=20),
    )
    return fig
