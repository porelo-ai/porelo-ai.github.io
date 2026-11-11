# SI07 — The Site Reads Each Repository At Its Central Address

```json
{
  "$schema": "issue-1.json",
  "id": "SI07",
  "title": "The Site Reads Each Repository At Its Central Address",
  "state": "Review",
  "size": "S",
  "priority": "High",
  "rank": 1,
  "blockedBy": [],
  "covers": "The site is built from every repository porelo-project's `project.yml` lists, each read at its `central` address in https form; one it cannot name on GitHub stops the build instead of leaving it out."
}
```

**Why this size.** one function in `build/assemble.py` and its tests, no contract another repository reads.

Filed 2026-11-11 from an operator's finding: the published site shows only porelo-project.

**What must be true.** https://porelo-ai.github.io/ shows every repository `project.yml` lists. Today
`build/assemble.py` reads `repositories.<name>.upstream`; since porelo-project renamed that key to `central` on
2026-11-07, every build logs "skipped <name>: no GitHub upstream in project.yml" for all 19 repositories and publishes
a site of the project's own pages alone. The builds stay green, as nothing checks that a listed repository is taken.

## Plan

- `parts` reads `central` and turns `git@github.com:<owner>/<repo>.git` into its https form, as it did `upstream`.
- A repository `project.yml` lists whose address names no GitHub repository stops the build, naming each such
  repository, as one that cannot be read already does; an empty site turns the build red.
- Red first in `tests/test_assemble.py`: the parts read `central`, and a listed repository with no GitHub central
  address stops the build.

## Acceptance

- The tests above, seen red first.
- The next published build shows every repository's section again.

## As built

- Only `central` is read; a repository still naming its address as `upstream` alone stops the build like one with no
  address, so a key renamed again cannot empty the site unseen.
- Built as a fix during an operator test: its unit tests seen red, then green; the reading by another model follows.
