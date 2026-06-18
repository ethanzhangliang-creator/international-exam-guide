# Agent Handoff / 后续 Agent 接手说明

Last updated: 2026-06-18

This file is the first place a new agent should read before continuing work on
this repository.

## Source Of Truth

- GitHub repository: `https://github.com/mianbaofang/igcse-a-level-revision-guide`
- GitHub Pages: `https://mianbaofang.github.io/igcse-a-level-revision-guide/`
- Current handoff working repository:
  `C:\Users\Ethan\Desktop\igcse-a-level-revision-guide-handoff\igcse-a-level-revision-guide`
- Current handoff task notes:
  `C:\Users\Ethan\Desktop\igcse-a-level-revision-guide-handoff\START_HERE_FOR_AGENT.md`
  and
  `C:\Users\Ethan\Desktop\igcse-a-level-revision-guide-handoff\NEXT_AGENT_UPGRADE_PLAN.md`
- Local generated outputs for this handoff should stay under this working copy's
  `outputs\goal-check-*` directories unless Ethan asks for a release package.
- Installed local Skill:
  `C:\Users\Ethan\.agents\skills\igcse-a-level-revision-guide`

## What This Project Is

This is an open-source Codex Skill and Python pipeline for generating
student-friendly, image-rich revision handbooks from official International
GCSE and International AS-A-level syllabus/specification sources.

The user-facing promise is simple:

1. give an agent the Skill link;
2. ask for a subject revision/study handbook;
3. confirm subject/provider, any required exam year, output language, and
   explanation style;
4. let the agent fetch the official syllabus/specification, plan the handbook,
   generate examples and visual briefs, render HTML, export PDF, and validate
   the result.

Current provider support:

- OxfordAQA: implemented with catalogue discovery.
- Pearson Edexcel: subject-name candidate discovery for common official page
  patterns, with official subject-page URL or direct specification PDF fallback.
- Cambridge International / CAIE: official subject-index candidate discovery,
  with official subject-page URL or direct syllabus PDF fallback and `exam_year`
  required when a page lists multiple syllabus ranges.

Do not claim support for all UK exam boards or full Pearson/Cambridge catalogue
crawling.

## Current State

- Repository name and links use `mianbaofang/igcse-a-level-revision-guide`.
- GitHub Pages is configured from `main` / `docs`.
- Public homepage: `docs/index.html`.
- Public intro animation: `docs/project-intro-animation.html`,
  `docs/project-intro-animation.mp4`, and `docs/assets/intro-animation-preview.gif`.
- README and Chinese README now describe ordinary agent usage first, not CLI usage.
- The three public screenshots are examples of final handbook quality, not a
  subject support limit and not a user-facing release workflow.
- SenseNova is named as **SenseNova U1 Fast** for user-facing model guidance;
  the machine option remains `sensenova-u1-fast`.
- Raw API keys must never be committed, pasted into docs, or printed in logs.

## Important Docs

- `README.md`: public English project entry.
- `README.zh-CN.md`: public Chinese project entry.
- `skill/SKILL.md`: the compact Skill instruction that other agents install.
- `skill/references/revision_guide_spec.md`: handbook contract and required
  output behavior.
- `skill/references/oxfordaqa.md`: OxfordAQA provider notes and quality gates.
- `docs/PROJECT_DETAILS.md`: architecture, MVP scope, provider roadmap.
- `docs/IMAGE_MODEL_GUIDE.md`: SVG vs image-model routing and provider guidance.
- `docs/ACCURACY_POLICY.md`: source, copyright, and student-safety rules.
- `docs/EXAMPLES.md`: developer examples and sample verification.
- `docs/RELEASE_CHECKLIST.md`: release checks before GitHub publication.

If a future agent only reads three files, read this file, `README.md`, and
`skill/SKILL.md`.

## Current Output Samples

The local `outputs/` folder contains generated sample guides and verification
artifacts. The most important samples are:

