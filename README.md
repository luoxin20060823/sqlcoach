# SQL随身教练

基于 DeepSeek 大模型 Agent 的 SQL 辅助学习系统。形成"建库 → 出题 → 判题 → 解析 / 答疑 → 分析"的完整闭环。

## ✨ 功能亮点

- 🗄️ **预置 4 个开箱即用数据库**（学生 / 电商 / 图书 / 人事），点一下立刻开始，无需等待 LLM
- 🆕 **自定义业务领域**：自己输入领域名（如「医院挂号系统」）也能 AI 生成
- 📝 **15 种 SQL 题型 + 3 档难度**，可指定类型或随机出题
- ✅ **快速判题**：默认走"语法 + 执行结果"双层校验，秒级反馈；可选 LLM 语义判题用于"碰巧结果对"的复核
- 📖 **错题解析 / 多轮自由答疑**
- 🔁 **错题复习 Tab**：列出做错的题，重新作答
- 📊 **学习报告**：能力雷达图 + 错误分布饼图 + 智能建议，支持 Markdown 导出
- ⚡ **预取下一题**：你做题时后台静默生成下一题，提交后秒切

## 🚀 性能优化（与初版对比）

| 场景 | 初版 | 现在 |
|---|---|---|
| 首次生成 4 个常用数据库 | 每次调 LLM ~30s | **预置直接加载 < 1ms** |
| 同领域第二次生成 | 重新调 LLM | **本地缓存命中** |
| 判题（执行结果一致） | 必调 LLM ~5-15s | **默认不调 LLM，秒返** |
| 答对后优化建议 | 必调 LLM ~5-10s | **默认关闭，可选** |
| 批量生成题目 | 串行 | **并发，4 倍提速** |
| LLM JSON 解析 | 手撕 markdown | **`response_format=json_object`** |
| max_tokens | 4096 | **题目 1024 / 判题 768** |
| 题库复用 | 无 | **同条件先抽老题** |

整体体验：从"点一次等十几秒"变成"点一次秒响应"。

## 🚦 快速开始

```bash
pip install -r requirements.txt
streamlit run app.py
# 或 python run.py
```

1. 在侧边栏输入 DeepSeek API Key（可选勾选"记住"持久化保存）
2. 选择领域（4 个内置 → 0 等待；自定义 → 走 LLM）
3. 点『生成数据库』，再点『生成题目』开始练习
4. SQL 编辑器中作答，先『运行』看结果，再『提交』判定

## 🛠️ 项目结构

```
agent/                    Agent 模块
├── llm.py                统一 LLM 客户端（含批量并发、JSON Mode）
├── schema_gen.py         数据库生成（预置 + 缓存 + LLM 三级回落）
├── question_gen.py       题目生成（题库复用 + 并发批量）
├── judge.py              三层判题引擎（语法 → 执行 → 可选 LLM 语义）
├── tutor.py              错题解析 + 多轮答疑
├── analyzer.py           学习分析
└── preset_schemas.py     4 个内置数据库 SQL
db/store.py               SQLite 持久化（题库/历史/Schema 缓存/错题）
ui/                       Streamlit 各 Tab
├── practice.py           练习 Tab
├── review.py             错题复习 Tab
├── chat.py               自由答疑 Tab
├── report.py             分析报告 Tab（含 Markdown 导出）
└── browser.py            数据浏览 Tab
prompts/templates.py      所有 Prompt（精简版）
config.py                 配置 + 用户偏好持久化
```

## ⚙️ 高级设置

侧边栏「⚙️ 高级设置」可调：

- LLM 语义判题：默认关闭。开启后判题更严格，但每题多花 5~15s
- 答对后自动优化建议：默认关闭
- 预取下一题：默认开启
- 题库复用：默认开启

## 🧪 运行测试

```bash
pytest -q
```

## 🔧 技术栈

- Python 3.10+
- Streamlit 1.31+ / Plotly / Pandas
- SQLite（题库 + 答题记录 + Schema 缓存）
- DeepSeek API（OpenAI 兼容协议）
- Electron（可选，桌面包装）


## 🌐 在线部署（Streamlit Community Cloud）

本项目已适配 Streamlit Cloud 一键部署：

1. Fork 或 clone 本仓库到自己的 GitHub
2. 访问 https://share.streamlit.io ，用 GitHub 账号登录
3. 点击「New app」，选择本仓库，主文件填 `app.py`，Python 版本会从 `runtime.txt` 读取
4. 部署完成后会得到形如 `https://<你的用户名>-sql-coach.streamlit.app` 的永久网址
5. 进入应用后，在侧边栏粘贴自己的 DeepSeek API Key 即可使用

> **注意**：API Key 不要写进代码或提交到 git。Streamlit Cloud 也支持在 App 设置 → Secrets 里配置环境变量 `DEEPSEEK_API_KEY`，本项目会自动读取。
