"""全局样式与卡片化组件。

设计要点：
- 通过 st.markdown 注入一份全局 CSS（方案 A）
- 提供 hero 横幅 / kpi 卡片 / section 容器（方案 B）
- 受 settings.theme_version 控制：default / classic（一键回滚到原生外观）
"""
import streamlit as st


# ----------------- 全局 CSS（方案 A） -----------------
_GLOBAL_CSS = """
<style>
/* === 全局排版 === */
.stApp {
    font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* === 主区域整体留白 === */
.block-container {
    padding-top: 2.0rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px;
}

/* === 标题层级 === */
h1, h2, h3 {
    letter-spacing: -0.01em;
    color: #0f172a;
}
h2 { margin-top: 1.6rem; }
h3 { margin-top: 1.0rem; }

/* === 按钮：圆角 + 过渡 === */
.stButton > button {
    border-radius: 8px !important;
    border: 1px solid #e2e8f0;
    transition: all .15s ease;
    font-weight: 500;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    border: none;
    color: white;
    box-shadow: 0 1px 3px rgba(37, 99, 235, 0.3);
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
}

/* === 输入框 / 下拉 / 文本域：统一圆角 + 边框颜色 === */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input {
    border-radius: 8px !important;
    border-color: #e2e8f0 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
}

/* === metric：放大数字、加微妙背景 === */
[data-testid="stMetric"] {
    background: white;
    padding: 14px 18px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
[data-testid="stMetricLabel"] {
    font-weight: 500 !important;
    color: #64748b !important;
}

/* === Tab 标签栏 === */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #e2e8f0;
}
.stTabs [data-baseweb="tab"] {
    height: 44px;
    background: transparent;
    border-radius: 8px 8px 0 0;
    padding: 0 18px;
    font-weight: 500;
    color: #64748b;
    transition: all .15s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #2563eb;
    background: #eff6ff;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #2563eb;
    background: #eff6ff;
    border-bottom: 2px solid #2563eb;
}

/* === 表格 === */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}

/* === 侧边栏 === */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff, #f1f5f9);
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] h1 {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
}
section[data-testid="stSidebar"] .stButton > button {
    box-shadow: none;
}

/* === Expander === */
.streamlit-expanderHeader, [data-testid="stExpander"] > details > summary {
    border-radius: 8px !important;
    background: #f8fafc;
}

/* === Alert / Info / Success === */
[data-testid="stAlert"] {
    border-radius: 10px;
    border-left-width: 4px;
}

/* === Hero 横幅 === */
.hero-banner {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 22px;
    color: white;
    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.20);
    position: relative;
    overflow: hidden;
}
.hero-banner::after {
    content: "";
    position: absolute;
    right: -40px;
    top: -40px;
    width: 180px;
    height: 180px;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-banner h2 {
    color: white !important;
    margin: 0 !important;
    font-size: 1.6rem !important;
    font-weight: 700;
    position: relative;
    z-index: 1;
}
.hero-banner p {
    color: rgba(255,255,255,0.85);
    margin: 6px 0 0 0;
    font-size: 0.95rem;
    position: relative;
    z-index: 1;
}
.hero-banner .hero-stats {
    margin-top: 14px;
    display: flex;
    gap: 24px;
    position: relative;
    z-index: 1;
}
.hero-banner .hero-stat {
    display: flex;
    flex-direction: column;
}
.hero-banner .hero-stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1;
}
.hero-banner .hero-stat-label {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.75);
    margin-top: 2px;
}

/* === Section 卡片（方案 B） === */
.sql-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

/* === 侧边栏顶部 logo 区 === */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 0 16px 0;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 16px;
}
.sidebar-logo-icon {
    width: 36px;
    height: 36px;
    border-radius: 9px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 1.0rem;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
}
.sidebar-logo-text { line-height: 1.1; }
.sidebar-logo-title {
    font-weight: 700;
    font-size: 1.1rem;
    color: #0f172a;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sidebar-logo-sub {
    font-size: 0.7rem;
    color: #94a3b8;
    margin-top: 2px;
}

/* === 进度条容器 === */
.progress-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 12px;
}
.progress-card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    font-size: 0.85rem;
    color: #64748b;
}
.progress-card-bar {
    height: 6px;
    background: #f1f5f9;
    border-radius: 3px;
    overflow: hidden;
}
.progress-card-fill {
    height: 100%;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    transition: width .4s ease;
}
</style>
"""


def inject_global_styles():
    """在每次 rerun 注入一次全局 CSS。受 settings.theme_version 控制。"""
    try:
        from config import load_settings
        settings = load_settings()
    except Exception:
        settings = {}

    if settings.get("theme_version", "default") == "classic":
        return  # 用户切回原生 UI

    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


# ----------------- 头部横幅（方案 B） -----------------
def hero(title: str, subtitle: str = "", stats: list = None):
    """渲染渐变 Hero 横幅。

    参数：
        title:    主标题
        subtitle: 副标题（说明文字）
        stats:    可选的关键指标列表 [{"value": "12", "label": "题目数"}]
    """
    try:
        from config import load_settings
        settings = load_settings()
    except Exception:
        settings = {}
    if settings.get("theme_version", "default") == "classic":
        # 经典模式下用普通的标题
        st.subheader(title)
        if subtitle:
            st.caption(subtitle)
        return

    stats_html = ""
    if stats:
        items = []
        for s in stats:
            items.append(
                f'<div class="hero-stat"><div class="hero-stat-value">{s.get("value", "")}</div>'
                f'<div class="hero-stat-label">{s.get("label", "")}</div></div>'
            )
        stats_html = f'<div class="hero-stats">{"".join(items)}</div>'

    sub_html = f'<p>{subtitle}</p>' if subtitle else ""
    html = (
        f'<div class="hero-banner">'
        f'<h2>{title}</h2>'
        f'{sub_html}'
        f'{stats_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ----------------- 侧边栏 logo（方案 B） -----------------
def sidebar_logo():
    """渲染侧边栏顶部的 logo 区。"""
    try:
        from config import load_settings
        settings = load_settings()
    except Exception:
        settings = {}
    if settings.get("theme_version", "default") == "classic":
        st.title("SQL 随身教练")
        return

    st.markdown(
        '<div class="sidebar-logo">'
        '<div class="sidebar-logo-icon">SQL</div>'
        '<div class="sidebar-logo-text">'
        '<div class="sidebar-logo-title">SQL 随身教练</div>'
        '<div class="sidebar-logo-sub">大模型驱动的学习系统</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ----------------- 进度卡片（方案 B） -----------------
def progress_card(label: str, current: int, total: int, suffix: str = ""):
    """渲染一个带进度条的卡片，给侧边栏的"学习进度"用。"""
    try:
        from config import load_settings
        settings = load_settings()
    except Exception:
        settings = {}
    if settings.get("theme_version", "default") == "classic":
        st.metric(label, f"{current} / {total}" if total else current)
        return

    pct = (current / total * 100) if total > 0 else 0
    st.markdown(
        '<div class="progress-card">'
        f'<div class="progress-card-header"><span>{label}</span>'
        f'<span><strong>{current}</strong>{suffix}</span></div>'
        f'<div class="progress-card-bar"><div class="progress-card-fill" style="width: {pct}%"></div></div>'
        '</div>',
        unsafe_allow_html=True,
    )
