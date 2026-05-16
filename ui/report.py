"""Streamlit 分析报告 Tab — 雷达图 + 历史 + 建议 + 导出"""
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from config import KNOWLEDGE_POINTS


def render_report_tab(llm_client, store):
    st.subheader("📊 学习分析报告")

    stats = store.get_stats()
    if stats["total"] == 0:
        st.info("还没有答题记录，先去练习吧！")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("总答题数", stats["total"])
    with c2:
        st.metric("正确数", stats["correct"])
    with c3:
        st.metric("正确率", f"{stats['accuracy']:.0%}")

    dim_stats = store.get_dimension_stats()
    st.markdown("### 🎯 能力雷达图")
    st.plotly_chart(_build_radar_chart(dim_stats), use_container_width=True)

    st.markdown("### 📝 答题历史（最近 20 条）")
    history = store.get_user_history(limit=50)
    if history:
        df = pd.DataFrame(history)
        df["结果"] = df["verdict"].map({
            "correct": "✅", "flawed": "⚠️", "wrong": "❌", "skipped": "🏳️",
        })
        cols = [c for c in ["question_text", "difficulty", "knowledge_point", "结果"] if c in df.columns]
        st.dataframe(df[cols].head(20), use_container_width=True, hide_index=True)

    if llm_client:
        st.markdown("### 💡 智能分析建议")
        if st.button("🔄 生成 / 刷新分析", type="primary"):
            with st.spinner("正在分析..."):
                from agent.analyzer import Analyzer
                analyzer = Analyzer(llm_client)
                analysis = analyzer.analyze(history, dim_stats)
                st.session_state["last_analysis"] = analysis
        analysis = st.session_state.get("last_analysis")
        if analysis:
            _render_analysis(analysis)
            _render_export(stats, history, dim_stats, analysis)

    st.markdown("### 🔍 错误类型分布")
    error_data = _count_error_types(history)
    if error_data:
        fig2 = px.pie(
            names=list(error_data.keys()),
            values=list(error_data.values()),
            title="错误分类统计",
        )
        st.plotly_chart(fig2, use_container_width=True)


def _render_analysis(analysis):
    st.markdown(f"**总评**: {analysis.get('summary', '')}")
    cs, cw = st.columns(2)
    with cs:
        st.markdown("**强项**:")
        for s in analysis.get("strengths", []):
            st.markdown(f"- ✅ {s}")
    with cw:
        st.markdown("**弱项**:")
        for w in analysis.get("weaknesses", []):
            st.markdown(f"- ⚠️ {w}")
    st.markdown("**改进建议**:")
    for sug in analysis.get("suggestions", []):
        st.markdown(f"- 💡 {sug}")
    next_diff = analysis.get("next_difficulty", "easy")
    diff_labels = {"easy": "初级", "medium": "中级", "hard": "高级"}
    st.info(f"📌 建议下次练习难度：**{diff_labels.get(next_diff, next_diff)}**")


def _render_export(stats, history, dim_stats, analysis):
    md = _build_markdown_report(stats, history, dim_stats, analysis)
    st.download_button(
        "⬇️ 导出 Markdown 报告",
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
    lines.append("## 最近 20 条记录")
    lines.append("| 难度 | 知识点 | 结果 | 题目 |")
    lines.append("|---|---|---|---|")
    for h in history[:20]:
        verdict = {"correct": "✅", "flawed": "⚠️", "wrong": "❌", "skipped": "🏳️"}.get(
            h.get("verdict", ""), h.get("verdict", "")
        )
        title = (h.get("question_text") or "").replace("|", "\\|").replace("\n", " ")[:60]
        lines.append(f"| {h.get('difficulty', '')} | {h.get('knowledge_point', '')} | {verdict} | {title} |")
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
        polar=dict(radialaxis=dict(range=[0, 1], tickformat=".0%")),
        height=400,
    )
    return fig


def _count_error_types(history: list) -> dict:
    counts = {}
    label_map = {
        "syntax": "语法错误", "join_logic": "JOIN错误", "aggregation": "聚合错误",
        "subquery": "子查询错误", "where_condition": "WHERE错误", "window_function": "窗口函数错误",
    }
    for h in history:
        et = h.get("error_type") or ""
        if et and et != "equivalent":
            counts[label_map.get(et, et)] = counts.get(label_map.get(et, et), 0) + 1
    return counts
