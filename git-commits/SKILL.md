---
name: git-commits
description: Use when writing any Git commit message — commit messages must be a single line with no Co-Authored-By trailer, ever
---

# Git Commit Formatting

## Rules

1. **Single line only.** No multi-line commit messages. No body, no bullet points, no blank line followed by details. One line.
2. **No Co-Authored-By.** Never append `Co-Authored-By` or any similar trailer. Omit it entirely.

## Why terse commits

Short, single-line commits keep `git log --oneline` identical to `git log`, making history scannable without formatting flags. Multi-line messages create noise in log output, PR merge commits, and blame annotations. The diff already captures *what* changed — the commit message only needs to capture *why* in a few words.
