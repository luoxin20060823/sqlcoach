"""自由答疑 Tab — 多轮 SQL 答疑"""
import streamlit as st
from agent.tutor import Tutor


def render_chat_tab(llm_client, schema_sql):
    from ui.styles import hero, empty_state
    history = st.session_state.get("chat_history", [])
    asked = len([m for m in history if m.get("role") == "user"])
    hero(
        "自由答疑",
        "对当前数据库 schema 提问，多轮对话，AI 助教随时在线。",
        stats=[{"value": str(asked), "label": "已提问"}] if asked else None,
    )

    if not llm_client:
        empty_state(
            "chat",
            "需要先配置 API Key 才能使用答疑",
            "在左侧侧边栏的「高级设置」里粘贴你的 DeepSeek API Key 即可"
        )
        return

    if schema_sql:
        st.caption("已绑定当前数据库，提问可结合具体表名/字段。")
    else:
        st.caption("尚未生成数据库。可以问通用 SQL 问题；如需基于具体 schema，请先生成数据库。")

    history = st.session_state.setdefault("chat_history", [])

    for msg in history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("问点 SQL 相关的问题，例如：JOIN 和子查询有什么区别？")
    if not user_input:
        col1, col2 = st.columns([1, 8])
        with col1:
            if st.button("清空对话"):
                st.session_state["chat_history"] = []
                st.rerun()
        return

    history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            tutor = Tutor(llm_client)
            answer = tutor.chat(schema_sql, history[:-1], user_input)
            st.markdown(answer)
    history.append({"role": "assistant", "content": answer})
    st.session_state["chat_history"] = history
