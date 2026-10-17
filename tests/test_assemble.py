"""Tests for build/assemble.py, run as `python -m unittest discover -s tests` from the repository's root."""

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "build"))
import assemble  # noqa: E402

HEADER = "http.https://github.com/.extraheader"


class GitTest(unittest.TestCase):

    def test_a_header_the_callers_checkout_keeps_is_not_sent_beside_the_read_token(self):
        # Measured on the first published build: actions/checkout keeps its own credential as this header in the
        # workflow's checkout, git sent both, and GitHub refused every repository with "Duplicate header".
        with tempfile.TemporaryDirectory() as checkout:
            subprocess.run(["git", "init", "-q", checkout], check=True)
            subprocess.run(["git", "-C", checkout, "config", HEADER, "AUTHORIZATION: basic theirs"], check=True)
            here = os.getcwd()
            os.chdir(checkout)
            try:
                with mock.patch.dict(os.environ, {"PORELO_DOCS_READ": "ours"}):
                    sent = assemble.git("config", "--get-all", HEADER).splitlines()
            finally:
                os.chdir(here)
        self.assertEqual(len(sent), 1, sent)
        self.assertNotIn("theirs", sent[0])


class PartsTest(unittest.TestCase):

    def test_the_project_comes_last_and_its_repositories_in_their_order(self):
        # Decided: the project's own repository is organizational, of little interest to a user.
        project = {"project": {"description": "the project"},
                   "repositories": {
                       "core": {"upstream": "git@github.com:porelo-ai/porelo.git"},
                       "frontend": {"upstream": "git@github.com:porelo-ai/porelo-frontend.git"},
                       "site": {"upstream": "git@github.com:porelo-ai/porelo-ai.github.io.git"},
                       "buildtools": {"upstream": "git@github.com:porelo-ai/porelo-buildtools.git"}}}

        self.assertEqual([name for name, _, _ in assemble.parts(project)],
                         ["core", "frontend", "buildtools", "porelo-project"])

    def test_the_project_row_says_what_the_repository_holds_not_what_porelo_is(self):
        # project.description describes Porelo itself; beside the project's repository it read as nonsense.
        project = {"project": {"description": "A hardened box an agent works in"}, "repositories": {}}

        description = dict((name, text) for name, _, text in assemble.parts(project))["porelo-project"]

        self.assertNotIn("hardened box", description)
        self.assertIn("repositories", description)


class RelinkedTest(unittest.TestCase):

    def test_a_relative_source_in_raw_html_reaches_its_file_from_the_pages_own_directory(self):
        # Measured on the site: core/how-it-works/ showed no picture, as its <img src="images/dummy.svg"> was read
        # from core/how-it-works/images/. MkDocs moves Markdown's links for a page that becomes a directory, not HTML.
        text = '<img align="left" src="images/dummy.svg" alt="a dummy">\n![shown](images/b.svg)\n'

        page = assemble.relinked(text, "/r/doc/how-it-works.md", "/r/doc", "porelo", "0" * 40)
        index = assemble.relinked(text, "/r/doc/index.md", "/r/doc", "porelo", "0" * 40)

        self.assertIn('src="../images/dummy.svg"', page)
        self.assertIn("](images/b.svg)", page)
        self.assertIn('src="images/dummy.svg"', index)

    def test_an_absolute_or_external_source_stays(self):
        text = '<img src="https://example.org/a.svg"> <img src="/a.svg"> <a href="#top">top</a>'

        self.assertEqual(assemble.relinked(text, "/r/doc/page.md", "/r/doc", "porelo", "0" * 40), text)


class FetchTest(unittest.TestCase):

    def test_takes_the_default_branch_even_when_a_release_is_tagged(self):
        # Decided: the site shows what is on main, so new pages appear within the hour of a push.
        with tempfile.TemporaryDirectory() as tmp:
            repository = os.path.join(tmp, "repository")
            subprocess.run(["git", "init", "-q", "-b", "main", repository], check=True)
            for message in ("released", "after the release"):
                subprocess.run(["git", "-C", repository, "-c", "user.name=t", "-c", "user.email=t@t", "-c",
                                "commit.gpgSign=false", "commit", "-q", "--allow-empty", "-m", message], check=True)
                if message == "released":
                    subprocess.run(["git", "-C", repository, "-c", "tag.gpgSign=false", "tag", "v0.4.0"], check=True)
            head = subprocess.run(["git", "-C", repository, "rev-parse", "HEAD"], check=True, capture_output=True,
                                  text=True).stdout.strip()

            taken = assemble.fetch("repository", repository, os.path.join(tmp, "checkout"))

        self.assertEqual(taken["commit"], head)
        self.assertEqual(taken["ref"], "main")


