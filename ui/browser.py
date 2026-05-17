"""Streamlit 数据浏览 Tab"""
import streamlit as st


def render_browser_tab(current_schema, current_data):
    """渲染数据浏览Tab — 展示当前数据库的表结构和数据"""
    from ui.styles import hero, empty_state
    table_count = len(current_data) if current_data else 0
    row_count = sum(len(rows) for rows in (current_data or {}).values())
    hero(
        "数据库浏览",
        "查看当前数据库的 schema 和示例数据。",
        stats=[
            {"value": str(table_count), "label": "表"},
            {"value": str(row_count), "label": "数据行"},
        ] if table_count else None,
    )

    if not current_schema:
        empty_state(
            "database",
            "还没有加载任何数据库",
            "在左侧侧边栏选择领域并点「生成数据库」，加载后即可在此查看 schema 与各表数据"
        )
        return

    st.code(current_schema, language="sql")

    if current_data:
        st.markdown("---")
        for table_name, rows in current_data.items():
            st.markdown(f"### {table_name} ({len(rows)} 行)")
            if rows:
                import pandas as pd
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.caption("（空表）")
