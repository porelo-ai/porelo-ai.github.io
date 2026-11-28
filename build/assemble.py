#!/usr/bin/env python3
"""Assembles one documentation site from the doc/ of every Porelo repository.

The list of repositories, and their order, is porelo-project's project.yml: its `repositories`, each with the
`central` address it is reached at, read in its https form; one with no GitHub address stops the build. For each, the
documentation on its default branch is taken, so a page appears within the hour of a push, and the start page says at
which commit. A repository with no doc/ is left out and named in the
log.

A section's order is the `nav` of that repository's own mkdocs.yml, when it has one; otherwise its index.md, then
its other pages by name. A relative link that leaves doc/ (to the README, to a source file) would be dead on the site,
so it is turned into a link to that file in the repository, at the commit the section was built from.

Reads only. While the repositories are private, PORELO_DOCS_READ (a token that can read them and nothing else) is
used, given to git through the environment, never on a command line; once they are public it is not needed. A
repository that cannot be read fails the build, naming it: a site that silently left a part out was published once,
and it was every part.

    assemble.py --out WORK [--project-yml FILE] [--local NAME=PATH ...]
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

import yaml

ORG = "porelo-ai"
SELF = "porelo-ai.github.io"
PROJECT = "porelo-project"
SITE_URL = "https://porelo-ai.github.io/"
PROJECT_DESCRIPTION = "How Porelo is developed as one project over these repositories, and what belongs to all of them"


def log(message):
    print(message, file=sys.stderr, flush=True)


def git_env():
    """git's environment: the read token as a header when there is one, and never a prompt for a password.

    No configuration but this: not the user's, not the system's, and - as git() runs nowhere else - not that of the
    repository it was started in. A workflow's checkout keeps its own credential as the same header, git sent both,
    and GitHub refused every repository with "Duplicate header".
    """
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    token = os.environ.get("PORELO_DOCS_READ", "")
    if token:
        basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        env.update(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
                   GIT_CONFIG_VALUE_0=f"AUTHORIZATION: basic {basic}")
    return env


def git(*args, cwd=None):
    """Runs git, in `cwd` or else in a directory outside every repository, so no repository's config applies."""
    return subprocess.run(["git", *args], cwd=cwd or tempfile.gettempdir(), env=git_env(), check=True,
                          capture_output=True, text=True).stdout


def unread_stops(unread):
    """Stops the build, naming every repository that could not be read; nothing is published without them."""
    if unread:
        raise SystemExit("cannot build the site, these repositories could not be read: " + ", ".join(unread))


def project_yml(path):
    if path:
        with open(path, encoding="utf-8") as file:
            return yaml.safe_load(file)
    request = urllib.request.Request(f"https://api.github.com/repos/{ORG}/{PROJECT}/contents/project.yml",
                                     headers={"Accept": "application/vnd.github.raw+json"})
    token = os.environ.get("PORELO_DOCS_READ", "")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return yaml.safe_load(response.read())


def https(address):
    """A GitHub address in any of git's spellings, as one https address in lower case.

    git@github.com:org/name.git, ssh://git@github.com[:port]/org/name.git and https://github.com/org/name, each
    with or without .git and a closing slash; GitHub reads an owner and a name in any case.
    """
    match = re.match(r"(?:git@github\.com:|ssh://git@github\.com(?::\d+)?/|https://github\.com/)"
                     r"([^/]+/[^/]+?)(?:\.git)?/?$", address or "", re.IGNORECASE)
    return f"https://github.com/{match.group(1).lower()}.git" if match else None


