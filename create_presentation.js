/**
 * SQL 随身教练 — 课程项目汇报 PPT
 * 时长：约 10 分钟
 * 结构：1 封面 + 2 项目介绍 + 1 总览 + 7 功能展示 + 1 性能 + 1 指标 + 1 总结
 *
 * 运行：node create_presentation.js
 * 输出：SQL随身教练-汇报.pptx
 */

const pptx = require("pptxgenjs");
const pres = new pptx();
pres.layout = "LAYOUT_16x9";
pres.author = "SQL 随身教练";
pres.title = "SQL 随身教练 项目汇报";

// ===== 颜色与字体 =====
const C = {
  darkBg:    "0F172A",
  darkBg2:   "1E293B",
  darkBg3:   "334155",
  accent:    "38BDF8",
  accent2:   "818CF8",
  green:     "34D399",
  amber:     "FBBF24",
  red:       "F87171",
  pink:      "F472B6",
  textLight: "F1F5F9",
  textMuted: "94A3B8",
  textDark:  "1E293B",
  lightBg:   "F8FAFC",
  lightCard: "FFFFFF",
  border:    "E2E8F0",
  blue50:    "EFF6FF",
  blue100:   "DBEAFE",
  blue600:   "2563EB",
  blue700:   "1D4ED8",
  purple50:  "F5F3FF",
  purple600: "7C3AED",
  green50:   "F0FDF4",
  green600:  "059669",
  amber50:   "FFFBEB",
  amber600:  "D97706",
  red50:     "FEF2F2",
  red600:    "DC2626",
  cyan50:    "ECFEFF",
  cyan600:   "0891B2",
  indigo50:  "EEF2FF",
  indigo600: "4F46E5",
  pink50:    "FDF2F8",
  pink600:   "DB2777",
};

const FONT_TITLE = "Arial Black";
const FONT_BODY  = "Microsoft YaHei";
const FONT_MONO  = "Consolas";

const shadow = () => ({
  type: "outer", blur: 8, offset: 2, angle: 90, color: "000000", opacity: 0.10,
});

// ===== 通用 slide 工厂 =====
function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: C.darkBg };
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent },
  });
  return s;
}

function lightSlide(title, subtitle) {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.05, fill: { color: C.accent },
  });
  s.addText(title, {
    x: 0.6, y: 0.22, w: 8.8, h: 0.6,
    fontSize: 26, fontFace: FONT_TITLE, color: C.textDark, bold: true, margin: 0,
  });
  if (subtitle) {
    s.addText(subtitle, {
      x: 0.6, y: 0.78, w: 8.8, h: 0.32,
      fontSize: 13, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  }
  s.addShape(pres.shapes.LINE, {
    x: 0.6, y: 1.12, w: 1.0, h: 0,
    line: { color: C.accent, width: 3 },
  });
  return s;
}

function darkTitled(s, title, subtitle) {
  s.addText(title, {
    x: 0.6, y: 0.25, w: 8.8, h: 0.6,
    fontSize: 28, fontFace: FONT_TITLE, color: C.textLight, bold: true, margin: 0,
  });
  if (subtitle) {
    s.addText(subtitle, {
      x: 0.6, y: 0.82, w: 8.8, h: 0.3,
      fontSize: 12, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  }
  s.addShape(pres.shapes.LINE, {
    x: 0.6, y: 1.15, w: 1.0, h: 0,
    line: { color: C.accent, width: 3 },
  });
}

function pageNumber(s, n, total) {
  s.addText(`${n} / ${total}`, {
    x: 9.0, y: 5.30, w: 0.9, h: 0.3,
    fontSize: 10, fontFace: FONT_BODY, color: C.textMuted,
    align: "right", margin: 0,
  });
}

const TOTAL = 14;

// ============================================================
// SLIDE 1: 封面
// ============================================================
(function () {
  const s = pres.addSlide();
  s.background = { color: C.darkBg };

  s.addShape(pres.shapes.OVAL, {
    x: 7.5, y: -1.5, w: 5, h: 5, fill: { color: C.accent, transparency: 90 },
  });
  s.addShape(pres.shapes.OVAL, {
    x: -1.5, y: 3, w: 4, h: 4, fill: { color: C.accent2, transparency: 90 },
  });
  s.addShape(pres.shapes.OVAL, {
    x: 6, y: 4.2, w: 2.5, h: 2.5, fill: { color: C.green, transparency: 92 },
  });

  s.addText("SQL 随身教练", {
    x: 0.8, y: 1.4, w: 8.4, h: 1.2,
    fontSize: 60, fontFace: FONT_TITLE, color: C.textLight, bold: true, margin: 0,
  });
  s.addText("基于大模型 Agent 的 SQL 辅助学习系统", {
    x: 0.8, y: 2.65, w: 8.4, h: 0.6,
    fontSize: 22, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
  });

  const tags = ["数据库课程项目", "完整闭环 · 性能优化", "在线可访问"];
  tags.forEach((t, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.8 + i * 2.7, y: 3.55, w: 2.5, h: 0.45,
      fill: { color: C.darkBg2 },
    });
    s.addText(t, {
      x: 0.8 + i * 2.7, y: 3.55, w: 2.5, h: 0.45,
      fontSize: 13, fontFace: FONT_BODY, color: C.accent,
      align: "center", valign: "middle", margin: 0,
    });
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 4.95, w: 10, h: 0.675, fill: { color: C.darkBg2 },
  });
  s.addText("Python + Streamlit + SQLite + DeepSeek API   |   GitHub: luoxin20060823/sqlcoach", {
    x: 0.6, y: 5.05, w: 8.8, h: 0.5,
    fontSize: 12, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
  });
})();

// ============================================================
// SLIDE 2: 项目背景
// ============================================================
(function () {
  const s = lightSlide("项目背景与目标", "为什么要做这个系统");

  // 痛点（左）
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.4, w: 4.3, h: 1.9,
    fill: { color: C.red50 }, shadow: shadow(),
  });
  s.addText("学习痛点", {
    x: 0.85, y: 1.5, w: 4.0, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.red600, bold: true, margin: 0,
  });
  s.addText([
    { text: "教科书例子单一，数据库切换成本高\n", options: { bullet: true } },
    { text: "在线判题平台需准备好 SQL 题库\n", options: { bullet: true } },
    { text: "做错的题缺乏针对性深入解析\n", options: { bullet: true } },
    { text: "缺少限时考试场景训练实战能力", options: { bullet: true } },
  ], {
    x: 0.85, y: 1.95, w: 4.0, h: 1.3,
    fontSize: 12, fontFace: FONT_BODY, color: C.textDark, paraSpaceAfter: 2,
  });

  // 解决方案（右）
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.4, w: 4.3, h: 1.9,
    fill: { color: C.green50 }, shadow: shadow(),
  });
  s.addText("我们的方案", {
    x: 5.35, y: 1.5, w: 4.0, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.green600, bold: true, margin: 0,
  });
  s.addText([
    { text: "LLM Agent 实时生成 schema、题目、解析\n", options: { bullet: true } },
    { text: "三层判题 + 结构化错题解析\n", options: { bullet: true } },
    { text: "练习 / 考试 / 复习 多场景覆盖\n", options: { bullet: true } },
    { text: "学习数据可视化 + 智能建议", options: { bullet: true } },
  ], {
    x: 5.35, y: 1.95, w: 4.0, h: 1.3,
    fontSize: 12, fontFace: FONT_BODY, color: C.textDark, paraSpaceAfter: 2,
  });

  // 设计目标
  s.addText("设计目标", {
    x: 0.6, y: 3.55, w: 8.8, h: 0.4,
    fontSize: 18, fontFace: FONT_TITLE, color: C.textDark, bold: true, margin: 0,
  });
  const goals = [
    { num: "01", title: "完整闭环", desc: "建库→出题→答题→判题→\n解析→分析→推荐难度", color: C.blue600 },
    { num: "02", title: "AI 驱动", desc: "Schema、题目、解析、\n学习分析全部 LLM 生成", color: C.purple600 },
    { num: "03", title: "高性能", desc: "并发、缓存、预取，\n90% 操作秒级响应", color: C.green600 },
    { num: "04", title: "易上手", desc: "Web 直接打开\n无需安装、无需注册", color: C.amber600 },
  ];
  goals.forEach((g, i) => {
    const x = 0.6 + i * 2.2;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 4.0, w: 2.05, h: 1.4,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addText(g.num, {
      x: x + 0.15, y: 4.10, w: 0.7, h: 0.35,
      fontSize: 14, fontFace: FONT_TITLE, color: g.color, bold: true, margin: 0,
    });
    s.addText(g.title, {
      x: x + 0.15, y: 4.45, w: 1.85, h: 0.3,
      fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
    });
    s.addText(g.desc, {
      x: x + 0.15, y: 4.80, w: 1.85, h: 0.55,
      fontSize: 9.5, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  });

  pageNumber(s, 2, TOTAL);
})();

