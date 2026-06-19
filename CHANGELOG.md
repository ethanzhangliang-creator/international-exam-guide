# Changelog

## 0.2.4 - 2026-06-19

### Fixed

- Updated the intro-animation copy so Edexcel and CAIE are no longer described
  as future/URL-only work. The animation now reflects the current v0.2.x support
  model: AQA catalogue discovery, Edexcel official candidate matching, and CAIE
  official subject-index matching with exam-year confirmation.

## 0.2.3 - 2026-06-19

### Fixed

- Restored the clickable intro-animation preview directly under the project
  origin section in both English and Chinese READMEs, using the tracked GIF
  preview and linking to the full HTML animation.
- Made the full HTML intro animation standalone by inlining the local animation
  scripts, so opening `docs/project-intro-animation.html` from `file://` also
  auto-plays instead of being blocked by browser CORS rules.

## 0.2.2 - 2026-06-19

### Changed

- Darwin-optimized `skill/SKILL.md` and raised the independent judge score from
  about `81.1/100` to `91.1/100`.
- Added explicit `STOP` / `CHECKPOINT` gates for missing preflight choices,
  official candidate selection, missing official routes, base-handbook
  completion, non-callable image models, and final quality validation.
- Added a standard Edexcel/CAIE official-candidate response template so agents
  return choices to the user instead of guessing a subject route.
- Documented the real provider-resolution commands: AQA supports catalogue
  discovery, while Edexcel and CAIE use URL-first / subject-candidate checks
  rather than full-site crawling.
- Clarified that scratch candidate-check outputs are not final handbooks; agents
  must re-run with the user's confirmed language, style, output directory, and
  PDF settings after the official route is selected.

## 0.2.1 - 2026-06-19

### Changed

- Updated the public naming convention to use the familiar exam-board names
  AQA, Edexcel, and CAIE across the Skill, README, homepage copy, handoff notes,
  and hero artwork, while keeping the full official names as explanatory notes:
  OxfordAQA / Oxford International AQA, Pearson Edexcel, and Cambridge
  International / CAIE.
- Darwin-tuned `skill/SKILL.md` so the agent flow is clearer: confirm exam
  board, subject, required exam year, output language, and explanation style
  first; do not ask for an image model before the base handbook run.
- Added `skill/test-prompts.json` with regression prompts for AQA Accounting,
  ambiguous Edexcel subject selection, CAIE exam-year selection, and non-callable
  image-model requests.

### Fixed

- Fixed Chinese handbook content generated during real Accounting/Economics
  runs so visible focus labels no longer fall back to generic text such as
  `第 N 个官方大纲要求`.
- Translated student-facing Chinese Accounting examples that previously leaked
  raw English terms such as `purchase invoice`, `purchases journal`, and
  `ledger accounts`.
- Fixed the Chinese visual-type classifier so the word `infographic` no longer
  accidentally triggers the pH/acid label merely because it contains `ph`.
- Added Accounting as a Chinese subject display name (`会计学`) in rendered
  handbook covers and overview blocks.
- Treated `sensenova-generated` image assets as renderable generated raster
  infographics, so externally generated SenseNova assets can be preserved and
  rendered.
- Increased browser PDF export timeout for image-heavy handbooks.
- Added validation and regression tests for the Chinese placeholder, Accounting
  Chinese terminology, SenseNova asset status, Accounting display name, and the
  visual-type classifier.
- Removed remaining user-facing wording that made the project look like an
  OxfordAQA-only Skill after the v0.2.0 three-board upgrade.
- Tightened image-generation instructions so recommended models such as GPT
  Image 2.0, Qwen Image 2.0 Pro, and SenseNova U1 Fast are described as
  recommendations, not guaranteed built-in capabilities.
- Generalized source-safety wording from OxfordAQA-only PDFs to official PDFs
  from all supported exam boards.

## 0.2.0 - 2026-06-19

