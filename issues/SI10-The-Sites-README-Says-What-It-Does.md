# SI10 — The Site's README Says What It Does

```json
{
  "$schema": "issue-1.json",
  "id": "SI10",
  "title": "The Site's README Says What It Does",
  "state": "Review",
  "size": "XS",
  "priority": "Highest",
  "rank": 1,
  "blockedBy": [],
  "covers": "Every claim of the site's README.md and doc/ that build/assemble.py and the workflows do not bear out is corrected."
}
```

**Why this size.** XS: two sentences of the README and one comment, each read against the code. Estimate: 9 minutes
(Core's median for XS).

**What must be true.** What the README says the site and its workflow do is what `build/assemble.py` and
`.github/workflows/` do.

Filed 2026-11-14 on the operator's order, under ST361.

## Built

A sub-agent read about 37 claims of README.md, doc/ and the workflows' comments. It found 2, both confirmed in the code
and fixed here; none is a fault of the code.

- README.md: the theme has a tab per kind of part, each repository a section beneath it (`GROUPS` in
  `build/assemble.py`), not a tab per repository. The same comment in `build/assemble.py` is corrected.
- README.md: an hourly run that finds the last build's manifest unchanged builds nothing (`site.yml`, the job
  `check`), so not every run builds the whole site.
