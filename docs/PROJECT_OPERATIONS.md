# Project Operations Guide / 项目维护说明

Last updated: 2026-06-21

This file is the operational memory for future sessions and agents. Update it
whenever release flow, validation rules, animation assets, repository hygiene, or
Skill usage changes.

## 1. Project Positioning

This repository publishes an AI Skill and Python pipeline for generating
International GCSE and International AS-A-level revision handbooks.

Current public scope:

- AQA, Edexcel, and CAIE are the supported exam-board families.
- AQA supports catalogue discovery through OxfordAQA / Oxford International AQA
  pages.
- Edexcel and CAIE use official candidate matching plus official URL/PDF
  fallback. If the route is ambiguous, return candidates and wait for the user.
- Do not claim support for OCR, WJEC/Eduqas, CCEA, or every UK exam board.
- Do not commit official PDFs, past papers, mark schemes, copied exam questions,
  API keys, local absolute paths, private local notes, or generated output
  folders.

User-facing promise:

1. User gives the Skill link to OpenClaw, Hermes, or another Skill-compatible
   Agent.
2. User asks for a subject revision/study handbook.
3. Agent confirms exam board, subject, required exam year, output language, and
   explanation style.
4. Agent fetches official public syllabus/specification sources.
5. Agent builds topic guides, worked examples, visual briefs, HTML, PDF, and
   validation output.

## 2. Source Of Truth

- GitHub repository: `https://github.com/mianbaofang/igcse-a-level-revision-guide`
- GitHub Pages: `https://mianbaofang.github.io/igcse-a-level-revision-guide/`
- Skill entry: `https://github.com/mianbaofang/igcse-a-level-revision-guide/tree/main/skill`
- Package version: `pyproject.toml` and `src/intl_exam_guide/__init__.py`
- Release history: `CHANGELOG.md` and GitHub Releases
- Public home page: `docs/index.html`
- English/Chinese README: `README.md`, `README.zh-CN.md`

Do not use old local clones or generated outputs as proof of current behavior.
When verifying user experience, start from the GitHub repository or the clean
current working copy.

## 3. Mandatory Update Rule

Every project update must decide whether these files need changes:

- `CHANGELOG.md`
- `README.md`
- `README.zh-CN.md`
- `docs/index.html`
- `docs/PROJECT_OPERATIONS.md`
- `docs/RELEASE_CHECKLIST.md`
- `skill/SKILL.md`
- `skill/references/revision_guide_spec.md`

If the change affects actual generation behavior, validation, provider support,
CLI options, image routing, release flow, or animation assets, update this file.

Documentation-only wording fixes do not require a package version bump. Any
functional change to Skill behavior, validation, CLI, providers, rendering, or
release assets should bump the patch version.

v0.2.17 added the anti-template language gate. Future wording/tone changes that
affect generated handbook text or validation warnings are functional changes and
should bump the patch version.

v0.2.18 raised the CI coverage gate to 70% and split infographic rendering out
of `rendering/html.py`. Keep parser, renderer, and practice-generator guard
tests updated whenever those areas change.

v0.2.19 fixed a real product-labeling regression: unknown, synthetic, or demo
sources must not fall back to AQA branding. Future provider-label changes need
tests for both explicit AQA detection and neutral unknown-provider output.

v0.2.20 closed the sixth-round audit loop around stale local artifacts and
generator coverage. Release evidence must come from fresh outputs produced by
the current code; ignored `outputs/` folders and old `validation.json` files are
not valid proof. Keep `rendering/icons.py` tracked whenever renderer icon usage
changes.

The seventh-round audit follow-up raised coverage evidence past 80% and added a
fresh offline demo evidence requirement. When preparing the next release, record
the fresh demo/generate command plus the `validation.json` summary in
`CHANGELOG.md` or the GitHub Release notes, but keep the generated `outputs/`
folder ignored and untracked.

