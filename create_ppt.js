const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "SQL随身教练";
pres.title = "SQL随身教练 - 基于大模型Agent的SQL辅助学习系统";

// === Color Palette ===
const C = {
  darkBg: "0F172A",
  darkBg2: "1E293B",
  cardBg: "1E293B",
  accent: "38BDF8",
  accent2: "818CF8",
  green: "34D399",
  amber: "FBBF24",
  red: "F87171",
  textLight: "F1F5F9",
  textMuted: "94A3B8",
  textDark: "1E293B",
  lightBg: "F8FAFC",
  lightCard: "FFFFFF",
  border: "E2E8F0",
  blue50: "EFF6FF",
  blue100: "DBEAFE",
  blue600: "2563EB",
  blue700: "1D4ED8",
  purple50: "F5F3FF",
  purple600: "7C3AED",
  green50: "F0FDF4",
  green600: "059669",
  amber50: "FFFBEB",
  amber600: "D97706",
  red50: "FEF2F2",
  red600: "DC2626",
};

const FONT_TITLE = "Arial Black";
const FONT_BODY = "Arial";

// === Helper Functions ===
function addDarkSlide(title) {
  const slide = pres.addSlide();
  slide.background = { color: C.darkBg };
  // Subtle gradient bar at top
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent }
  });
  return slide;
}

function addLightSlide(title) {
  const slide = pres.addSlide();
  slide.background = { color: C.lightBg };
  // Top accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.accent }
  });
  // Title
  slide.addText(title, {
    x: 0.6, y: 0.25, w: 8.8, h: 0.6,
    fontSize: 28, fontFace: FONT_TITLE, color: C.textDark, bold: true,
    margin: 0
  });
  // Divider
  slide.addShape(pres.shapes.LINE, {
    x: 0.6, y: 0.9, w: 1.2, h: 0,
    line: { color: C.accent, width: 3 }
  });
  return slide;
}

function makeCardShadow() {
  return { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 };
}

// ============================================================
// SLIDE 1: Title Slide
// ============================================================
(function () {
  const slide = addDarkSlide();
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.darkBg }
  });
  // Decorative circles
  slide.addShape(pres.shapes.OVAL, {
    x: 7.5, y: -1.5, w: 5, h: 5,
    fill: { color: C.accent, transparency: 92 }
  });
  slide.addShape(pres.shapes.OVAL, {
    x: -1.5, y: 3, w: 4, h: 4,
    fill: { color: C.accent2, transparency: 92 }
  });

  // Icon placeholder (database symbol with shapes)
  slide.addShape(pres.shapes.OVAL, {
    x: 0.8, y: 1.2, w: 0.7, h: 0.35,
    fill: { color: C.accent, transparency: 30 }
  });
  slide.addShape(pres.shapes.OVAL, {
    x: 0.8, y: 1.7, w: 0.7, h: 0.35,
    fill: { color: C.accent, transparency: 50 }
  });
  slide.addShape(pres.shapes.OVAL, {
    x: 0.8, y: 2.2, w: 0.7, h: 0.35,
    fill: { color: C.accent, transparency: 70 }
  });

  slide.addText("SQL 随身教练", {
    x: 1.8, y: 1.3, w: 6, h: 1.0,
    fontSize: 44, fontFace: FONT_TITLE, color: C.textLight, bold: true,
    margin: 0
  });
  slide.addText("基于大模型 Agent 的 SQL 辅助学习系统", {
    x: 1.8, y: 2.3, w: 6, h: 0.6,
    fontSize: 18, fontFace: FONT_BODY, color: C.textMuted,
    margin: 0
  });

  // Bottom info bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 4.8, w: 10, h: 0.825, fill: { color: C.darkBg2 }
  });
  slide.addText("数据库课程项目  |  DeepSeek-V4-Pro  |  Streamlit + SQLite + Electron", {
    x: 0.6, y: 4.95, w: 8.8, h: 0.5,
    fontSize: 12, fontFace: FONT_BODY, color: C.textMuted,
    margin: 0
  });
})();

