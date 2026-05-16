/**
 * SQL 随身教练 — 项目展示 PPT 生成脚本
 *
 * 涵盖：项目背景、系统架构、五大 Agent、性能优化、UI 6 个 Tab、
 *       挑战模式、错题复习、技术栈、关键指标、总结与展望
 *
 * 运行：
 *   node create_ppt.js
 * 输出：SQL随身教练-展示.pptx
 */

const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "SQL 随身教练";
pres.title = "SQL 随身教练 — 基于大模型 Agent 的 SQL 辅助学习系统";

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
};

const FONT_TITLE = "Arial Black";
const FONT_BODY  = "Microsoft YaHei";
const FONT_MONO  = "Consolas";

// ===== 工具函数 =====
function shadow() {
  return { type: "outer", blur: 8, offset: 2, angle: 90, color: "000000", opacity: 0.10 };
}

function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: C.darkBg };
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent }
  });
  return s;
}

function lightSlide(title) {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.05, fill: { color: C.accent }
  });
  s.addText(title, {
    x: 0.6, y: 0.25, w: 8.8, h: 0.6,
    fontSize: 26, fontFace: FONT_TITLE, color: C.textDark, bold: true, margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.6, y: 0.85, w: 1.0, h: 0,
    line: { color: C.accent, width: 3 }
  });
  return s;
}

function darkTitled(s, title) {
  s.addText(title, {
    x: 0.6, y: 0.3, w: 8.8, h: 0.7,
    fontSize: 28, fontFace: FONT_TITLE, color: C.textLight, bold: true, margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.6, y: 0.85, w: 1.0, h: 0,
    line: { color: C.accent, width: 3 }
  });
}

// ============================================================
// SLIDE 1: 封面
// ============================================================
(function () {
  const s = pres.addSlide();
  s.background = { color: C.darkBg };

  // 装饰圆
  s.addShape(pres.shapes.OVAL, {
    x: 7.5, y: -1.5, w: 5, h: 5,
    fill: { color: C.accent, transparency: 92 },
  });
  s.addShape(pres.shapes.OVAL, {
    x: -1.5, y: 3, w: 4, h: 4,
    fill: { color: C.accent2, transparency: 92 },
  });
  s.addShape(pres.shapes.OVAL, {
    x: 6, y: 4, w: 2.5, h: 2.5,
    fill: { color: C.green, transparency: 94 },
  });

  // 标题
  s.addText("SQL 随身教练", {
    x: 0.8, y: 1.6, w: 8.4, h: 1.2,
    fontSize: 56, fontFace: FONT_TITLE, color: C.textLight, bold: true, margin: 0,
  });
  s.addText("基于大模型 Agent 的 SQL 辅助学习系统", {
    x: 0.8, y: 2.85, w: 8.4, h: 0.6,
    fontSize: 22, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
  });

  // 三个标签
  const tags = ["数据库课程项目", "DeepSeek API + Streamlit", "六大功能闭环"];
  tags.forEach((t, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.8 + i * 2.7, y: 3.7, w: 2.5, h: 0.45,
      fill: { color: C.darkBg2 },
    });
    s.addText(t, {
      x: 0.8 + i * 2.7, y: 3.7, w: 2.5, h: 0.45,
      fontSize: 13, fontFace: FONT_BODY, color: C.accent,
      align: "center", valign: "middle", margin: 0,
    });
  });

  // 底栏
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 4.95, w: 10, h: 0.675, fill: { color: C.darkBg2 },
  });
  s.addText("Streamlit + SQLite + Python · GitHub: luoxin20060823/sqlcoach", {
    x: 0.6, y: 5.05, w: 8.8, h: 0.5,
    fontSize: 12, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
  });
})();

