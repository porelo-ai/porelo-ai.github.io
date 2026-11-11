# SI08 — The Site's Build Takes Its Packages From The Cache

```json
{
  "$schema": "issue-1.json",
  "id": "SI08",
  "title": "The Site's Build Takes Its Packages From The Cache",
  "state": "Idea",
  "size": "S",
  "priority": "Medium",
  "rank": 2,
  "blockedBy": [],
  "covers": "The site's workflows take Maven's dependencies and the pinned Python packages from the Actions cache, keyed by what pins them, and keep only the newest entry of each."
}
```

**Why this size.** cache steps in three workflows and one pruning step; no code.

Filed 2026-11-11 as this repository's part of `porelo-project` ST317, "Builds take outside downloads from a cache".

**What must be true.** Every download from outside GitHub that a build of the site makes comes from the Actions cache
after its first run, and the cache holds only the newest state of each.

How it is today, read in the workflows:

- `shared-rules.yml`, `site.yml` and `workflows.yml` cache the wrapper's Maven only; `dependency:build-classpath`
  over `build/pom.xml` fetches the tools and every dependency from Maven Central on each run.
- `site.yml`'s two jobs run `pip install --require-hashes -r build/requirements.txt` with no pip cache.

## Plan

- Cache Maven's local repository keyed by `hashFiles('build/pom.xml')`, and pip's cache keyed by
  `hashFiles('build/requirements.txt')` (`actions/setup-python`'s `cache: pip`, or one `actions/cache` step).
- After saving a new entry, delete the older entries of the same cache (`gh cache delete` by prefix).

## Acceptance

- A second run on one commit downloads nothing from Maven Central or PyPI; the cache list holds one entry per cache.