def parts(project):
    """Every repository the project names, in its order, and the project's own repository last.

    Last because it is organizational, of little interest to someone who uses Porelo (2026-10-05); the
    menu and the start page follow this order.
    """
    listed = project.get("repositories") or {}
    if not listed:
        # The project's own pages alone, published green, when the key is renamed or moved.
        raise SystemExit("cannot build the site, project.yml lists no repositories")
    found, unnamed = [], []
    for name, repository in listed.items():
        url = https((repository or {}).get("central"))
        if url is None:
            unnamed.append(name)
            continue
        found.append((name, url, (repository or {}).get("description", "")))
    if unnamed:
        # A site built without them would be published green and as good as empty.
        raise SystemExit("cannot build the site, project.yml gives these repositories no GitHub central address: "
                         + ", ".join(unnamed))
    # Not project.description: that says what Porelo is, and beside this repository it read as if it were the box.
    found.append((PROJECT, f"https://github.com/{ORG}/{PROJECT}.git", PROJECT_DESCRIPTION))
    return [part for part in found if not part[1].endswith(f"/{SELF}.git")]


def fetch(name, url, where):
    """Checks a repository out into `where`, at its default branch; returns what was taken."""
    git("init", "-q", where)
    git("fetch", "-q", "--depth=1", url, "HEAD", cwd=where)
    git("checkout", "-q", "FETCH_HEAD", cwd=where)
    commit = git("rev-parse", "HEAD", cwd=where).strip()
    return {"name": name, "ref": "main", "commit": commit}


# Material's theme as Zensical builds it, by configuration alone: a tab per kind of part (GROUPS), search, light or dark
# as the reader's system says, and tables that wrap their cells instead of cutting them off.
THEME = {
    "name": "material",
    "features": ["navigation.tabs", "navigation.sections", "navigation.top", "navigation.indexes",
                 "search.suggest", "search.highlight", "content.code.copy"],
    "palette": [
        {"media": "(prefers-color-scheme: light)", "scheme": "default",
         "toggle": {"icon": "material/weather-night", "name": "Dark"}},
        {"media": "(prefers-color-scheme: dark)", "scheme": "slate",
         "toggle": {"icon": "material/weather-sunny", "name": "Light"}},
    ],
}

# The menu: a tab per kind of part, in this order, each repository a section in its tab's sidebar under its label. Here
# and not in project.yml, which is a Porelo project file with no field for groups. A tab alone in its group shows its
# pages directly, with no section between. A repository with pages that no group names gets a tab of its own after
# these, so a new one is never lost.
# A tab that shows more than one repository opens on an overview of its own: the heading and text here, then a line
# per repository with its title and its description from project.yml. Each member is (name, menu label, title).
GROUPS = [
    ("porelo", None, None, [("core", "porelo", "Porelo")]),
    ("agents", "Agents",
     "Porelo names no agent. Each one is an agent adapter: a program and a package of its own, installed beside "
     "Porelo, which finds it at runtime and talks to it through the agent API. The adapter says how its agent is "
     "installed into a task and driven there, and each lives in a repository of its own.",
     [("claude", "claude code", "Claude Code"), ("pi", "pi", "Pi"), ("omp", "omp", "Oh My Pi"),
      ("codex", "codex", "Codex"), ("agy", "agy", "Antigravity")]),
    ("build readers", "Build readers",
     "A build reader tells a task how its build went: it reads the verdict and the failing job's log from the build "
     "server.",
     [("github", "github", "GitHub and Forgejo"), ("bitbucket", "bitbucket", "Bitbucket"),
      ("jenkins", "jenkins", "Jenkins")]),
    ("messaging", "Messaging",
     "The tasks of one project talk to each other in the project's room: a transport carries the messages, and the "
     "sluice decides what may pass between tasks.",
     [("matrix", "matrix", "Matrix"), ("sluice", "sluice", "Sluice")]),
    ("ui", "User interfaces",
     "Where the person sees and steers their tasks: the window, a graphical view of them, and the IntelliJ plugin, "
     "which reviews an agent's waiting work in the IDE.",
     [("frontend", "frontend", "The window"), ("intellij", "intellij", "IntelliJ")]),
    ("host", None, None, [("host", "host", "Host")]),
    ("internal", "Internal",
     "How Porelo itself is built and developed: the tooling its repositories build and test with, and the project's "
     "own rules.",
     [("buildtools", "buildtools", "Build tools"), (PROJECT, "porelo project", "Porelo project")]),
]


