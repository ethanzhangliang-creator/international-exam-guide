# International Exam Guide

<p align="center">
  <img src="docs/assets/hero.svg" alt="International Exam Guide hero" width="100%">
</p>

<p align="center">
  <a href="README.zh-CN.md">中文 README</a>
  ·
  <a href="https://ethanzhangliang-creator.github.io/international-exam-guide/">Project site</a>
  ·
  <a href="https://ethanzhangliang-creator.github.io/international-exam-guide/project-intro-animation.html">Intro video</a>
  ·
  <a href="docs/PROJECT_DETAILS.md">Project details</a>
  ·
  <a href="docs/SKILL_EXPLAINED.md">Skill explained</a>
  ·
  <a href="docs/EXAMPLES.md">Examples</a>
  ·
  <a href="docs/ACCURACY_POLICY.md">Accuracy policy</a>
  ·
  <a href="docs/RELEASE_CHECKLIST.md">Release checklist</a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-1454A5">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-B83246">
  <img alt="Source traceable" src="https://img.shields.io/badge/source-traceable-1F7A5B">
  <img alt="OxfordAQA" src="https://img.shields.io/badge/provider-OxfordAQA-D99A24">
</p>

International Exam Guide is a Codex Skill for generating source-traceable,
print-ready revision guides for OxfordAQA International GCSE and International
AS/A-level subjects.

For parents, students, tutors, and teachers: you do **not** need to install
Python, run commands, or understand the codebase. Give the Skill link to your
Codex/agent, ask it to install the Skill, then request a subject guide in plain
language. The agent handles the official syllabus download, guide generation,
validation, and PDF export.

## Start Here: Use the Skill

Send this link to your Codex/agent:

```text
https://github.com/ethanzhangliang-creator/international-exam-guide/tree/main/skill
```

Then say:

```text
请安装这个 Skill，然后帮我生成 OxfordAQA Chemistry International GCSE 复习手册，并导出 PDF。
```

After installation, normal prompts are enough:

```text
帮我生成 OxfordAQA Biology International GCSE 学习手册。
帮我生成 Chemistry 9202 复习手册，并导出 PDF。
帮我生成 OxfordAQA Business International AS/A-level revision guide。
```

The Skill will ask the agent to find the public OxfordAQA qualification page,
download the public course specification PDF, extract the syllabus and
assessment structure, attach page-level source snippets, and render an HTML/PDF
guide with topic maps, example frames, practice cards, answer checkpoints, and
validation checks.

Current scope is intentionally narrow: OxfordAQA is implemented now. Pearson
Edexcel and Cambridge International / CAIE are planned next for the China-market
roadmap.

## 24-Second Intro

<p align="center">
  <a href="https://ethanzhangliang-creator.github.io/international-exam-guide/project-intro-animation.html">
    <img src="docs/assets/intro-animation-preview.png" alt="International Exam Guide intro animation preview" width="100%">
  </a>
</p>

<p align="center">
  <a href="https://ethanzhangliang-creator.github.io/international-exam-guide/project-intro-animation.html">Open the live HTML intro</a>
  ·
  <a href="https://ethanzhangliang-creator.github.io/international-exam-guide/project-intro-animation.mp4">Play or download the MP4</a>
  ·
  <a href="https://ethanzhangliang-creator.github.io/international-exam-guide/">Open the project home page</a>
</p>

## Why This Exists

This project began at home. My son is taking his International GCSE exams this
year after moving from a Chinese public-school path into an international
curriculum. In less than a year, the classroom language shifted from Chinese to
English, while the exam clock kept moving. The knowledge itself can be learned;
the hard part is reorganizing it under a new language, a new exam style, and real
time pressure.

So I turned AI into a revision skill: first read the official specification, then
break the knowledge into understandable structures, examples, checkpoints, and
reviewable practice. The goal is not to let AI learn for a child. The goal is to
lower the noise around learning so a student can face schoolwork with more calm
and control.

That is why this tool is built around one rule:

> No syllabus fact should appear in the guide unless it is discoverable from the
> public qualification page or the downloaded specification.

