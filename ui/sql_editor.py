"""SQL 编辑器组件 — 基于 streamlit-ace 的 SQL 高亮编辑器。

如果环境中没有 streamlit-ace（如部分受限部署），自动回落到 st.text_area。

设计要点：
- ace 控件 key 一旦确定就会保留组件内部状态，外部 `value` 变更后无法刷新（如换题清空）。
  解决方案：把 value 的哈希拼到 ace 的 key 上，value 变化即重挂载。
"""
import streamlit as st

try:
    from streamlit_ace import st_ace
    _HAS_ACE = True
except ImportError:  # pragma: no cover
    _HAS_ACE = False


def sql_editor(value: str = "", key: str = "sql_input",
               height: int = 200, theme: str = "github",
               placeholder: str = "在此输入 SQL...") -> str:
    """渲染 SQL 编辑器并返回当前文本。"""
    if not _HAS_ACE:
        return st.text_area(
            "SQL 语句",
            value=value,
            placeholder=placeholder,
            height=height,
            key=key,
        )

    ace_key = f"{key}_ace_{hash(value) & 0xFFFF}"
    result = st_ace(
        value=value,
        language="sql",
        theme=theme,
        keybinding="vscode",
        font_size=14,
        tab_size=2,
        wrap=True,
        show_gutter=True,
        show_print_margin=False,
        auto_update=True,
        readonly=False,
        min_lines=max(8, height // 22),
        max_lines=24,
        placeholder=placeholder,
        key=ace_key,
    )
    return result or ""