// ============================================================
// SLIDE 3: 系统架构与技术栈
// ============================================================
(function () {
  const s = lightSlide("系统架构与技术栈", "5 层架构 · 单一外部依赖（LLM API）");

  const layers = [
    { label: "前端展示层 — Streamlit Web UI",        desc: "6 大功能 Tab · 自定义 CSS 主题 · streamlit-ace SQL 编辑器", color: C.accent2,  y: 1.4  },
    { label: "Agent 引擎层 — Python",                desc: "SchemaGen · QuestionGen · JudgeEngine · Tutor · Analyzer", color: C.blue600,  y: 2.15 },
    { label: "调度层 — LLMClient",                   desc: "OpenAI 兼容协议 · 并发批量 · JSON Mode · 失败回退",         color: C.green600, y: 2.90 },
    { label: "数据层 — SQLite",                      desc: "题库 / 答题历史 / Schema 缓存 / 考试记录",                color: C.amber600, y: 3.65 },
    { label: "外部模型 — DeepSeek API",              desc: "deepseek-chat（V3）— 单模型驱动全部 Agent 调用",           color: C.pink600,  y: 4.40 },
  ];

  layers.forEach((layer) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.9, y: layer.y, w: 8.2, h: 0.6,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.9, y: layer.y, w: 0.08, h: 0.6, fill: { color: layer.color },
    });
    s.addText(layer.label, {
      x: 1.2, y: layer.y + 0.04, w: 4.5, h: 0.3,
      fontSize: 13, fontFace: FONT_BODY, color: layer.color, bold: true, margin: 0,
    });
    s.addText(layer.desc, {
      x: 1.2, y: layer.y + 0.30, w: 7.7, h: 0.28,
      fontSize: 10.5, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  });
  for (let i = 0; i < layers.length - 1; i++) {
    s.addText("V", {
      x: 4.8, y: layers[i].y + 0.62, w: 0.4, h: 0.15,
      fontSize: 10, color: C.textMuted, align: "center", margin: 0,
    });
  }

  pageNumber(s, 3, TOTAL);
})();

