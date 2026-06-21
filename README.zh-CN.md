# IGCSE & A-Level AI Revision Guide Skill

<p align="center">
  <img src="docs/assets/hero.svg" alt="IGCSE 与 A-Level AI 复习手册 Skill 封面" width="100%">
</p>

## 为什么要做这个 Skill

这个项目最早不是为了做一个“工具”，而是为了帮一个真实的孩子轻一点地走过转轨期。
我的儿子今年要参加 International GCSE 大考；他从公办体系转到国际课程还不到一年，
课堂语言几乎一下从全中文切换到全英文。知识点本身可以慢慢学，但新的语言、新的考试方式
和临近大考的时间压力叠在一起，很容易让孩子觉得自己被推着走。

我用 AI 做了一个学习、复习用的 Skill：让它围绕对应课程要求，把知识点拆成能理解的结构、
例题、图解和检查点。这个项目的初衷很简单：不是替孩子学习，而是把学习路上的噪音降下来，
利用人工智能帮助孩子更轻松、更有掌控感地面对学业。

<p align="center">
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation.html">
    <img src="docs/assets/intro-animation-preview.gif" alt="三大考试局复习手册 Skill 介绍动画预览" width="100%">
  </a>
</p>

<p align="center">
  <a href="README.md">English</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/">项目主页</a>
  ·
  <a href="https://mianbaofang.github.io/igcse-a-level-revision-guide/project-intro-animation.html">介绍动画</a>
  ·
  <a href="docs/PROJECT_DETAILS.md">项目详情</a>
  ·
  <a href="docs/PROJECT_OPERATIONS.md">维护说明</a>
  ·
  <a href="docs/IMAGE_MODEL_GUIDE.md">生图建议</a>
</p>

一个给 AI Agent 使用的复习手册 Skill：输入国内常用三大国际考试局的科目要求，
生成图文并茂、可打印的 International GCSE / International AS-A-level 学习复习手册。

当前版本以三大考试局为基础设计：

| 考试局 | 当前支持方式 |
|---|---|
| AQA | 支持从官网科目目录发现课程，并读取公开大纲 PDF。 |
| Edexcel | 会先根据科目名尝试匹配官方候选页面；无法唯一确认时列出候选，也支持用户直接提供官方科目页或大纲 PDF。 |
| CAIE | 会从官方科目索引匹配候选；无法唯一确认时列出候选，也支持官方科目页或大纲 PDF；遇到多个考试年份时会先确认年份。 |

说明：文档和用户提示里优先使用国内更常见的简称 AQA、Edexcel、CAIE；对应全称分别是 OxfordAQA / Oxford International AQA、Pearson Edexcel、Cambridge International / CAIE。

这套流程面向三大考试局统一设计：先读取官方大纲，再生成知识点讲解、例题、图文学习单元、复习题和 PDF。

## 快速使用

普通用户不需要安装 Python，也不需要看懂代码。把下面这个 Skill 链接发给你的
OpenClaw、Hermes 或其他支持 Skill 的 Agent：

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide/tree/main/skill
```

然后直接说：

```text
请安装这个 Skill，然后帮我生成 AQA Chemistry International GCSE 中文复习手册，并导出 PDF。
```

也可以这样说：

```text
帮我生成 Edexcel Accounting International GCSE 复习手册。
帮我生成 Cambridge IGCSE Economics 2027 考试用的中文学习手册。
帮我生成 AQA Mathematics 9260 复习手册，需要图文例题和最终复习题。
```

开始生成前，Agent 应先确认四件事：

1. 考试局、课程阶段、科目和代码，必要时确认官方链接。
2. 考试年份，尤其是 Cambridge 页面同时列出多个年份范围时。
3. 输出语言：中文或英文。手册正文、标签、例题和配图提示只使用一种语言。
4. 讲解风格：严谨、轻松、生活化、故事性、侦探推理、闯关式等。

注意：不需要在一开始选择生图模型。基础手册先生成，之后 Agent 会告诉你有多少张复杂信息图需要生成或复核。
如果你有可调用的生图 API、Skill、脚本或已经生成好的图片目录，Agent 应该自动调用该路线生成图片，并自动导入或挂接到手册；如果没有，就使用 SVG 草图兜底，并提示复杂图需要复核。

## 会生成什么

每次生成会输出一个完整手册包：

```text
outputs/chemistry-9202/
  guide.html                 可预览、可打印的学习手册
  guide.pdf                  PDF 文件
  sections/                  分章节手册内容，便于 Agent 复查
  images/                    SVG 草图、信息图资产和配图清单
  run-options.json           本次确认的科目、语言和讲解风格
  guide-plan.json            知识点、例题和复习任务规划
  qualification.json         课程与来源信息
  validation.json            完整性检查结果
  handbook-package.json      最终交付清单
