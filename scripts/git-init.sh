#!/usr/bin/env bash
# MemoryWeave — Phase 1, Chapter 1.1
# Run this script once inside the memoryweave/ directory to initialize
# the local git repo and make your first commit.
#
# Usage:
#   chmod +x scripts/git-init.sh
#   ./scripts/git-init.sh
#
# Ravi Kashyap 2025-03-22 — Phase 1, Chapter 1.1

set -e

echo "==> Initializing MemoryWeave git repository..."

git init
git checkout -b main

git add .
git commit -m "chore(p1/ch1.1): init repo, add LICENSE, .gitignore, .editorconfig, issue templates, CONTRIBUTING.md, README, CHANGELOG, docs/phase-1-setup.md"

echo ""
echo "==> Creating branch structure..."
git checkout -b dev
git checkout -b phase/1-foundation
git checkout dev

echo ""
echo "Done. Branch structure:"
git branch

echo ""
echo "Next steps:"
echo "  1. Create a new repo on GitHub: https://github.com/new"
echo "  2. Add the remote:"
echo "     git remote add origin https://github.com/ravii-k/memoryweave.git"
echo "  3. Push:"
echo "     git push -u origin main"
echo "     git push origin dev"
echo "     git push origin phase/1-foundation"
echo ""
echo "Then continue with Chapter 1.2: Python package skeleton"