// ============================================================
// SLIDE 4: 六大功能总览
// ============================================================
(function () {
  const s = lightSlide("六大功能总览", "覆盖完整的 SQL 学习闭环");

  const tabs = [
    { title: "练习",      desc: "AI 出题\n判题与解析",     color: C.blue600,   bg: C.blue50    },
    { title: "考试模式",  desc: "限时多题\n按难度计分",     color: C.purple600, bg: C.purple50  },
    { title: "分析报告",  desc: "雷达图 / 趋势\nAI 建议",   color: C.cyan600,   bg: C.cyan50    },
    { title: "数据浏览",  desc: "Schema\n表数据预览",       color: C.green600,  bg: C.green50   },
    { title: "错题复习",  desc: "错题集中\n反复练习",       color: C.amber600,  bg: C.amber50   },
    { title: "自由答疑",  desc: "多轮对话\nAI 助教",        color: C.red600,    bg: C.red50     },
  ];

  // 2 × 3 网格
  const cellW = 2.85, cellH = 1.85, hGap = 0.15, vGap = 0.2;
  const startX = (10 - 3 * cellW - 2 * hGap) / 2;
  tabs.forEach((tab, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = startX + col * (cellW + hGap);
    const y = 1.5 + row * (cellH + vGap);
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: cellW, h: cellH,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: cellW, h: 0.06, fill: { color: tab.color },
    });
    // 圆形标号
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.2, y: y + 0.25, w: 0.4, h: 0.4, fill: { color: tab.bg },
    });
    s.addText(String(i + 1), {
      x: x + 0.2, y: y + 0.25, w: 0.4, h: 0.4,
      fontSize: 16, fontFace: FONT_TITLE, color: tab.color, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(tab.title, {
      x: x + 0.7, y: y + 0.3, w: cellW - 0.8, h: 0.4,
      fontSize: 18, fontFace: FONT_BODY, color: tab.color, bold: true, margin: 0,
    });
    s.addText(tab.desc, {
      x: x + 0.25, y: y + 0.85, w: cellW - 0.4, h: 0.85,
      fontSize: 11, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  });

  // 底部一句话
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 5.0, w: 8.8, h: 0.45, fill: { color: C.blue50 },
  });
  s.addText(
    "学习闭环：建库 → 出题 → 答题 → 判题 → 解析 → 分析 → 推荐难度 → 出题",
    {
      x: 0.6, y: 5.0, w: 8.8, h: 0.45,
      fontSize: 12.5, fontFace: FONT_BODY, color: C.blue700,
      align: "center", valign: "middle", margin: 0,
    }
  );

  pageNumber(s, 4, TOTAL);
})();

// ============================================================
// SLIDE 5: 多元化建库方式
// ============================================================
(function () {
  const s = lightSlide("亮点 1 · 多元化建库", "三种数据库加载方式，零成本到完全定制");

  const items = [
    {
      title: "8 个内置预置库",
      sub: "瞬时加载 · 0 等待",
      details: ["学生管理 · 电商订单", "图书管理 · 企业人事", "医院挂号 · 银行交易", "餐厅外卖 · 博客社交"],
      color: C.blue600, bg: C.blue50,
    },
    {
      title: "自定义 SQL 上传",
      sub: "完全自主 · 0 LLM 调用",
      details: [
        "粘贴 CREATE TABLE +",
        "INSERT INTO 即可",
        "用真实业务数据训练",
        "校验后自动加载",
      ],
      color: C.green600, bg: C.green50,
    },
    {
      title: "一句话 LLM 生成",
      sub: "自然语言 · 即说即生",
      details: [
        "「健身房系统，需要",
        "会员、教练、课程...」",
        "→ AI 自动设计表结构",
        "→ 写入示例数据",
      ],
      color: C.purple600, bg: C.purple50,
    },
  ];

  items.forEach((it, i) => {
    const x = 0.4 + i * 3.2;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.4, w: 2.95, h: 3.6,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.4, w: 2.95, h: 0.06, fill: { color: it.color },
    });
    // 图标圆
    s.addShape(pres.shapes.OVAL, {
      x: x + 1.1, y: 1.6, w: 0.75, h: 0.75, fill: { color: it.bg },
    });
    s.addText(String(i + 1), {
      x: x + 1.1, y: 1.6, w: 0.75, h: 0.75,
      fontSize: 24, fontFace: FONT_TITLE, color: it.color, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(it.title, {
      x: x + 0.15, y: 2.5, w: 2.65, h: 0.4,
      fontSize: 16, fontFace: FONT_BODY, color: C.textDark, bold: true,
      align: "center", margin: 0,
    });
    s.addText(it.sub, {
      x: x + 0.15, y: 2.92, w: 2.65, h: 0.3,
      fontSize: 11, fontFace: FONT_BODY, color: it.color,
      align: "center", margin: 0,
    });
    it.details.forEach((d, j) => {
      s.addText(d, {
        x: x + 0.25, y: 3.3 + j * 0.35, w: 2.45, h: 0.32,
        fontSize: 10.5, fontFace: FONT_BODY, color: C.textMuted,
        align: "center", margin: 0,
      });
    });
  });

  // 底部
  s.addText("缓存机制：自定义 / LLM 生成的 schema 都会进入 SQLite 缓存，下次秒加载，永不重复调用", {
    x: 0.6, y: 5.15, w: 8.8, h: 0.4,
    fontSize: 11.5, fontFace: FONT_BODY, color: C.textDark,
    align: "center", italic: true, margin: 0,
  });

  pageNumber(s, 5, TOTAL);
})();

