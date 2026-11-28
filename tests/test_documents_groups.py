"""Holds that every tab of the site that can show several repositories has its overview text in doc/groups/."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "build"))
import assemble  # noqa: E402

GROUPS = os.path.join(os.path.dirname(__file__), "..", "doc", "groups")


class OverviewTextsTest(unittest.TestCase):

    def test_every_tab_that_can_hold_several_repositories_has_a_text_with_the_place_for_them(self):
        # A missing text fails the build only on the day the tab's second repository gets pages.
        several = [assemble.slug(tab) for tab, members in assemble.GROUPS if len(members) > 1]
        self.assertIn("agents", several)
        for tab in several:
            with open(os.path.join(GROUPS, f"{tab}.md"), encoding="utf-8") as file:
                self.assertEqual(file.read().count(assemble.MARKER), 1, tab)

    def test_no_text_lies_there_for_a_tab_the_menu_does_not_have(self):
        # A text for a renamed tab would be changed by hand and never shown.
        tabs = {f"{assemble.slug(tab)}.md" for tab, _ in assemble.GROUPS}
        self.assertEqual(sorted(set(os.listdir(GROUPS)) - tabs), [])


if __name__ == "__main__":
    unittest.main()
