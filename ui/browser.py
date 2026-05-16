"""Streamlit 数据浏览 Tab"""
import streamlit as st


def render_browser_tab(current_schema, current_data):
    """渲染数据浏览Tab — 展示当前数据库的表结构和数据"""
    st.subheader("🗄️ 数据库浏览")

    if not current_schema:
        st.info('还没有生成数据库，请先在侧边栏选择领域并点击"生成数据库"。')
        return

    st.code(current_schema, language="sql")

    if current_data:
        st.markdown("---")
        for table_name, rows in current_data.items():
            st.markdown(f"### 📋 {table_name} ({len(rows)} 行)")
            if rows:
                import pandas as pd
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.caption("（空表）")