// ============================================================
// SLIDE 6: 题目生成（15 类型 × 3 难度）
// ============================================================
(function () {
  const s = lightSlide("亮点 2 · 多样化题目生成", "15 种类型 × 3 个难度 · 题库复用 · 并发生成");

  // 左：题目类型 9 个示例
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.4, w: 5.5, h: 3.8,
    fill: { color: C.lightCard }, shadow: shadow(),
  });
  s.addText("题目类型（部分）", {
    x: 0.8, y: 1.5, w: 5.1, h: 0.35,
    fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
  });

  const types = [
    { name: "基础查询",     color: C.blue600,   tag: "SELECT" },
    { name: "排序分页",     color: C.blue600,   tag: "ORDER BY" },
    { name: "聚合统计",     color: C.green600,  tag: "GROUP BY" },
    { name: "内连接",       color: C.green600,  tag: "INNER JOIN" },
    { name: "外连接",       color: C.green600,  tag: "LEFT JOIN" },
    { name: "标量子查询",   color: C.amber600,  tag: "Subquery" },
    { name: "EXISTS 子查询", color: C.amber600, tag: "EXISTS" },
    { name: "窗口函数",     color: C.purple600, tag: "RANK()" },
    { name: "CTE 表达式",   color: C.purple600, tag: "WITH" },
  ];
  // 3x3 grid
  types.forEach((t, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.8 + col * 1.7;
    const y = 1.95 + row * 0.95;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 1.6, h: 0.8,
      fill: { color: C.lightBg },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 0.06, h: 0.8, fill: { color: t.color },
    });
    s.addText(t.name, {
      x: x + 0.12, y: y + 0.05, w: 1.45, h: 0.32,
      fontSize: 11.5, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
    });
    s.addText(t.tag, {
      x: x + 0.12, y: y + 0.40, w: 1.45, h: 0.32,
      fontSize: 9.5, fontFace: FONT_MONO, color: t.color, margin: 0,
    });
  });
  s.addText("...等 15 种", {
    x: 0.8, y: 4.85, w: 5.1, h: 0.25,
    fontSize: 10, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
  });

  // 右：智能特性
  s.addText("生成特性", {
    x: 6.4, y: 1.4, w: 3.2, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
  });

  const features = [
    { title: "题库复用", desc: "同 schema/难度/类型已生成过的题目，优先抽取，节省 LLM 调用" },
    { title: "并发生成", desc: "ThreadPoolExecutor 4 路并发，3 题串行 18s → 并发 6s" },
    { title: "JSON Mode", desc: "强制 LLM 返回结构化 JSON，避免格式解析失败" },
    { title: "执行验证", desc: "生成后立刻在内存数据库验证 SQL 可执行，过滤脏题" },
  ];
  features.forEach((f, i) => {
    const y = 1.95 + i * 0.83;
    s.addShape(pres.shapes.OVAL, {
      x: 6.4, y: y + 0.05, w: 0.3, h: 0.3, fill: { color: C.accent2 },
    });
    s.addText(String(i + 1), {
      x: 6.4, y: y + 0.05, w: 0.3, h: 0.3,
      fontSize: 12, color: "FFFFFF", bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(f.title, {
      x: 6.85, y: y, w: 2.7, h: 0.3,
      fontSize: 12.5, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
    });
    s.addText(f.desc, {
      x: 6.85, y: y + 0.32, w: 2.7, h: 0.55,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  });

  pageNumber(s, 6, TOTAL);
})();

// ============================================================
// SLIDE 7: 三层判题机制
// ============================================================
(function () {
  const s = lightSlide("亮点 3 · 三层判题引擎", "默认快速路径 ~50ms · 可选 LLM 语义复核");

  const layers = [
    { num: "1", title: "语法检查", tag: "无 LLM",
      desc: "SQLite EXPLAIN 解析 SQL\n语法错误零成本拦截",
      color: C.blue600 },
    { num: "2", title: "执行结果对比", tag: "无 LLM",
      desc: "在 :memory: 数据库执行\n排序后比较，忽略字段顺序",
      color: C.green600 },
    { num: "3", title: "LLM 语义复核", tag: "可选",
      desc: "结果一致时审查 SQL 逻辑\n识别 WHERE 1=1 等碰巧情况",
      color: C.amber600 },
  ];

  layers.forEach((layer, i) => {
    const y = 1.45 + i * 1.0;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 8.8, h: 0.85,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 0.08, h: 0.85, fill: { color: layer.color },
    });
    s.addShape(pres.shapes.OVAL, {
      x: 0.95, y: y + 0.18, w: 0.5, h: 0.5, fill: { color: layer.color },
    });
    s.addText(layer.num, {
      x: 0.95, y: y + 0.18, w: 0.5, h: 0.5,
      fontSize: 22, color: "FFFFFF", bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(layer.title, {
      x: 1.65, y: y + 0.08, w: 4, h: 0.32,
      fontSize: 16, fontFace: FONT_BODY, color: layer.color, bold: true, margin: 0,
    });
    s.addText(layer.desc, {
      x: 1.65, y: y + 0.40, w: 5.8, h: 0.45,
      fontSize: 11.5, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 7.7, y: y + 0.25, w: 1.5, h: 0.35,
      fill: { color: layer.color, transparency: 80 },
    });
    s.addText(layer.tag, {
      x: 7.7, y: y + 0.25, w: 1.5, h: 0.35,
      fontSize: 11, color: layer.color, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
  });

  // 性能对比
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 4.55, w: 8.8, h: 1.0,
    fill: { color: C.lightCard }, shadow: shadow(),
  });
  s.addText("快速路径性能", {
    x: 0.85, y: 4.62, w: 4, h: 0.32,
    fontSize: 12, fontFace: FONT_BODY, color: C.green600, bold: true, margin: 0,
  });
  // 三个对比柱
  const compareItems = [
    { label: "纯 LLM 方案",   value: "~10s",  width: 7.0, color: C.red600 },
    { label: "本系统快速路径", value: "~50ms", width: 0.6, color: C.green600 },
  ];
  compareItems.forEach((c, i) => {
    const y = 4.95 + i * 0.27;
    s.addText(c.label, {
      x: 0.85, y: y, w: 1.5, h: 0.22,
      fontSize: 9.5, fontFace: FONT_BODY, color: C.textDark, margin: 0,
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 2.5, y: y + 0.04, w: c.width, h: 0.16, fill: { color: c.color },
    });
    s.addText(c.value, {
      x: 8.5, y: y, w: 0.85, h: 0.22,
      fontSize: 10, fontFace: FONT_BODY, color: c.color, bold: true,
      align: "right", margin: 0,
    });
  });

  pageNumber(s, 7, TOTAL);
})();

// ============================================================
// SLIDE 8: 考试模式
// ============================================================
(function () {
  const s = lightSlide("亮点 4 · 考试模式", "限时多题 · 难度均分 · 100 分制 · 自动交卷");

  // 上半：流程
  const steps = [
    { title: "配置考试", desc: "题数 / 时长\n领域选择",      color: C.blue600 },
    { title: "并发生成", desc: "按难度均分\nLLM 一次拉取",    color: C.purple600 },
    { title: "限时作答", desc: "倒计时实时显示\n题间自由切换", color: C.amber600 },
    { title: "评级复盘", desc: "5 档评级\n每题详细解析",      color: C.green600 },
  ];

  steps.forEach((step, i) => {
    const x = 0.55 + i * 2.35;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.4, w: 2.0, h: 1.45,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.85, y: 1.5, w: 0.3, h: 0.3, fill: { color: step.color },
    });
    s.addText(String(i + 1), {
      x: x + 0.85, y: 1.5, w: 0.3, h: 0.3,
      fontSize: 14, color: "FFFFFF", bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(step.title, {
      x: x, y: 1.85, w: 2.0, h: 0.3,
      fontSize: 14, fontFace: FONT_BODY, color: step.color,
      bold: true, align: "center", margin: 0,
    });
    s.addText(step.desc, {
      x: x + 0.1, y: 2.20, w: 1.8, h: 0.6,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    });
    if (i < steps.length - 1) {
      s.addText(">", {
        x: x + 2.0, y: 2.05, w: 0.35, h: 0.3,
        fontSize: 18, color: C.textMuted, align: "center", margin: 0,
      });
    }
  });

  // 中：核心规则
  s.addText("核心规则", {
    x: 0.6, y: 3.05, w: 4, h: 0.35,
    fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
  });
  const rules = [
    "题数 3~30、时长 1~120 分钟，由用户自定义",
    "难度按 easy/medium/hard 平均分配",
    "分数按难度权重 1/2/3 加权，总分恒为 100",
    "倒计时归零自动交卷，30s 内倒计时变红警示",
  ];
  rules.forEach((r, i) => {
    s.addShape(pres.shapes.OVAL, {
      x: 0.6, y: 3.5 + i * 0.32, w: 0.18, h: 0.18, fill: { color: C.purple600 },
    });
    s.addText(r, {
      x: 0.85, y: 3.42 + i * 0.32, w: 4.4, h: 0.32,
      fontSize: 11, fontFace: FONT_BODY, color: C.textDark, margin: 0,
    });
  });

  // 右：评级体系
  const grades = [
    { rank: "A+", desc: "≥ 90", color: C.green600 },
    { rank: "A",  desc: "≥ 80", color: C.blue600 },
    { rank: "B",  desc: "≥ 70", color: C.cyan600 },
    { rank: "C",  desc: "≥ 60", color: C.amber600 },
    { rank: "D",  desc: "< 60", color: C.red600 },
  ];
  s.addText("评级体系", {
    x: 5.5, y: 3.05, w: 4, h: 0.35,
    fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
  });
  const gw = 0.8, gg = 0.04;
  const totalW = grades.length * gw + (grades.length - 1) * gg;
  const startGX = 5.5 + ((4) - totalW) / 2;
  grades.forEach((g, i) => {
    const x = startGX + i * (gw + gg);
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 3.55, w: gw, h: 1.4,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 3.55, w: gw, h: 0.06, fill: { color: g.color },
    });
    s.addText(g.rank, {
      x: x, y: 3.7, w: gw, h: 0.65,
      fontSize: 28, fontFace: FONT_TITLE, color: g.color, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(g.desc, {
      x: x, y: 4.45, w: gw, h: 0.4,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    });
  });

  // 底
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 5.1, w: 8.8, h: 0.4, fill: { color: C.purple50 },
  });
  s.addText(
    "考试记录单独存表，不影响日常练习统计 · 题间自由切换 · 单题解析按需生成",
    {
      x: 0.6, y: 5.1, w: 8.8, h: 0.4,
      fontSize: 11, fontFace: FONT_BODY, color: C.purple600,
      align: "center", valign: "middle", italic: true, margin: 0,
    }
  );

  pageNumber(s, 8, TOTAL);
})();