// ============================================================
// SLIDE 2: 项目背景
// ============================================================
(function () {
  const s = lightSlide("项目背景与目标");

  // 痛点（左）
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.2, w: 4.3, h: 1.8,
    fill: { color: C.red50 }, shadow: shadow(),
  });
  s.addText("学习痛点", {
    x: 0.85, y: 1.3, w: 4.0, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.red600, bold: true, margin: 0,
  });
  s.addText([
    { text: "传统 SQL 学习缺乏即时反馈\n", options: { bullet: true } },
    { text: "题库固定，难以按需出题\n", options: { bullet: true } },
    { text: "错题缺少针对性解析\n", options: { bullet: true } },
    { text: "学习进度难以量化追踪", options: { bullet: true } },
  ], {
    x: 0.85, y: 1.75, w: 4.0, h: 1.2,
    fontSize: 12, fontFace: FONT_BODY, color: C.textDark, paraSpaceAfter: 2,
  });

  // 解决方案（右）
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.1, y: 1.2, w: 4.3, h: 1.8,
    fill: { color: C.green50 }, shadow: shadow(),
  });
  s.addText("解决方案", {
    x: 5.35, y: 1.3, w: 4.0, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.green600, bold: true, margin: 0,
  });
  s.addText([
    { text: "LLM Agent 实时生成 schema 与题目\n", options: { bullet: true } },
    { text: "三层快速判题 + 可选语义复核\n", options: { bullet: true } },
    { text: "错题复习 + 多轮自由答疑\n", options: { bullet: true } },
    { text: "雷达图 / 趋势图 / 智能建议", options: { bullet: true } },
  ], {
    x: 5.35, y: 1.75, w: 4.0, h: 1.2,
    fontSize: 12, fontFace: FONT_BODY, color: C.textDark, paraSpaceAfter: 2,
  });

  // 六大亮点
  s.addText("六大功能模块", {
    x: 0.6, y: 3.25, w: 8.8, h: 0.4,
    fontSize: 18, fontFace: FONT_TITLE, color: C.textDark, bold: true, margin: 0,
  });
  const highlights = [
    { title: "练习",       desc: "出题 / 判题\n查看解析",    color: C.blue600 },
    { title: "挑战模式",   desc: "限时多题\n等级评定",       color: C.purple600 },
    { title: "分析报告",   desc: "雷达 / 趋势\nAI 建议",      color: C.cyan600 },
    { title: "数据浏览",   desc: "Schema 与\n表数据预览",   color: C.green600 },
    { title: "错题复习",   desc: "错题 / 放弃\n重新作答",     color: C.amber600 },
    { title: "自由答疑",   desc: "多轮对话\nSQL 助教",        color: C.red600 },
  ];
  highlights.forEach((h, i) => {
    const x = 0.6 + i * 1.5;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 3.7, w: 1.42, h: 1.5,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 3.7, w: 1.42, h: 0.05, fill: { color: h.color },
    });
    s.addText(h.title, {
      x: x, y: 3.85, w: 1.42, h: 0.4,
      fontSize: 14, fontFace: FONT_BODY, color: h.color, bold: true,
      align: "center", margin: 0,
    });
    s.addText(h.desc, {
      x: x + 0.05, y: 4.3, w: 1.32, h: 0.85,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    });
  });
})();

// ============================================================
// SLIDE 3: 系统架构
// ============================================================
(function () {
  const s = darkSlide();
  darkTitled(s, "系统架构");

  const layers = [
    { label: "用户层 — Streamlit Web UI",  desc: "练习 · 挑战 · 报告 · 浏览 · 复习 · 答疑（6 Tab）",          color: C.accent2,  y: 1.15 },
    { label: "Agent 引擎层 — Python",       desc: "SchemaGen · QuestionGen · JudgeEngine · Tutor · Analyzer", color: C.accent,   y: 1.95 },
    { label: "调度层 — LLMClient",          desc: "OpenAI 兼容协议 · 并发批量 · JSON Mode · 超时与回退",      color: C.green,    y: 2.75 },
    { label: "存储层 — SQLite",             desc: "题库 / 答题历史 / Schema 缓存 / 挑战记录",                 color: C.amber,    y: 3.55 },
    { label: "外部模型 — DeepSeek API",     desc: "deepseek-chat（V3）— 单模型驱动全部 Agent",                color: C.pink,     y: 4.35 },
  ];

  layers.forEach((layer) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.9, y: layer.y, w: 8.2, h: 0.65,
      fill: { color: C.darkBg2 }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.9, y: layer.y, w: 0.08, h: 0.65, fill: { color: layer.color },
    });
    s.addText(layer.label, {
      x: 1.2, y: layer.y + 0.02, w: 4, h: 0.32,
      fontSize: 14, fontFace: FONT_BODY, color: layer.color, bold: true, margin: 0,
    });
    s.addText(layer.desc, {
      x: 1.2, y: layer.y + 0.34, w: 7.7, h: 0.3,
      fontSize: 11, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  });

  for (let i = 0; i < layers.length - 1; i++) {
    const arrowY = layers[i].y + 0.7;
    s.addText("V", {
      x: 4.7, y: arrowY - 0.06, w: 0.6, h: 0.2,
      fontSize: 12, color: C.textMuted, align: "center", margin: 0,
    });
  }

  // 底栏：核心技术
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.05, w: 10, h: 0.575, fill: { color: C.darkBg2 },
  });
  s.addText("Streamlit · streamlit-ace · Plotly · Pandas · SQLite · OpenAI SDK · DeepSeek", {
    x: 0.6, y: 5.15, w: 8.8, h: 0.5,
    fontSize: 12, fontFace: FONT_BODY, color: C.textMuted, margin: 0, align: "center",
  });
})();