// ============================================================
// SLIDE 2: Project Background
// ============================================================
(function () {
  const slide = addLightSlide("项目背景与目标");

  // Problem section
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.2, w: 4.2, h: 1.3,
    fill: { color: C.red50 },
    shadow: makeCardShadow()
  });
  slide.addText("🔴 痛点", {
    x: 0.8, y: 1.3, w: 3.8, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.red600, bold: true, margin: 0
  });
  slide.addText([
    { text: "SQL 学习缺乏即时反馈", options: { bullet: true, breakLine: true } },
    { text: "传统题库固定，无法按需生成", options: { bullet: true, breakLine: true } },
    { text: "缺乏针对性错误解析和答疑", options: { bullet: true } }
  ], {
    x: 0.8, y: 1.7, w: 3.8, h: 0.7,
    fontSize: 12, fontFace: FONT_BODY, color: C.textDark,
    paraSpaceAfter: 2
  });

  // Solution section
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 1.2, w: 4.2, h: 1.3,
    fill: { color: C.green50 },
    shadow: makeCardShadow()
  });
  slide.addText("🟢 解决方案", {
    x: 5.4, y: 1.3, w: 3.8, h: 0.4,
    fontSize: 16, fontFace: FONT_BODY, color: C.green600, bold: true, margin: 0
  });
  slide.addText([
    { text: "LLM Agent 实时出题与判题", options: { bullet: true, breakLine: true } },
    { text: "三层判题 + 语义级错误分析", options: { bullet: true, breakLine: true } },
    { text: "能力雷达图 + 个性化建议", options: { bullet: true } }
  ], {
    x: 5.4, y: 1.7, w: 3.8, h: 0.7,
    fontSize: 12, fontFace: FONT_BODY, color: C.textDark,
    paraSpaceAfter: 2
  });

  // Bottom: Key features preview
  slide.addText("核心亮点", {
    x: 0.6, y: 2.75, w: 8.8, h: 0.4,
    fontSize: 18, fontFace: FONT_TITLE, color: C.textDark, bold: true, margin: 0
  });

  const highlights = [
    { icon: "🗄️", title: "自动建库", desc: "LLM生成Schema\n与实例数据" },
    { icon: "📝", title: "智能出题", desc: "3个难度等级\n按需生成题目" },
    { icon: "✅", title: "三层判题", desc: "语法→执行→语义\n精准反馈" },
    { icon: "📊", title: "分析报告", desc: "雷达图+历史\n改进建议" },
  ];

  highlights.forEach((h, i) => {
    const x = 0.6 + i * 2.25;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 3.3, w: 2.0, h: 1.8,
      fill: { color: C.lightCard },
      shadow: makeCardShadow()
    });
    slide.addText(h.icon, {
      x: x, y: 3.35, w: 2.0, h: 0.5,
      fontSize: 28, align: "center", margin: 0
    });
    slide.addText(h.title, {
      x: x + 0.15, y: 3.85, w: 1.7, h: 0.35,
      fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, align: "center", margin: 0
    });
    slide.addText(h.desc, {
      x: x + 0.15, y: 4.2, w: 1.7, h: 0.7,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted, align: "center", margin: 0
    });
  });
})();

