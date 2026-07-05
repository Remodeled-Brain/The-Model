# ADR 0002 — Repository location and sync model

**Date:** 2026-07-05
**Status:** Adopted (supersedes any earlier assumption about where the repo lived)

## Context

The Model is worked on by several LLMs across machines. An earlier setup kept the repo inside a cloud file-sync folder so it would sync across machines. During setup that synced folder **silently emptied itself** — the file-sync tool and git fought over the same `.git` directory. At that point different LLMs held different assumptions about where the repo lived (one still assumed the old synced location), which is exactly the drift this project's structure exists to prevent.

## Decision

1. **Canonical working copy lives at `C:\Users\david\Documents\The Model`** — a plain local folder that is **not** inside any cloud file-sync folder.
2. **Cross-machine sync is via a private GitHub repo (`origin`) only.** No file-sync tool may sync the repo, and especially not `.git`.
3. The local path may differ on other machines, but the **sync source of truth is always the GitHub remote**, not a synced folder.

## Consequences

- Every LLM/machine clones or pulls from GitHub; nobody relies on a file-sync tool for this repo.
- Any prior note (memory, chat, doc) that names a synced-folder path as the home is void — this ADR overrides it.
- File-sync tools go back to syncing ordinary documents only.

## Propagation

Because this changes a project-wide fact, it is recorded here and referenced from `README.md` and the bootstrap files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) so any LLM re-reading the repo picks it up. Other LLMs already in flight (e.g. ChatGPT) must be pointed at this ADR to correct their assumption.

## Remote

`origin` is the private GitHub repo **`Remodeled-Brain/The-Model`** - https://github.com/Remodeled-Brain/The-Model . All machines clone/pull/push against it. The local `origin` URL embeds the account username (`https://Remodeled-Brain@github.com/Remodeled-Brain/The-Model.git`) so Windows Credential Manager selects the correct account's token instead of another cached GitHub account.
