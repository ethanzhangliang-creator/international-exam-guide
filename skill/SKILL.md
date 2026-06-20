---
name: igcse-a-level-revision-guide
description: Use when generating image-rich International GCSE or International AS-A-level revision handbooks from official syllabus/specification sources, with AQA, Edexcel, and CAIE support.
---

# IGCSE & A-Level AI Revision Guide Skill

Use this skill when the user asks for an International GCSE or International
AS-A-level subject study/revision guide. Treat IGCSE as a user-facing alias for
International GCSE, but use the full qualification names in generated
documentation.

Before generating a guide, read `references/revision_guide_spec.md`. That file
defines the handbook contract inherited from the original IGCSE revision-guide
Skill: the output must be a student study/revision handbook with HTML, PDF,
modular sections, visual assets, worked examples, and validation. Do not turn
the output into project documentation.

Current exam-board support:

- AQA: implemented through OxfordAQA / Oxford International AQA public pages,
  including catalogue discovery. In Chinese user requests, treat "AQA" as this
  international AQA route unless the user explicitly gives a UK AQA page.
- Edexcel: subject-name candidate discovery for common official Pearson Edexcel
  International GCSE / International AS-A-level page patterns, plus official
  subject-page URL or direct specification PDF URL fallback.
- CAIE: official Cambridge International subject-index candidate discovery,
  plus official subject-page URL or direct syllabus PDF URL fallback. If a CAIE
  page lists multiple syllabus year ranges, ask for `exam_year` and use the
  range containing that year.

Do not run the AQA/OxfordAQA provider against Edexcel, CAIE, or generic UK AQA
pages. If the user says only "AQA" with no UK AQA URL, treat it as the
China-facing International GCSE / International AS-A-level AQA route. Do not
claim full subject-catalogue crawling for Edexcel. When Edexcel or CAIE cannot
uniquely identify a subject from exam board, level, subject, and code, return the
matching official candidates and ask the user to choose one. Do not silently pick
a likely route.

## Operational Gates

- STOP: preflight incomplete. If subject/provider, required exam year, output
  language, or explanation style is missing, ask only for the missing items and
  do not download or write the handbook yet.
- CHECKPOINT: official candidate selected. Continue only when discovery returns
  one official subject route or the user has chosen from the candidate list.
- STOP: no official candidate. Ask for an official subject-page URL, direct
  specification/syllabus PDF URL, or subject code. Do not switch boards, use an
  AQA syllabus, or guess a likely URL.
- CHECKPOINT: base handbook generated. After `guide-plan.json` and
  `validation.json` exist, report the complex infographic count before starting
  any image-generation or import workflow.
- STOP: no callable image route. If the user names GPT Image, Qwen, SenseNova,
  or another image model but there is no installed Skill, script, custom
  provider configuration, or matching asset directory, keep `prompt-queue` and
  SVG fallbacks with a review warning.
- CHECKPOINT: quality passed. Present the guide as usable only after validation
  has no `error` issues and the output includes detailed units, worked examples,
  source snippets, visual briefs, `sections/`, and `images/`.

When Edexcel or CAIE discovery returns more than one official match, show the
choices in this shape and wait:

```text
Official candidates found:
1. board:
   level:
   subject:
   code:
   official_url:
   spec_pdf_url:
   why_matched:

Please choose a number, or provide the official subject page / syllabus PDF URL.
```

Provider resolution commands from a full repository checkout:

```bash
# AQA has catalogue discovery.
python -m intl_exam_guide discover --provider oxfordaqa

# Edexcel and CAIE are URL-first / subject-candidate routes, not full crawlers.
# Use a scratch output directory to verify whether the provider resolves one
# official route or returns an ambiguity/error message to show the user.
python -m intl_exam_guide generate --provider pearson --query "Accounting" --level igcse --language en --explanation-style friendly --out ./outputs/_candidate-check-edexcel --skip-pdf
python -m intl_exam_guide generate --provider cambridge --query "Accounting 0452" --level igcse --exam-year 2027 --language en --explanation-style friendly --out ./outputs/_candidate-check-caie --skip-pdf
```