// ============================================================
// SLIDE 4: 五大 Agent 模块
// ============================================================
(function () {
  const s = lightSlide("五大 Agent 模块");

  const agents = [
    { num: "1", title: "SchemaGenerator",   desc: "三级回退\n预置 → 缓存 → LLM",    color: C.blue600,   bg: C.blue50   },
    { num: "2", title: "QuestionGenerator", desc: "题库复用\n并发批量生成",          color: C.purple600, bg: C.purple50 },
    { num: "3", title: "JudgeEngine",       desc: "三层判题\n语法-执行-语义",         color: C.green600,  bg: C.green50  },
    { num: "4", title: "Tutor",             desc: "错题解析\n多轮自由答疑",           color: C.amber600,  bg: C.amber50  },
    { num: "5", title: "Analyzer",          desc: "维度分析\n个性化建议",             color: C.red600,    bg: C.red50    },
  ];

  const cardW = 1.7, gap = 0.18;
  const total = agents.length * cardW + (agents.length - 1) * gap;
  const offsetX = (10 - total) / 2;

  agents.forEach((a, i) => {
    const x = offsetX + i * (cardW + gap);
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.3, w: cardW, h: 2.4,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.OVAL, {
      x: x + cardW / 2 - 0.3, y: 1.45, w: 0.6, h: 0.6,
      fill: { color: a.color },
    });
    s.addText(a.num, {
      x: x + cardW / 2 - 0.3, y: 1.45, w: 0.6, h: 0.6,
      fontSize: 22, color: "FFFFFF", bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(a.title, {
      x: x + 0.05, y: 2.2, w: cardW - 0.1, h: 0.4,
      fontSize: 13, fontFace: FONT_BODY, color: C.textDark,
      bold: true, align: "center", margin: 0,
    });
    s.addText(a.desc, {
      x: x + 0.1, y: 2.65, w: cardW - 0.2, h: 0.95,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    });
  });

  // 中间循环条
  s.addShape(pres.shapes.RECTANGLE, {
    x: 1.0, y: 4.0, w: 8.0, h: 0.55, fill: { color: C.blue50 },
  });
  s.addText(
    "学习闭环：建库 → 出题 → 答题 → 判题 → 解析 → 分析 → 推荐难度 → 出题",
    {
      x: 1.0, y: 4.0, w: 8.0, h: 0.55,
      fontSize: 13, fontFace: FONT_BODY, color: C.blue700,
      align: "center", valign: "middle", margin: 0,
    }
  );

  // 底部：知识领域
  s.addText("内置 4 个开箱即用领域 + 自定义", {
    x: 0.6, y: 4.75, w: 8.8, h: 0.35,
    fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
  });
  const domains = ["学生管理系统", "电商订单系统", "图书管理系统", "企业人事系统", "自定义领域"];
  const domainW = 1.7, domainGap = 0.1;
  const domainTotalW = domains.length * domainW + (domains.length - 1) * domainGap;
  const domainOffsetX = (10 - domainTotalW) / 2;
  domains.forEach((d, i) => {
    const isCustom = i === domains.length - 1;
    s.addShape(pres.shapes.RECTANGLE, {
      x: domainOffsetX + i * (domainW + domainGap), y: 5.15, w: domainW, h: 0.35,
      fill: { color: isCustom ? C.purple50 : C.blue50 },
    });
    s.addText(d, {
      x: domainOffsetX + i * (domainW + domainGap), y: 5.15, w: domainW, h: 0.35,
      fontSize: 11, fontFace: FONT_BODY,
      color: isCustom ? C.purple600 : C.blue600,
      align: "center", valign: "middle", margin: 0,
    });
  });
})();

// ============================================================
// SLIDE 5: 三层判题机制
// ============================================================
(function () {
  const s = darkSlide();
  darkTitled(s, "核心创新一：三层判题机制");

  const layers = [
    {
      num: "1", title: "语法检查", tag: "无 LLM",
      desc: "SQLite EXPLAIN 解析 SQL\n语法错误零成本拦截",
      color: C.accent,
    },
    {
      num: "2", title: "执行结果对比", tag: "无 LLM",
      desc: "在 :memory: 数据库执行\n排序后比较，忽略字段顺序",
      color: C.green,
    },
    {
      num: "3", title: "LLM 语义复核", tag: "可选 / 默认关闭",
      desc: "结果一致时审查 SQL 逻辑\n识别 WHERE 1=1 等碰巧情况",
      color: C.amber,
    },
  ];

  layers.forEach((layer, i) => {
    const y = 1.15 + i * 1.15;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 8.8, h: 1.0,
      fill: { color: C.darkBg2 }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 0.08, h: 1.0, fill: { color: layer.color },
    });

    s.addShape(pres.shapes.OVAL, {
      x: 1.0, y: y + 0.2, w: 0.55, h: 0.55, fill: { color: layer.color },
    });
    s.addText(layer.num, {
      x: 1.0, y: y + 0.2, w: 0.55, h: 0.55,
      fontSize: 22, color: C.darkBg, bold: true,
      align: "center", valign: "middle", margin: 0,
    });

    s.addText(layer.title, {
      x: 1.75, y: y + 0.08, w: 4, h: 0.35,
      fontSize: 18, fontFace: FONT_BODY, color: layer.color, bold: true, margin: 0,
    });
    s.addText(layer.desc, {
      x: 1.75, y: y + 0.42, w: 5.5, h: 0.55,
      fontSize: 12, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });

    s.addShape(pres.shapes.RECTANGLE, {
      x: 7.55, y: y + 0.3, w: 1.7, h: 0.4,
      fill: { color: layer.color, transparency: 80 },
    });
    s.addText(layer.tag, {
      x: 7.55, y: y + 0.3, w: 1.7, h: 0.4,
      fontSize: 11, color: layer.color, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
  });

  // 性能数据
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 4.7, w: 8.8, h: 0.95,
    fill: { color: C.darkBg2 }, shadow: shadow(),
  });
  s.addText("默认快速路径性能：~50ms 平均判题，比纯 LLM 方案快 100~200 倍", {
    x: 0.6, y: 4.75, w: 8.8, h: 0.4,
    fontSize: 14, fontFace: FONT_BODY, color: C.green, bold: true,
    align: "center", margin: 0,
  });
  s.addText(
    "支持 7 类错误自动分类：syntax · join_logic · aggregation · subquery · where_condition · window_function · equivalent",
    {
      x: 0.6, y: 5.15, w: 8.8, h: 0.45,
      fontSize: 11, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    }
  );
})();

