# SI06 — The Site's Agent Works In A Porelo Task

```json
{
  "$schema": "issue-1.json",
  "id": "SI06",
  "title": "The Site's Agent Works In A Porelo Task",
  "state": "Analyzed",
  "size": "S",
  "priority": "Medium",
  "rank": 1,
  "blockedBy": ["SI05"],
  "openQuestions": 1,
  "covers": "The site's agent works in a Porelo task on the move's host as `Agent Docsite` and talks in the room; its build's Pages upload and its reading of GitHub are first switched by variables on both forges"
}
```

**Why this size.** S: one workflow, the collector and its tests, then the trial on the rented host. Estimate: 38
minutes (Core's median for S), the trial's waits not counted.

**How it stands.** Blocked by [SI05](README.md#si05); one open question.

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
  GitHub token. The host's forge has no such secret. How the site's Build reads them there is the open question;
  whichever answer, it is switched by a variable both forges carry, never by a branch in the workflow, and
  `tests/test_assemble.py` gets a test for each value, the one for the host's red first.
- **Steps:** (1) the two switches and their tests; (2) the procedure's dry run on the development machine; (3) the
  trial on the rented host, this issue taken to Review inside the task with the forge's Build green, the agent
  talking as `Agent Docsite`; (4) the way back.

## Acceptance

- `site.yml` green on GitHub with the Pages artifact uploaded, and green on the host's forge with none uploaded and
  nothing read from GitHub with a token the host does not have.
- On the host: the procedure's check, each line green.

## Open questions

- How the site's Build reads the other repositories on the host's forge, where `secrets.PORELO_DOCS_READ` (a GitHub
  read token) is not set: (a) the host's forge gets that read-only token as an organization secret, set by
  porelo-host's `up`, so the host builds the whole site as GitHub does; (b) on the host the Build runs the collector's
  tests and this repository's own checks only, and the whole site is built on GitHub alone, which needs no token on
  the host. Proposed: (b), since no GitHub credential then reaches a rented host, and the site published is GitHub's
  anyway.
