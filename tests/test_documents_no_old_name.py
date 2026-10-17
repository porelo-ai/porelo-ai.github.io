"""Holds that no tracked file of this repository says the product's old name, but where it must.

The repository was renamed by a script; a word it left behind, or one written later out of habit, names something
that is no longer there. The old name is spelled here in two pieces, so that this file does not say it.
"""

import os
import re
import subprocess
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

OLD = "so" + "kar"

# Paths that keep the old name, name and text: the issue of the rename.
KEPT_PATHS = re.compile(r"issues/SI03-[^/]+\.md")  # not-a-citation: the issue's own file

# Lines that keep it: the rename's own row in the issue index.
KEPT_LINES = re.compile(r'.*<a id="si03"></a>.*')


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True).stdout
    return [name for name in out.decode("utf-8").split("\0") if name]


def lines(path):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as text:
            return text.read().splitlines()
    except UnicodeDecodeError:
        # Not text: nothing in it is read as a word.
        return []


class NoOldNameTest(unittest.TestCase):

    def test_no_tracked_file_says_the_old_name(self):
        files = tracked()
        found = []
        for name in files:
            if KEPT_PATHS.fullmatch(name):
                continue
            if OLD in name.lower():
                found.append(f"{name}: its path")
            for number, line in enumerate(lines(name), 1):
                if not KEPT_LINES.fullmatch(line) and OLD in line.lower():
                    found.append(f"{name}:{number}: {line.strip()}")

        # A guard that reads nothing passes forever: assert what it read, then what it checks.
        self.assertTrue({"AGENTS.md", "build/assemble.py", "issues/README.md"} <= set(files), files)
        self.assertEqual([], found, "tracked files that say the old name")


if __name__ == "__main__":
    unittest.main()