// ============================================================
// SLIDE 6: 性能优化
// ============================================================
(function () {
  const s = lightSlide("核心创新二：性能优化");

  // 表头
  const cols = ["场景", "原始版本", "优化后", "提升"];
  const colW = [2.5, 2.4, 2.4, 1.7];
  const colX = [0.5];
  for (let i = 1; i < cols.length; i++) colX.push(colX[i - 1] + colW[i - 1]);

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.1, w: 9, h: 0.4, fill: { color: C.darkBg2 },
  });
  cols.forEach((c, i) => {
    s.addText(c, {
      x: colX[i], y: 1.1, w: colW[i], h: 0.4,
      fontSize: 13, color: C.textLight, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
  });

  const rows = [
    ["生成内置数据库",      "调 LLM ~30s",          "预置加载 < 1ms",  "30000x"],
    ["重复领域生成",        "重新调 LLM",            "缓存命中",         "瞬时"],
    ["执行结果一致的判题",  "调 LLM ~10s",           "本地比对 ~50ms",   "200x"],
    ["3 题批量生成",        "串行 ~18s",            "并发 ~6s",         "3x"],
    ["max_tokens",          "4096",                 "1024 / 768",       "降低 4x"],
    ["JSON 解析",           "手撕 markdown",        "json_object 模式", "稳定"],
    ["题库复用",            "无",                    "同条件抽老题",     "节省 LLM"],
    ["预取下一题",          "无",                    "做题时后台生成",   "无感切题"],
  ];

  rows.forEach((row, i) => {
    const y = 1.55 + i * 0.4;
    if (i % 2 === 0) {
      s.addShape(pres.shapes.RECTANGLE, {
        x: 0.5, y: y, w: 9, h: 0.4, fill: { color: C.lightCard },
      });
    }
    row.forEach((cell, ci) => {
      const isHighlight = ci === 3;
      s.addText(cell, {
        x: colX[ci] + 0.1, y: y, w: colW[ci] - 0.2, h: 0.4,
        fontSize: 11, fontFace: FONT_BODY,
        color: isHighlight ? C.green600 : C.textDark,
        bold: isHighlight,
        align: ci === 0 ? "left" : "center", valign: "middle", margin: 0,
      });
    });
  });

  // 底部总结
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 4.95, w: 9, h: 0.55, fill: { color: C.green50 },
  });
  s.addText("整体体验：从「点一次等十几秒」变成「点一次秒响应」", {
    x: 0.5, y: 4.95, w: 9, h: 0.55,
    fontSize: 14, fontFace: FONT_BODY, color: C.green600, bold: true,
    align: "center", valign: "middle", margin: 0,
  });
})();