// ============================================================
// SLIDE 3: System Architecture
// ============================================================
(function () {
  const slide = addDarkSlide();
  slide.addText("系统架构", {
    x: 0.6, y: 0.3, w: 8.8, h: 0.7,
    fontSize: 32, fontFace: FONT_TITLE, color: C.textLight, bold: true, margin: 0
  });
  slide.addShape(pres.shapes.LINE, {
    x: 0.6, y: 0.9, w: 1.2, h: 0, line: { color: C.accent, width: 3 }
  });

  const layers = [
    { label: "Electron 桌面壳", desc: "加载 localhost:8501，包装为桌面应用", color: C.accent2, y: 1.3 },
    { label: "Streamlit 前端", desc: "3 Tab: 练习 | 分析报告 | 数据浏览  +  侧边栏控制面板", color: C.accent, y: 2.15 },
    { label: "LLM Agent 引擎 (Python)", desc: "Schema生成 · 题目生成 · 判题 · 答疑 · 评分分析", color: C.green, y: 3.0 },
    { label: "SQLite 持久化", desc: "题库 (question_bank) + 答题记录 (user_history)", color: C.amber, y: 3.85 },
    { label: "DeepSeek-V4-Pro API", desc: "OpenAI 兼容接口 · 单模型驱动全部 Agent 模块", color: "F472B6", y: 4.7 },
  ];

  layers.forEach((layer) => {
    const w = 8.2;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.9, y: layer.y, w: w, h: 0.7,
      fill: { color: C.darkBg2 },
      shadow: makeCardShadow()
    });
    // Left accent bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.9, y: layer.y, w: 0.08, h: 0.7,
      fill: { color: layer.color }
    });
    slide.addText(layer.label, {
      x: 1.2, y: layer.y + 0.02, w: 3, h: 0.32,
      fontSize: 14, fontFace: FONT_BODY, color: layer.color, bold: true, margin: 0
    });
    slide.addText(layer.desc, {
      x: 1.2, y: layer.y + 0.34, w: 7.5, h: 0.3,
      fontSize: 11, fontFace: FONT_BODY, color: C.textMuted, margin: 0
    });
  });

  // Connection arrows between layers
  for (let i = 0; i < layers.length - 1; i++) {
    const arrowY = layers[i].y + 0.7;
    slide.addText("▼", {
      x: 4.7, y: arrowY - 0.02, w: 0.6, h: 0.2,
      fontSize: 14, color: C.textMuted, align: "center", margin: 0
    });
  }
})();

// ============================================================
// SLIDE 4: Learning Loop (5 Core Functions)
// ============================================================
(function () {
  const slide = addLightSlide("学习闭环：五大核心功能");

  const steps = [
    { num: "1", title: "Schema生成", desc: "LLM 根据领域自动生成\n数据库表结构和实例数据", color: C.blue600, bg: C.blue50 },
    { num: "2", title: "题目生成", desc: "按初级/中级/高级生成\nSQL 查询题目 + 标准答案", color: C.amber600, bg: C.amber50 },
    { num: "3", title: "答题判题", desc: "三层判题机制\n语法→执行→语义验证", color: C.green600, bg: C.green50 },
    { num: "4", title: "错题解析", desc: "LLM 分析错误原因\n提供针对性解析和答疑", color: C.red600, bg: C.red50 },
    { num: "5", title: "评分分析", desc: "能力雷达图 + 历史记录\n个性化改进建议", color: C.purple600, bg: C.purple50 },
  ];

  // Flow arrow at top
  const startX = 0.3, cardW = 1.7, gap = 0.2;
  const totalW = steps.length * cardW + (steps.length - 1) * gap;
  const offsetX = (10 - totalW) / 2;

  steps.forEach((step, i) => {
    const x = offsetX + i * (cardW + gap);
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.25, w: cardW, h: 2.4,
      fill: { color: C.lightCard },
      shadow: makeCardShadow()
    });
    // Number circle
    slide.addShape(pres.shapes.OVAL, {
      x: x + cardW / 2 - 0.3, y: 1.4, w: 0.6, h: 0.6,
      fill: { color: step.color }
    });
    slide.addText(step.num, {
      x: x + cardW / 2 - 0.3, y: 1.4, w: 0.6, h: 0.6,
      fontSize: 20, color: "FFFFFF", bold: true, align: "center", valign: "middle", margin: 0
    });
    slide.addText(step.title, {
      x: x + 0.1, y: 2.15, w: cardW - 0.2, h: 0.35,
      fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, align: "center", margin: 0
    });
    slide.addText(step.desc, {
      x: x + 0.1, y: 2.55, w: cardW - 0.2, h: 0.9,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted, align: "center", margin: 0
    });
  });

  // Arrows between cards
  for (let i = 0; i < steps.length - 1; i++) {
    const x = offsetX + i * (cardW + gap) + cardW;
    slide.addText("→", {
      x: x, y: 2.05, w: gap, h: 0.5,
      fontSize: 22, color: C.textMuted, align: "center", valign: "middle", margin: 0
    });
  }

  // Bottom: loop description
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 1.5, y: 3.95, w: 7, h: 0.55,
    fill: { color: C.blue50 }
  });
  slide.addText("🔄 闭环反馈：分析结果自动推荐下次练习难度，形成持续提升的正向循环", {
    x: 1.7, y: 3.98, w: 6.6, h: 0.5,
    fontSize: 13, fontFace: FONT_BODY, color: C.blue700, align: "center", valign: "middle", margin: 0
  });

  // Bottom: database domains
  slide.addText("支持的知识领域", {
    x: 0.6, y: 4.75, w: 3, h: 0.35,
    fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0
  });
  const domains = ["学生管理系统", "电商订单系统", "图书管理系统", "企业人事系统"];
  domains.forEach((d, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.6 + i * 2.2, y: 5.1, w: 2.0, h: 0.35,
      fill: { color: C.blue50 }
    });
    slide.addText(d, {
      x: 0.6 + i * 2.2, y: 5.1, w: 2.0, h: 0.35,
      fontSize: 11, fontFace: FONT_BODY, color: C.blue600, align: "center", valign: "middle", margin: 0
    });
  });
})();

