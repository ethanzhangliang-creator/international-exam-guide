# Examples / 示例

## Offline Demo

The offline demo uses `src/intl_exam_guide/assets/demo_qualification.json`. It
does not download OxfordAQA content and does not include copyrighted PDFs.

```bash
python -m intl_exam_guide demo --out ./outputs/demo-science --skip-pdf
```

With local Chrome/Edge PDF export:

```bash
python -m intl_exam_guide demo --out ./outputs/demo-science
```

Expected files:

```text
outputs/demo-science/
  guide.html
  guide.pdf                  optional if browser export succeeds
  guide-plan.json
  qualification.json
  validation.json
```

Open `validation.json` after each run. The `issues` list must not contain
errors, and `review_summary` should show the expected topic count, one diagram
per topic, practice-card coverage for every topic, and source-snippet coverage
where the PDF text matched.

The HTML includes one inline concept map per topic. These SVG diagrams are
generated from extracted or synthetic syllabus points and do not require external
image files.

Each topic also receives practice cards. A card records the command word,
difficulty, focus point, public solution steps, answer checkpoints, and the
source points used to shape the prompt.

## OxfordAQA International GCSE Example

First inspect the subject page listings:

```bash
python -m intl_exam_guide discover --subject-url https://www.oxfordaqa.com/subjects/science/
```

The science page should show International GCSE rows tagged as
`international_gcse` with the blue listing group, and International AS/A-level
rows tagged as `international_as_a_level` with the red listing group.

```bash
python -m intl_exam_guide generate --query chemistry --level igcse --out ./outputs/chemistry-9202
```

## OxfordAQA International AS/A-level Example

```bash
python -m intl_exam_guide generate --query chemistry --level a-level --out ./outputs/chemistry-9620
```

## OxfordAQA Non-Science International GCSE Example

```bash
python -m intl_exam_guide generate --query economics --level igcse --out ./outputs/economics-9214
```

## OxfordAQA Revised Non-Science AS/A-level Example

```bash
python -m intl_exam_guide generate --query 9725 --level a-level --out ./outputs/business-9725
```

This covers a revised qualification page where the subject listing text does
not include the code, but the qualification detail page does.

## 中文说明

离线 demo 使用仓库内置的合成 qualification，不下载 OxfordAQA 内容，也不包含任何
受版权限制的 PDF。它适合用于测试安装环境、查看 HTML/PDF 样式、验证
`validation.json` 的结构。

每次生成后都应打开 `validation.json`：`issues` 不能有 error，
`review_summary` 应显示 topic、diagram、practice card 和 source snippet 覆盖情况。

HTML 会为每个 topic 生成一张 inline concept map。图中的节点来自抽取出的
或合成的 syllabus points，不依赖外部图片文件。

每个 topic 也会生成练习卡片。卡片会记录 command word、difficulty、
focus point、public solution steps、answer checkpoints，以及用于约束题干的
source points。

建议先运行 `discover --subject-url` 检查学科页。International GCSE 行应标记为
`international_gcse` 和蓝色 listing；International AS/A-level 行应标记为
`international_as_a_level` 和红色 listing。

真实 OxfordAQA 示例会在运行时下载公开 specification PDF。不要把下载得到的 PDF
提交到仓库。

Economics 示例用于覆盖非 Science 页面结构：该页面使用 strong headings 和 paragraph
points 描述 syllabus summary。

Business 9725 示例用于覆盖修订版 A-level 页面结构：subject listing 的文字不带
代码，但 qualification 详情页带代码，因此可以验证代码查询不会被同级别科目带偏。
