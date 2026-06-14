# Contributing

Thank you for considering a contribution.

## Principles

- Keep source traceability intact.
- Do not commit downloaded specification PDFs, past papers, mark schemes, or
  copied question content.
- Add tests for parser changes.
- Prefer deterministic extraction and validation before optional AI authoring.
- Keep the Codex skill concise; put stable logic in Python code.

## Local Checks

```bash
pip install -e ".[dev]"
python -m pytest
python -m compileall -q src tests
```

## Adding a Provider

1. Add a module under `src/intl_exam_guide/providers/`.
2. Preserve source URLs and downloaded-file hashes.
3. Add synthetic fixtures. Do not commit copyrighted PDFs.
4. Add validation rules if the provider has different qualification structures.

## Adding Authoring

Deep examples, answers, diagrams, or generated explanations must cite extracted
source snippets and pass review. A pretty answer that cannot be traced is not a
valid answer for this project.