// ============================================================
// SLIDE 5: LLM Agent Design
// ============================================================
(function () {
  const slide = addLightSlide("LLM Agent 设计");

  // Left: architecture diagram
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.2, w: 4.8, h: 3.9,
    fill: { color: C.darkBg },
    shadow: makeCardShadow()
  });

  slide.addText("Agent 引擎架构", {
    x: 0.8, y: 1.3, w: 4.4, h: 0.4,
    fontSize: 14, fontFace: FONT_BODY, color: C.textLight, bold: true, margin: 0
  });

  const agents = [
    { name: "SchemaGenerator", icon: "🗄️", color: C.accent },
    { name: "QuestionGenerator", icon: "📝", color: C.accent2 },
    { name: "JudgeEngine", icon: "⚖️", color: C.green },
    { name: "Tutor", icon: "📖", color: C.amber },
    { name: "Analyzer", icon: "📊", color: "F472B6" },
  ];

  // Central: LLMClient
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 2.1, y: 2.6, w: 1.8, h: 0.6,
    fill: { color: C.accent }
  });
  slide.addText("LLMClient", {
    x: 2.1, y: 2.6, w: 1.8, h: 0.6,
    fontSize: 12, color: C.textLight, bold: true, align: "center", valign: "middle", margin: 0
  });

  slide.addText("DeepSeek API", {
    x: 2.1, y: 3.4, w: 1.8, h: 0.35,
    fontSize: 10, color: C.textMuted, align: "center", margin: 0
  });

  agents.forEach((a, i) => {
    const topY = 1.8;
    const x = i < 3 ? 0.8 : 2.5 + (i - 3) * 1.35;
    const y = i < 3 ? topY : topY + 1.1;

    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: y, w: 1.2, h: 0.45,
      fill: { color: C.darkBg2 }
    });
    slide.addText(`${a.icon} ${a.name}`, {
      x: x, y: y, w: 1.2, h: 0.45,
      fontSize: 8, color: a.color, align: "center", valign: "middle", margin: 0
    });
  });

  // Right: prompt design
  slide.addText("Prompt 设计策略", {
    x: 5.8, y: 1.2, w: 3.8, h: 0.4,
    fontSize: 16, fontFace: FONT_TITLE, color: C.textDark, bold: true, margin: 0
  });

  const prompts = [
    "System Prompt 定义角色和能力边界",
    "User Prompt 注入数据库 Schema 上下文",
    "强制 JSON 输出，便于程序解析",
    "temperature=0.1 保证 SQL 准确性",
    "中文 Prompt 适配国产模型偏好",
  ];

  prompts.forEach((p, i) => {
    const y = 1.75 + i * 0.55;
    slide.addShape(pres.shapes.OVAL, {
      x: 5.8, y: y + 0.05, w: 0.3, h: 0.3,
      fill: { color: C.accent }
    });
    slide.addText(String(i + 1), {
      x: 5.8, y: y + 0.05, w: 0.3, h: 0.3,
      fontSize: 12, color: "FFFFFF", bold: true, align: "center", valign: "middle", margin: 0
    });
    slide.addText(p, {
      x: 6.25, y: y, w: 3.3, h: 0.4,
      fontSize: 12, fontFace: FONT_BODY, color: C.textDark, valign: "middle", margin: 0
    });
  });

  // Code example
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.8, y: 3.55, w: 3.8, h: 1.55,
    fill: { color: C.darkBg }
  });
  slide.addText([
    { text: "client = OpenAI(\n", options: { color: "94A3B8" } },
    { text: "  api_key='sk-xxx',\n", options: { color: "FBBF24" } },
    { text: "  base_url='https://api.deepseek.com'\n", options: { color: "FBBF24" } },
    { text: ")\n", options: { color: "94A3B8" } },
    { text: "response = client.chat.completions.create(\n", options: { color: "94A3B8" } },
    { text: "  model='deepseek-chat',\n", options: { color: "FBBF24" } },
    { text: "  temperature=0.1\n", options: { color: "FBBF24" } },
    { text: ")", options: { color: "94A3B8" } },
  ], {
    x: 6.0, y: 3.65, w: 3.4, h: 1.35,
    fontSize: 9, fontFace: "Consolas", margin: 0, lineSpacingMultiple: 1.2
  });
})();

