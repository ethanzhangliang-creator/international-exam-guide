# GitHub Release Checklist / GitHub 发布检查清单

## Repository

- [ ] Repository name, description, and topics are set.
- [ ] `README.md` renders correctly on GitHub.
- [ ] `README.zh-CN.md` is linked from the English README.
- [ ] SVG assets render in GitHub Markdown.
- [ ] License is visible.
- [ ] CI is enabled.
- [ ] Issue templates and PR template are visible.

## Source and Copyright

- [ ] No downloaded OxfordAQA PDFs are committed.
- [ ] No past-paper questions or mark schemes are committed.
- [ ] `outputs/` is ignored.
- [ ] Source policy is clear in README and docs.

## Commands

- [ ] Offline demo works:

```bash
python -m intl_exam_guide demo --out ./outputs/demo-science --skip-pdf
```

- [ ] Subject-page discovery shows qualification metadata:

```bash
python -m intl_exam_guide discover --subject-url https://www.oxfordaqa.com/subjects/science/
```

- [ ] Discovery output includes `international_gcse` rows with the blue listing
  group and `international_as_a_level` rows with the red listing group.

- [ ] OxfordAQA International GCSE sample works:

```bash
python -m intl_exam_guide generate --query chemistry --level igcse --out ./outputs/chemistry-9202
```

- [ ] OxfordAQA International AS/A-level sample works:

```bash
python -m intl_exam_guide generate --query chemistry --level a-level --out ./outputs/chemistry-9620
```

- [ ] OxfordAQA non-Science International GCSE sample works:

```bash
python -m intl_exam_guide generate --query economics --level igcse --out ./outputs/economics-9214
```

- [ ] OxfordAQA revised non-Science International AS/A-level code lookup sample works:

```bash
python -m intl_exam_guide generate --query 9725 --level a-level --out ./outputs/business-9725
```

## Validation

- [ ] `validation.json` has no `error` issues for the offline demo.
- [ ] `validation.json` has no `error` issues for one International GCSE subject.
- [ ] `validation.json` has no `error` issues for one International AS/A-level subject.
- [ ] `validation.json` has no `error` issues for one non-Science International GCSE subject.
- [ ] `validation.json` has no `error` issues for one revised non-Science
  International AS/A-level code lookup subject.
- [ ] Live parser audit across discovered OxfordAQA qualification pages shows
  no missing topics, assessments, specification links, or listing/type conflicts.
- [ ] `validation.json.review_summary` has the expected topic, guide, practice-card, diagram, and source-snippet counts.
- [ ] Generated HTML includes source checks.
- [ ] Generated HTML includes website listing metadata when discovered from a subject page.
- [ ] Generated HTML includes one concept map per topic.
- [ ] Generated HTML includes practice cards with command words, solution steps, and answer checkpoints.
- [ ] Generated HTML includes the language policy section.
- [ ] Template labels use bilingual `Chinese / English` wording.
- [ ] Official topic titles remain in OxfordAQA English unless a reviewed glossary is provided.
- [ ] Generated PDF opens locally.

## Accuracy

- [ ] The README clearly says the MVP creates source-bound frames, not copied past-paper questions.
- [ ] Deep worked examples are marked as requiring subject review.
- [ ] Regional/exam-centre availability is described as something families must confirm locally.

## 中文发布检查

- [ ] 中文 README 能解释项目是什么、适合谁、怎么跑。
- [ ] 中文 README 解释 International GCSE / International AS/A-level 的蓝色/红色 listing 映射。
- [ ] 准确性政策中明确说明“不编造 syllabus、不复制真题、不提交 PDF”。
- [ ] 给孩子正式使用前，需要老师或熟悉大纲的人复核深度例题。
