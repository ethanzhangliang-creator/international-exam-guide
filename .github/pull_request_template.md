## Summary

Describe the change.

## Type of change

- [ ] Parser/provider
- [ ] Rendering/design
- [ ] Validation/accuracy
- [ ] Documentation
- [ ] Tests/CI

## Checks

- [ ] `python -m pytest`
- [ ] `python -m compileall -q src tests scripts`
- [ ] `python scripts/scan_for_raw_keys.py .`
- [ ] Demo command runs, or change does not affect runtime behavior
- [ ] Runtime/validation evidence comes from the current code in a fresh output directory, not from old ignored `outputs/` or `validation.json` files
- [ ] No downloaded PDFs, past papers, mark schemes, or copied question content were committed
- [ ] Accuracy-sensitive changes preserve source URLs, PDF hashes, and validation behavior

## Notes for reviewers

Mention any manual review needed.
