# Examples / 示例

## Offline Demo

The offline demo uses `src/intl_exam_guide/assets/demo_qualification.json`. It
does not download OxfordAQA content and does not include copyrighted PDFs.

```bash
python -m intl_exam_guide demo --out ./outputs/demo-science --language en --image-provider deterministic-svg --explanation-style friendly --skip-pdf
```

With local Chrome/Edge PDF export:

```bash
python -m intl_exam_guide demo --out ./outputs/demo-science --language en --image-provider deterministic-svg --explanation-style friendly
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
`international_gcse` with the blue listing group, and International AS-A-level
rows tagged as `international_as_a_level` with the red listing group.

```bash
python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out ./outputs/chemistry-9202
```

## OxfordAQA International AS-A-level Example

```bash
python -m intl_exam_guide generate --query chemistry --level a-level --language en --image-provider prompt-queue --explanation-style detective --out ./outputs/chemistry-9620
```

## OxfordAQA Non-Science International GCSE Example

```bash
python -m intl_exam_guide generate --query economics --level igcse --language en --explanation-style life --out ./outputs/economics-9214
```

## OxfordAQA Revised Non-Science AS-A-level Example

```bash
python -m intl_exam_guide generate --query 9725 --level a-level --language en --explanation-style story --out ./outputs/business-9725
```

This covers a revised qualification page where the subject listing text does
not include the code, but the qualification detail page does.

## Pearson Edexcel Examples

Pearson support first tries official subject-page candidates from the subject
name. If several routes match, the CLI returns the choices for the user to pick.
Official subject-page URLs or direct specification PDF URLs still work as exact
inputs:

```bash
python -m intl_exam_guide generate --provider pearson --query "https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses/international-gcse-mathematics-a-2016.html" --level igcse --language en --explanation-style friendly --out ./outputs/pearson-igcse-maths --skip-pdf
python -m intl_exam_guide generate --provider pearson --query "https://qualifications.pearson.com/en/qualifications/edexcel-international-advanced-levels/mathematics-2018.html" --level a-level --language en --explanation-style friendly --out ./outputs/pearson-ial-maths --skip-pdf
```

## Cambridge International / CAIE Examples

Cambridge support searches the official subject indexes by subject name or code.
If several routes match, the CLI returns the choices for the user to pick.
Cambridge subject pages often list several syllabus year ranges, so provide
`--exam-year` when the selected page has multiple syllabus PDFs:

```bash
python -m intl_exam_guide generate --provider cambridge --query "https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-chemistry-0620/" --level igcse --exam-year 2027 --language en --explanation-style friendly --out ./outputs/cambridge-igcse-chemistry-2027 --skip-pdf
python -m intl_exam_guide generate --provider cambridge --query "https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-international-as-and-a-level-chemistry-9701/" --level a-level --exam-year 2029 --language en --explanation-style friendly --out ./outputs/cambridge-ial-chemistry-2029 --skip-pdf
```

## Release Sample Verification

The repository's public homepage should be built from completed guide samples.
Use the release verifier before publishing:

```bash
python scripts/verify_release_samples.py --outputs-root ./outputs --allow-pending
```

`--allow-pending` is only for pre-image checks. Final publication must pass
without that flag:

```bash
python scripts/generate_pending_infographics_router.py ./outputs/mathematics-9260-sample ./outputs/economics-9214-sample ./outputs/chemistry-9202-sample --size 1536x1024 --quality high --output-format png
python scripts/finalize_release_samples.py --outputs-root ./outputs
python scripts/verify_release_samples.py --outputs-root ./outputs
python scripts/capture_release_assets.py --outputs-root ./outputs --docs-assets docs/assets
python scripts/render_intro_animation.py --html docs/project-intro-animation.html --mp4 docs/project-intro-animation.mp4 --gif docs/assets/intro-animation-preview.gif
```

If your image provider writes files outside the guide package, import them first.
Generated filenames should start with the manifest ID, such as
`visual_001.png` or `visual_001_lab-apparatus.png`:

```bash
python scripts/import_infographic_assets.py ./outputs/chemistry-9202 \
  --asset-dir ./generated-infographics/chemistry-9202 \
  --provider "custom-image-model"
```

## 中文说明

离线 demo 使用仓库内置的合成 qualification，不下载 OxfordAQA 内容，也不包含任何
受版权限制的 PDF。它适合用于测试安装环境、查看 HTML/PDF 样式、验证
`validation.json` 的结构。

每次生成后都应打开 `validation.json`：`issues` 不能有 error，
`review_summary` 应显示 topic、diagram、practice card 和 source snippet 覆盖情况。

HTML 会为每个 topic 生成一张 inline concept map。图中的节点来自抽取出的
或合成的大纲点，不依赖外部图片文件。

每个 topic 也会生成练习卡片。卡片会记录指令词、难度、
聚焦知识点、公开解题步骤、答案检查点，以及用于约束题干的
source points。

建议先运行 `discover --subject-url` 检查学科页。International GCSE 行应标记为
`international_gcse` 和蓝色 listing；International AS-A-level 行应标记为
`international_as_a_level` 和红色 listing。

真实 OxfordAQA 示例会在运行时下载公开 specification PDF。不要把下载得到的 PDF
提交到仓库。

Economics 示例用于覆盖非 Science 页面结构：该页面使用 strong headings 和 paragraph
points 描述 syllabus summary。

Business 9725 示例用于覆盖修订版 A-level 页面结构：subject listing 的文字不带
代码，但 qualification 详情页带代码，因此可以验证代码查询不会被同级别科目带偏。

发布前应使用 release verifier 检查 Mathematics 9260、Economics 9214、Chemistry
9202 三份样板。`--allow-pending` 只适合信息图还没生成时做预检查；最终发布前必须
去掉这个参数，并确认三份手册都已经导出 PDF、合并信息图、截图更新到 `docs/assets/`。
这三份只是公开展示和回归验证样例，不是 OxfordAQA 科目支持上限。
截图更新后，再用 `scripts/render_intro_animation.py` 重新导出介绍动画 MP4 和 GIF。

如果你的生图服务把图片输出到手册目录外，可以先用
`scripts/import_infographic_assets.py` 导入。文件名需要以 manifest ID 开头，
例如 `visual_001.png` 或 `visual_001_lab-apparatus.png`。
