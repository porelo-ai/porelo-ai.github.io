"""Tests for build/check_images.py, which runs over the built site."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "build"))
import check_images  # noqa: E402


def write(site, path, text=""):
    target = os.path.join(site, path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as file:
        file.write(text)


class MissingTest(unittest.TestCase):

    def test_a_page_one_directory_lower_asking_two_levels_up_is_found(self):
        # As the site served core/how-it-works/: the picture lay in core/images/, the page asked images/ at the root.
        with tempfile.TemporaryDirectory() as site:
            write(site, "core/images/dummy.svg", "<svg/>")
            write(site, "core/how-it-works/index.html", '<p><img align="left" src="../../images/dummy.svg"></p>')

            lost, checked = check_images.missing(site)

        self.assertEqual(lost, [("core/how-it-works/index.html", "../../images/dummy.svg")])
        self.assertEqual(checked, 1)

    def test_an_image_the_site_holds_passes_by_a_relative_or_a_root_path(self):
        with tempfile.TemporaryDirectory() as site:
            write(site, "core/images/dummy.svg", "<svg/>")
            write(site, "core/how-it-works/index.html",
                  '<img src="../images/dummy.svg"><img src="/core/images/dummy.svg?v=1"><img src="../images/du%6Dmy.svg">')

            lost, checked = check_images.missing(site)

        self.assertEqual((lost, checked), ([], 3))

    def test_an_image_from_another_host_or_inline_is_not_the_sites_to_hold(self):
        with tempfile.TemporaryDirectory() as site:
            write(site, "index.html", '<img src="https://example.org/a.svg"><img src="data:image/png;base64,AA==">')

            self.assertEqual(check_images.missing(site), ([], 0))

    def test_a_source_that_climbs_out_of_the_site_is_missing_even_when_the_file_exists(self):
        with tempfile.TemporaryDirectory() as outside:
            write(outside, "a.svg", "<svg/>")
            site = os.path.join(outside, "site")
            write(site, "index.html", '<img src="../a.svg">')

            lost, _ = check_images.missing(site)

        self.assertEqual(lost, [("index.html", "../a.svg")])


if __name__ == "__main__":
    unittest.main()
