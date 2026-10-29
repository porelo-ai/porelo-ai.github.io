# SI06 — The Site's Agent Works In A Porelo Task

**Status:** Idea; blocked by [SI05](README.md#si05).

**What must be true.** porelo-ai.github.io's agent works in a Porelo task on the move's host, as the project's procedure for an agent's
move lays out, and takes this issue to
Review inside the task with the host's Forgejo build green. It talks in the project's room as `Agent Docsite`, from
the nickname `Docsite` that porelo-project's `project.yml` is to give the repository `site`.

## What moves, and what to check

- **The repository:** `porelo-ai.github.io`, the repository `site` in porelo-project's `project.yml`, alone; `porelo`
  and `porelo-adapters` move by issues of their own.
- **The task's image:** this repository's `porelo.yml`, which builds in a task once [SI05](README.md#si05) is done.
- **Forgejo's build:** `site.yml` builds and checks the site in the runner. Its `publish` job is already switched by
  `vars.PUBLISH`, but the `build` job uploads the Pages artifact unconditionally, and `build/assemble.py` reads every
  repository's `doc/` from GitHub's API with `secrets.PORELO_DOCS_READ`. Both are switched by variables present on
  both forges before the move, with the values of porelo-host's `doc/local-forge.md`, *The local
  registry and publication settings*, never a branch in the
  workflow.