// ============================================================
// SLIDE 9: 错题复习 + 自由答疑
// ============================================================
(function () {
  const s = lightSlide("亮点 5 · 错题复习 + 自由答疑", "巩固薄弱点 · 实时答疑");

  // 左：错题复习
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.4, w: 4.3, h: 4.0,
    fill: { color: C.lightCard }, shadow: shadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.4, w: 4.3, h: 0.06, fill: { color: C.amber600 },
  });
  s.addText("错题复习", {
    x: 0.85, y: 1.55, w: 3.8, h: 0.45,
    fontSize: 18, fontFace: FONT_BODY, color: C.amber600, bold: true, margin: 0,
  });

  const reviewFeatures = [
    "自动收集 wrong / flawed / 看答案 三类题",
    "每题保留最近一次尝试结果",
    "点击表格行直接选题（streamlit 1.35+ row select）",
    "可在原 schema 上重新作答 + 重新判定",
    "可切换查看标准答案",
    "首次答错则统计中永久记错（防刷分）",
  ];
  reviewFeatures.forEach((f, i) => {
    s.addShape(pres.shapes.OVAL, {
      x: 0.9, y: 2.2 + i * 0.45, w: 0.18, h: 0.18, fill: { color: C.amber600 },
    });
    s.addText(f, {
      x: 1.15, y: 2.12 + i * 0.45, w: 3.65, h: 0.42,
      fontSize: 11, fontFace: FONT_BODY, color: C.textDark, margin: 0,
    });
  });

  // 右：自由答疑
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.4, w: 4.3, h: 4.0,
    fill: { color: C.lightCard }, shadow: shadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.4, w: 4.3, h: 0.06, fill: { color: C.red600 },
  });
  s.addText("自由答疑", {
    x: 5.35, y: 1.55, w: 3.8, h: 0.45,
    fontSize: 18, fontFace: FONT_BODY, color: C.red600, bold: true, margin: 0,
  });

  const chatFeatures = [
    "标准 chat 界面，多轮对话历史",
    "自动注入当前数据库 schema 上下文",
    "可问语法、举例、对比写法、性能等",
    "也支持通用 SQL 概念性问题",
    "对话保存在 session，刷新前一直可见",
    "一键清空对话，开启新话题",
  ];
  chatFeatures.forEach((f, i) => {
    s.addShape(pres.shapes.OVAL, {
      x: 5.4, y: 2.2 + i * 0.45, w: 0.18, h: 0.18, fill: { color: C.red600 },
    });
    s.addText(f, {
      x: 5.65, y: 2.12 + i * 0.45, w: 3.65, h: 0.42,
      fontSize: 11, fontFace: FONT_BODY, color: C.textDark, margin: 0,
    });
  });

  pageNumber(s, 9, TOTAL);
})();