def grouped(sections, described):
    """The menu from each built repository's section, by name, grouped as GROUPS says, and each tab's overview.

    Returns the menu and the overview pages, each a path under docs/ with its text; described maps a repository's
    name to its description.
    """
    nav, named, pages = [], set(), {}
    for tab, heading, about, members in GROUPS:
        named.update(name for name, _, _ in members)
        built = [(name, label, title) for name, label, title in members if name in sections]
        if not built:
            continue
        if tab == "porelo":
            nav.append({tab: sections[built[0][0]]})
            continue
        entries = [{label: sections[name]} for name, label, _ in built]
        if len(built) > 1:
            if not about:
                raise SystemExit(f"the tab {tab} shows {len(built)} repositories and has no overview text in GROUPS")
            # Named index.md, so the theme's navigation.indexes makes it the tab's own page.
            page = f"groups/{tab.replace(' ', '-')}/index.md"
            pages[page] = overview(page, heading, about, built, sections, described)
            entries.insert(0, page)
        nav.append({tab: entries})
    for name, section in sections.items():
        if name not in named:
            log(f"{name} is in no group of the menu: a tab of its own")
            nav.append({name: section})
    return nav, pages


def overview(page, heading, about, built, sections, described):
    lines = [f"# {heading}", "", about, ""]
    for name, _, title in built:
        first = first_page(sections[name])
        if first is None:
            raise SystemExit(f"cannot write the tab's overview {page}: {name}'s section names no page")
        link = first if re.match(r"^[a-z]+://", first) else urllib.parse.quote(
            os.path.relpath(first, os.path.dirname(page)))
        # A folded description from project.yml would end the list item at its first line break.
        what = " ".join(described.get(name, "").split())
        lines.append(f"- [{title}]({link})" + (f" - {what}" if what else ""))
    return "\n".join(lines) + "\n"


# What a page shows besides its text. Anything else in doc/ - a walk's JSON, a fixture - is not for the site.
ASSETS = (".png", ".svg", ".jpg", ".jpeg", ".gif", ".webp")

# The maturity graphic the home page shows, kept here rather than taken from a repository the site reads.
MATURITY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "doc", "images", "crazy-chicken.svg")

LINK = re.compile(r"(\]\()([^)\s]+)(\))")

# A link inside raw HTML, which leaves doc/ as a Markdown link does.
HTML_LINK = re.compile(r"""(<[a-zA-Z][^>]*?\s(?:src|href)=")([^"]+)(")""")


def relinked(text, page, doc, repository, commit):
    """Links that leave doc/ point at the file in the repository, at the commit the section was built from."""

    def one(match):
        target = match.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/", target):
            return match.group(0)
        path, _, anchor = target.partition("#")
        resolved = os.path.normpath(os.path.join(os.path.dirname(page), path))
        if resolved == os.path.normpath(doc) or resolved.startswith(os.path.normpath(doc) + os.sep):
            return match.group(0)
        relative = os.path.relpath(resolved, os.path.dirname(doc))
        return (f"{match.group(1)}https://github.com/{ORG}/{repository}/blob/{commit}/{relative}"
                f"{'#' + anchor if anchor else ''}{match.group(3)}")

    def html(match):
        target = match.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/", target):
            return match.group(0)
        moved = one(re.match(r"(\]\()(.*)(\))", f"]({target})"))
        # One inside doc/ stays as written: Zensical moves it for a page served one directory lower.
        return f"{match.group(1)}{moved[2:-1]}{match.group(3)}"

    return HTML_LINK.sub(html, LINK.sub(one, text))


