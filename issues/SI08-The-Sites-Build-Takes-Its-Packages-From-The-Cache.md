# SI08 — The Site's Build Takes Its Packages From The Cache

```json
{
  "$schema": "issue-1.json",
  "id": "SI08",
  "title": "The Site's Build Takes Its Packages From The Cache",
  "state": "Review",
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

## As built

What is cached, under which key:

| Cache | Path | Key | Jobs |
|---|---|---|---|
| Maven's local repository | Maven's local repository | `maven-repository-<OS>-<hash of build/pom.xml>` | Shared rules check, Workflow check, the site's check (push only) |
| The wrapper's Maven | the wrapper's distribution directory | `maven-wrapper-<OS>-<hash of .mvn/wrapper/maven-wrapper.properties>` | the same three |
| The pinned Python packages | `wheels` in the runner's temporary directory | `pip-wheels-<OS>-python<version>-<hash of build/requirements.txt>` | the site's check and build |
| The last build's manifest | `now.json` | `site-<hash of the manifest>` | the site's build saves, its check looks up |

- **Restored and saved apart** (`actions/cache/restore` and `actions/cache/save`, the SHAs already pinned for v6.1.0),
  so a cache is saved as soon as the step that filled it passed, and a check that fails later still leaves it to the
  next run; the restore's key is what the pruning keeps. A cache is saved only when its restore missed. No older entry
  is restored in a new key's place, since its leftovers would be saved again under the new key and only ever grow.
- **The Python packages are kept as wheels, not as pip's own cache**: pip's cache still asks PyPI's index on every
  run, so a miss fetches the wheels with `pip download --require-hashes --only-binary=:all:` into the cached
  directory, and every run installs with `--no-index --find-links` from it, each package checked against its hash.
  Every pinned package has a hashed wheel for CPython 3.13 on Linux x86-64. The key names the Python version, which
  the check and build jobs each set (`PYTHON`), since the wheels are built for it; the prune job inherits no variable.
- **Pruning**: each of the three workflows ends with a job of its own, `prune`, after the jobs that save. It lists
  the entries under each cache's prefix with `gh cache list --key <prefix>` and deletes every one whose key is not
  the run's, by id (`gh cache delete <id>`), since one key may stand under several refs; the keys come from the
  saving jobs' outputs, and a cache the run did not restore names none and is left alone. A run on main prunes every
  ref; any other run - a pull request above all - prunes only its own ref, so a pull request never deletes the entry
  main still restores. It runs on every run that was not cancelled, not only after a save, so a delete that failed
  is tried again. A list or delete that fails only warns; a fork's read-only token and Dependabot's are expected to.
  It runs only where `github.server_url` is GitHub's, so another forge's token never goes to GitHub's API.
- **Permissions**: the `prune` job alone holds `actions: write`, and nothing else - no checkout, no fetched tool - so
  the token that may delete never meets the code the other jobs fetch. The workflows' own `permissions:` and the
  other jobs stay `contents: read`. `check-actions` refuses this until its list of jobs that may write names
  `shared-rules.yml/prune`, `site.yml/prune` and `workflows.yml/prune` with `actions`; that list belongs to the
  shared build tools, and the Workflow check fails on these workflows until it does.
- **The manifest's cache is pruned too**, under the prefix `site-`, and only when the site's build job passed. Its
  purpose is that an hourly run finding the current manifest's key has nothing to build; keeping only the last
  build's key keeps that, and a return to an older manifest now builds again, which is right, since the published
  site is the last build.
- **Retention**: only the newest entry of each cache is kept, per ref; main's run deletes every older one under every
  ref. Same-key copies under a pull request's ref stay until GitHub evicts them unused.
- **What still goes outside GitHub on a hit**: `build/pom.xml` takes the shared build tools as a snapshot with
  `updatePolicy` `always`, so Maven still asks Central's snapshot repository for their metadata on every run, and a
  moved snapshot's jars are fetched again on each run until the pom changes, since a hit saves nothing. Releases and
  plugins come from the cache alone. The pinned GraalVM that `porelo-machines jdk --github` installs is not part of
  this issue.
