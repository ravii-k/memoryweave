# Phase 1 — Repo foundation & project setup

**Phase:** 1 of 8
**Timeline:** Week 1, Days 1–7
**Chapters:** 1.1 · 1.2 · 1.3 · 1.4
**Author:** Ravi Kashyap
**Started:** 2025-03-22

---

## Overview

Phase 1 establishes every project-wide convention, tool, and scaffold that all future
phases depend on. Nothing functional is built here — but getting this right means every
future chapter has a clean, consistent foundation to build on.

The goal at the end of Phase 1: a clean GitHub repo, passing CI, an installable (empty)
Python package, and all conventions documented so any contributor can onboard instantly.

---

## Chapter 1.1 — Repo & Git setup

**Days:** 1–2
**Status:** In progress
**Author:** Ravi Kashyap · 2025-03-22

### What was built

| File / Directory | Purpose |
|-----------------|---------|
| `LICENSE` | MIT License — maximises adoption and contribution |
| `.gitignore` | Ignores Python caches, venvs, node_modules, secrets, vector store data |
| `.editorconfig` | Enforces consistent indentation and line endings across all editors |
| `README.md` | Project overview, quickstart stub, roadmap, badge placeholders |
| `CHANGELOG.md` | Version history — updated every phase end |
| `CONTRIBUTING.md` | Full contributor guide: setup, branch conventions, commit format, comment rules, docstring format, testing and doc requirements |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Structured bug report template |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Structured feature request template |
| `.github/pull_request_template.md` | PR checklist enforcing tests, docs, and comment conventions |

### Design decisions

**Why MIT License?**
MIT is the most permissive common license. It allows commercial use, modification, and
distribution with no restrictions beyond attribution. For a developer tool like
MemoryWeave, this maximises adoption. AGPL (as used by MiroFish) is a valid choice for
server-side tools but would deter embedding in commercial products.
*Decision by:  Ravi Kashyap · 2025-03-22*

**Why `.editorconfig` over only `ruff` / `prettier`?**
`.editorconfig` works at the editor level — before any linter runs. This means even
contributors who haven't set up the full dev environment get consistent formatting
from day one. It complements, not replaces, `ruff` and `prettier`.
*Decision by: Ravi Kashyap · 2025-03-22*

**Branch strategy chosen:**
```
main          — always stable, always tagged, never committed to directly
dev           — active development, all PRs merge here first
phase/N-name  — per-phase feature branches, created at phase start,
                merged to dev at each chapter completion
fix/short-name   — hotfix branches off main
feat/short-name  — feature branches for community contributions
```
*Decision by: Ravi Kashyap · 2025-03-22*

### Commit for this chapter

```bash
git add .
git commit -m "chore(p1/ch1.1): init repo, add LICENSE, .gitignore, .editorconfig, issue templates, CONTRIBUTING.md"
```

---

## Chapter 1.2 — Python package skeleton

**Days:** 2–3
**Status:** Planned
**Author:** Ravi Kashyap

*To be documented when Chapter 1.2 is complete.*

---

## Chapter 1.3 — CI/CD pipeline

**Days:** 4–5
**Status:** Planned
**Author:** Ravi Kashyap

*To be documented when Chapter 1.3 is complete.*

---

## Chapter 1.4 — Config & base classes

**Days:** 6–7
**Status:** Planned
**Author:** Ravi Kashyap

*To be documented when Chapter 1.4 is complete.*

---

## Phase 1 deliverables (end of week 1)

- [ ] Clean GitHub repo with all conventions in place
- [ ] Passing CI on every push
- [ ] Installable empty Python package (`pip install -e .`)
- [ ] Tagged `v0.0.1-setup` on `main`

---

## Dependencies introduced this phase

| Package | Version | Purpose |
|---------|---------|---------|
| *(none yet — Chapter 1.2)* | | |

---

## Known limitations

- README badges will show errors until PyPI and npm packages are published (Phase 4/5).
- CI workflow is a placeholder until Chapter 1.3.

---

## What Phase 2 builds on top of

Phase 2 (NLP pipeline) will import the base classes and config dataclass defined in
Chapter 1.4. The virtual environment and pre-commit hooks set up in Chapter 1.3 will
enforce code quality from the first line of real code written.

---

*Document created: Ravi Kashyap 2025-03-22 (Phase 1, Chapter 1.1)*
*Last updated: Ravi Kashyap 2025-03-22*