v0.2.21 closed the eighth-round testing-coverage gap by adding direct renderer
contract tests for cover identity, stylesheet/print layout, visual manifests,
generated raster reuse, SVG fallback assets, modular handbook packaging, and the
Playwright Chrome-to-Edge PDF fallback route. Future rendering changes should
update these contract tests instead of relying only on end-to-end demo coverage.

v0.2.22 closed the ninth-round rendering coverage gap by adding direct
`rendering/html.py` contract tests for the full HTML entry point, topic-section
renderer, guide cards, diagrams, story-mode blocks, practice cards, visual
example routing, source appendix, assessment fallback, navigation, and topic
title localization. Keep this module covered with direct unit tests whenever
handbook structure changes.

v0.2.23 closed the tenth-round P3 audit items: weak truthy assertions were
converted to exact-value assertions, `zh-CN` rendering branches received direct
contract coverage, `rendering/svg_templates.py` and `rendering/text.py` gained
dedicated tests, and fresh offline demo evidence was restored in the release
notes. Future test-only releases still need fresh demo evidence unless this
operations document and `docs/RELEASE_CHECKLIST.md` explicitly define an
exemption.

v0.2.24 closed the eleventh-round P3 follow-up: dedicated tests now cover
explanation-style branches, localization helpers, `zh-CN` HTML helpers, the
`render_html()` Chinese entry path, SVG slash wrapping, and long-text truncation.
The concept fallback SVG is English-only because Chinese visuals already use
`render_zh_visual_svg()`. Raw-key release scans must use the same command as
`docs/RELEASE_CHECKLIST.md`: `python scripts/scan_for_raw_keys.py . ./outputs`.

## 4. Version And Release Rules

Use GitHub Releases, not tags alone.

Standard flow for a functional release:

```powershell
python -m pytest --cov --cov-report=term-missing --cov-fail-under=70 -q
python -m ruff check .
python -m compileall -q src tests scripts
python scripts/scan_for_raw_keys.py . ./outputs
git diff --check
git status --short
```

Then:

1. Update `pyproject.toml`.
2. Update `src/intl_exam_guide/__init__.py`.
3. Update `CHANGELOG.md`.
4. Update README/project docs if the public promise changed.
5. Commit intentionally.
6. Create an annotated tag, for example `vX.Y.Z`.
7. Push `main`.
8. Push the tag.
9. Create or update the GitHub Release for that tag.

The Release should contain:

- version title;
- what changed;
- validation commands and results;
- usage reminder with the Skill link;
- Source code assets generated by GitHub.