- `outputs/mathematics-9260-sample/guide.html`
- `outputs/mathematics-9260-sample/guide.pdf`
- `outputs/economics-9214-sample/guide.html`
- `outputs/economics-9214-sample/guide.pdf`
- `outputs/chemistry-9202-sample/guide.html`
- `outputs/chemistry-9202-sample/guide.pdf`
- `outputs/repo-home-preview.html`
- `outputs/project-intro-animation.html`
- `outputs/igcse-a-level-revision-guide-source.zip`

Generated guide folders are large and are not committed to Git. Treat them as
local release artifacts.

## Validation Commands

From the repository root:

```powershell
python -m pytest -q
python -m compileall -q src tests scripts
python scripts/scan_for_raw_keys.py . ..\..\outputs
python scripts/verify_release_samples.py --outputs-root ..\..\outputs
```

If the current Python environment does not have test dependencies installed,
install the package in editable development mode first:

```powershell
python -m pip install -e ".[dev]"
```

Before committing or pushing, run at least:

```powershell
git diff --check
python scripts/scan_for_raw_keys.py . ..\..\outputs
```

## Image Generation Rules

- Do not require an image model before starting the base guide run. The default
  complex-visual route is source-bound `visual_brief` plus prompt queue.
- Use deterministic SVG only for simple structure diagrams and source-bound
  concept maps.
- Recommend GPT Image 2.0, Qwen Image 2.0 Pro, and SenseNova U1 Fast for
  complex text+diagram infographics, but treat them as external options unless
  the user supplies a callable skill/API/script/asset directory/custom provider.
- If the provider is custom, record model name, endpoint URL, and environment
  variable name for the key. Do not record the raw key.
- Every generated image should keep provider/model, prompt, source topic,
  caption, alt text, and review status metadata.

## Known Follow-Up Priorities

1. Improve PDF section segmentation for command words, assessment objectives,
   appendices, and version history.
2. Add synthetic provider fixtures and tests so parser changes do not depend on
   downloaded official PDFs.
3. Add deeper subject-aware authoring adapters for worked examples, with
   review gates.
4. Add richer SVG templates for common Maths, Science, Economics, and Business
   diagram types.
5. Improve real image-provider adapter interfaces beyond the current
   prompt-queue/import workflow.
6. Add visual regression checks for generated HTML and public homepage assets.
7. Expand Pearson Edexcel beyond candidate discovery MVP after fixtures and
   validation are stable.
8. Expand Cambridge International / CAIE beyond candidate discovery MVP with its
   own provider fixtures and source model.

## Do Not Do

- Do not commit downloaded OxfordAQA PDFs, past papers, mark schemes, or copied
  question content.
- Do not describe the project as supporting all IGCSE/A-Level providers.
- Do not mix Chinese and English labels in student-facing guide bodies unless
  the user explicitly requests bilingual output.
- Do not use generated images as factual sources. Images explain source-bound
  content; they do not create syllabus facts.
- Do not push private API keys, generated key logs, or provider credentials.

## 中文快速交接

下一个 agent 优先看：

1. `docs/HANDOFF.md`
2. `README.zh-CN.md`
3. `skill/SKILL.md`
4. `skill/references/revision_guide_spec.md`

当前项目已经开源到：

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide
```

当前公开主页：

```text
https://mianbaofang.github.io/igcse-a-level-revision-guide/
```

用户侧理解方式：

```text
把 Skill 链接给 agent -> 让 agent 安装 -> 用户说“帮我生成某科复习手册”
-> agent 先确认科目、语言、生图方式、讲解风格 -> 自动生成 HTML/PDF。
```

核心逻辑不能变：先根据官方 syllabus/specification 生成知识点和例题，再二次判断哪些内容
需要图文结合；简单图用 SVG，复杂信息图默认进入 visual brief / prompt queue，
只有用户提供可调用生图能力或图片资产时才真实生成或导入。
