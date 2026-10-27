# SI06 — The Site's Agent Works In A Porelo Task

**Status:** Idea; blocked by [SI05](README.md#si05).

**What must be true.** porelo-ai.github.io's own agent works in a Porelo task of the project `porelo` on the move's
host, as porelo-project [PJ59](https://github.com/porelo-ai/porelo-project/blob/main/issues/README.md#pj59) lays out
for sprint 8, beside porelo-adapters. The task follows this repository through the gate and pushes to the host's
Forgejo, whose build is read through the `forgejo` reader. The agent is reached in the project's room as
`Agent porelo-ai.github.io` or by the nickname `project.yml` gives it (porelo
[B298](https://github.com/porelo-ai/porelo/blob/main/issues/base/README.md#b298)). This issue is taken from start to
Review inside the task, with the forge's build green.

## What moves, and what to check

- **The repository:** `porelo-ai.github.io` alone; `porelo` and `porelo-adapters` move by issues of their own.
- **The task's image:** this repository's `porelo.yml`, which builds in a task once [SI05](README.md#si05) is done.
- **Forgejo's build:** `site.yml` builds and checks the site in the runner; its Pages deployment is the central
  forge's only, so on the local forge it is switched off by a variable present on both forges, as porelo-project
  [PJ60](https://github.com/porelo-ai/porelo-project/blob/main/issues/README.md#pj60) asks, never a branch in the
  workflow.