class AssembleTest(unittest.TestCase):

    def run_with(self, fetched):
        project = {"repositories": {}}
        parts = [("porelo-project", "https://github.com/porelo-ai/porelo-project.git", ""),
                 ("core", "https://github.com/porelo-ai/porelo.git", "")]
        with tempfile.TemporaryDirectory() as out, \
                mock.patch.object(assemble, "parts", return_value=parts), \
                mock.patch.object(assemble, "fetch", side_effect=fetched):
            return assemble.assemble(os.path.join(out, "site"), project, {})

    def test_a_repository_that_cannot_be_read_fails_the_build(self):
        def unreadable(name, url, where):
            raise subprocess.CalledProcessError(128, ["git", "fetch"], stderr="remote: Duplicate header")

        with self.assertRaises(SystemExit) as stopped:
            self.run_with(unreadable)
        self.assertIn("porelo-project", str(stopped.exception.code))
        self.assertIn("core", str(stopped.exception.code))

    def test_one_repository_that_cannot_be_read_fails_it_too(self):
        def one_unreadable(name, url, where):
            if name == "core":
                raise subprocess.CalledProcessError(128, ["git", "fetch"], stderr="not found")
            os.makedirs(os.path.join(where, "doc"))
            with open(os.path.join(where, "doc", "index.md"), "w", encoding="utf-8") as page:
                page.write("# The project\n")
            return {"name": name, "ref": "main", "commit": "0" * 40}

        with self.assertRaises(SystemExit) as stopped:
            self.run_with(one_unreadable)
        self.assertIn("core", str(stopped.exception.code))
        self.assertNotIn("porelo-project", str(stopped.exception.code))

    def test_the_site_is_built_with_material_tabs_search_and_both_schemes(self):
        def readable(name, url, where):
            os.makedirs(os.path.join(where, "doc"))
            with open(os.path.join(where, "doc", "index.md"), "w", encoding="utf-8") as page:
                page.write(f"# {name}\n")
            return {"name": name, "ref": "main", "commit": "0" * 40}

        project = {"repositories": {}}
        parts = [("porelo-project", "https://github.com/porelo-ai/porelo-project.git", "")]
        with tempfile.TemporaryDirectory() as out, \
                mock.patch.object(assemble, "parts", return_value=parts), \
                mock.patch.object(assemble, "fetch", side_effect=readable):
            assemble.assemble(os.path.join(out, "site"), project, {})
            with open(os.path.join(out, "site", "mkdocs.yml"), encoding="utf-8") as file:
                config = assemble.yaml.safe_load(file)

        theme = config["theme"]
        self.assertEqual(theme["name"], "material")
        self.assertIn("navigation.tabs", theme["features"])
        self.assertEqual([scheme["scheme"] for scheme in theme["palette"]], ["default", "slate"])
        self.assertTrue(all("prefers-color-scheme" in scheme["media"] for scheme in theme["palette"]))
        self.assertIn("search", config["plugins"])

    def test_the_home_page_opens_with_the_early_bird_and_its_note(self):
        def readable(name, url, where):
            os.makedirs(os.path.join(where, "doc"))
            with open(os.path.join(where, "doc", "index.md"), "w", encoding="utf-8") as page:
                page.write(f"# {name}\n")
            return {"name": name, "ref": "main", "commit": "0" * 40}

        project = {"repositories": {}}
        parts = [("porelo-project", "https://github.com/porelo-ai/porelo-project.git", "")]
        with tempfile.TemporaryDirectory() as out, \
                mock.patch.object(assemble, "parts", return_value=parts), \
                mock.patch.object(assemble, "fetch", side_effect=readable):
            assemble.assemble(os.path.join(out, "site"), project, {})
            with open(os.path.join(out, "site", "docs", "index.md"), encoding="utf-8") as file:
                home = file.read().split("\n")
            graphic = os.path.join(out, "site", "docs", "images", "early-bird.svg")
            self.assertTrue(os.path.isfile(graphic), "the graphic the home page names is in the site")

        self.assertEqual(home[0], "# Porelo")
        self.assertEqual(home[2], '<img src="images/early-bird.svg" width="350" alt="Early bird - work in progress">')
        self.assertEqual(home[4], "> **Early bird - work in progress.** Porelo is not stable yet: until release 1.0.0,"
                                  " its code, commands")
        self.assertEqual(home[5], "> and file formats can change without notice.")

    def test_the_home_page_offers_a_way_in_for_each_reader_whose_page_is_there(self):
        pages = {"core": ["index.md", "pitch.md", "how-it-works.md", "corporate-security.md"],
                 "porelo-project": ["index.md"]}

        def readable(name, url, where):
            os.makedirs(os.path.join(where, "doc"))
            for page in pages[name]:
                with open(os.path.join(where, "doc", page), "w", encoding="utf-8") as file:
                    file.write(f"# {page}\n")
            return {"name": name, "ref": "main", "commit": "0" * 40}

        parts = [("core", "https://github.com/porelo-ai/porelo.git", ""),
                 ("porelo-project", "https://github.com/porelo-ai/porelo-project.git", "")]

        def home():
            with tempfile.TemporaryDirectory() as out, \
                    mock.patch.object(assemble, "parts", return_value=parts), \
                    mock.patch.object(assemble, "fetch", side_effect=readable):
                assemble.assemble(os.path.join(out, "site"), {"repositories": {}}, {})
                with open(os.path.join(out, "site", "docs", "index.md"), encoding="utf-8") as file:
                    return file.read()

        text = home()
        self.assertIn("**If you have thirty seconds**", text)
        self.assertIn("[The elevator pitch](core/pitch.md)", text)
        self.assertIn("[How it works](core/how-it-works.md)", text)
        self.assertIn("[Porelo in a company](core/corporate-security.md)", text)
        self.assertNotIn("If you want to build it with us", text, "hidden while porelo-project has no contributing page")
        self.assertLess(text.index("Early bird"), text.index("If you have thirty seconds"))
        self.assertLess(text.index("If you have thirty seconds"), text.index("Porelo runs AI coding agents"))

        pages["porelo-project"].append("contributing.md")
        self.assertIn("[Contributing](porelo-project/contributing.md)", home(), "shown once the page is there")

    def test_every_repository_read_builds(self):
        def readable(name, url, where):
            os.makedirs(os.path.join(where, "doc"))
            with open(os.path.join(where, "doc", "index.md"), "w", encoding="utf-8") as page:
                page.write(f"# {name}\n")
            return {"name": name, "ref": "main", "commit": "0" * 40}

        self.assertEqual([part["name"] for part in self.run_with(readable)], ["porelo-project", "core"])