// ============================================================
// SLIDE 7: UI 总览
// ============================================================
(function () {
  const s = lightSlide("界面与交互");

  const tabs = [
    {
      title: "练习",
      items: [
        "Ace SQL 编辑器（语法高亮）",
        "运行 / 提交 / 提示三按钮",
        "三层渐进式提示",
        "查看答案 / 隐藏答案切换",
        "AI 错题解析",
      ],
      color: C.blue600,
    },
    {
      title: "挑战模式",
      items: [
        "3 / 5 / 10 题任选",
        "并发预生成全部题目",
        "限时连续作答",
        "S / A / B / C 评级",
        "历史最佳记录",
      ],
      color: C.purple600,
    },
    {
      title: "分析报告",
      items: [
        "雷达图 + 维度条形图",
        "每日正确率 / 做题量趋势",
        "错误类型饼图",
        "AI 智能分析建议",
        "Markdown 报告导出",
      ],
      color: C.cyan600,
    },
  ];

  tabs.forEach((tab, i) => {
    const x = 0.4 + i * 3.2;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.2, w: 2.95, h: 3.4,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.2, w: 2.95, h: 0.05, fill: { color: tab.color },
    });
    s.addText(tab.title, {
      x: x + 0.15, y: 1.4, w: 2.65, h: 0.4,
      fontSize: 16, fontFace: FONT_BODY, color: tab.color, bold: true, margin: 0,
    });
    tab.items.forEach((item, j) => {
      s.addText(item, {
        x: x + 0.3, y: 1.95 + j * 0.45, w: 2.5, h: 0.4,
        fontSize: 11, fontFace: FONT_BODY, color: C.textDark,
        bullet: true, margin: 0, valign: "middle",
      });
    });
  });

  // 第二行 3 个 Tab
  const row2 = [
    {
      title: "数据浏览",
      items: ["完整 Schema SQL", "各表 DataFrame 预览"],
      color: C.green600,
    },
    {
      title: "错题复习",
      items: ["wrong / flawed / skipped 全记录", "可重新作答 + 重新判定", "切换查看标准答案"],
      color: C.amber600,
    },
    {
      title: "自由答疑",
      items: ["多轮对话历史", "自动注入当前 schema 上下文", "通用 SQL 问题也能问"],
      color: C.red600,
    },
  ];
  row2.forEach((tab, i) => {
    const x = 0.4 + i * 3.2;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 4.7, w: 2.95, h: 1.55,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 4.7, w: 2.95, h: 0.05, fill: { color: tab.color },
    });
    s.addText(tab.title, {
      x: x + 0.15, y: 4.85, w: 2.65, h: 0.35,
      fontSize: 14, fontFace: FONT_BODY, color: tab.color, bold: true, margin: 0,
    });
    tab.items.forEach((item, j) => {
      s.addText(item, {
        x: x + 0.3, y: 5.2 + j * 0.32, w: 2.5, h: 0.3,
        fontSize: 10, fontFace: FONT_BODY, color: C.textDark,
        bullet: true, margin: 0, valign: "middle",
      });
    });
  });
})();