def nav_of(checkout, name):
    """The section's order: the repository's own mkdocs.yml nav, prefixed with its directory here."""
    own = os.path.join(checkout, "mkdocs.yml")
    if os.path.isfile(own):
        with open(own, encoding="utf-8") as file:
            config = yaml.load(file, Loader=yaml.BaseLoader) or {}
        if config.get("nav"):
            return prefixed(config["nav"], name)
    pages = sorted(page for page in os.listdir(os.path.join(checkout, "doc")) if page.endswith(".md"))
    if "index.md" in pages:
        pages.remove("index.md")
        pages.insert(0, "index.md")
    return [f"{name}/{page}" for page in pages]


def first_page(nav):
    if isinstance(nav, str):
        return nav
    for entry in (nav if isinstance(nav, list) else nav.values()):
        found = first_page(entry)
        if found:
            return found
    return None


def prefixed(nav, name):
    if isinstance(nav, str):
        return nav if re.match(r"^[a-z]+://", nav) else f"{name}/{nav}"
    if isinstance(nav, list):
        return [prefixed(entry, name) for entry in nav]
    return {title: prefixed(entry, name) for title, entry in nav.items()}


def assemble(out, project, local):
    docs = os.path.join(out, "docs")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(docs, "images"))
    shutil.copyfile(MATURITY, os.path.join(docs, "images", "crazy-chicken.svg"))
    # Every repository read, with or without doc/: what an hourly run compares, so one with nothing to show does not
    # look changed at every hour.
    built, considered, unread, sections = [], [], [], {}
    for name, url, description in parts(project):
        checkout = os.path.join(out, "repositories", name)
        if name in local:
            # Only what the site reads: a whole checkout holds build output, and links into it that lead nowhere.
            os.makedirs(checkout)
            if os.path.isdir(os.path.join(local[name], "doc")):
                shutil.copytree(os.path.join(local[name], "doc"), os.path.join(checkout, "doc"))
            if os.path.isfile(os.path.join(local[name], "mkdocs.yml")):
                shutil.copyfile(os.path.join(local[name], "mkdocs.yml"), os.path.join(checkout, "mkdocs.yml"))
            taken = {"name": name, "ref": "local", "commit": "local"}
        else:
            try:
                taken = fetch(name, url, checkout)
            except subprocess.CalledProcessError as failed:
                log(f"cannot read {name}: {failed.stderr.strip() or failed}")
                unread.append(name)
                continue
        considered.append({k: taken[k] for k in ("name", "ref", "commit")})
        doc = os.path.join(checkout, "doc")
        if not os.path.isdir(doc):
            log(f"skipped {name}: no doc/ at {taken['ref']}")
            continue
        if not any(file.endswith(".md") for _, _, files in os.walk(doc) for file in files):
            log(f"skipped {name}: no page in doc/ at {taken['ref']}")
            continue
        repository = url.rsplit("/", 1)[1].removesuffix(".git")
        for root, _, files in os.walk(doc):
            for file in files:
                source = os.path.join(root, file)
                target = os.path.join(docs, name, os.path.relpath(source, doc))
                os.makedirs(os.path.dirname(target), exist_ok=True)
                if file.endswith(".md"):
                    with open(source, encoding="utf-8") as read:
                        text = relinked(read.read(), source, doc, repository, taken["commit"])
                    with open(target, "w", encoding="utf-8") as write:
                        write.write(text)
                elif file.lower().endswith(ASSETS):
                    shutil.copyfile(source, target)
        taken.update(repository=repository, description=description or "")
        built.append(taken)
        section = nav_of(checkout, name)
        taken["first"] = first_page(section)
        sections[name] = section
    unread_stops(unread)
    with open(os.path.join(docs, "index.md"), "w", encoding="utf-8") as index:
        index.write(landing(built, docs))
    with open(os.path.join(docs, "parts.json"), "w", encoding="utf-8") as manifest:
        json.dump(considered, manifest, indent=1)
    nav, overviews = grouped(sections, {part["name"]: part["description"] for part in built})
    for page, text in overviews.items():
        target = os.path.join(docs, page)
        if os.path.exists(target):
            raise SystemExit(f"cannot write the tab's overview {page}: a repository's section already holds it")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as write:
            write.write(text)
    config = {"site_name": "Porelo", "site_url": SITE_URL, "repo_url": f"https://github.com/{ORG}",
              "docs_dir": "docs", "site_dir": "site", "theme": THEME, "plugins": ["search"],
              "markdown_extensions": ["tables", "admonition", "attr_list", {"toc": {"permalink": True}}],
              # The landing page is the site's root, where the title leads, and no tab of its own.
              "strict": True, "not_in_nav": "/index.md", "nav": nav}
    with open(os.path.join(out, "mkdocs.yml"), "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file, sort_keys=False, allow_unicode=True)
    return built


# A way in for each kind of reader, under the maturity graphic (approved 2026-10-09). An entry shows only
# when its page is among the parts taken: a link to a page a repository does not have yet would fail the strict build,
# and the entry appears by itself once the page is pushed.
WAYS_IN = [
    ("If you have thirty seconds", "The elevator pitch", "core/pitch.md",
     "what Porelo is, in a few sentences to remember."),
    ("If you have ten minutes", "How it works", "core/how-it-works.md",
     "the parts, and what happens when a task starts."),
    ("If you look after security", "Porelo in a company", "core/corporate-security.md",
     "what a task can reach, what it never holds, and what the host guarantees."),
    ("If you want to build it with us", "Contributing", f"{PROJECT}/contributing.md",
     "how a change gets in, the rules, the licence."),
]


def ways_in(docs):
    lines = []
    for heading, title, page, what in WAYS_IN:
        if os.path.isfile(os.path.join(docs, page)):
            # Two spaces: a line break, so the link stands under its heading rather than beside it.
            lines += [f"**{heading}**  ", f"[{title}]({page}) - {what}", ""]
    return lines


def landing(built, docs):
    lines = ["# Porelo", "",
             '<img src="images/crazy-chicken.svg" width="350" alt="Crazy chicken - just hatched">', "",
             "> **Crazy chicken - just hatched.** Interfaces, formats and even the purpose may change any day. Use it",
             "> only to try ideas, never to build on.", ""] + ways_in(docs) + [
             "Porelo runs AI coding agents in containers they cannot leave. This site holds the documentation of",
             "every part of it, each taken from its own repository.", "",
             "| Part | What it is | Taken from |", "|---|---|---|"]
    for part in built:
        source = f"`{part['ref']}` at `{part['commit'][:12]}`"
        lines.append(f"| [{part['name']}]({part['first']}) | {part['description']} | {source} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, help="the working directory, emptied first")
    parser.add_argument("--project-yml", help="read this file instead of porelo-project's on GitHub")
    parser.add_argument("--local", action="append", default=[], metavar="NAME=PATH",
                        help="take a repository from a checkout here instead of GitHub")
    parser.add_argument("--manifest", action="store_true",
                        help="print only what would be taken, as parts.json says it, and build nothing")
    args = parser.parse_args()
    project = project_yml(args.project_yml)
    if args.manifest:
        taken, unread = [], []
        for name, url, _ in parts(project):
            try:
                commit = git("ls-remote", url, "HEAD").split("\t")[0]
                taken.append({"name": name, "ref": "main", "commit": commit})
            except subprocess.CalledProcessError as failed:
                log(f"cannot read {name}: {failed.stderr.strip() or failed}")
                unread.append(name)
        unread_stops(unread)
        print(json.dumps(taken, indent=1))
        return
    local = dict(entry.split("=", 1) for entry in args.local)
    for part in assemble(args.out, project, local):
        log(f"took {part['name']} at {part['ref']} ({part['commit'][:12]})")


if __name__ == "__main__":
    main()