If those checks create a scratch guide only for route confirmation, do not
present it as the final handbook. Re-run with the user's confirmed language,
style, output directory, and PDF setting after the official route is selected.

## User-Facing Use

The end user should not need to run Python commands. They can install the skill
by giving this link to OpenClaw, Hermes, or another Skill-compatible Agent:

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide/tree/main/skill
```

After installation, plain-language requests are enough, for example:

```text
帮我生成 AQA Chemistry International GCSE 复习手册，并导出 PDF。
帮我生成 Edexcel Accounting International GCSE 中文复习手册。
帮我生成 CAIE IGCSE Economics 2027 考试用中文学习手册。
```

Do not start generation immediately after a broad request. Run the preflight
choice step first.

## Required Preflight Choices

Before downloading a specification or generating content, ask for and confirm
these choices if the user did not already provide them:

1. **Subject choice**: exam board, qualification level, subject, and code if
   known. The user may only know the exam board and subject. First resolve an
   official candidate yourself. If the provider finds several matching official
   routes, show the choices and wait for the user to pick one. Official
   subject-page URLs and direct specification/syllabus PDF URLs are accepted as
   precise overrides.
2. **Exam year when needed**: Cambridge subject pages often expose multiple
   syllabus ranges. If more than one range is available, ask for the student's
   exam year before selecting a syllabus.
3. **Output language**: ask whether the handbook should be `en` or `zh-CN`.
   This is a required language lock, not a bilingual mode. Do not offer a
   combined bilingual output. Do not render handbook labels
   as bilingual `Chinese / English`, `English / Chinese`, `中文 / English`, or
   similar mixed pairs. Template labels, explanations, topic framing, worked
   examples, image prompts, and visible infographic text must follow the
   selected language. If `zh-CN` is selected, keep official English snippets in
   structured source files or a clearly separated source appendix for review;
   do not mix English source paragraphs, raw English topic headings, or raw
   English syllabus bullet points into the student-facing topic map/body. If the
   user changes language, regenerate the guide in the new language instead of
   merging old sections.
4. **Explanation style**: ask how the knowledge points and examples should read:
   `formal`, `friendly`, `life`, `story`, `detective`, or `adventure`.
Do not ask the user to choose an image model before the base guide is generated.
Do not show an image-model choice menu that mixes SVG, prompt queue, and
recommended model names. The only required preflight choices are
subject/provider, required exam year, output language, and explanation style.

The recommended complex-image models are GPT Image 2.0, Qwen Image 2.0 Pro, and
SenseNova U1 Fast because they tend to handle text+diagram educational
infographics better than generic art models. These are recommendations only.
Do not imply every user can call them by default.

When no callable image model is available, do not treat every visual as a rough
generic SVG. For chart-like or rule-driven visuals, use the internal
scientific-vector fallback described in
`references/scientific_vector_fallback.md`: number lines, axes, probability
trees, function graphs, statistics charts, rate curves, pH scales, energy
profiles, and simple labelled geometry should be rendered as source-bound,
editable SVG where possible. This is not a user-facing image model choice.
Complex infographics still require an external model, script, imported asset, or
reviewed designer workflow.

After the guide plan is built, inspect `validation.json.review_summary` or
`images/visual_manifest.json` and tell the user how many complex infographic
briefs were found. Then the user may provide or confirm their own
image-generation model, API, Skill, script, designer workflow, or generated
image directory. If a callable route exists, the Agent should run it and then
import or attach the reviewed outputs automatically; do not make the user move
files by hand. If they do not provide a callable route or assets, deliver the
SVG fallback images already generated by the package, but say clearly that
complex-information SVG fallbacks can be less accurate and need review.

## Callable Image Capability Gate

Before using any real image model name after the base guide run, verify one of
these concrete capabilities:

- a named image-generation Skill is installed and the user explicitly asked to
  use it for this run; the Agent may call that Skill and then import/attach the
  generated files;
- a script path exists and is designed to generate or import the pending
  `visual_manifest.json` entries;
- an asset directory exists with generated image files matching the visual IDs;
- `--image-provider custom` has model name, endpoint URL, and API-key
  environment variable name, and the environment variable is set.

If none of those checks passes, do not choose a model. Keep the base guide on
`prompt-queue` and use the generated SVG fallback images with a review warning.
Never ask the user to paste a raw API key into chat or commit one to the
repository.

Handle repository setup, CLI execution, validation checks, and PDF export as the
Agent. Do not ask the user to install dependencies unless the local environment
is genuinely missing the required runtime and cannot proceed.

## Core Contract

This skill is a cross-subject framework, not a Mathematics, Chemistry, or
Economics template. Do not hard-code one subject's examples, diagrams, topic
counts, tone, or revision structure into another subject.
Within a supported board, do not maintain a per-subject allowlist. If the
official qualification page and specification PDF can be discovered or supplied,
run the same source-bound generation pipeline. Specialist subject profiles may
improve examples and visual decisions; subjects without a specialist profile
must fall back to generic source-bound examples instead of borrowing another
subject's template.

The end product is a study/revision handbook package. A valid run writes:

- `guide.html`;
- `guide.pdf` when PDF export is available;
- `sections/` with modular handbook source fragments;
- `images/` with deterministic SVG drafts or reviewed infographic assets;
- `guide-plan.json`;
- `qualification.json`;
- `validation.json`;
- `handbook-package.json`.

The required generation logic is:

1. Find the public qualification page and course specification PDF.
2. Use the web page only as discovery metadata; use the downloaded PDF as the
   source of truth for detailed syllabus content.
3. Parse the detailed subject content into teachable knowledge units. If the PDF
   has specification references such as `N1`, `A13`, `G20`, `S18`, or equivalent
   subject codes, use those references as the unit level. If a subject has no
   codes, use the lowest reliable section/subsection level available in the PDF.
4. Generate source-bound study notes and original worked examples for each unit.
   Each worked example must include a real question prompt, a solve-it-first
   frame, public solution steps, final answer/checkpoints, and source anchors.
5. Run the anti-template language pass before finalizing student-facing
   explanation and practice text. Remove safe formulaic transitions such as
   `In conclusion`, `Overall`, `总之`, and `值得注意的是`; if a phrase still reads
   like generic AI prose, keep it as a validation warning for review instead of
   hiding it.
6. Run a second visual-needs pass over each knowledge unit and worked example.
   Decide whether text is enough, a deterministic SVG is enough, or a richer
   infographic/image model is needed.
7. Render the guide to HTML/PDF only after the content, examples, visual briefs,
   and source checks are present.

For student-facing guides, do not produce a text-only template. During visual
planning:

- `prompt-queue` is the default route for complex visuals when no callable image
  capability exists;
- `deterministic-svg` for offline concept maps and simple diagrams only;
- GPT Image 2.0, Qwen Image 2.0 Pro, and SenseNova U1 Fast are recommended
  external options for text+diagram educational infographics;
- `custom` if the user has another provider, URL, model name, and key env var.

These recommended model names are not CLI providers. Do not pass them as
`--image-provider` values to the base generator. Use `prompt-queue` for the
guide, then run or import external images only after the callable gate above
passes.

If the user has not chosen the subject, required exam year, output language, and
explanation style, stop and ask. Do not block the base handbook on image-model
choice. Do not claim that complex infographics have been finalized until a
callable image route has produced reviewed image assets; SVG fallbacks are
draft aids.

The public repository does not include a fixed built-in image-generation router.
That does not mean image work must be manual. If the user has a callable model,
API, Skill, script, or designer workflow, the Agent should run that capability
after the base handbook is generated, save the reviewed files, and use
`scripts/import_infographic_assets.py` when the files need to be copied into the
guide package before finalizing HTML/PDF.

## Repository Access

This skill may be installed from the repository's `skill/` directory, which
contains the Agent instructions but not the Python engine. Before running the
generator, check whether the current workspace has `pyproject.toml` and
`src/intl_exam_guide`.

If the full repository is not available, clone or otherwise fetch this public
repository into a workspace directory, then run commands from that checkout:

```text
https://github.com/mianbaofang/igcse-a-level-revision-guide.git
```

## Workflow

1. Confirm the required preflight choices: subject/provider, required exam
   year, output language, and explanation style. Do not ask for an image model
   at this stage.
2. Read `references/revision_guide_spec.md`.
3. For AQA, read `references/oxfordaqa.md` because the implemented AQA route is
   based on OxfordAQA / Oxford International AQA pages.
4. For Edexcel or CAIE, first try official
   candidate discovery from the user's subject request. If more than one
   official candidate matches, return the choices and wait. If none matches,
   ask for an official subject-page URL, direct specification/syllabus PDF URL,
   or subject code. Do not silently switch to another board or reuse an AQA
   syllabus.
5. Run the generator CLI from the repository root with the confirmed
   `--language`, `--explanation-style`, optional `--exam-year`, and optional
   `--image-provider`. Confirm that detailed PDF
   syllabus units were extracted; do not accept broad web summary topics as the
   final guide structure when the PDF contains finer subject content.
6. Check `validation.json` before presenting the guide. A usable student guide
   needs detailed units, worked examples, source snippets, visual briefs,
   `sections/`, and `images/`; a guide with only broad topic headings is a
   failed draft.
7. Report how many complex infographic briefs were found. If the user provides
   a generation/import method, use it after the callable gate passes. If not,
   deliver the SVG fallbacks and warn that they are less reliable for complex
   information diagrams.
8. If the guide will be used with children, require subject-specialist review for
   worked examples before treating it as final exam preparation material.
9. Preserve the visual and narrative learning layer: after the base topic guide
   and practice items are generated, analyze which knowledge points or examples
   need visual explanation. Use deterministic SVG for simple diagrams. For
   complex infographic needs, create source-bound briefs and SVG fallbacks
   marked as needing review unless a callable route is available.
   When the visual is an exact chart/axis/curve/simple geometry case, read
   `references/scientific_vector_fallback.md` and keep the SVG editable,
   source-bound, and recorded as a scientific-vector fallback in the manifest.

## Commands

From a full repository checkout, install the package first when possible:

```bash
python -m pip install -e .
python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out ./outputs/chemistry-9202
```

If the package is not installed and the Agent only needs a local run, set
`PYTHONPATH` for the current shell:

```powershell
$env:PYTHONPATH='src'; python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out ./outputs/chemistry-9202
```

```bash
PYTHONPATH=src python -m intl_exam_guide generate --query chemistry --level igcse --language en --explanation-style friendly --out ./outputs/chemistry-9202
```

Use `--skip-pdf` only when no local browser or Playwright runtime is available.

## Anti-Patterns

- Do not ask for an image model during preflight.
- Do not show `gpt-image-2`, `qwen-image-pro`, `sensenova-u1-fast`,
  `deterministic-svg`, and `prompt-queue` as one user-facing model menu.
- Do not treat a recommended model name as a callable capability.
- Do not use AQA syllabus content when the user asked for Edexcel or CAIE.
- Do not accept a guide with only broad topic headings, missing worked examples,
  or missing visual briefs.
- Do not present SVG fallbacks for complex infographics as final reviewed
  teaching diagrams.
- Do not mix Chinese and English in student-facing handbook labels or topic
  bodies after the language lock is chosen.
- Do not leave obvious AI-template transitions in student-facing explanations
  or practice cards when a concrete sentence will do.

## Safety Rules

- Do not copy official past-paper questions, mark schemes, or large passages of
  specification/syllabus text into generated public examples.
- Keep the official page URL, specification URL, and PDF hash in every output.
- Treat the generated guide as incomplete if topic extraction, assessment
  extraction, source download, or HTML validation fails.
- Do not invent exam claims. If a topic needs deeper explanation, keep it inside
  the extracted syllabus text and mark it for review.
- Use AI image generation only as an optional illustration layer. Prefer
  deterministic SVG concept maps for simple structures. If an AI image model is
  used, record the model, prompt, source topic, caption, and review status; never
  let an illustration introduce unsupported exam claims.
