# Project Details / 项目详情

## English

IGCSE & A-Level AI Revision Guide Skill is an open-source Skill and Python pipeline for
generating image-rich study/revision handbooks from official International GCSE
and International AS-A-level syllabus/specification sources.

It is intentionally narrower than a generic AI education platform. The core
principle is stable across subjects: confirm how the user wants the handbook,
then turn the official syllabus into a reusable revision-handbook framework.

1. confirm the user's subject/provider, required exam year, output language, and explanation style;
2. retrieve the relevant official syllabus/specification source;
3. keep official PDFs out of the repository;
4. extract detailed syllabus units and assessment structure;
5. keep review metadata beside each knowledge unit;
6. generate student-facing explanations and original worked examples in the
   chosen style;
7. run a second pass to decide which knowledge points and examples need visuals;
8. use deterministic SVG for simple diagrams or a user-selected infographic
   model for complex visual explanations;
9. render the handbook package: HTML, PDF, `sections/`, `images/`, manifests,
   source metadata, and validation;
10. validate that the output is complete enough to review and hand to the user.

### What Makes It Different

- **Syllabus-grounded**: handbook content starts from the official syllabus.
- **Repository-safe sources**: public PDFs are used at runtime, not committed.
- **Review metadata**: topic blocks keep enough context for later checking.
- **Explicit language policy**: the student-facing handbook follows one selected
  language. Official source text stays available for traceability in structured
  files or a separated review appendix, not mixed into the topic body.
- **Visual learning layer**: the generator first builds source-bound knowledge
  points and practice examples, then analyzes which items need visual
  explanation. Simple visuals use deterministic SVG; complex lab, geometry,
  circuit, economics, or text-heavy infographic needs are routed to source-bound
  visual briefs and prompt queues unless a callable image route or imported
  asset directory is available.
- **Narrative explanation modes**: topic blocks can be explained as life
  scenes, detective reasoning, or anime-quest style study missions while
  avoiding protected-IP copying by default.
- **Child-safety mindset**: examples are original and source-bound, and should
  be reviewed by a subject specialist before high-stakes exam preparation.
- **International qualification structure**: International GCSE is handled as
  linear; International AS-A-level is handled as modular.
- **Website listing checks**: OxfordAQA subject buttons are recorded as the
  blue International GCSE listing or red International AS-A-level listing when
  that metadata is available.

### Current MVP

The current MVP can generate guides for AQA International GCSE and
International AS-A-level qualification pages, plus Pearson Edexcel and
Cambridge International / CAIE candidate discovery with official URL/PDF
fallbacks. It has been verified on:

The entries below are validation samples, not a subject support matrix. The
provider/parser pipeline is designed to work across discovered OxfordAQA
qualification pages; unprofiled subjects fall back to source-bound generic
examples instead of borrowing Mathematics, Chemistry, or Economics templates.

- Offline synthetic demo: no network, no copyrighted PDF, handbook package
  output, validation issues: none.
- International GCSE Mathematics (9260): detailed PDF extraction produces 90
  syllabus units, 180 worked/practice cards, 43 SVG-safe visuals, and 39
  complex infographic briefs.
- International GCSE Chemistry (9202): detailed PDF extraction produces 35
  syllabus units, 70 worked/practice cards, 14 SVG-safe visuals, and 18 complex
  infographic briefs.
- International AS and A-level Chemistry (9620): 3 topic groups, 6 assessment
  entries, HTML/PDF output, no validation issues.
- International GCSE Economics (9214): detailed PDF extraction produces 38
  syllabus units, 76 worked/practice cards, and 38 complex infographic briefs.
- International AS and A-level Business (9725) revised: qualification-page
  lookup, assessment extraction, HTML/PDF output, and validation checks. This verifies code
  lookup when the subject listing omits the qualification code.

The three public release showcase guides are treated as final only after their
selected image provider has generated all infographic assets, those assets have
been merged into `guide.html`, `guide.pdf` has been exported, and
`scripts/verify_release_samples.py --outputs-root <outputs>` passes without
`--allow-pending`.

The repository commits the source, skill package, documentation, screenshots,
and intro animation. Full `outputs/*-sample/` folders are reproducible release
artifacts and are kept out of Git because the image-rich packages are large.

Listing discovery has also been audited across the live OxfordAQA subject index:
17 subject pages, 48 qualification links, 31 International GCSE listings, 17
International AS-A-level listings, and no unknown listing types.