### Added

- Added URL-first MVP providers for Pearson Edexcel and Cambridge International / CAIE while keeping OxfordAQA generation working.
- Added `--exam-year` support so Cambridge subject pages with multiple syllabus year ranges can select the correct syllabus or fail with a clear request for the exam year.
- Added provider/source metadata fields for provider name, qualification family, specification URL, PDF hash, syllabus year range, selected exam year, route tags, command words, assessment objectives, and paper/unit/component details.
- Added live smoke coverage for OxfordAQA, Pearson International GCSE, Pearson International AS/A Level, Cambridge IGCSE, and Cambridge International AS/A Level.

### Changed

- Complex infographic routing now defaults to source-bound `visual_brief` / prompt queue output. GPT Image 2.0, Qwen Image 2.0 Pro, and SenseNova U1 Fast are documented as recommended external options, not guaranteed built-in capabilities for every user.
- `--image-provider` is optional and defaults to `prompt-queue`. Real image generation or import only happens when the user supplies a callable skill, API, script, asset directory, or custom provider configuration.
- Validation now treats missing complex infographic files as pending external-generation work instead of claiming provider-selected images were generated.

### Fixed

- Cambridge missing `exam_year` on multi-range syllabus pages now stops clearly instead of silently choosing a syllabus.
- Provider validation no longer applies OxfordAQA modular assumptions to Cambridge AS/A Level outputs.
- Topic-count sanity checks now catch obviously thin extraction from downloaded specification/syllabus PDFs.

## 0.1.1 - 2026-06-18

### Fixed

- Fixed OxfordAQA syllabus parsing so subjects such as Accounting no longer fall back to a few top-level table-of-contents headings.
- Expanded body-table syllabus sections into teachable knowledge units when the official PDF uses broad `3.x` sections instead of many leaf topic codes.
- Preserved PDF body source snippets from the parser and skipped contents/index pages during fallback source matching.
- Added Accounting/finance subject profiling so Accounting examples use source documents, books of prime entry, ledgers, reconciliation, statements, and ratios instead of borrowed Mathematics templates.
- Routed Accounting, Economics, Business, and other complex visual explanations to infographic prompts instead of unsafe or misleading SVG drafts.
- Strengthened validation to fail empty syllabus topics, contents-page-only source anchors, placeholder practice frames, and cross-subject borrowed practice questions.
- Added regression tests for Accounting-style body tables, source-snippet preservation, and non-math example generation.

### Added

- Added the first multi-provider foundation: a common `ExamBoardProvider` contract, provider registry, URL-based provider inference, and model fields for Cambridge syllabus year ranges and Edexcel modular/unit structures.
- Added explicit guardrails for Pearson Edexcel and Cambridge International / CAIE URLs. In this release they were recognised as roadmap providers and stopped with a clear roadmap message.

### Verified

- Accounting International GCSE: 68 topics, 136 practice cards, 68 infographic briefs.
- Mathematics International GCSE: 90 topics, 180 practice cards, 43 SVG-safe briefs, 39 infographic briefs.
- Chemistry International GCSE: 35 topics, 70 practice cards, 14 SVG-safe briefs, 18 infographic briefs.
- Economics International GCSE: 38 topics, 76 practice cards, 38 infographic briefs.
- Business International AS-A-level: 29 topics, 58 practice cards, 29 infographic briefs.

### Notes

- `prompt-queue` remains the safe no-API image route. Complex infographic briefs require a callable external skill/API/script, generated asset directory, or custom provider before final raster assets are added.
- Official specification PDFs and extracted official text are generated at runtime and are not committed to the repository.

## 0.1.0 - Initial public architecture draft

- Initial OxfordAQA-focused Skill architecture for generating International GCSE and International AS-A-level revision handbooks.
- Added language selection, explanation style selection, visual routing, source appendix, HTML/PDF packaging, and release-sample documentation.