```

手册内容包括：

- 官方大纲整理出的知识点结构；
- 学生能读懂的讲解；
- 原创例题、步骤和答案检查点；
- 适合图文讲解的知识点与例题；
- 简单 SVG 图和复杂信息图需求清单；
- 最终备考复习题；
- 可打印 HTML/PDF。

## 效果预览

| Mathematics | Economics | Chemistry |
|---|---|---|
| <img src="docs/assets/sample-math-guide.png" alt="数学复习手册图文例题截图" width="100%"> | <img src="docs/assets/sample-economics-guide.png" alt="经济学复习手册信息图截图" width="100%"> | <img src="docs/assets/sample-chemistry-guide.png" alt="化学复习手册信息图截图" width="100%"> |

这些截图只是展示最终手册长什么样，不代表项目只支持这三门课。

## 三大考试局支持范围

| 考试局 | International GCSE | International AS-A-level | 当前说明 |
|---|---:|---:|---|
| AQA | 支持 | 支持 | 可从官网科目目录发现课程。 |
| Edexcel | 支持 | 支持 | 根据科目名匹配官方候选；多个候选时让用户选择；官方 URL/PDF 可作为精确输入。 |
| CAIE | 支持 | 支持 | 从官方科目索引匹配候选；多个候选时让用户选择；官方 URL/PDF 可作为精确输入；多年份页面会先确认考试年份。 |
| OCR、WJEC/Eduqas、CCEA 等其他英国考试局 | 暂不支持 | 暂不支持 | 不在当前版本范围内。 |

项目当前聚焦国内常用的 AQA、Edexcel 和 CAIE。
以后可以继续扩展，但不会把未支持的考试局写成已经支持。

## 图文与讲解风格

孩子愿意看的手册不能只有文字。生成流程会做两次判断：

1. 先根据官方大纲生成知识点、讲解和例题。
2. 再判断哪些知识点或例题需要图文结合讲解。

简单、可复现的结构图使用 SVG，例如概念地图、基础几何图、粒子示意图、流程图。
复杂内容先生成配图需求清单，例如实验装置、复杂几何、电路、经济学图表、带大量文字的信息图。

如果用户没有可调用的生图模型，图表、坐标轴、曲线、概率树、简单几何等可精确表达的内容会走脚本化科学矢量图 fallback：输出可编辑 SVG，并记录来源、标签和复核风险。它不替代复杂信息图；复杂信息图仍然等待外部模型或人工审核后的图片资产。

推荐的外部生图模型包括：

- OpenAI GPT Image 2.0；
- Qwen Image 2.0 Pro；
- SenseNova U1 Fast。

这些只是推荐选项，不代表每个用户都能直接调用。用户需要自己提供可用的 API、Skill、脚本或图片目录。
生图只负责解释已经选中的知识点，不能编造大纲里没有的考试结论。

讲解风格也可以选择：严谨备考、轻松愉快、生活场景、故事化、侦探推理、闯关式等。
默认使用原创表达，不复刻受保护角色或世界观。

生成链路里也加入了一个轻量“反模板腔”检查：会先清理“总之”“综上所述”“值得注意的是”
这类安全可删的 AI 腔过渡语；如果仍然出现明显模板化表达，验证报告会给出 warning，方便后续复核。

设计参考说明：讲解文字的反模板腔检查借鉴了 `qiaomu-novel-generator` 里的 anti-AI language gate 思路；
科学矢量 SVG fallback 借鉴了
[`Yuan1z0825/nature-skills`](https://github.com/Yuan1z0825/nature-skills)
里 `nature-figure` 的 figure contract 思路。两者都已经改造成复习手册场景，不是运行时依赖。

## 语言策略

生成前必须选择一种输出语言：

- 选择中文，学生看到的正文、标签、例题和配图提示都用中文。
- 选择英文，学生看到的正文、标签、例题和配图提示都用英文。
- 不做中英拼接标签。
- 官方英文术语可以保留在来源文件或复核附录里，学生正文尽量保持单一语言。

## 从 v0.1.0 到现在，核心能力更新了什么

README 只保留会影响 Skill 实际生成流程的变化；完整历史统一放在 [CHANGELOG.md](CHANGELOG.md)。

- **v0.2.0：** 从 AQA 单线升级为 AQA、Edexcel、CAIE 三大考试局框架；加入语言锁、先生成基础手册再处理复杂配图、SVG 兜底风险提示和跨学科回归样例。
- **v0.2.1：** 修复 Accounting 和 Economics 实际生成时暴露的问题，包括中文术语、会计学科显示名、外部生成图片渲染、PDF 导出超时和验证覆盖。
- **v0.2.2：** 评审后强化 Skill 流程门槛：先确认科目/年份/语言/讲解风格；Edexcel/CAIE 出现多个官方候选时返回给用户选择；候选检查生成的 scratch 手册不能当最终交付。
- **v0.2.7：** 清理公开文档里的本地私有路径，删除重复 CLI provider resolver，并把中文占位符、重复例题纳入错误级验证。
- **v0.2.8：** 加固生成引擎：统一三大考试局下载与文本清洗入口，新增 Pearson Edexcel 表格型大纲解析，PDF 导出优先用 Playwright 并回退到 Chrome/Edge，补上 CLI `discover` / `generate` 覆盖，同时把 `Content unit` 兜底主题和缺失考试结构解析列为错误。
- **v0.2.9：** 补齐剩余审查闭环：CI 改为系统/Python 版本矩阵并加入覆盖率门槛；新增跨学科视觉路由基准；Physics 力与运动会进入信息图 brief；修复 `preparation` 误命中 `ratio`、`graph` 误命中 `ph` 这类 SVG 错配；并把 HTML 渲染器拆成页面结构、SVG 模板和 CSS 模块。
- **v0.2.10：** 修复第二轮审查和真实样本暴露的问题：Edexcel 不再把 Pearson 版权/前言页接进 topic；CAIE 跳过 content overview 和 AO 表；中文手册标题不再退化成“知识单元 1”式占位；HTML 增加快速目录和阅读宽度约束；SVG 兜底图改为会计、经济、数学、物理、化学等学科专用模板。
- **v0.2.11：** 梳理视觉资产验证摘要：外部模型生成的位图信息图、SVG 兜底图、仍待外部生成或审核的信息图 brief 分开统计，避免 prompt-queue 运行被误判成“没有任何配图产物”。
- **v0.2.12：** 清理 Skill 和项目说明中的生图逻辑：生图不再写成生成前必选项，而是基础手册完成后的配图生成或复核步骤；说明图也统一为 AQA、Edexcel、CAIE 三大考试局流程。
- **v0.2.13：** 优化生成手册前三页：封面只保留考试局、课程、科目、课程代码、大纲版本和考试年份；次页去掉内部工程词；复习路线表格删除多余的“学习路径”列。
- **v0.2.14：** 完成第三轮审计中可落地的剩余项：拆分 `guide_plan.py` 大文件，CI 加入 mypy 和 Codecov 覆盖率上传，补强 Pearson/CAIE 解析测试、加密 PDF 测试和 topic-aware 叙事化讲解；内置生图模型继续保持不做。
- **v0.2.15：** 完成第三轮审计收尾清理：公开仓库移除本地生图 router 脚本，发布流程改为导入外部生成并复核过的信息图资产，并补上 guide-plan、provider PDF 选择、PDF 导出错误和按 topic 切换故事化讲解的直接回归测试。
- **v0.2.16：** 修正生图流程说明：外部生图不等于让用户手动搬图。如果用户有可调用的生图 Skill、API、脚本或生成好的图片目录，Agent 应该在基础手册完成后自动调用或导入，并把复核后的图片挂接进手册。
- **v0.2.17：** 生成器加入反模板腔语言门：讲解和例题会清理安全可删的 AI 腔过渡语，验证器会对残留模板化表达给出 warning；主页和 README 也补充 anti-AI language 与 nature-figure 的设计参考说明。
- **v0.2.18：** 完成第四轮审计加固：信息图渲染从主 HTML 渲染器拆出，例题生成复用统一学科匹配逻辑，修复考试时长和百分比权重解析，补充例题与公共解析器单元测试，并把 CI 覆盖率门槛提升到 70%。
- **v0.2.19：** 修复第五轮审计发现的产物问题：未知或 demo 来源不再默认显示成 AQA；反模板腔检测覆盖更多中英文 AI 套话；并补上信息图三种渲染分支、数学/生物/经济/通用例题路径和 `python -m intl_exam_guide` 入口测试。
- **v0.2.20：** 闭环第六轮审计：共享渲染图标，防止旧 ignored `outputs/` 被当作发布证据，收紧例题生成器架构守卫，并扩展例题生成与 PDF 导出分支测试。
- **v0.2.21：** 闭环第八轮测试覆盖缺口：新增生成手册渲染契约测试，覆盖封面身份信息、样式与打印布局、视觉 manifest、外部生成位图复用、SVG 兜底、模块化手册打包，以及 Playwright 从 Chrome 降级到 Edge 的 PDF 导出路径。
- **v0.2.22：** 闭环第九轮渲染覆盖缺口：给 `html.py` 增加直接契约测试，覆盖完整 HTML 入口、`render_topics()`、知识点卡片、概念图、故事化讲解、例题卡、视觉例题路由、来源附录、考试结构兜底、导航和 topic 标题本地化。
- **v0.2.23：** 闭环第十轮 P3 审计项：弱断言改为精确等值，补齐中文渲染路径直接测试，恢复发布所需的新鲜 demo 证据，并为 `svg_templates.py` 与 `text.py` 增加专用测试。
- **v0.2.24：** 闭环第十一轮 P3 建议：为讲解风格和本地化 helper 增加专用测试，补齐中文 HTML helper 与 `render_html()` 中文入口直接覆盖，覆盖 SVG 斜杠换行和超长文本截断，raw-key 扫描命令与发布清单对齐，并移除英文概念 fallback SVG 中不会被生产路径调用的中文分支。

## 开发者快速开始

普通用户可以跳过这一节。只有想修改 Python 引擎或本地调试时才需要看。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m intl_exam_guide generate --query chemistry --level igcse --language zh-CN --explanation-style friendly --out ./outputs/chemistry-9202
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m intl_exam_guide generate --query chemistry --level igcse --language zh-CN --explanation-style friendly --out .\outputs\chemistry-9202
```

常用检查：

```bash
python -m pytest --cov --cov-report=term-missing --cov-fail-under=70 -q
python -m ruff check .
python -m compileall -q src tests scripts
python scripts/scan_for_raw_keys.py . ./outputs
```

## 目录结构

```text
src/intl_exam_guide/
  providers/      各考试局官方页面读取与解析
  parsing/        PDF 文本抽取
  planning/       知识点、例题和配图需求规划
  rendering/      HTML 与 PDF 渲染
  validation/     完整性检查
skill/            Agent 使用的 Skill 说明
docs/             项目详情、准确性政策、示例和展示页面
tests/            测试与回归样例
```

## 版权与来源

不要把下载的官方 PDF、past papers、mark schemes 或复制来的真题内容提交到仓库。
公开样例应使用原创讲解、原创练习卡和必要的来源信息。

给孩子正式备考使用前，建议由老师或熟悉大纲的人复核深度例题和答案。

## License

MIT.
