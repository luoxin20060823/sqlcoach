"""全局样式与组件 — 深色主题版。

设计要点：
- 深色背景 (#0f172a / #1e293b)
- 强调色蓝紫渐变 (#818cf8 → #38bdf8)
- 卡片用 #1e293b 底 + 微妙边框
- 受 settings.theme_version 控制：default / classic
"""
import streamlit as st


# ----------------- 全局 CSS -----------------
_GLOBAL_CSS = """
<style>
/* === 全局排版 === */
.stApp {
    font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.block-container {
    padding-top: 4.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px;
}

/* Streamlit 顶部 header 透明化，避免挡住控制栏 */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3rem;
}

h1, h2, h3 {
    letter-spacing: -0.01em;
    color: #f1f5f9;
}

/* === 按钮 === */
.stButton > button {
    border-radius: 8px !important;
    border: 1px solid #334155;
    transition: all .15s ease;
    font-weight: 500;
    background: #1e293b;
    color: #f1f5f9;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(129, 140, 248, 0.2);
    border-color: #818cf8;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #818cf8);
    border: none;
    color: white;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
    background: linear-gradient(135deg, #4f46e5, #6366f1);
}

/* === 输入框 === */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input {
    border-radius: 8px !important;
    border-color: #334155 !important;
    background: #0f172a !important;
    color: #f1f5f9 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.15) !important;
}

/* === metric === */
[data-testid="stMetric"] {
    background: #1e293b;
    padding: 14px 18px;
    border-radius: 12px;
    border: 1px solid #334155;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #818cf8, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
[data-testid="stMetricLabel"] {
    font-weight: 500 !important;
    color: #94a3b8 !important;
}

/* === Tab 标签栏 === */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    height: 44px;
    background: transparent;
    border-radius: 8px 8px 0 0;
    padding: 0 18px;
    font-weight: 500;
    color: #94a3b8;
    transition: all .15s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #818cf8;
    background: rgba(129, 140, 248, 0.08);
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #818cf8;
    background: rgba(129, 140, 248, 0.1);
    border-bottom: 2px solid #818cf8;
}

/* === 表格 === */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #334155;
}

/* === Expander === */
.streamlit-expanderHeader, [data-testid="stExpander"] > details > summary {
    border-radius: 8px !important;
    background: #1e293b;
}

/* === Alert === */
[data-testid="stAlert"] {
    border-radius: 10px;
    border-left-width: 4px;
}

/* === Hero 横幅 === */
.hero-banner {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
    border-radius: 16px;
    padding: 22px 28px;
    margin-bottom: 22px;
    color: white;
    box-shadow: 0 4px 20px rgba(79, 70, 229, 0.25);
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
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-banner h2 {
    color: white !important;
    margin: 0 !important;
    font-size: 1.5rem !important;
    font-weight: 700;
    position: relative;
    z-index: 1;
}
.hero-banner p {
    color: rgba(255,255,255,0.8);
    margin: 6px 0 0 0;
    font-size: 0.9rem;
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
    font-size: 1.4rem;
    font-weight: 700;
    line-height: 1;
}
.hero-banner .hero-stat-label {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.7);
    margin-top: 2px;
}

/* === 题目卡 === */
.question-card {
    position: relative;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px 22px 18px 26px;
    margin: 12px 0 18px 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    overflow: hidden;
}
.question-card::before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #818cf8, #38bdf8);
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
    color: #e2e8f0;
    border-left: 3px solid #818cf8;
    background: #0f172a;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    margin: 0;
}

/* === chip 标签 === */
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
.chip-difficulty-easy { background: #064e3b; color: #6ee7b7; }
.chip-difficulty-medium { background: #78350f; color: #fcd34d; }
.chip-difficulty-hard { background: #7f1d1d; color: #fca5a5; }
.chip-knowledge { background: #312e81; color: #a5b4fc; }
.chip-type { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }

/* === 判题横幅 === */
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
.verdict-banner-text { flex: 1; }
.verdict-banner-title { font-weight: 700; font-size: 1.05rem; margin-bottom: 2px; }
.verdict-banner-sub { font-size: 0.85rem; color: #94a3b8; line-height: 1.4; }

.verdict-correct { background: #064e3b; border-left-color: #10b981; }
.verdict-correct .verdict-banner-icon { background: #10b981; }
.verdict-correct .verdict-banner-title { color: #6ee7b7; }

.verdict-wrong { background: #450a0a; border-left-color: #ef4444; }
.verdict-wrong .verdict-banner-icon { background: #ef4444; }
.verdict-wrong .verdict-banner-title { color: #fca5a5; }

.verdict-flawed { background: #451a03; border-left-color: #f59e0b; }
.verdict-flawed .verdict-banner-icon { background: #f59e0b; }
.verdict-flawed .verdict-banner-title { color: #fcd34d; }

.verdict-skipped { background: #1e1b4b; border-left-color: #6366f1; }
.verdict-skipped .verdict-banner-icon { background: #6366f1; }
.verdict-skipped .verdict-banner-title { color: #a5b4fc; }

/* === 空状态 === */
.empty-state {
    text-align: center;
    padding: 48px 16px;
    background: #1e293b;
    border: 1px dashed #475569;
    border-radius: 14px;
    margin: 20px 0;
}
.empty-state-svg { margin: 0 auto 16px auto; display: block; }
.empty-state-title { font-size: 1.05rem; font-weight: 600; color: #e2e8f0; margin: 0 0 6px 0; }
.empty-state-desc { color: #94a3b8; font-size: 0.9rem; margin: 0; line-height: 1.5; }

/* === 进度卡 === */
.progress-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 12px;
}
.progress-card-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    font-size: 0.85rem;
    color: #94a3b8;
}
.progress-card-bar {
    height: 6px;
    background: #334155;
    border-radius: 3px;
    overflow: hidden;
}
.progress-card-fill {
    height: 100%;
    background: linear-gradient(90deg, #6366f1, #38bdf8);
    transition: width .4s ease;
}

/* === 顶部控制栏 === */
.top-bar {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 16px;
}

/* === 隐藏侧边栏 === */
section[data-testid="stSidebar"] {
    display: none !important;
}
</style>
"""


