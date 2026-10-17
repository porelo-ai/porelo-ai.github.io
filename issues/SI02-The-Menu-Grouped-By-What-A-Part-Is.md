# SI02 — The Menu Grouped By What A Part Is

**Status:** Review.
**Size:** S - one mapping and the grouping in `build/assemble.py`, the landing page out of the menu, and tests of the
menu's shape.

**What must be true.** The site's menu has six tabs, in this order and in lower case. Each repository is a section
in the left sidebar of its tab, with its own pages beneath:

| Tab | Sections |
|---|---|
| `porelo` | the core's own pages, with no section between |
| `agents` | `claude code`, `pi`, `omp` |
| `build readers` | `github` |
| `messaging` | `matrix`, `sluice` |
| `ui` | `frontend`, `intellij` |
| `internal` | `buildtools`, `porelo project` |

- **The landing page** has no tab. The site's title at the top left leads to it, and its ways in still link to their
  pages.
- **A repository with pages that the mapping does not name** is a tab of its own after these, under its name, so a
  new one is never lost.
- **The site itself and the parent POM** have no `doc/`, so they stay out of the menu as today.

## Plan

Read in today's code:

- `assemble()` builds `nav` as `[{"Porelo": "index.md"}]`, then appends `{name: section}` for every repository with a
  `doc/`, in the order `parts(project)` gives. That order is `porelo-project`'s `project.yml`, with `porelo-project`
  last.
- The names are those in `project.yml`: `core`, `claude`, `pi`, `omp`, `github`, `matrix`, `sluice`, `frontend`,
  `intellij`, `buildtools`, plus `porelo-project`. Each repository's pages are copied under `docs/<name>/`.
- The theme has `navigation.tabs`, `navigation.sections` and `navigation.indexes`. A top-level entry of `nav` is a
  tab, and a list under it shows as sections in the sidebar. Material has no drop-downs in the top bar.

The plan:

- **The mapping in `assemble.py`,** not in `project.yml`: that is a real Porelo project file with no field for groups.
  It is an ordered list of tabs. Each tab has a list of `(name in project.yml, label)` pairs:
  - `porelo`: `core` alone, whose section becomes the tab's own pages with no section level;
  - `agents`: `claude` as `claude code`, `pi`, `omp`;
  - `build readers`: `github`;
  - `messaging`: `matrix`, `sluice`;
  - `ui`: `frontend`, `intellij`;
  - `internal`: `buildtools`, `porelo-project` as `porelo project`.

  The Bitbucket and Jenkins readers join `build readers` as `bitbucket` and `jenkins` once they exist.
- **`grouped(sections)`** takes the per-repository sections as `assemble()` builds them now and returns the `nav`:
  - one tab per group that has at least one built repository, in the mapping's order;
  - a tab with no repository is left out;
  - after them, every built repository the mapping does not name, as its own tab, with a log line naming it.
- **The landing page:**
  - `{"Porelo": "index.md"}` goes. `index.md` is still written and is the site's root, where the title links.
  - MkDocs reports a page outside `nav` at level INFO by default (`validation.omitted_files`), which `strict` does
    not fail on. The config still sets `not_in_nav: /index.md`, so this does not hang on a default.
  - The ways in and the table of parts keep their links, since the pages' paths (`core/...`) do not change.
- **URLs stay as they are:** only the menu changes, not where a page is served, so no link from outside breaks.

Steps:

1. **Red first,** in `tests/test_assemble.py`:
   - the `nav` of a build with all the repositories has the six tabs in order, their labels, and the core's pages
     directly under `porelo`;
   - an unnamed repository is a tab at the end;
   - a group with nothing built is left out;
   - `index.md` is not in `nav` and is still written.
2. The mapping and `grouped`.
3. A strict build of the site from local checkouts passes, with the tabs as above.

## As built

- `GROUPS` and `grouped()` in `build/assemble.py`. `assemble()` collects each built repository's section by name and
  writes `nav: grouped(sections)` with `not_in_nav: /index.md`.
- `messaging` (`matrix`, `sluice`) was added: both repositories have a `doc/`.
- **A strict build from local checkouts of every repository passes:** Material for MkDocs at the pinned versions, in a
  throwaway Python container. It shows the six tabs in order, the landing page with its ways in, and the logo leading
  to it.
- `tests/test_assemble.py`'s `MenuTest`: the six tabs with their labels, a repository no group names at the end, a
  group with nothing built left out, and the landing page written and out of the menu.