class MenuTest(unittest.TestCase):

    @staticmethod
    def config(names):
        def readable(name, url, where):
            os.makedirs(os.path.join(where, "doc"))
            with open(os.path.join(where, "doc", "index.md"), "w", encoding="utf-8") as page:
                page.write(f"# {name}\n")
            return {"name": name, "ref": "main", "commit": "0" * 40}

        parts = [(name, f"https://github.com/porelo-ai/{name}.git", "") for name in names]
        with tempfile.TemporaryDirectory() as out, \
                mock.patch.object(assemble, "parts", return_value=parts), \
                mock.patch.object(assemble, "fetch", side_effect=readable):
            assemble.assemble(os.path.join(out, "site"), {"repositories": {}}, {})
            with open(os.path.join(out, "site", "mkdocs.yml"), encoding="utf-8") as file:
                config = assemble.yaml.safe_load(file)
            written = os.path.isfile(os.path.join(out, "site", "docs", "index.md"))
        return config, written

    def test_the_menu_is_a_tab_per_kind_of_part_with_each_repository_a_section(self):
        config, _ = self.config(["core", "frontend", "sluice", "matrix", "claude", "pi", "omp", "buildtools", "github",
                                 "intellij", "porelo-project"])

        self.assertEqual(config["nav"], [
            {"porelo": ["core/index.md"]},
            {"agents": [{"claude code": ["claude/index.md"]}, {"pi": ["pi/index.md"]}, {"omp": ["omp/index.md"]}]},
            {"build readers": [{"github": ["github/index.md"]}]},
            {"messaging": [{"matrix": ["matrix/index.md"]}, {"sluice": ["sluice/index.md"]}]},
            {"ui": [{"frontend": ["frontend/index.md"]}, {"intellij": ["intellij/index.md"]}]},
            {"internal": [{"buildtools": ["buildtools/index.md"]}, {"porelo project": ["porelo-project/index.md"]}]},
        ])

    def test_a_repository_no_group_names_is_a_tab_of_its_own_at_the_end(self):
        config, _ = self.config(["newcomer", "core"])

        self.assertEqual(config["nav"], [{"porelo": ["core/index.md"]}, {"newcomer": ["newcomer/index.md"]}])

    def test_a_group_with_nothing_built_is_left_out(self):
        config, _ = self.config(["core", "pi"])

        self.assertEqual([next(iter(tab)) for tab in config["nav"]], ["porelo", "agents"])

    def test_the_landing_page_is_written_and_has_no_tab(self):
        config, written = self.config(["core"])

        self.assertTrue(written)
        self.assertNotIn("index.md", str(config["nav"]).replace("core/index.md", ""))
        self.assertEqual(config["not_in_nav"], "/index.md")


if __name__ == "__main__":
    unittest.main()
