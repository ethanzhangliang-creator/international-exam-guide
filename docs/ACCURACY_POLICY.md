# Accuracy Policy / 准确性政策

## English

This project is intended for student revision support. Accuracy matters more
than generation speed or stylistic fluency.

### Non-negotiable Rules

1. Do not invent syllabus topics.
2. Do not copy past-paper questions or mark schemes.
3. Do not commit downloaded official PDFs to the repository.
4. Do not treat a generated guide as final if validation has errors.
5. Do not use deep worked examples with students until they have been reviewed
   against the extracted specification text.

### What the Current Release Can Safely Do

- Extract topic titles and syllabus summary points from the public page.
- Record provider-specific listing metadata when the official page exposes it,
  such as AQA International GCSE / International AS-A-level listing groups.
- Download the public specification PDF at runtime.
- Record source URLs and PDF hash.
- Match topic-level source snippets from extracted PDF pages.
- Render deterministic concept maps from extracted topic points.
- Generate safe mini worked-example frames and practice cards with command
  words, solution steps, and answer checkpoints.
- Render a polished HTML/PDF study guide.

### What Requires Review

- Full numerical worked examples.
- Subject-specific diagrams with labels and equations.
- Final answer keys.
- Any advice about exam entry, regional availability, or equivalency.

### Recommended Review Loop

1. Run the generator.
2. Open `validation.json`.
3. Check every warning or error.
4. Review `qualification.json` topic extraction.
5. Review source snippets in `guide.html`.
6. Add or approve deep worked examples manually.
7. Export final PDF.

## 中文

这个项目面向学生复习，准确性比生成速度和文风更重要。

### 不可妥协的规则

1. 不编造 syllabus topics。
2. 不复制 past-paper questions 或 mark schemes。
3. 不把下载的官方 PDFs 提交到仓库。
4. validation 有 error 时，不把指南当完成品。
5. 深度 worked examples 必须对照抽取出的大纲文本复核后，才能给孩子正式使用。

### 当前版本可以安全完成什么

- 从公开页面抽取 topic titles 和 syllabus summary points。
- 当官方页面提供 listing 元数据时进行记录，例如 AQA 的 International GCSE /
  International AS-A-level 分组。
- 运行时下载公开 specification PDF。
- 记录 source URLs 和 PDF hash。
- 从 PDF 页文本中匹配 topic-level source snippets。
- 根据抽取出的 topic points 渲染确定性概念图。
- 生成安全的 mini worked-example frames，以及带指令词、解题步骤、
  答案检查点的 practice cards。
- 渲染精美 HTML/PDF 学习指南。

### 哪些内容必须复核

- 完整数值型 worked examples。
- 带标签、公式或坐标轴的学科图解。
- 最终答案 key。
- 有关考试报名、地区可用性或等效性的建议。

### 推荐复核流程

1. 运行生成器。
2. 打开 `validation.json`。
3. 检查所有 warning 和 error。
4. 复核 `qualification.json` 里的 topic 抽取结果。
5. 复核 `guide.html` 中的 source snippets。
6. 人工添加或批准深度 worked examples。
7. 导出最终 PDF。
