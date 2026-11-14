# SI06 — The Site's Agent Works In A Porelo Task

```json
{
  "$schema": "issue-1.json",
  "id": "SI06",
  "title": "The Site's Agent Works In A Porelo Task",
  "state": "Backlog",
  "size": "S",
  "priority": "Medium",
  "rank": 1,
  "blockedBy": ["SI05"],
  "openQuestions": 0,
  "covers": "The site's agent works in a Porelo task on the move's host as `Agent Docsite` and talks in the room; its build's Pages upload and its reading of GitHub are first switched by variables on both forges"
}
```

**Why this size.** S: one workflow, the collector and its tests, then the trial on the rented host. Estimate: 38
minutes (Core's median for S), the trial's waits not counted.

**How it stands.** Blocked by [SI05](README.md#si05).

**What must be true.** porelo-ai.github.io's agent works in a Porelo task on the move's host, as the project's procedure for an agent's
move lays out, and takes this issue to
Review inside the task with the host's Forgejo build green. It talks in the project's room as `Agent Docsite`, from
the nickname `Docsite` that porelo-project's `project.yml` is to give the repository `site`.

## Plan

- **The repository:** `porelo-ai.github.io`, the repository `site` in porelo-project's `project.yml`, alone; `porelo`
  and `porelo-adapters` move by issues of their own.
- **The task's image:** this repository's `porelo.yml`, which builds in a task once [SI05](README.md#si05) is done.
- **The Pages upload**, read in today's `site.yml`: the `build` job's `actions/upload-pages-artifact` step runs on every
  push, while `publish` is already off unless `vars.PUBLISH` is `true` and `prune` runs only where `github.server_url`
  is GitHub's. The upload step takes `if: vars.PORELO_PUBLISH != 'false'`, the variable porelo-host's
  `doc/local-forge.md` (*The local registry and publication settings*) sets to `false` on the host's forge and `true`
  centrally, so the workflow reads the same on both forges.
- **The reading of the other repositories:** `build/assemble.py` reads porelo-project's `project.yml` from
  `api.github.com` and clones every repository at its central GitHub address with `secrets.PORELO_DOCS_READ`, a
  GitHub token the host's forge does not have and never gets. On the host's forge the Build runs only the collector's
  tests (`tests/`) and this repository's own checks; the whole site is collected and built on GitHub alone. The steps
  that read the other repositories - the `check` job's "What would be taken now", and in `build` the collection, the
  strict site build and the upload - take `if: vars.PORELO_PUBLISH != 'false'`, the same variable as the upload, so
  the workflow reads the same on both forges and nothing in it names a forge.
- **Steps:** (1) the switch; (2) the procedure's dry run on the development machine; (3) the
  trial on the rented host, this issue taken to Review inside the task with the forge's Build green, the agent
  talking as `Agent Docsite`; (4) the way back.

## Acceptance

- `site.yml` green on GitHub with the whole site collected, built strict and its Pages artifact uploaded.
- `site.yml` green on the host's forge with the collector's tests and the repository's own checks run, and no step
  reading another repository: seen to fail first, a run there that still reaches the collection fails for lack of
  `PORELO_DOCS_READ`.
- On the host: the procedure's check, each line green.

## To be checked

- The `check` job's `decide` step and the `build` job's `if` read the key of "What would be taken now". With that step
  switched off, the host's run must still run the collector's tests and the repository's checks, and must not read a
  missing key as "nothing changed" or as a failure.