That makes it suitable for families, tutors, and international schools that want
beautiful revision materials without losing source traceability.

## Demo

| Generated cover | Pipeline |
|---|---|
| <img src="docs/assets/output-anatomy.svg" alt="Generated guide anatomy" width="100%"> | <img src="docs/assets/pipeline.svg" alt="Pipeline diagram" width="100%"> |

## Developer Quick Start

This section is only for developers who want to run or modify the Python engine
directly. Normal Skill users can skip it.

Run the offline synthetic demo first:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m intl_exam_guide demo --out ./outputs/demo-science --skip-pdf
```

Then run a real OxfordAQA public qualification:

```bash
python -m intl_exam_guide generate --query chemistry --level igcse --out ./outputs/chemistry-9202
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m intl_exam_guide demo --out .\outputs\demo-science --skip-pdf
python -m intl_exam_guide generate --query chemistry --level igcse --out .\outputs\chemistry-9202
```

Run from a checkout without installing:

```bash
PYTHONPATH=src python -m intl_exam_guide generate --query chemistry --level a-level --out ./outputs/chemistry-9620
```

## What It Generates

```text
outputs/chemistry-9202/
  guide.html                 print-friendly student guide
  guide.pdf                  PDF export when Chrome/Edge or Playwright is available
  guide-plan.json            structured guide plan and practice cards
  qualification.json         extracted qualification metadata
  validation.json            quality gate report
  source/
    oxfordaqa-9202-specification.pdf   downloaded at runtime, do not commit
    oxfordaqa-9202-specification.txt   extracted text, do not commit
