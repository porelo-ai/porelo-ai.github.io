# SI06 — The Site's Agent Works In A Porelo Task

**Status:** Idea; blocked by [SI05](README.md#si05).

**What must be true.** porelo-ai.github.io's agent works in a Porelo task on the move's host, as porelo-project
[PJ59](https://github.com/porelo-ai/porelo-project/blob/main/issues/README.md#pj59) lays out, and takes this issue to
Review inside the task with the host's Forgejo build green. It talks in the project's room as `Agent Docsite`, from
the nickname `Docsite` that porelo-project's `project.yml` is to give the repository `site` (porelo
[B298](https://github.com/porelo-ai/porelo/blob/main/issues/base/README.md#b298)).

## What moves, and what to check

- **The repository:** `porelo-ai.github.io`, the repository `site` in porelo-project's `project.yml`, alone; `porelo`
  and `porelo-adapters` move by issues of their own.
- **The task's image:** this repository's `porelo.yml`, which builds in a task once [SI05](README.md#si05) is done.
- **Forgejo's build:** `site.yml` builds and checks the site in the runner. Its `publish` job is already switched by
  `vars.PUBLISH`, but the `build` job uploads the Pages artifact unconditionally, and `build/assemble.py` reads every
  repository's `doc/` from GitHub's API with `secrets.PORELO_DOCS_READ`. Both are switched by variables present on
  both forges before the move, as porelo-project
  [PJ60](https://github.com/porelo-ai/porelo-project/blob/main/issues/README.md#pj60) asks, never a branch in the
  workflow.
