# SI01 — The Site Moves To Zensical

**Status:** Analyzed.
**Size:** M - the requirements with their hashes, the workflow's build step and a side-by-side check of the rendered
pages; the collector (`build/assemble.py`) keeps writing a `mkdocs.yml`, which the successor reads.

**What must be true.** The site is built by a generator its makers maintain: Zensical, the successor of Material for
MkDocs, once it reaches 1.0 or once Material's promised support ends, about 2026-11-05, whichever comes first.

## Why

Material for MkDocs has been in maintenance mode since 2025-11-05; its makers committed to fixing critical bugs and
security vulnerabilities for at least twelve months, and call MkDocs 1.x, which it builds on, unmaintained. Zensical
is their successor and reads an existing `mkdocs.yml` with Material's configuration, so the collector's output should
carry over; it was at 0.0.68 on 2026-10-05, releasing every few days.

## Plan

- `build/requirements.txt`: the successor and its dependencies, pinned with `--hash` as today; `mkdocs`,
  `mkdocs-material` and what only they need taken out.
- `.github/workflows/site.yml:109`: the build step runs the successor's build command on the same
  `$RUNNER_TEMP/site/mkdocs.yml` instead of `mkdocs build --strict`, with its strict mode if it has one.
- `build/assemble.py` stays: it writes the `mkdocs.yml` (`:265`) the successor reads; only a key the successor does not
  take is changed there.
- Red first: both builds of the same collected tree side by side - the Agents table, a long page of `core` and the tabs
  - a page cut off or missing in the new build is the failing case; the collector's tests (`tests/`) stay green.

## Acceptance

- The workflow builds the whole site with Zensical, pinned by hash like the rest, and the collector's tests pass.
  Seen to fail: a page Material rendered (the Agents table, a long page of `core`, the tabs) missing or cut off in
  Zensical's build, compared side by side before the switch.
- Nothing of MkDocs or Material is installed any more.

## To be checked

- Whether every feature the site uses (tabs, sections, search, both colour schemes, permalinks) is there in the
  version taken (Agent Core's, measured on its build).
- Whether to wait for its 1.0 or switch by 2026-11-05 whatever its version (the operator's).
