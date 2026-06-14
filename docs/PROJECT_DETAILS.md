# Project Details / 项目详情

## English

International Exam Guide is an open-source pipeline for generating
source-traceable revision guides for OxfordAQA International GCSE and
International AS/A-level subjects.

It is intentionally narrower than a generic AI education platform. The first
goal is to make one thing reliable:

1. discover the official qualification page;
2. download the public course specification at runtime;
3. extract syllabus topics, assessment structure, and page text;
4. record subject-page listing metadata where available;
5. attach page-level snippets to topics;
6. generate a guide plan;
7. render deterministic concept-map diagrams from syllabus points;
8. render HTML/PDF;
9. validate that the output is complete enough to review.

### What Makes It Different

- **Specification-first**: the official page and PDF are the authority.
- **Runtime downloads**: public PDFs are not committed to the repository.
- **Page-level traceability**: topic blocks can show matched source snippets.
- **Explicit language policy**: official syllabus names stay in OxfordAQA
  English, while template labels are bilingual; topic translations require a
  reviewed glossary or subject-specialist pass.
- **Deterministic diagrams**: concept maps use extracted topic points instead of
  unsourced illustration prompts.
- **Child-safety mindset**: the generator avoids fully invented numerical
  answers until a reviewed authoring layer is available.
- **International qualification structure**: International GCSE is handled as
  linear; International AS/A-level is handled as modular.
- **Website listing checks**: OxfordAQA subject buttons are recorded as the
  blue International GCSE listing or red International AS/A-level listing when
  that metadata is available.

### Current MVP

The current MVP can generate guides for OxfordAQA International GCSE and
International AS/A-level qualification pages. It has been verified on:

- Offline synthetic demo: no network, no copyrighted PDF, HTML output,
  validation issues: none.
- International GCSE Chemistry (9202): 10 topics, 2 assessment papers, HTML/PDF
  output, no validation issues.
- International AS and A-level Chemistry (9620): 3 topic groups, 6 assessment
  entries, HTML/PDF output, no validation issues.
- International GCSE Economics (9214): 2 broad syllabus topics, 2 assessment
  papers, HTML/PDF output, no validation issues.
- International AS and A-level Business (9725) revised: 2 broad topic groups, 4
  assessment entries, HTML/PDF output, no validation issues. This verifies code
  lookup when the subject listing omits the qualification code.

Listing discovery has also been audited across the live OxfordAQA subject index:
17 subject pages, 48 qualification links, 31 International GCSE listings, 17
International AS/A-level listings, and no unknown listing types.

The same audit opened all 48 discovered qualification pages. Every page produced
at least one topic group, at least one assessment structure entry, and a
specification link, with no blue/red listing conflict. The parser now covers
Science-style heading lists, Economics-style `strong` headings with paragraph
points, revised Business `span` lists, Literature text-list labels, new
History/Sociology assessment-derived topic groupings, and project-based learning
components.

### Provider Scope

The current product is OxfordAQA-only. Do not describe it as covering all
International GCSE or International AS/A-level providers. The China-market
roadmap is:

| Provider / exam board | Status | Notes |
|---|---|---|
| OxfordAQA / Oxford International AQA Examinations | implemented | Current parser, renderer, samples, and validation are built around this site. |
| Pearson Edexcel | planned | Add only after OxfordAQA fixtures and quality gates are stable. |
| Cambridge International / CAIE | planned | Add as a separate provider with its own source model and qualification structure. |
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
5. Add visual regression snapshots for generated HTML.
6. Add Pearson Edexcel, then Cambridge International / CAIE, only after
   OxfordAQA is stable.

## 中文

International Exam Guide 是一个开源流水线，用来为 OxfordAQA International
GCSE 与 International AS/A-level 学科生成可追溯来源的复习指南。

它不是泛泛的 AI 教育平台，而是先把一个问题做稳：

1. 找到官方 qualification 页面；
2. 在运行时下载公开 course specification；
3. 抽取 syllabus topics、assessment structure 和 PDF 页文本；
4. 尽量记录 subject 页面上的蓝色/红色 listing 元数据；
5. 给 topic 匹配页码级 source snippets；
6. 生成 guide plan；
7. 用 syllabus points 生成确定性 concept-map diagrams；
8. 渲染 HTML/PDF；
9. 校验输出是否完整到足以进入人工复核。