The same audit opened all 48 discovered qualification pages. Every page produced
at least one topic group, at least one assessment structure entry, and a
specification link, with no blue/red listing conflict. The parser now covers
Science-style heading lists, Economics-style `strong` headings with paragraph
points, revised Business `span` lists, Literature text-list labels, new
History/Sociology assessment-derived topic groupings, and project-based learning
components.

### Provider Scope

The current product covers the three China-market provider families in staged
form. Do not describe it as covering all International GCSE or International
AS-A-level providers, and do not claim full Pearson/Cambridge catalogue
crawling yet.

| Provider / exam board | Status | Notes |
|---|---|---|
| AQA / Oxford International AQA Examinations | implemented | Catalogue discovery plus qualification parsing. |
| Pearson Edexcel | implemented MVP | Subject-name candidate discovery for common official page patterns; official URL/PDF fallback. |
| Cambridge International / CAIE | implemented MVP | Official subject-index candidate discovery; official URL/PDF fallback; `exam_year` required for multi-range pages. |
| OCR, WJEC/Eduqas, CCEA, and other UK boards | out of scope | Do not promise support in README or generated examples. |

Market comments about relative exam difficulty, vocabulary load, or scoring
friendliness should stay in planning notes until reviewed by a subject expert.
They are useful positioning context, but they are not official provider facts.

### Roadmap

1. Improve PDF section segmentation for subject content, command words,
   assessment objectives, appendices, and version history.
2. Add provider fixtures with synthetic test PDFs.
3. Add a reviewed authoring adapter for deeper worked examples.
4. Add richer subject-specific SVG diagram templates for common question types.
5. Add configurable explanation-style presets for different student audiences.
6. Add an optional image-provider adapter for reviewed educational
   illustrations, with model/prompt/source metadata recorded for every asset.
7. Add visual regression snapshots for generated HTML.
8. Expand Pearson Edexcel and Cambridge International / CAIE beyond candidate
   discovery MVP only after provider fixtures and quality gates are stable.

## 中文

IGCSE & A-Level AI Revision Guide Skill 是一个开源流水线，用来为 OxfordAQA International
GCSE 与 International AS-A-level 学科生成可追溯来源的复习指南。

它不是泛泛的 AI 教育平台。核心原理对各学科通用：以官方 specification 为输入，
再把大纲内容融合进统一的学习复习手册框架。

1. 先确认用户选择的科目、输出语言、生图路线和讲解风格；
2. 找到官方 qualification 页面；
3. 在运行时下载公开 course specification；
4. 抽取详细 syllabus units、assessment structure 和 PDF 页文本；
5. 给每个知识单元匹配页码级 source snippets；
6. 按用户选择的风格生成学生能读懂的讲解和原创例题；
7. 二次分析哪些知识点和例题需要图文结合；
8. 简单图用确定性 SVG，复杂图文讲解交给用户选择的信息图模型；
9. 渲染完整交付包：HTML、PDF、`sections/`、`images/`、manifest、source metadata
   和 validation；
10. 校验输出是否完整到足以交付用户或进入人工复核。

### 它和普通 AI 总结器有什么不同

- **大纲优先**：官方页面和 PDF 是权威来源。
- **运行时下载**：公开 PDF 不提交到仓库，避免版权和版本问题。
- **页码级追溯**：topic block 可以显示匹配到的 source snippets。
- **明确语言策略**：学生看到的手册正文跟随一种输出语言；官方原文保留在结构化文件
  或独立复核附录中，不混入 topic 正文。
- **图文学习层**：先生成可追溯的基础知识点和例题，再由 AI 判断哪些条目需要图文
  结合讲解。简单图用确定性 SVG；复杂实验装置、几何、电路、经济学图表或单语言信息图
  交给用户选择的生图模型，并记录 prompt/source metadata。
- **叙事讲解模式**：topic block 可以切换成生活场景、侦探推理、动漫闯关感等讲法，
  默认不复刻受保护 IP。
- **给孩子用的谨慎逻辑**：例题必须原创、绑定来源，并建议正式备考前由学科老师复核。
- **区分资格结构**：International GCSE 按 linear qualification 处理；
  International AS-A-level 按 modular qualification 处理。
- **记录网站分组**：如果从 OxfordAQA subject 页面发现 qualification，会记录蓝色
  International GCSE listing 或红色 International AS-A-level listing。