// ============================================================
// SLIDE 8: 挑战模式
// ============================================================
(function () {
  const s = lightSlide("特色功能：挑战模式");

  // 流程
  const steps = [
    { title: "选配置", desc: "领域 / 难度\n3-5-10 题",        color: C.blue600   },
    { title: "并发生成", desc: "ThreadPoolExecutor\n4 路并发",  color: C.purple600 },
    { title: "限时作答", desc: "无提示 / 不可看答案\n用时全程计时", color: C.amber600  },
    { title: "评级与复盘", desc: "S/A/B/C 评级\n每题对错明细",   color: C.green600  },
  ];

  steps.forEach((step, i) => {
    const x = 0.6 + i * 2.3;
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.3, w: 2.0, h: 1.6,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.85, y: 1.4, w: 0.3, h: 0.3, fill: { color: step.color },
    });
    s.addText(String(i + 1), {
      x: x + 0.85, y: 1.4, w: 0.3, h: 0.3,
      fontSize: 14, color: "FFFFFF", bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(step.title, {
      x: x, y: 1.8, w: 2.0, h: 0.3,
      fontSize: 14, fontFace: FONT_BODY, color: step.color,
      bold: true, align: "center", margin: 0,
    });
    s.addText(step.desc, {
      x: x + 0.1, y: 2.15, w: 1.8, h: 0.7,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    });

    if (i < steps.length - 1) {
      s.addText(">", {
        x: x + 2.0, y: 2.0, w: 0.3, h: 0.3,
        fontSize: 18, color: C.textMuted, align: "center", margin: 0,
      });
    }
  });

  // 评级体系
  s.addText("评级体系", {
    x: 0.6, y: 3.2, w: 8.8, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
  });

  const grades = [
    { rank: "S", desc: "正确率 ≥ 90%", color: C.green600 },
    { rank: "A", desc: "正确率 ≥ 70%", color: C.blue600 },
    { rank: "B", desc: "正确率 ≥ 50%", color: C.amber600 },
    { rank: "C", desc: "正确率 < 50%", color: C.red600 },
  ];
  const gradeW = 2.0, gradeGap = 0.15;
  const gradeTotalW = grades.length * gradeW + (grades.length - 1) * gradeGap;
  const gradeOffsetX = (10 - gradeTotalW) / 2;
  grades.forEach((g, i) => {
    const x = gradeOffsetX + i * (gradeW + gradeGap);
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 3.7, w: gradeW, h: 1.1,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addText(g.rank, {
      x: x, y: 3.75, w: gradeW, h: 0.55,
      fontSize: 36, fontFace: FONT_TITLE, color: g.color, bold: true,
      align: "center", margin: 0,
    });
    s.addText(g.desc, {
      x: x, y: 4.3, w: gradeW, h: 0.4,
      fontSize: 12, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    });
  });

  // 数据持久化
  s.addText(
    "挑战记录单独存表（challenge_runs），不与日常练习的统计混合",
    {
      x: 0.6, y: 5.05, w: 8.8, h: 0.4,
      fontSize: 11, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0, italic: true,
    }
  );
})();

// ============================================================
// SLIDE 9: Prompt 与 LLM 调度
// ============================================================
(function () {
  const s = lightSlide("Prompt 与 LLM 调度策略");

  // 左：策略
  s.addText("Prompt 设计", {
    x: 0.6, y: 1.2, w: 4.2, h: 0.4,
    fontSize: 18, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
  });

  const strategies = [
    "System Prompt 短小精炼，节省 token",
    "强制 JSON Schema 输出，避免解析失败",
    "字段最小化：只要必要的 verdict / analysis",
    "中文 Prompt 适配国产模型偏好",
    "temperature 按场景区分：判题=0，生成=0.4",
  ];
  strategies.forEach((p, i) => {
    const y = 1.7 + i * 0.55;
    s.addShape(pres.shapes.OVAL, {
      x: 0.6, y: y + 0.1, w: 0.3, h: 0.3, fill: { color: C.accent2 },
    });
    s.addText(String(i + 1), {
      x: 0.6, y: y + 0.1, w: 0.3, h: 0.3,
      fontSize: 11, color: "FFFFFF", bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(p, {
      x: 1.05, y: y, w: 3.7, h: 0.5,
      fontSize: 11, fontFace: FONT_BODY, color: C.textDark,
      valign: "middle", margin: 0,
    });
  });

  // 右：代码片段
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.2, w: 4.2, h: 4.0,
    fill: { color: C.darkBg }, shadow: shadow(),
  });
  s.addText("LLMClient.chat_many(...)", {
    x: 5.4, y: 1.3, w: 4.0, h: 0.3,
    fontSize: 12, fontFace: FONT_MONO, color: C.accent, margin: 0,
  });
  s.addText([
    { text: "def ", options: { color: "FBBF24" } },
    { text: "chat_many(self, requests):\n", options: { color: C.textLight } },
    { text: "    # ", options: { color: "94A3B8" } },
    { text: "并发执行多个 LLM 请求\n", options: { color: "94A3B8" } },
    { text: "    with ", options: { color: "FBBF24" } },
    { text: "ThreadPoolExecutor(\n", options: { color: C.textLight } },
    { text: "        max_workers=4\n", options: { color: C.textLight } },
    { text: "    ) as pool:\n", options: { color: C.textLight } },
    { text: "        futures = [\n", options: { color: C.textLight } },
    { text: "            pool.submit(self.chat_json, **r)\n", options: { color: C.textLight } },
    { text: "            for r in requests\n", options: { color: C.textLight } },
    { text: "        ]\n", options: { color: C.textLight } },
    { text: "    return ", options: { color: "FBBF24" } },
    { text: "[f.result() for f in futures]", options: { color: C.textLight } },
  ], {
    x: 5.4, y: 1.7, w: 3.8, h: 3.4,
    fontSize: 10, fontFace: FONT_MONO, lineSpacingMultiple: 1.4, margin: 0,
  });
})();

