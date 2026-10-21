# SI05 — The Site Builds In A Porelo Task

**Status:** Idea; blocked by porelo [B241](https://github.com/porelo-ai/porelo/blob/main/issues/base/README.md#b241).

**What must be true.** The site's whole check runs green inside a Porelo task, in the image its `porelo.yml` names.

## Why

Measured in a task on the VM (porelo `0.5.1~snapshot.307`, agent `stub`), the image could not be built:
- `porelo.yml:8` takes `python:3.13-slim`, which is Debian. Porelo writes Ubuntu's mirror into Debian's sources, and
  no `package_sources` value builds it: porelo [B241](https://github.com/porelo-ai/porelo/blob/main/issues/base/README.md#b241).
- `porelo.yml:33`, `COPY build/requirements.txt`, cannot work: the image is built in Porelo's own build directory, not
  in the repository, so the file is not in its context. `site.yml` installs the same file at run time with
  `pip install --require-hashes -r build/requirements.txt`, which a task can do too, with egress to PyPI.
- The repository's name has dots, which porelo refuses as a repository name today: porelo
  [B240](https://github.com/porelo-ai/porelo/blob/main/issues/base/README.md#b240).