### 当前 MVP

当前 MVP 已验证：

下面列的是验证样例，不是科目支持范围。provider/parser 流程面向已发现的
OxfordAQA qualification pages；暂未做专门 profile 的科目会使用基于官方大纲的
通用例题和图文判断，不会借用 Mathematics、Chemistry 或 Economics 的模板。

- Offline synthetic demo：无网络、无版权 PDF，能生成完整 handbook package，
  validation 无问题。
- International GCSE Mathematics (9260)：PDF 详细抽取 90 个 syllabus units，
  生成 180 张例题/练习卡、43 个 SVG-safe visuals 和 39 个复杂信息图 briefs。
- International GCSE Chemistry (9202)：PDF 详细抽取 35 个 syllabus units，
  生成 70 张例题/练习卡、14 个 SVG-safe visuals 和 18 个复杂信息图 briefs。
- International AS and A-level Chemistry (9620)：3 个 topic groups、6 个
  assessment entries、HTML/PDF 输出、validation 无问题。
- International GCSE Economics (9214)：PDF 详细抽取 38 个 syllabus units，
  生成 76 张例题/练习卡和 38 个复杂信息图 briefs。
- International AS and A-level Business (9725) revised：能通过 qualification page
  lookup 抽取 assessment structure，生成 HTML/PDF 并通过 validation。这个样例验证
  subject listing 没有代码时，代码查询仍然会进入详情页精确匹配。

三份公开发布用 showcase guides 只有在所选生图 provider 生成全部信息图、
图片合并进 `guide.html`、导出 `guide.pdf`，并且
`scripts/verify_release_samples.py --outputs-root <outputs>` 不带
`--allow-pending` 通过之后，才算最终完成。
这三份是首页展示和发布验收样例，不是生成器的科目支持上限。

仓库提交源码、Skill 包、文档、截图和介绍动画；完整的
`outputs/*-sample/` 目录是可复现发布产物，因为图文版 HTML/PDF 包体积较大，
不直接放进 Git。

同时已对 live OxfordAQA subject index 做 discovery audit：17 个 subject pages、
48 个 qualification links、31 个 International GCSE listings、17 个
International AS-A-level listings，没有 unknown listing types。

同一轮审计还打开了全部 48 个 qualification pages。每个页面都能抽取至少一个
topic group、至少一个 assessment structure entry 和一个 specification link，
并且没有蓝色/红色 listing 冲突。解析器已经覆盖 Science 的 heading/list 结构、
Economics 的 strong heading + paragraph points、修订版 Business 的 span 列表、
Literature 的 text-list 标签、History/Sociology 从 assessment 回推 topic 的结构，
以及 project-based learning 的项目组件。

### Provider 范围

当前产品只实现 OxfordAQA，不应写成覆盖全部 International GCSE 或
International AS-A-level provider。国内市场路线图是：

| Provider / exam board | 状态 | 备注 |
|---|---|---|
| OxfordAQA / Oxford International AQA Examinations | 已实现 | 当前 parser、renderer、样例和 validation 都围绕这个网站构建。 |
| Pearson Edexcel | 计划支持 | 等 OxfordAQA fixtures 和质量门槛稳定后再加。 |
| Cambridge International / CAIE | 计划支持 | 作为独立 provider 实现，不复用 OxfordAQA 的网页假设。 |
| OCR、WJEC/Eduqas、CCEA 等其他英国考试局 | 暂不支持 | README 和样例里都不承诺覆盖。 |

关于考试难度、词汇负担、得分友好度这类市场判断，只能作为 planning note，
不能写成官方事实或产品能力，除非经过学科老师或升学顾问复核。

### 后续路线

1. 强化 PDF 分段：subject content、指令词、assessment objectives、
   appendices、version history。
2. 用合成 PDF fixtures 补测试，避免提交 OxfordAQA PDF。
3. 增加经过审核的 authoring adapter，生成更深度 worked examples。
4. 为常见题型增加更专业的学科 SVG 图解模板。
5. 增加可配置的 explanation-style presets，适配不同学生的阅读偏好。
6. 增加可选 image-provider adapter，用于经过复核的教学插图，并记录每张图的
   model、prompt、source metadata 和 review status。
7. 增加 HTML 视觉回归检查。
8. OxfordAQA 稳定后，按 Pearson Edexcel、Cambridge International / CAIE
   的顺序扩 provider。