// ============================================================
// SLIDE 10: 技术栈
// ============================================================
(function () {
  const s = darkSlide();
  darkTitled(s, "技术栈");

  const stackItems = [
    { category: "前端",     techs: ["Streamlit 1.31+", "streamlit-ace", "Plotly", "Pandas"], color: C.accent  },
    { category: "后端",     techs: ["Python 3.11", "OpenAI SDK", "concurrent.futures", "sqlite3"], color: C.green },
    { category: "LLM",      techs: ["DeepSeek-Chat", "OpenAI 兼容 API", "JSON Mode", "并发批量"], color: C.amber },
    { category: "持久化",   techs: ["SQLite (零配置)", "schema_cache", "challenge_runs", "用户偏好 JSON"], color: C.accent2 },
    { category: "部署",     techs: ["Streamlit Cloud", "GitHub Actions", "Electron 壳", "在线访问"], color: C.pink },
  ];

  const cardW = 1.7, gap = 0.15;
  const totalW = stackItems.length * cardW + (stackItems.length - 1) * gap;
  const offsetX = (10 - totalW) / 2;

  stackItems.forEach((item, i) => {
    const x = offsetX + i * (cardW + gap);
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.15, w: cardW, h: 4.0,
      fill: { color: C.darkBg2 }, shadow: shadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.15, w: cardW, h: 0.06, fill: { color: item.color },
    });
    s.addText(item.category, {
      x: x + 0.05, y: 1.4, w: cardW - 0.1, h: 0.4,
      fontSize: 14, fontFace: FONT_BODY, color: item.color,
      bold: true, align: "center", margin: 0,
    });
    item.techs.forEach((tech, j) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: x + 0.1, y: 2.0 + j * 0.7, w: cardW - 0.2, h: 0.55,
        fill: { color: C.darkBg },
      });
      s.addText(tech, {
        x: x + 0.1, y: 2.0 + j * 0.7, w: cardW - 0.2, h: 0.55,
        fontSize: 10, fontFace: FONT_BODY, color: C.textLight,
        align: "center", valign: "middle", margin: 0,
      });
    });
  });
})();