// ============================================================
// SLIDE 6: Three-Layer Judge Engine
// ============================================================
(function () {
  const slide = addDarkSlide();
  slide.addText("核心创新：三层判题机制", {
    x: 0.6, y: 0.3, w: 8.8, h: 0.7,
    fontSize: 32, fontFace: FONT_TITLE, color: C.textLight, bold: true, margin: 0
  });
  slide.addShape(pres.shapes.LINE, {
    x: 0.6, y: 0.9, w: 1.2, h: 0, line: { color: C.accent, width: 3 }
  });

  const layers = [
    {
      num: "1", title: "语法检查", icon: "🔍",
      desc: "SQLite EXPLAIN 解析 SQL\n语法错误直接拦截，零成本",
      color: C.accent, tag: "无 LLM 调用",
    },
    {
      num: "2", title: "执行对比", icon: "⚡",
      desc: "在临时 :memory: 库中执行\n排序后比较结果集（忽略顺序）",
      color: C.green, tag: "无 LLM 调用",
    },
    {
      num: "3", title: "语义验证", icon: "🧠",
      desc: "LLM 审查 SQL 逻辑正确性\n识别'歪打正着'的边界情况",
      color: C.amber, tag: "LLM 深度分析",
    },
  ];

  layers.forEach((layer, i) => {
    const y = 1.2 + i * 1.3;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 8.8, h: 1.1,
      fill: { color: C.darkBg2 },
      shadow: makeCardShadow()
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: y, w: 0.08, h: 1.1,
      fill: { color: layer.color }
    });

    // Number
    slide.addShape(pres.shapes.OVAL, {
      x: 1.0, y: y + 0.2, w: 0.55, h: 0.55,
      fill: { color: layer.color }
    });
    slide.addText(layer.num, {
      x: 1.0, y: y + 0.2, w: 0.55, h: 0.55,
      fontSize: 22, color: C.darkBg, bold: true, align: "center", valign: "middle", margin: 0
    });

    slide.addText(layer.icon + "  " + layer.title, {
      x: 1.75, y: y + 0.08, w: 4, h: 0.35,
      fontSize: 18, fontFace: FONT_BODY, color: layer.color, bold: true, margin: 0
    });
    slide.addText(layer.desc, {
      x: 1.75, y: y + 0.45, w: 4.5, h: 0.55,
      fontSize: 12, fontFace: FONT_BODY, color: C.textMuted, margin: 0
    });

    // Tag
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 7.8, y: y + 0.3, w: 1.4, h: 0.35,
      fill: { color: layer.color, transparency: 85 }
    });
    slide.addText(layer.tag, {
      x: 7.8, y: y + 0.3, w: 1.4, h: 0.35,
      fontSize: 9, color: layer.color, align: "center", valign: "middle", margin: 0
    });
  });

  // Error classification
  slide.addText("支持 7 种错误类型自动分类", {
    x: 0.6, y: 4.95, w: 8.8, h: 0.35,
    fontSize: 12, fontFace: FONT_BODY, color: C.textMuted, margin: 0
  });
  const errTypes = ["语法错误", "JOIN逻辑", "聚合/分组", "子查询", "WHERE条件", "窗口函数", "逻辑等价"];
  errTypes.forEach((e, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.6 + i * 1.28, y: 5.25, w: 1.15, h: 0.3,
      fill: { color: C.darkBg2 }
    });
    slide.addText(e, {
      x: 0.6 + i * 1.28, y: 5.25, w: 1.15, h: 0.3,
      fontSize: 10, color: C.textMuted, align: "center", valign: "middle", margin: 0
    });
  });
})();