// ============================================================
// SLIDE 10: 详细解析（结构化）
// ============================================================
(function () {
  const s = lightSlide("亮点 6 · 结构化详细解析", "Tutor Agent 按 4 个固定章节输出 · 250~450 字");

  // 左：4 个章节卡
  const sections = [
    { num: "1", title: "题目解读",    desc: "用 1-2 句话翻译题目真实需求\n明确取哪些表、返回什么字段", color: C.blue600 },
    { num: "2", title: "解题思路",    desc: "分步说明思考过程\n每步在做什么、为什么", color: C.purple600 },
    { num: "3", title: "答案点评",    desc: "答对：肯定 + 1-2 处优化建议\n答错：明确指出错在哪一步", color: C.amber600 },
    { num: "4", title: "关键知识点",  desc: "1-3 条相关 SQL 语法\n常见易错点提醒", color: C.green600 },
  ];

  sections.forEach((sec, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 4.4;
    const y = 1.4 + row * 1.5;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 4.2, h: 1.35,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.2, y: y + 0.3, w: 0.7, h: 0.7, fill: { color: sec.color },
    });
    s.addText(sec.num, {
      x: x + 0.2, y: y + 0.3, w: 0.7, h: 0.7,
      fontSize: 22, fontFace: FONT_TITLE, color: "FFFFFF", bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(sec.title, {
      x: x + 1.05, y: y + 0.25, w: 3.0, h: 0.4,
      fontSize: 16, fontFace: FONT_BODY, color: sec.color, bold: true, margin: 0,
    });
    s.addText(sec.desc, {
      x: x + 1.05, y: y + 0.65, w: 3.0, h: 0.65,
      fontSize: 10.5, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  });

  // 底部一句话
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 4.55, w: 8.8, h: 0.85, fill: { color: C.indigo50 },
  });
  s.addText("不仅说『错在哪』，还说『怎么想』、『以后怎么避免』 — 让每一道错题都成为学习的契机", {
    x: 0.6, y: 4.55, w: 8.8, h: 0.85,
    fontSize: 13, fontFace: FONT_BODY, color: C.indigo600,
    align: "center", valign: "middle", italic: true, margin: 0,
  });

  pageNumber(s, 10, TOTAL);
})();