// ============================================================
// SLIDE 11: 关键指标 / 测试
// ============================================================
(function () {
  const s = lightSlide("关键指标与质量保证");

  // 4 个关键指标卡片
  const metrics = [
    { value: "35",   label: "单元测试",   sub: "全部通过", color: C.green600  },
    { value: "6",    label: "功能 Tab",   sub: "完整闭环", color: C.blue600   },
    { value: "15",   label: "题目类型",   sub: "覆盖核心", color: C.purple600 },
    { value: "200x", label: "判题加速",   sub: "对比纯 LLM", color: C.amber600  },
  ];

  const mw = 2.0, mgap = 0.2;
  const mTotal = metrics.length * mw + (metrics.length - 1) * mgap;
  const mOffsetX = (10 - mTotal) / 2;
  metrics.forEach((m, i) => {
    const x = mOffsetX + i * (mw + mgap);
    s.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.15, w: mw, h: 1.6,
      fill: { color: C.lightCard }, shadow: shadow(),
    });
    s.addText(m.value, {
      x: x, y: 1.25, w: mw, h: 0.7,
      fontSize: 40, fontFace: FONT_TITLE, color: m.color, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(m.label, {
      x: x, y: 2.0, w: mw, h: 0.3,
      fontSize: 13, fontFace: FONT_BODY, color: C.textDark, bold: true,
      align: "center", margin: 0,
    });
    s.addText(m.sub, {
      x: x, y: 2.35, w: mw, h: 0.3,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    });
  });

  // 测试覆盖
  s.addText("测试覆盖", {
    x: 0.6, y: 3.0, w: 8.8, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0,
  });

  const tests = [
    { file: "test_judge.py",            count: 7,  desc: "三层判题、语法、执行、完整流程" },
    { file: "test_store.py",            count: 9,  desc: "建表、CRUD、统计去重、维度" },
    { file: "test_llm.py",              count: 3,  desc: "客户端默认值、Mock 响应" },
    { file: "test_prompts.py",          count: 5,  desc: "5 个 Prompt 模板格式化" },
    { file: "test_smoke_optimized.py",  count: 8,  desc: "预置 schema、缓存、快速路径" },
    { file: "test_e2e_offline.py",      count: 3,  desc: "完整闭环 + 第一次错锁定" },
  ];
  tests.forEach((t, i) => {
    const y = 3.55 + i * 0.32;
    s.addText(t.file, {
      x: 0.7, y: y, w: 2.5, h: 0.3,
      fontSize: 11, fontFace: FONT_MONO, color: C.cyan600, margin: 0,
    });
    s.addText(`${t.count} 个`, {
      x: 3.2, y: y, w: 0.8, h: 0.3,
      fontSize: 11, fontFace: FONT_BODY, color: C.green600, bold: true, margin: 0,
    });
    s.addText(t.desc, {
      x: 4.0, y: y, w: 5.4, h: 0.3,
      fontSize: 11, fontFace: FONT_BODY, color: C.textMuted, margin: 0,
    });
  });
})();

// ============================================================
// SLIDE 12: 总结与展望
// ============================================================
(function () {
  const s = darkSlide();
  darkTitled(s, "总结与展望");

  // 装饰
  s.addShape(pres.shapes.OVAL, {
    x: 7, y: -1, w: 5, h: 5,
    fill: { color: C.accent, transparency: 92 },
  });

  // 左：成果
  s.addText("已实现成果", {
    x: 0.6, y: 1.15, w: 4.5, h: 0.4,
    fontSize: 18, fontFace: FONT_BODY, color: C.green, bold: true, margin: 0,
  });
  const achievements = [
    "完整 SQL 学习闭环（6 大功能）",
    "三层判题 + 7 类错误分类",
    "默认快速路径，~50ms 判题",
    "并发题目生成、预取下一题",
    "题库复用、Schema 缓存",
    "挑战模式 + S/A/B/C 评级",
    "雷达图 / 趋势 / Markdown 导出",
    "35 单元测试 100% 通过",
  ];
  achievements.forEach((a, i) => {
    s.addText([
      { text: ">  ", options: { color: C.green } },
      { text: a, options: { color: C.textMuted } },
    ], {
      x: 0.8, y: 1.65 + i * 0.38, w: 4.3, h: 0.35,
      fontSize: 12, fontFace: FONT_BODY, margin: 0,
    });
  });

  // 右：展望
  s.addText("后续扩展方向", {
    x: 5.5, y: 1.15, w: 4.0, h: 0.4,
    fontSize: 18, fontFace: FONT_BODY, color: C.amber, bold: true, margin: 0,
  });
  const futures = [
    "题目质量回流：用户评分 → 自动重生成",
    "自适应难度：根据能力评分动态调度",
    "知识图谱可视化（先修关系）",
    "多人对战 / 排行榜",
    "课程模式：分章节解锁",
    "SQL 执行计划可视化",
    "本地 SQL 文件导入",
  ];
  futures.forEach((f, i) => {
    s.addText([
      { text: ">  ", options: { color: C.amber } },
      { text: f, options: { color: C.textMuted } },
    ], {
      x: 5.7, y: 1.65 + i * 0.38, w: 3.8, h: 0.35,
      fontSize: 12, fontFace: FONT_BODY, margin: 0,
    });
  });

  // 底部
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.05, w: 10, h: 0.575, fill: { color: C.darkBg2 },
  });
  s.addText(
    "感谢观看 · GitHub: luoxin20060823/sqlcoach · 在线试用：sqlcoach.streamlit.app",
    {
      x: 0.6, y: 5.15, w: 8.8, h: 0.5,
      fontSize: 12, fontFace: FONT_BODY, color: C.textMuted,
      align: "center", margin: 0,
    }
  );
})();

// ===== 输出 =====
pres.writeFile({ fileName: "SQL随身教练-展示.pptx" })
  .then((name) => console.log("PPT 生成成功：" + name))
  .catch((err) => console.error("生成失败：", err));