def inject_global_styles():
    """注入全局 CSS。"""
    try:
        from config import load_settings
        settings = load_settings()
    except Exception:
        settings = {}
    if settings.get("theme_version", "default") == "classic":
        return
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


# ----------------- Hero 横幅 -----------------
def hero(title: str, subtitle: str = "", stats: list = None):
    try:
        from config import load_settings
        settings = load_settings()
    except Exception:
        settings = {}
    if settings.get("theme_version", "default") == "classic":
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


# ----------------- 进度卡 -----------------
def progress_card(label: str, current: int, total: int, suffix: str = ""):
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


# ----------------- 题目卡 / 判题横幅 / 空状态 -----------------
_DIFF_LABELS = {"easy": "初级", "medium": "中级", "hard": "高级"}


def _is_classic() -> bool:
    try:
        from config import load_settings
        return load_settings().get("theme_version", "default") == "classic"
    except Exception:
        return False


def _esc(text: str) -> str:
    if text is None:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def question_card(question: str, difficulty: str = "",
                  question_type_label: str = "", knowledge_point: str = ""):
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
        chips.append(f'<span class="chip chip-difficulty-{difficulty}">{_DIFF_LABELS.get(difficulty, difficulty)}</span>')
    if knowledge_point:
        chips.append(f'<span class="chip chip-knowledge">{_esc(knowledge_point)}</span>')
    if question_type_label:
        chips.append(f'<span class="chip chip-type">{_esc(question_type_label)}</span>')

    chips_html = f'<div class="question-card-meta">{"".join(chips)}</div>' if chips else ""
    st.markdown(
        '<div class="question-card">'
        f'{chips_html}'
        f'<p class="question-card-text">{_esc(question)}</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def verdict_banner(verdict: str, analysis: str = "", suggestion: str = ""):
    titles = {"correct": "正确", "wrong": "错误", "flawed": "结果对但逻辑有瑕疵", "skipped": "已查看答案"}
    icons = {"correct": "✓", "wrong": "✕", "flawed": "!", "skipped": "?"}
    klass = {"correct": "verdict-correct", "wrong": "verdict-wrong",
             "flawed": "verdict-flawed", "skipped": "verdict-skipped"}.get(verdict, "verdict-skipped")

    if _is_classic():
        st.markdown(f"## {titles.get(verdict, verdict)}")
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
    sub_html = f'<div class="verdict-banner-sub">{"<br>".join(sub_parts)}</div>' if sub_parts else ""
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


# SVG 空状态
_SVG = {
    "database": '<svg class="empty-state-svg" width="100" height="100" viewBox="0 0 120 120" fill="none"><ellipse cx="60" cy="32" rx="36" ry="12" stroke="url(#dbg)" stroke-width="3" fill="#1e293b"/><path d="M24 32v28c0 6.6 16.1 12 36 12s36-5.4 36-12V32" stroke="url(#dbg)" stroke-width="3" fill="#1e293b" fill-opacity="0.6"/><path d="M24 60v28c0 6.6 16.1 12 36 12s36-5.4 36-12V60" stroke="url(#dbg)" stroke-width="3" fill="#1e293b" fill-opacity="0.4"/><defs><linearGradient id="dbg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#818cf8"/><stop offset="1" stop-color="#38bdf8"/></linearGradient></defs></svg>',
    "trophy": '<svg class="empty-state-svg" width="100" height="100" viewBox="0 0 120 120" fill="none"><path d="M30 22h60v18c0 16.6-13.4 30-30 30s-30-13.4-30-30V22z" fill="#1e293b" stroke="url(#tg)" stroke-width="3"/><rect x="48" y="80" width="24" height="6" fill="url(#tg)"/><rect x="38" y="86" width="44" height="10" rx="3" fill="url(#tg)"/><defs><linearGradient id="tg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#f59e0b"/><stop offset="1" stop-color="#ef4444"/></linearGradient></defs></svg>',
    "checkmark": '<svg class="empty-state-svg" width="100" height="100" viewBox="0 0 120 120" fill="none"><circle cx="60" cy="60" r="45" fill="#064e3b" stroke="url(#ckg)" stroke-width="3"/><path d="M40 62l14 14 28-32" stroke="url(#ckg)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"/><defs><linearGradient id="ckg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#10b981"/><stop offset="1" stop-color="#38bdf8"/></linearGradient></defs></svg>',
    "chat": '<svg class="empty-state-svg" width="100" height="100" viewBox="0 0 120 120" fill="none"><rect x="14" y="22" width="70" height="52" rx="10" fill="#1e293b" stroke="url(#cg)" stroke-width="3"/><path d="M30 78l-6 14 18-14" fill="#1e293b" stroke="url(#cg)" stroke-width="3" stroke-linejoin="round"/><rect x="36" y="46" width="60" height="44" rx="10" fill="#0f172a" stroke="url(#cg)" stroke-width="3"/><defs><linearGradient id="cg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#818cf8"/><stop offset="1" stop-color="#38bdf8"/></linearGradient></defs></svg>',
    "chart": '<svg class="empty-state-svg" width="100" height="100" viewBox="0 0 120 120" fill="none"><rect x="14" y="20" width="92" height="80" rx="8" fill="#1e293b" stroke="url(#chg)" stroke-width="3"/><rect x="28" y="64" width="14" height="22" rx="3" fill="url(#chg)"/><rect x="50" y="48" width="14" height="38" rx="3" fill="url(#chg)" fill-opacity="0.7"/><rect x="72" y="34" width="14" height="52" rx="3" fill="url(#chg)" fill-opacity="0.5"/><defs><linearGradient id="chg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#818cf8"/><stop offset="1" stop-color="#38bdf8"/></linearGradient></defs></svg>',
    "exam": '<svg class="empty-state-svg" width="100" height="100" viewBox="0 0 120 120" fill="none"><rect x="22" y="14" width="68" height="92" rx="8" fill="#1e293b" stroke="url(#eg)" stroke-width="3"/><rect x="34" y="30" width="44" height="6" rx="2" fill="#334155"/><rect x="34" y="46" width="44" height="6" rx="2" fill="#334155"/><rect x="34" y="62" width="30" height="6" rx="2" fill="#334155"/><circle cx="92" cy="86" r="18" fill="#312e81" stroke="url(#eg)" stroke-width="3"/><text x="92" y="92" text-anchor="middle" font-size="18" font-weight="800" fill="#a5b4fc">A</text><defs><linearGradient id="eg" x1="0" y1="0" x2="120" y2="120"><stop stop-color="#818cf8"/><stop offset="1" stop-color="#38bdf8"/></linearGradient></defs></svg>',
}


def empty_state(kind: str, title: str, desc: str = ""):
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


# sidebar_logo 不再需要（侧边栏已移除），保留空函数兼容
def sidebar_logo():
    pass