// ============================================================
// SLIDE 11: 学习分析报告
// ============================================================
(function () {
  const s = lightSlide("亮点 7 · 学习分析报告", "可视化进度 · AI 个性化建议 · Markdown 导出");

  // 左：图表清单
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.4, w: 4.3, h: 4.0,
    fill: { color: C.lightCard }, shadow: shadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.4, w: 4.3, h: 0.06, fill: { color: C.cyan600 },
  });
  s.addText("数据可视化", {
    x: 0.85, y: 1.55, w: 3.8, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.cyan600, bold: true, margin: 0,
  });

  const charts = [
    { name: "能力雷达图",     desc: "10 个知识维度全景视图" },
    { name: "维度条形图",     desc: "≥80% 绿、50-80% 橙、<50% 红" },
    { name: "每日正确率",     desc: "学习曲线趋势" },
    { name: "每日做题量",     desc: "练习强度热度" },
    { name: "答题历史表",     desc: "每题第一次结果" },
  ];
  charts.forEach((c, i) => {
    const y = 2.05 + i * 0.6;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.85, y: y, w: 3.8, h: 0.5,
      fill: { color: C.cyan50 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.85, y: y, w: 0.06, h: 0.5, fill: { color: C.cyan600 },
    });
    s.addText(c.name, {
      x: 1.0, y: y + 0.05, w: 3.6, h: 0.22,
      fontSize: 11.5, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
    });
    s.addText(c.desc, {
      x: 1.0, y: y + 0.27, w: 3.6, h: 0.2,
      fontSize: 9.5, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  });

  // 右：智能分析
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.4, w: 4.3, h: 4.0,
    fill: { color: C.lightCard }, shadow: shadow(),
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.4, w: 4.3, h: 0.06, fill: { color: C.purple600 },
  });
  s.addText("Analyzer Agent 输出", {
    x: 5.35, y: 1.55, w: 3.8, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.purple600, bold: true, margin: 0,
  });

  const aiOutputs = [
    "总评：用 1 句话归纳学习状态",
    "强项：≤3 个掌握良好的维度",
    "弱项：≤3 个需要加强的维度",
    "维度评分：6 项 0-1 浮点数",
    "改进建议：≤3 条具体可执行操作",
    "推荐难度：下次练习的难度建议",
  ];
  aiOutputs.forEach((o, i) => {
    const y = 2.10 + i * 0.45;
    s.addShape(pres.shapes.OVAL, {
      x: 5.35, y: y + 0.05, w: 0.18, h: 0.18, fill: { color: C.purple600 },
    });
    s.addText(o, {
      x: 5.6, y: y, w: 3.7, h: 0.4,
      fontSize: 11, fontFace: FONT_BODY, color: C.textDark, margin: 0,
    });
  });

  s.addText("一键导出为 Markdown 报告，便于存档和分享", {
    x: 5.35, y: 4.95, w: 3.8, h: 0.3,
    fontSize: 10, fontFace: FONT_BODY, color: C.purple600, italic: true, margin: 0,
  });

  pageNumber(s, 11, TOTAL);
})();

// ============================================================
// SLIDE 12: 性能优化
// ============================================================
(function () {
  const s = lightSlide("性能优化对比", "工程化优化让 90% 操作秒级响应");

  // 表头
  const cols = ["场景", "原始版本", "优化后", "提升"];
  const colW = [2.5, 2.4, 2.4, 1.7];
  const colX = [0.5];
  for (let i = 1; i < cols.length; i++) colX.push(colX[i - 1] + colW[i - 1]);

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.4, w: 9, h: 0.4, fill: { color: C.darkBg2 },
  });
  cols.forEach((c, i) => {
    s.addText(c, {
      x: colX[i], y: 1.4, w: colW[i], h: 0.4,
      fontSize: 12, color: C.textLight, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
  });

  const rows = [
    ["生成内置数据库",      "调 LLM ~30s",      "预置加载 < 1ms",   "30000x"],
    ["重复领域生成",        "重新调 LLM",        "缓存命中",         "瞬时"],
    ["执行结果一致的判题",  "调 LLM ~10s",       "本地比对 ~50ms",   "200x"],
    ["3 题批量生成",        "串行 ~18s",         "并发 ~6s",         "3x"],
    ["max_tokens",         "4096",             "1024 / 768",       "降低 4x"],
    ["JSON 解析",          "手撕 markdown",      "json_object 模式", "稳定"],
    ["题库复用",            "无",                "同条件抽老题",     "节省 LLM"],
    ["预取下一题",          "无",                "做题时后台生成",   "无感切题"],
  ];

  rows.forEach((row, i) => {
    const y = 1.85 + i * 0.36;
    if (i % 2 === 0) {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 0.5, y: y, w: 9, h: 0.36, fill: { color: C.lightCard },
      });
    }
    row.forEach((cell, ci) => {
      s.addText(cell, {
        x: colX[ci] + 0.1, y: y, w: colW[ci] - 0.2, h: 0.36,
        fontSize: 10.5, fontFace: FONT_BODY,
        color: ci === 3 ? C.green600 : C.textDark,
        bold: ci === 3,
        align: ci === 0 ? "left" : "center", valign: "middle", margin: 0,
      });
    });
  });

  // 底部总结
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.0, w: 9, h: 0.5, fill: { color: C.green50 },
  });
  s.addText("整体体验：从『点一次等十几秒』变成『点一次秒响应』", {
    x: 0.5, y: 5.0, w: 9, h: 0.5,
    fontSize: 13, fontFace: FONT_BODY, color: C.green600, bold: true,
    align: "center", valign: "middle", margin: 0,
  });

  pageNumber(s, 12, TOTAL);
})();

