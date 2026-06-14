---
name: international-exam-guide
description: Generate source-traceable OxfordAQA International GCSE and International AS/A-level revision guides from public subject pages and course specification PDFs, including syllabus extraction, assessment summaries, student guide rendering, validation, and optional PDF export.
---

# International Exam Guide

Use this skill when the user asks for an International GCSE or International
AS/A-level subject revision guide, especially for OxfordAQA. Treat IGCSE as a
user-facing alias for International GCSE, but use the full qualification names
in generated documentation.

Current provider support is OxfordAQA only. Pearson Edexcel and Cambridge
International / CAIE are roadmap providers for the China-market version, but
they need their own provider references and parser checks before generation.
Do not run the OxfordAQA provider against Edexcel, Cambridge, or generic AQA UK
pages.

## Workflow

1. Identify the qualification board, subject, level, and code if available.
2. For OxfordAQA, read `references/oxfordaqa.md`.
3. If the requested provider is Pearson Edexcel or Cambridge International /
   CAIE, explain that it is planned but not implemented in the current release.
4. Run the generator CLI from the repository root.
5. Check `validation.json` before presenting the guide.
6. If the guide will be used with children, require subject-specialist review for
   worked examples before treating it as final exam preparation material.

## Commands

```bash
PYTHONPATH=src python -m intl_exam_guide generate --query chemistry --level igcse --out ./outputs/chemistry-9202
```

Use `--skip-pdf` only when no local browser or Playwright runtime is available.

## Safety Rules

- Do not copy OxfordAQA past paper questions, mark schemes, or large passages of
  specification text into generated public examples.
- Keep the official page URL, specification URL, and PDF hash in every output.
- Treat the generated guide as incomplete if topic extraction, assessment
  extraction, source download, or HTML validation fails.
- Do not invent syllabus facts. If a topic needs deeper explanation, generate it
  from the extracted specification text and mark it for review.
