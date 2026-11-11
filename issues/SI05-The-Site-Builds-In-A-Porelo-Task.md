# SI05 — The Site Builds In A Porelo Task

```json
{
  "$schema": "issue-1.json",
  "id": "SI05",
  "title": "The Site Builds In A Porelo Task",
  "state": "Backlog",
  "size": "S",
  "priority": "Medium",
  "rank": 1,
  "blockedBy": [],
  "covers": "The site's check green in a Porelo task: `porelo.yml` without `COPY`, its Debian base built once porelo can."
}
```

**Why this size.** `porelo.yml` without `COPY` and one run of the check in a task.

**How it stands.** `porelo.yml` has no `COPY`; the run in a task follows.

**What must be true.** The site's whole check runs green inside a Porelo task, in the image its `porelo.yml` names.

## Why

Measured in a task on the VM (porelo `0.5.1~snapshot.307`, agent `stub`), the image could not be built:
- `porelo.yml:8` takes `python:3.13-slim`, which is Debian. Porelo writes Ubuntu's mirror into Debian's sources, and
  no `package_sources` value built it then; porelo now replaces a stanza's `URIs:` only where its archive path
  matches the source's.
- `porelo.yml:33` held `COPY build/requirements.txt`, since taken out, which could not work: the image is built in Porelo's own build directory, not
  in the repository, so the file is not in its context. `site.yml` installs the same file at run time with
  `pip install --require-hashes -r build/requirements.txt`, which a task can do too, with egress to PyPI.
- The repository's name has dots, which porelo refused as a repository name then; porelo now takes single dots
  between letters or digits.
