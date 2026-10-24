import unittest

from dinky.tools.intent import match_tool


class IntentTests(unittest.TestCase):
    def test_direct_command(self):
        self.assertEqual(match_tool("open file explorer"), "app.open_explorer")

    def test_spoken_command(self):
        self.assertEqual(
            match_tool("Dinky, open file explorer."),
            "app.open_explorer",
        )

    def test_extra_action_does_not_match(self):
        self.assertIsNone(
            match_tool("open file explorer and delete my files")
        )

    def test_unrelated_request_does_not_match(self):
        self.assertIsNone(match_tool("explain what File Explorer does"))


if __name__ == "__main__":
    unittest.main()