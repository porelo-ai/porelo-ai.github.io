# SI03 — Sokar Renamed Porelo Here

**Status:** Estimated.
**Size:** S - 141 occurrences in 9 of 20 files, no path; the site's repository, its address and one secret are
renamed at GitHub.

**What must be true.** The site is Porelo's, published from `porelo-ai.github.io` at its own address, assembled
from the renamed repositories' documents; no tracked file outside the exceptions says `sokar`. From [PJ41](https://github.com/sokar-ai/sokar-project/blob/main/issues/README.md#pj41).

## Plan

**How:** one commit, made by a script this repository's agent runs and reviews, never by hand: `git mv` for every
path naming `sokar`, then `sokar`/`Sokar`/`SOKAR` replaced by `porelo`/`Porelo`/`PORELO`, then the exceptions below
put back. Nothing is renamed before the window is announced.

**What carries the name:** `build/assemble.py` (23) and its tests (35), which name the repositories it reads and the
tabs; the two workflows; `build/pom.xml` (the tools' coordinates); `AGENTS.md` and the README.

**Names outside, renamed in the window's preparation:** the repository `sokar-ai.github.io` itself, which GitHub
Pages serves at the organisation's address, and the secret `SOKAR_DOCS_READ` the site workflow reads - after the
replacement it reads `PORELO_DOCS_READ`, which must exist first.

**Exceptions:** a sentence that says what the old name was.

**What the script cannot do by replacement:** nothing found; the site shows the logo from `sokar`'s documents.

**Published before this builds:** every repository the site assembles, renamed on GitHub, so its reads resolve.

**How it is tested:** red first, a `test_documents_*.py` that fails while any tracked file outside the exceptions
says `sokar`; then `check-shared`, `check-citations` and the tests, and the site built and served at its new address.

## Acceptance

- The test above is red before the script and green after it, and stays.
- The site is served at `porelo-ai.github.io` with every repository's pages.
