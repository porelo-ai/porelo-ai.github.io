"""Every image a built page shows exists in the built site.

Run as `python build/check_images.py <site directory>` after the site is built: a picture a page asks for at a path
the site does not hold shows as nothing, and a strict build does not see it, as it checks Markdown's links only.
"""

import html.parser
import os
import sys
import urllib.parse


class Images(html.parser.HTMLParser):
    """The src of every <img> on one page."""

    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            source = dict(attrs).get("src")
            if source:
                self.sources.append(source)


def missing(site):
    """Each (page, src) whose image the site does not hold, and how many local images were checked."""
    lost, checked = [], 0
    # Absolute, so a site given as "." still holds what lies inside it.
    site = os.path.abspath(site)
    for root, _, files in os.walk(site):
        for file in sorted(files):
            if not file.endswith(".html"):
                continue
            page = os.path.join(root, file)
            images = Images()
            with open(page, encoding="utf-8") as read:
                images.feed(read.read())
            for source in images.sources:
                parsed = urllib.parse.urlsplit(source)
                if parsed.scheme or parsed.netloc:
                    continue
                path = urllib.parse.unquote(parsed.path)
                base = site if path.startswith("/") else os.path.dirname(page)
                target = os.path.normpath(os.path.join(base, path.lstrip("/")))
                checked += 1
                inside = target == os.path.normpath(site) or target.startswith(os.path.normpath(site) + os.sep)
                if not inside or not os.path.isfile(target):
                    lost.append((os.path.relpath(page, site), source))
    return lost, checked


def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        raise SystemExit("usage: python build/check_images.py <built site directory>")
    lost, checked = missing(sys.argv[1])
    if checked == 0:
        # The home page shows the maturity graphic: no image at all means the check read no built site.
        raise SystemExit(f"no page in {sys.argv[1]} shows a local image: not a built site")
    for page, source in lost:
        print(f"FAULT {page} shows {source}, which the site does not hold")
    if lost:
        raise SystemExit(f"{len(lost)} of {checked} images do not show")
    print(f"OK    all {checked} images the pages show are in the site")


if __name__ == "__main__":
    main()
