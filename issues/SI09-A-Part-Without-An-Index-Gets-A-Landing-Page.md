# SI09 — A Part Without An Index Gets A Landing Page

```json
{
  "$schema": "issue-1.json",
  "id": "SI09",
  "title": "A Part Without An Index Gets A Landing Page",
  "state": "Idea",
  "size": "S",
  "priority": "Medium",
  "rank": 3,
  "blockedBy": [],
  "covers": "A part whose doc/ has pages but no index.md gets a landing page the site writes, listing its pages by their titles, so its section root answers and the home page links it."
}
```

**Why this size.** one function in `build/assemble.py` beside `nav_of`, the home page's link to a part's first page,
and their tests; no contract another repository reads.

Filed 2026-11-11 from a finding on the first site built after [SI07](README.md#si07).

**What must be true.** Every part the site takes has a page at its section root. Today `forge-clients`, `ecosystems`
and `mcp` have pages (`/mcp/binding/` answers), but their doc/ holds no `index.md`: `/<name>/` answers 404 and the
home page's navigation does not link them.

## Plan

- When a part's doc/ has pages and no `index.md`, the site writes `<name>/index.md`: the part's name and description
  from `project.yml`, and a list of its pages, each by its first heading (the file name when it has none), in the
  section's order. A part with its own `index.md` keeps it unchanged.
- The written page leads the section's `nav`, so `first_page` and the home page link it.
- Red first in `tests/test_assemble.py`: a part with two pages and no index gets a landing page listing both by title,
  first in its section; a part with its own index keeps it.

## Acceptance

- The tests above, seen red first.
- After the next published build, `/forge-clients/`, `/ecosystems/` and `/mcp/` answer 200 and the home page links them.
