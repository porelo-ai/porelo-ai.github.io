# SI05 — The Site Builds In A Porelo Task

**Status:** Implementing: `porelo.yml` has no `COPY`; the run in a task follows.

**What must be true.** The site's whole check runs green inside a Porelo task, in the image its `porelo.yml` names.

## Why

Measured in a task on the VM (porelo `0.5.1~snapshot.307`, agent `stub`), the image could not be built:
- `porelo.yml:8` takes `python:3.13-slim`, which is Debian. Porelo writes Ubuntu's mirror into Debian's sources, and
  no `package_sources` value built it then; porelo now replaces a stanza's `URIs:` only where its archive path
  matches the source's.
- `porelo.yml:33`, `COPY build/requirements.txt`, cannot work: the image is built in Porelo's own build directory, not
  in the repository, so the file is not in its context. `site.yml` installs the same file at run time with
  `pip install --require-hashes -r build/requirements.txt`, which a task can do too, with egress to PyPI.
- The repository's name has dots, which porelo refused as a repository name then; porelo now takes single dots
  between letters or digits.
