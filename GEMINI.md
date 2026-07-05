# Gemini bootstrap

You are working on **The Model**, a platform-agnostic scaffold shared across multiple LLMs.

1. Read `CONTRIBUTING.md` in full and follow every rule. It governs how all LLMs work here.
2. Then read `model/00_readme_for_llms.md`.
3. Provider-specific notes for you live in `providers/google/`.
4. Log any change as a new fragment in `changelog.d/` — do not edit `CHANGELOG.md` directly.

Do not treat candidate material as adopted. Stress-test; do not praise.

> Note: auto-loaded only by Gemini CLI. In a browser chat, the user must paste `CONTRIBUTING.md` manually.

## Canonical location & sync (read this)

The working copy lives at `C:\Users\david\Documents\The Model` (a plain local folder, **not** inside any cloud file-sync folder). Cross-machine sync is via the private GitHub remote **only**: `git pull --rebase origin main` before you start, push when done. Never let a file-sync tool sync this repo. See `decisions/0002-repo-location-and-sync.md`. If you were told the home is a synced-folder path, that is outdated — ADR 0002 overrides it.