### 它和普通 AI 总结器有什么不同

- **大纲优先**：官方页面和 PDF 是权威来源。
- **运行时下载**：公开 PDF 不提交到仓库，避免版权和版本问题。
- **页码级追溯**：topic block 可以显示匹配到的 source snippets。
- **明确语言策略**：官方 syllabus 名称保留 OxfordAQA 英文原文，模板标签采用双语；
  topic 中文翻译需要经过 glossary 或学科老师复核。
- **确定性图解**：concept maps 只使用抽取出的 topic points，不添加无来源内容。
- **给孩子用的谨慎逻辑**：在没有审核 authoring layer 前，不编造完整数值答案。
- **区分资格结构**：International GCSE 按 linear qualification 处理；
  International AS/A-level 按 modular qualification 处理。
- **记录网站分组**：如果从 OxfordAQA subject 页面发现 qualification，会记录蓝色
  International GCSE listing 或红色 International AS/A-level listing。

### 当前 MVP

已在两个真实 OxfordAQA 页面上验证：

- International GCSE Chemistry (9202)：10 个 topics、2 个 assessment papers、
  HTML/PDF 输出、validation 无问题。
- International AS and A-level Chemistry (9620)：3 个 topic groups、6 个
  assessment entries、HTML/PDF 输出、validation 无问题。
- International GCSE Economics (9214)：2 个 broad syllabus topics、2 个
  assessment papers、HTML/PDF 输出、validation 无问题。
- International AS and A-level Business (9725) revised：2 个 broad topic
  groups、4 个 assessment entries、HTML/PDF 输出、validation 无问题。这个样例验证
  subject listing 没有代码时，代码查询仍然会进入详情页精确匹配。

同时已对 live OxfordAQA subject index 做 discovery audit：17 个 subject pages、
48 个 qualification links、31 个 International GCSE listings、17 个
International AS/A-level listings，没有 unknown listing types。

同一轮审计还打开了全部 48 个 qualification pages。每个页面都能抽取至少一个
topic group、至少一个 assessment structure entry 和一个 specification link，
并且没有蓝色/红色 listing 冲突。解析器已经覆盖 Science 的 heading/list 结构、
Economics 的 strong heading + paragraph points、修订版 Business 的 span 列表、
Literature 的 text-list 标签、History/Sociology 从 assessment 回推 topic 的结构，
以及 project-based learning 的项目组件。

### Provider 范围

当前产品只实现 OxfordAQA，不应写成覆盖全部 International GCSE 或
International AS/A-level provider。国内市场路线图是：

| Provider / exam board | 状态 | 备注 |
|---|---|---|
| OxfordAQA / Oxford International AQA Examinations | 已实现 | 当前 parser、renderer、样例和 validation 都围绕这个网站构建。 |
| Pearson Edexcel | 计划支持 | 等 OxfordAQA fixtures 和质量门槛稳定后再加。 |
| Cambridge International / CAIE | 计划支持 | 作为独立 provider 实现，不复用 OxfordAQA 的网页假设。 |
| OCR、WJEC/Eduqas、CCEA 等其他英国考试局 | 暂不支持 | README 和样例里都不承诺覆盖。 |

关于考试难度、词汇负担、得分友好度这类市场判断，只能作为 planning note，
不能写成官方事实或产品能力，除非经过学科老师或升学顾问复核。

### 后续路线

1. 强化 PDF 分段：subject content、command words、assessment objectives、
   appendices、version history。
2. 用合成 PDF fixtures 补测试，避免提交 OxfordAQA PDF。
3. 增加经过审核的 authoring adapter，生成更深度 worked examples。
4. 为常见题型增加更专业的学科 SVG 图解模板。
5. 增加 HTML 视觉回归检查。
6. OxfordAQA 稳定后，按 Pearson Edexcel、Cambridge International / CAIE
   的顺序扩 provider。
