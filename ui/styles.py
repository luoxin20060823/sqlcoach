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

/* === 题目卡（方案 F） === */
.question-card {
    position: relative;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px 22px 18px 26px;
    margin: 12px 0 18px 0;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    overflow: hidden;
}
.question-card::before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #2563eb, #7c3aed);
}
.question-card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
}
.question-card-text {
    font-size: 1.0rem;
    line-height: 1.6;
    color: #0f172a;
    border-left: 3px solid #2563eb;
    background: #f8fafc;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    margin: 0;
}

/* === 状态药丸 chip === */
.chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1.4;
}
.chip-difficulty-easy {
    background: #d1fae5; color: #047857;
}
.chip-difficulty-medium {
    background: #fef3c7; color: #b45309;
}
.chip-difficulty-hard {
    background: #fee2e2; color: #b91c1c;
}
.chip-knowledge {
    background: #e0e7ff; color: #4338ca;
}
.chip-type {
    background: #f1f5f9; color: #475569;
}

/* === 判题结果卡（方案 F） === */
.verdict-banner {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 20px;
    border-radius: 12px;
    border-left: 5px solid;
    margin: 14px 0;
}
.verdict-banner-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    font-weight: 900;
    color: white;
    flex-shrink: 0;
}
.verdict-banner-text {
    flex: 1;
}
.verdict-banner-title {
    font-weight: 700;
    font-size: 1.05rem;
    margin-bottom: 2px;
}
.verdict-banner-sub {
    font-size: 0.85rem;
    color: #475569;
    line-height: 1.4;
}
.verdict-correct {
    background: linear-gradient(90deg, #d1fae5, #ecfdf5);
    border-left-color: #10b981;
}
.verdict-correct .verdict-banner-icon { background: #10b981; }
.verdict-correct .verdict-banner-title { color: #047857; }

.verdict-wrong {
    background: linear-gradient(90deg, #fee2e2, #fef2f2);
    border-left-color: #ef4444;
}
.verdict-wrong .verdict-banner-icon { background: #ef4444; }
.verdict-wrong .verdict-banner-title { color: #b91c1c; }

.verdict-flawed {
    background: linear-gradient(90deg, #fef3c7, #fffbeb);
    border-left-color: #f59e0b;
}
.verdict-flawed .verdict-banner-icon { background: #f59e0b; }
.verdict-flawed .verdict-banner-title { color: #b45309; }

.verdict-skipped {
    background: linear-gradient(90deg, #e0e7ff, #eef2ff);
    border-left-color: #6366f1;
}
.verdict-skipped .verdict-banner-icon { background: #6366f1; }
.verdict-skipped .verdict-banner-title { color: #4338ca; }

/* === 空状态插图（方案 K） === */
.empty-state {
    text-align: center;
    padding: 48px 16px;
    background: white;
    border: 1px dashed #cbd5e1;
    border-radius: 14px;
    margin: 20px 0;
}
.empty-state-svg {
    margin: 0 auto 16px auto;
    display: block;
}
.empty-state-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #334155;
    margin: 0 0 6px 0;
}
.empty-state-desc {
    color: #64748b;
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.5;
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


# ----------------- 题目卡 / 判题横幅（方案 F） -----------------

_DIFF_LABELS = {"easy": "初级", "medium": "中级", "hard": "高级"}


def _is_classic() -> bool:
    try:
        from config import load_settings
        return load_settings().get("theme_version", "default") == "classic"
    except Exception:
        return False


def _esc(text: str) -> str:
    """轻量 HTML 转义，避免题目里 < > & 串到样式里。"""
    if text is None:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def question_card(question: str, difficulty: str = "",
                  question_type_label: str = "",
                  knowledge_point: str = ""):
    """渲染当前题目的卡片：标签 chip + 题目正文。"""
    if _is_classic():
        if difficulty:
            st.markdown(f"**难度**: {_DIFF_LABELS.get(difficulty, difficulty)}")
        if question_type_label:
            st.markdown(f"**类型**: {question_type_label}")
        if knowledge_point:
            st.markdown(f"**知识点**: {knowledge_point}")
        st.markdown(f"> {question}")
        return

    chips = []
    if difficulty:
        diff_cls = f"chip-difficulty-{difficulty}"
        chips.append(
            f'<span class="chip {diff_cls}">{_DIFF_LABELS.get(difficulty, difficulty)}</span>'
        )
    if knowledge_point:
        chips.append(f'<span class="chip chip-knowledge">{_esc(knowledge_point)}</span>')
    if question_type_label:
        chips.append(f'<span class="chip chip-type">{_esc(question_type_label)}</span>')

    chips_html = (
        f'<div class="question-card-meta">{"".join(chips)}</div>'
        if chips else ""
    )
    st.markdown(
        '<div class="question-card">'
        f'{chips_html}'
        f'<p class="question-card-text">{_esc(question)}</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def verdict_banner(verdict: str, analysis: str = "", suggestion: str = ""):
    """渲染判题结果横幅。verdict ∈ correct/wrong/flawed/skipped。"""
    titles = {
        "correct": "正确",
        "wrong": "错误",
        "flawed": "结果对但逻辑有瑕疵",
        "skipped": "已查看答案",
    }
    icons = {"correct": "✓", "wrong": "✕", "flawed": "!", "skipped": "?"}
    klass = {
        "correct": "verdict-correct",
        "wrong": "verdict-wrong",
        "flawed": "verdict-flawed",
        "skipped": "verdict-skipped",
    }.get(verdict, "verdict-skipped")

    if _is_classic():
        labels = {"correct": "正确", "wrong": "错误",
                  "flawed": "结果正确但逻辑有瑕疵", "skipped": "已查看答案"}
        st.markdown(f"## {labels.get(verdict, verdict)}")
        if analysis:
            st.markdown(f"**分析**: {analysis}")
        if suggestion:
            st.markdown(f"**建议**: {suggestion}")
        return

    title = titles.get(verdict, verdict)
    icon = icons.get(verdict, "i")
    sub_parts = []
    if analysis:
        sub_parts.append(_esc(analysis).replace("\n", "<br>"))
    if suggestion:
        sub_parts.append(f"<strong>建议</strong>：{_esc(suggestion)}")
    sub_html = (
        f'<div class="verdict-banner-sub">{"<br>".join(sub_parts)}</div>'
        if sub_parts else ""
    )
    st.markdown(
        f'<div class="verdict-banner {klass}">'
        f'<div class="verdict-banner-icon">{icon}</div>'
        f'<div class="verdict-banner-text">'
        f'<div class="verdict-banner-title">{title}</div>'
        f'{sub_html}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ----------------- 空状态插图（方案 K） -----------------

# 各种空状态的 SVG（纯内联，无外部资源依赖）
_SVG = {
    "database": """<svg class="empty-state-svg" width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="60" cy="32" rx="36" ry="12" stroke="url(#dbg)" stroke-width="3" fill="#eff6ff"/>
<path d="M24 32v28c0 6.6 16.1 12 36 12s36-5.4 36-12V32" stroke="url(#dbg)" stroke-width="3" fill="#eff6ff" fill-opacity="0.6"/>
<path d="M24 60v28c0 6.6 16.1 12 36 12s36-5.4 36-12V60" stroke="url(#dbg)" stroke-width="3" fill="#eff6ff" fill-opacity="0.4"/>
<defs><linearGradient id="dbg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#2563eb"/><stop offset="1" stop-color="#7c3aed"/></linearGradient></defs>
</svg>""",
    "trophy": """<svg class="empty-state-svg" width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M30 22h60v18c0 16.6-13.4 30-30 30s-30-13.4-30-30V22z" fill="#fef3c7" stroke="url(#tg)" stroke-width="3"/>
<path d="M30 30h-8c-4.4 0-8 3.6-8 8 0 8 6 14 14 14M90 30h8c4.4 0 8 3.6 8 8 0 8-6 14-14 14" stroke="url(#tg)" stroke-width="3" fill="none"/>
<rect x="48" y="80" width="24" height="6" fill="url(#tg)"/>
<rect x="38" y="86" width="44" height="10" rx="3" fill="url(#tg)"/>
<defs><linearGradient id="tg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#f59e0b"/><stop offset="1" stop-color="#dc2626"/></linearGradient></defs>
</svg>""",
    "checkmark": """<svg class="empty-state-svg" width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="60" cy="60" r="45" fill="#d1fae5" stroke="url(#ckg)" stroke-width="3"/>
<path d="M40 62l14 14 28-32" stroke="url(#ckg)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
<defs><linearGradient id="ckg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#10b981"/><stop offset="1" stop-color="#2563eb"/></linearGradient></defs>
</svg>""",
    "chat": """<svg class="empty-state-svg" width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect x="14" y="22" width="70" height="52" rx="10" fill="#eff6ff" stroke="url(#cg)" stroke-width="3"/>
<path d="M30 78l-6 14 18-14" fill="#eff6ff" stroke="url(#cg)" stroke-width="3" stroke-linejoin="round"/>
<rect x="36" y="46" width="60" height="44" rx="10" fill="white" stroke="url(#cg)" stroke-width="3"/>
<path d="M76 90l4 14-14-14" fill="white" stroke="url(#cg)" stroke-width="3" stroke-linejoin="round"/>
<defs><linearGradient id="cg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#2563eb"/><stop offset="1" stop-color="#7c3aed"/></linearGradient></defs>
</svg>""",
    "chart": """<svg class="empty-state-svg" width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect x="14" y="20" width="92" height="80" rx="8" fill="#eff6ff" stroke="url(#chg)" stroke-width="3"/>
<rect x="28" y="64" width="14" height="22" rx="3" fill="url(#chg)"/>
<rect x="50" y="48" width="14" height="38" rx="3" fill="url(#chg)" fill-opacity="0.7"/>
<rect x="72" y="34" width="14" height="52" rx="3" fill="url(#chg)" fill-opacity="0.5"/>
<defs><linearGradient id="chg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#2563eb"/><stop offset="1" stop-color="#7c3aed"/></linearGradient></defs>
</svg>""",
    "exam": """<svg class="empty-state-svg" width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect x="22" y="14" width="68" height="92" rx="8" fill="white" stroke="url(#eg)" stroke-width="3"/>
<rect x="34" y="30" width="44" height="6" rx="2" fill="#e0e7ff"/>
<rect x="34" y="46" width="44" height="6" rx="2" fill="#e0e7ff"/>
<rect x="34" y="62" width="30" height="6" rx="2" fill="#e0e7ff"/>
<circle cx="92" cy="86" r="18" fill="#fef3c7" stroke="url(#eg)" stroke-width="3"/>
<text x="92" y="92" text-anchor="middle" font-size="18" font-weight="800" fill="#b45309">A</text>
<defs><linearGradient id="eg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#2563eb"/><stop offset="1" stop-color="#7c3aed"/></linearGradient></defs>
</svg>""",
}


def empty_state(kind: str, title: str, desc: str = ""):
    """渲染带 SVG 插图的空状态。

    kind: database / trophy / checkmark / chat / chart / exam
    """
    if _is_classic():
        st.info(f"{title}{(' — ' + desc) if desc else ''}")
        return

    svg = _SVG.get(kind, _SVG["database"])
    desc_html = f'<p class="empty-state-desc">{_esc(desc)}</p>' if desc else ""
    st.markdown(
        f'<div class="empty-state">{svg}'
        f'<p class="empty-state-title">{_esc(title)}</p>'
        f'{desc_html}'
        f'</div>',
        unsafe_allow_html=True,
    )