Do not leave a version visible only under `/tags`. The user-facing release page
should be under:

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide/releases
```

## 5. GitHub Release Creation

Preferred method when GitHub CLI is installed:

```powershell
gh release create vX.Y.Z --repo mianbaofang/igcse-a-level-revision-guide --title "vX.Y.Z · short title" --notes-file RELEASE_NOTES.md --latest
```

If GitHub CLI is unavailable, use the GitHub Releases REST API with the existing
Git credential manager token. Never print or commit the token.

Minimum release payload fields:

- `tag_name`
- `target_commitish`
- `name`
- `body`
- `draft: false`
- `prerelease: false`

If the release already exists, update it instead of creating a duplicate.

## 6. Animation Asset Rules

Animation files:

- Chinese wrapper: `docs/project-intro-animation.html`
- English wrapper: `docs/project-intro-animation-en.html`
- Chinese source: `docs/assets/three-board-support-video/`
- English source: `docs/assets/three-board-support-video-en/`
- README GIF previews:
  - `docs/assets/intro-animation-preview.gif`
  - `docs/assets/intro-animation-preview-en.gif`

Rules:

- Chinese README must show Chinese animation/GIF.
- English README must show English animation/GIF.
- Stage size is `1920x1080`.
- Stage duration is `48` seconds.
- README GIF preview should be 16:9, normally `960x540`.
- HTML animation must autoplay in page, not require opening raw code.
- If animation source text changes, regenerate the relevant preview GIF.
- MP4 export is optional and should not be committed unless a release explicitly
  needs a downloadable video file.

Render command:

```powershell
python scripts/render_intro_animation.py --html docs/project-intro-animation.html --mp4 outputs/project-intro-animation.mp4 --gif docs/assets/intro-animation-preview.gif
python scripts/render_intro_animation.py --html docs/project-intro-animation-en.html --mp4 outputs/project-intro-animation-en.mp4 --gif docs/assets/intro-animation-preview-en.gif
```

For quick README preview refresh, a shorter preview may be rendered, but the
HTML source must still represent the current project.

## 7. Skill And Image Routing Rules

The Skill must not present GPT Image, Qwen Image, or SenseNova as built-in
callable providers.

Current public logic:

- recommended external models: GPT Image 2.0, Qwen Image 2.0 Pro, SenseNova U1
  Fast;
- base generator writes visual briefs and prompt queues;
- real image generation only happens if the user provides a callable route,
  API/script, image-generation Skill, designer workflow, or generated asset
  directory;
- "external" does not mean manual user file-moving. If the route is callable,
  the Agent should run it after the base handbook exists and import or attach
  the reviewed assets automatically;
- SVG is only a fallback for simple diagrams and must carry review warnings when
  used for complex visuals.

Do not show a user-facing menu that implies these models are always available.
Ask for the subject/language/style first. Report complex infographic needs after
the base handbook plan exists.

After changing `skill/`, synchronize any locally installed Skill copy from the
repository's `skill/` directory.

## 8. Validation Rules

Validation must fail on student-facing output that is visibly incomplete.

Important error cases:

- downloaded specification yields too few syllabus topics;
- missing topic guides or practice coverage;
- Chinese placeholder text such as numbered generic syllabus points;
- repeated practice questions under the same topic;
- cross-subject borrowed practice templates;
- missing source URLs or missing specification metadata;
- Edexcel/CAIE ambiguity resolved by guessing instead of returning candidates;
- downloaded official PDFs that only produce generic `Content unit` topics;
- downloaded official PDFs that produce no assessment-paper structure;
- missing manifest files or broken image references.

Important warning cases:

- remaining formulaic AI-style wording in student-facing topic guides or
  practice cards after the anti-template language pass.

PDF export should try Playwright first, then fall back to a local Chrome/Edge
browser. If both routes fail, record a clear PDF export error instead of
masking the rest of the generation run.

Do not treat `issues: []` as meaningful unless the run was generated from the
current code and not copied from old `outputs/` folders.

For visual-output audits, read the three counters together:

- `generated_infographic_assets`: reviewed/generated raster infographic files;
- `svg_fallback_assets`: local SVG fallback files written for draft review;
- `pending_infographic_assets`: complex briefs still waiting for external
  image generation or human review.

A prompt-queue run can legitimately have `generated_infographic_assets: 0` if
SVG fallback assets were written and the warning clearly states that final
complex infographics still need an external model, script, or imported asset.

## 9. Repository Hygiene

Keep committed files focused on source, docs, Skill, tests, screenshots, and
animation assets.

Ignored or local-only artifacts:

- `outputs/`
- `.pytest_cache/`
- `.ruff_cache/`
- `__pycache__/`
- `*.egg-info/`
- downloaded official PDFs;
- generated release sample folders unless explicitly converted into tracked
  screenshots/assets.

Before committing:

```powershell
git clean -fdX -n
python scripts/scan_for_raw_keys.py . ./outputs
rg -n "local-private-path-pattern" . -S -g "!outputs/**" -g "!.git/**"
```

Run `git clean -fdX` only after reviewing the dry run. Never remove unrelated
user folders or subject-study materials.

## 10. Local Folder Migration Notes

Local project paths may change. Do not write machine-specific absolute paths
into public docs.

When moving the repository:

1. confirm `git status --short` is clean or commit changes first;
2. copy or move the entire repository directory;
3. run `git status --short` in the new location;
4. run a smoke test or at least
   `python -m pytest --cov --cov-report=term-missing --cov-fail-under=70 -q`;
5. synchronize the installed Skill copy if `skill/` changed;
6. remove old duplicate clones and ignored outputs after confirming the new
   location works.

The public docs should describe procedure, not a private workstation path.