```

## Supported Scope

| Provider / exam board | International GCSE | International AS/A-level | Status |
|---|---:|---:|---|
| OxfordAQA / Oxford International AQA Examinations | yes | yes | MVP implemented |
| Pearson Edexcel | planned | planned | China-market roadmap |
| Cambridge International / CAIE | planned | planned | China-market roadmap |
| Other UK boards, including OCR, WJEC/Eduqas, and CCEA | no | no | outside current scope |

The current implementation is for OxfordAQA, not the whole AQA UK portfolio and
not every A-level awarding organisation. This boundary is intentional: in
mainland China, the practical international-school roadmap is OxfordAQA,
Pearson Edexcel, and Cambridge International.

OxfordAQA's subject index lists International GCSE and International AS/A-level
qualification pages. The public subject page also explains that International
GCSEs are linear, while International AS/A-levels are modular. The generator
keeps that difference in the guide instead of forcing one structure onto both.
On subject pages, the provider records the website listing group too:
`btn--type-8` is treated as the blue International GCSE listing and
`btn--type-7` as the red International AS/A-level listing.

The current discovery audit found 17 subject pages and 48 qualification links:
31 International GCSE listings and 17 International AS/A-level listings, with no
unknown listing types.

The parser audit also opened all 48 discovered qualification pages and found no
missing topic extraction, assessment extraction, specification link, or
blue/red listing conflict.

Official source anchors used for this scope:

- [OxfordAQA](https://www.oxfordaqa.com/) for the current provider and
  International GCSE / International AS/A-level subject pages.
- [Pearson Edexcel International Advanced Levels](https://qualifications.pearson.com/en/qualifications/edexcel-international-advanced-levels.html)
  for the planned Pearson provider family.
- [Cambridge International facts and figures](https://www.cambridgeinternational.org/about-us/facts-and-figures/)
  for the planned Cambridge International / CAIE provider family.

## Language Policy

Generated guides are intentionally mixed-language:

- Official qualification titles, topic titles, paper titles, syllabus points,
  and source snippets stay in English from OxfordAQA.
- Template navigation labels are bilingual, with Chinese first and English
  second, for example `知识地图 / Knowledge Map`.
- Chinese topic translations should be added only from a reviewed glossary or a
  subject-specialist authoring pass.

This prevents the generator from creating attractive but unreviewed translations
of official syllabus terms.

## Accuracy Model

The generator separates reliable extraction from optional authoring:

1. **Discovery**: find the public qualification page and specification link.
2. **Extraction**: download the PDF, extract page text, parse topics and assessment.
3. **Source matching**: attach page-level snippets to each topic where possible.
4. **Guide planning**: create source-bound topic blocks, diagram briefs, and practice cards.
5. **Rendering**: embed deterministic SVG concept maps from extracted syllabus points.
6. **Validation**: fail or warn on missing source, topic, assessment, diagram, guide, or output coverage.

Current practice cards are source-bound frames, not copied past-paper questions
and not fully invented numerical answers. Each card records a command word,
difficulty, focus point, public solution steps, and answer checkpoints. A future
LLM authoring layer can deepen examples only if it cites extracted source
snippets and passes review.

`validation.json` includes both machine-readable issues and a `review_summary`
with topic counts, practice-card counts, diagram counts, PDF/source-snippet
coverage, listing metadata, and audience-note checks.

## CLI

List subject pages:

```bash
python -m intl_exam_guide discover
```

List qualifications under a subject:

```bash
python -m intl_exam_guide discover --subject-url https://www.oxfordaqa.com/subjects/science/
```

This prints tab-separated columns:

```text
title    qualification_type    subject_heading    website_group    url
```

Generate an International GCSE guide:

```bash
python -m intl_exam_guide generate --query chemistry --level igcse --out ./outputs/chemistry-9202
```

Generate the offline demo:

```bash
python -m intl_exam_guide demo --out ./outputs/demo-science --skip-pdf
```

Generate an International AS/A-level guide:

```bash
python -m intl_exam_guide generate --query chemistry --level a-level --out ./outputs/chemistry-9620
```

Generate a non-science International GCSE guide:

```bash
python -m intl_exam_guide generate --query economics --level igcse --out ./outputs/economics-9214
```

Generate a revised non-science International AS/A-level guide by code:

```bash
python -m intl_exam_guide generate --query 9725 --level a-level --out ./outputs/business-9725
```

Skip PDF export when no browser runtime is available:

```bash
python -m intl_exam_guide generate --query 9202 --level igcse --out ./outputs/chemistry-9202 --skip-pdf
```

## Codex Skill

This repository also includes a compact Codex skill wrapper in `skill/`.

<p align="center">
  <img src="docs/assets/skill-system.svg" alt="Skill system diagram" width="100%">
</p>

The skill keeps the agent workflow concise and pushes deterministic operations
into the Python package. See [Skill explained](docs/SKILL_EXPLAINED.md).

## Copyright and Source Policy

Do not commit downloaded OxfordAQA PDFs, past papers, mark schemes, or copied
question content to this repository. The generator downloads public
specifications at runtime, records source URLs and hashes, and creates original
guide scaffolds and practice cards.

Generated guides should include source URLs, PDF hashes, and a local availability
note. Families should confirm exam entry routes with their school or centre.

## Development

```bash
pip install -e ".[dev]"
python -m pytest
python -m compileall -q src tests
```

## Repository Layout

```text
src/intl_exam_guide/
  providers/      website-specific discovery and parsing
  parsing/        PDF text extraction
  planning/       source-safe guide and practice planning
  rendering/      HTML and PDF rendering
  validation/     completeness and safety checks
skill/            Codex skill wrapper
docs/             project, skill, accuracy, and research notes
tests/            parser and pipeline tests
```

## README Presentation References

These repositories are not comparable education or syllabus-generation tools.
They were used only as references for open-source README presentation patterns:
badges, hero imagery, quick start placement, documentation navigation, trust
messaging, and contribution links.

The README structure was informed by presentation patterns from projects such as
[Open WebUI](https://github.com/open-webui/open-webui),
[uv](https://github.com/astral-sh/uv),
[Ruff](https://github.com/astral-sh/ruff),
[RAGFlow](https://github.com/infiniflow/ragflow), and
[awesome-readme](https://github.com/matiassingers/awesome-readme). See
[README research notes](docs/README_RESEARCH.md).

## License

MIT.