// ============================================================
// SLIDE 7: UI Walkthrough
// ============================================================
(function () {
  const slide = addLightSlide("界面设计总览");

  // Three tabs
  const tabs = [
    {
      title: "📝 练习 Tab",
      items: [
        "对话式答题交互",
        "SQL 代码输入区 + 提交",
        "增量提示系统（3层）",
        "放弃查看答案 / 下一题",
        "即时判题结果 + 解析",
      ],
      color: C.blue600,
    },
    {
      title: "📊 分析报告 Tab",
      items: [
        "总体统计卡片",
        "能力维度雷达图",
        "答题历史记录表",
        "LLM 智能分析建议",
        "错误类型分布饼图",
      ],
      color: C.purple600,
    },
    {
      title: "🗄️ 数据浏览 Tab",
      items: [
        "完整 Schema SQL 展示",
        "各表数据预览",
        "Pandas DataFrame 渲染",
      ],
      color: C.green600,
    },
  ];

  tabs.forEach((tab, i) => {
    const x = 0.4 + i * 3.2;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.2, w: 2.95, h: 3.3,
      fill: { color: C.lightCard },
      shadow: makeCardShadow()
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.2, w: 2.95, h: 0.05,
      fill: { color: tab.color }
    });
    slide.addText(tab.title, {
      x: x + 0.15, y: 1.4, w: 2.65, h: 0.4,
      fontSize: 15, fontFace: FONT_BODY, color: tab.color, bold: true, margin: 0
    });
    tab.items.forEach((item, j) => {
      slide.addText(item, {
        x: x + 0.3, y: 1.9 + j * 0.45, w: 2.5, h: 0.35,
        fontSize: 11, fontFace: FONT_BODY, color: C.textDark, bullet: true, margin: 0
      });
    });
  });

  // Sidebar
  slide.addText("侧边栏面板", {
    x: 0.6, y: 4.8, w: 3, h: 0.35,
    fontSize: 14, fontFace: FONT_BODY, color: C.textDark, bold: true, margin: 0
  });
  const sidebarItems = ["API Key 设置（本地持久化）", "学习进度实时统计", "知识领域 / 难度选择", "一键生成数据库 / 题目"];
  sidebarItems.forEach((item, i) => {
    slide.addText(item, {
      x: 0.6 + (i % 2) * 4.6, y: 5.15 + Math.floor(i / 2) * 0.3, w: 4.3, h: 0.28,
      fontSize: 10, fontFace: FONT_BODY, color: C.textMuted, bullet: true, margin: 0
    });
  });
})();

// ============================================================
// SLIDE 8: Tech Stack
// ============================================================
(function () {
  const slide = addDarkSlide();
  slide.addText("技术栈", {
    x: 0.6, y: 0.3, w: 8.8, h: 0.7,
    fontSize: 32, fontFace: FONT_TITLE, color: C.textLight, bold: true, margin: 0
  });
  slide.addShape(pres.shapes.LINE, {
    x: 0.6, y: 0.9, w: 1.2, h: 0, line: { color: C.accent, width: 3 }
  });

  const stackItems = [
    { category: "前端", techs: ["Streamlit 1.57", "Plotly 雷达图", "Pandas DataFrame"], color: C.accent },
    { category: "后端引擎", techs: ["Python 3.12", "OpenAI SDK", "sqlite3 内置"], color: C.green },
    { category: "LLM", techs: ["DeepSeek-V4-Pro", "统一 Chat API", "5 Prompt 模板"], color: C.amber },
    { category: "数据", techs: ["SQLite (零配置)", "题库 + 历史表", "JSON 配置持久化"], color: C.accent2 },
    { category: "部署", techs: ["Electron 桌面壳", "一键启动 run.py", "虚拟环境隔离"], color: "F472B6" },
  ];

  stackItems.forEach((item, i) => {
    const x = 0.5 + i * 1.9;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.2, w: 1.7, h: 4.0,
      fill: { color: C.darkBg2 },
      shadow: makeCardShadow()
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: x, y: 1.2, w: 1.7, h: 0.06,
      fill: { color: item.color }
    });
    slide.addText(item.category, {
      x: x + 0.1, y: 1.45, w: 1.5, h: 0.35,
      fontSize: 13, fontFace: FONT_BODY, color: item.color, bold: true, align: "center", margin: 0
    });
    item.techs.forEach((tech, j) => {
      slide.addShape(pres.shapes.RECTANGLE, {
        x: x + 0.1, y: 2.1 + j * 0.7, w: 1.5, h: 0.55,
        fill: { color: C.darkBg }
      });
      slide.addText(tech, {
        x: x + 0.1, y: 2.1 + j * 0.7, w: 1.5, h: 0.55,
        fontSize: 11, fontFace: FONT_BODY, color: C.textLight, align: "center", valign: "middle", margin: 0
      });
    });
  });
})();

