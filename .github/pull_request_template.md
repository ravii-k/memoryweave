## Summary
What does this PR do? One paragraph max.

## Phase & Chapter
- Phase: P__
- Chapter: __.__
- Related issue: #___

## Type of change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change (existing behaviour changes)
- [ ] Documentation update
- [ ] Refactor (no behaviour change)
- [ ] Test addition / fix
- [ ] CI / tooling change

## Changes made
- Added `...`
- Updated `...`
- Removed `...`

## How to test
Steps to verify this works:

```bash
cd packages/core
pytest tests/test_xxx.py -v
```

## Checklist
- [ ] All tests pass (`pytest`)
- [ ] No linting errors (`ruff check .`)
- [ ] New public functions have docstrings with `Added: [Name] [Date] (Phase X, Chapter X.X)`
- [ ] Changed lines have inline comments with name + date where behaviour changed
- [ ] Relevant doc file in `docs/` updated or created
- [ ] `CHANGELOG.md` entry added
- [ ] No secrets or API keys committed