// ============================================================
// SLIDE 13: 关键指标
// ============================================================
(function () {
  const s = lightSlide("关键指标 & 工程质量", "数据 + 测试 = 可信度");

  // 上：4 个核心指标
  const metrics = [
    { value: "6",   label: "功能 Tab",     sub: "完整闭环",     color: C.blue600   },
    { value: "8",   label: "内置数据库",   sub: "0 等待加载",   color: C.green600  },
    { value: "15",  label: "题目类型",     sub: "× 3 难度",     color: C.purple600 },
    { value: "35",  label: "单元测试",     sub: "100% 通过",    color: C.amber600  },
  ];
  const mw = 2.0, mgap = 0.2;
  const mTotal = metrics.length * mw + (metrics.length - 1) * mgap;
  const mOffsetX = (10 - mTotal) / 2;
  metrics.forEach((m, i) => {
    const x = mOffsetX + i * (mw + mgap);
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.4, w: mw, h: 1.5,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.4, w: mw, h: 0.06, fill: { color: m.color },
    });
    s.addText(m.value, {
      x: x, y: 1.55, w: mw, h: 0.7,
      fontSize: 38, fontFace: FONT_TITLE, color: m.color, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(m.label, {
      x: x, y: 2.25, w: mw, h: 0.3,
      fontSize: 13, fontFace: FONT_BODY, color: C.textDark, bold: true,
      align: "center", margin: 0,
    });
    s.addText(m.sub, {
      x: x, y: 2.55, w: mw, h: 0.3,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    });
  });

  // 下：测试覆盖
  s.addText("测试覆盖", {
    x: 0.6, y: 3.2, w: 8.8, h: 0.35,
    fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
  });

  const tests = [
    { file: "test_judge.py",            count: 7, desc: "三层判题、语法、执行" },
    { file: "test_store.py",            count: 9, desc: "建表、CRUD、统计去重" },
    { file: "test_llm.py",              count: 3, desc: "客户端默认值、Mock 响应" },
    { file: "test_prompts.py",          count: 5, desc: "5 个 Prompt 模板" },
    { file: "test_smoke_optimized.py",  count: 8, desc: "预置 schema、缓存路径" },
    { file: "test_e2e_offline.py",      count: 3, desc: "完整闭环 + 第一次错锁定" },
  ];

  tests.forEach((t, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.6 + col * 4.5;
    const y = 3.65 + row * 0.45;
    s.addText(t.file, {
      x: x, y: y, w: 1.9, h: 0.3,
      fontSize: 10.5, fontFace: FONT_MONO, color: C.cyan600, margin: 0,
    });
    s.addText(`${t.count} 个`, {
      x: x + 1.85, y: y, w: 0.6, h: 0.3,
      fontSize: 10.5, fontFace: FONT_BODY, color: C.green600, bold: true,
      align: "center", margin: 0,
    });
    s.addText(t.desc, {
      x: x + 2.45, y: y, w: 1.95, h: 0.3,
      fontSize: 10.5, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  });

  // 部署信息
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 5.0, w: 8.8, h: 0.5, fill: { color: C.blue50 },
  });
  s.addText("已部署到 Streamlit Cloud · 在线访问 · 自动从 GitHub main 分支同步", {
    x: 0.6, y: 5.0, w: 8.8, h: 0.5,
    fontSize: 12, fontFace: FONT_BODY, color: C.blue700,
    align: "center", valign: "middle", margin: 0,
  });

  pageNumber(s, 13, TOTAL);
})();

// ============================================================
// SLIDE 14: 总结与展望
// ============================================================
(function () {
  const s = lightSlide("总结与展望", "感谢倾听 · 期待您的建议");

  // 装饰
  s.addShape(pres.shapes.OVAL, {
    x: 7, y: -1, w: 5, h: 5,
    fill: { color: C.accent, transparency: 92 },
  });

  // 左：项目成果
  s.addText("项目成果", {
    x: 0.6, y: 1.4, w: 4.5, h: 0.4,
    fontSize: 18, fontFace: FONT_BODY, color: C.green600, bold: true, margin: 0,
  });
  const achievements = [
    "完整 SQL 学习闭环（6 大功能 Tab）",
    "三层判题，~50ms 默认响应",
    "考试模式 + A/B/C/D 五档评级",
    "结构化错题解析（4 章节）",
    "8 内置 + 自定义 + 一句话生成",
    "可视化分析 + AI 个性化建议",
    "已部署到云端，在线可访问",
  ];
  achievements.forEach((a, i) => {
    s.addText([
      { text: ">  ", options: { color: C.green600 } },
      { text: a, options: { color: C.textDark } },
    ], {
      x: 0.8, y: 1.85 + i * 0.36, w: 4.3, h: 0.32,
      fontSize: 12, fontFace: FONT_BODY, margin: 0,
    });
  });

  // 右：扩展方向
  s.addText("扩展方向", {
    x: 5.5, y: 1.4, w: 4.0, h: 0.4,
    fontSize: 18, fontFace: FONT_BODY, color: C.amber600, bold: true, margin: 0,
  });
  const futures = [
    "自适应难度（基于能力评分）",
    "知识图谱可视化（先修关系）",
    "题目质量回流（用户评分 → 重生成）",
    "多人对战 / 排行榜",
    "课程模式：按章节解锁",
    "SQL 执行计划可视化",
    "多模型对比（DeepSeek vs GPT）",
  ];
  futures.forEach((f, i) => {
    s.addText([
      { text: ">  ", options: { color: C.amber600 } },
      { text: f, options: { color: C.textDark } },
    ], {
      x: 5.7, y: 1.85 + i * 0.36, w: 3.8, h: 0.32,
      fontSize: 12, fontFace: FONT_BODY, margin: 0,
    });
  });

  // 底栏
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.05, w: 10, h: 0.575, fill: { color: C.blue50 },
  });
  s.addText(
    "GitHub: github.com/luoxin20060823/sqlcoach   |   在线试用：sqlcoach-hkj6rtcdfbgkxebdzeuegd.streamlit.app",
    {
      x: 0.6, y: 5.15, w: 8.8, h: 0.5,
      fontSize: 11, fontFace: FONT_BODY, color: C.blue700,
      align: "center", margin: 0,
    }
  );

  pageNumber(s, 14, TOTAL);
})();

// ===== 输出 =====
pres.writeFile({ fileName: "SQL随身教练-汇报.pptx" })
  .then((name) => console.log("汇报 PPT 生成成功：" + name))
  .catch((err) => console.error("生成失败：", err));