// ============================================================
// SLIDE 9: Summary & Roadmap
// ============================================================
(function () {
  const slide = addDarkSlide();

  // Decorative
  slide.addShape(pres.shapes.OVAL, {
    x: 8, y: 3.5, w: 6, h: 6,
    fill: { color: C.accent, transparency: 95 }
  });

  slide.addText("总结与展望", {
    x: 0.6, y: 0.3, w: 8.8, h: 0.7,
    fontSize: 32, fontFace: FONT_TITLE, color: C.textLight, bold: true, margin: 0
  });
  slide.addShape(pres.shapes.LINE, {
    x: 0.6, y: 0.9, w: 1.2, h: 0, line: { color: C.accent, width: 3 }
  });

  // Left: Achievements
  slide.addText("项目成果", {
    x: 0.6, y: 1.2, w: 4.5, h: 0.4,
    fontSize: 18, fontFace: FONT_BODY, color: C.green, bold: true, margin: 0
  });
  const achievements = [
    "完整的 SQL 学习闭环系统",
    "三层判题机制，7 类错误识别",
    "4 个知识领域 × 3 个难度等级",
    "增量提示 + 放弃查看答案",
    "能力雷达图 + 个性化建议",
    "本地 API Key 持久化",
    "22 个单元测试全覆盖",
  ];
  achievements.forEach((a, i) => {
    slide.addText([
      { text: "✓  ", options: { color: C.green } },
      { text: a, options: { color: C.textMuted } },
    ], {
      x: 0.8, y: 1.7 + i * 0.4, w: 4.3, h: 0.35,
      fontSize: 12, fontFace: FONT_BODY, margin: 0
    });
  });

  // Right: Future work
  slide.addText("后续扩展方向", {
    x: 5.5, y: 1.2, w: 4.0, h: 0.4,
    fontSize: 18, fontFace: FONT_BODY, color: C.amber, bold: true, margin: 0
  });
  const futures = [
    "多用户/账号系统",
    "题目收藏与错题复习",
    "SQL 执行计划可视化",
    "知识点覆盖均衡调度",
    "多模型切换对比",
    "社区题目分享",
  ];
  futures.forEach((f, i) => {
    slide.addText([
      { text: "→  ", options: { color: C.amber } },
      { text: f, options: { color: C.textMuted } },
    ], {
      x: 5.7, y: 1.7 + i * 0.4, w: 3.8, h: 0.35,
      fontSize: 12, fontFace: FONT_BODY, margin: 0
    });
  });

  // Quote
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 1.5, y: 4.5, w: 7, h: 0.8,
    fill: { color: C.darkBg2 }
  });
  slide.addText([
    { text: "'SQL 随身教练'\n", options: { italic: true, color: C.textLight, fontSize: 18 } },
    { text: "让每一个 SQL 学习者都能拥有自己的 AI 私人教练", options: { color: C.textMuted, fontSize: 13 } },
  ], {
    x: 1.7, y: 4.55, w: 6.6, h: 0.7,
    align: "center", valign: "middle", margin: 0
  });
})();

// === Generate PPT ===
pres.writeFile({ fileName: "c:/Users/lingod/Desktop/数据库大实验/SQL随身教练-展示.pptx" })
  .then(() => console.log("PPT generated successfully!"))
  .catch(err => console.error("Error:", err));
