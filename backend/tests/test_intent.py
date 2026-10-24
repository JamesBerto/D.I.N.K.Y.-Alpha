import unittest

from dinky.tools.intent import match_tool, mentions_device_status


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

    def test_spoken_status_command(self):
        self.assertEqual(
            match_tool("Dinky, show my system status."),
            "system.status",
        )

    def test_status_question_does_not_trigger_tool(self):
        self.assertIsNone(
            match_tool("What does system status mean?")
        )
    def test_misheard_explorer_does_not_open_app(self):
        self.assertIsNone(match_tool("Open file experience."))

    def test_spoken_show_me_status(self):
        self.assertEqual(
            match_tool("show me system status."),
            "system.status",
        )
    def test_display_system_status(self):
        self.assertEqual(
            match_tool("display my system status."),
            "system.status",
        )

    def test_unrecognized_status_reference(self):
        self.assertTrue(
            mentions_device_status("Tell me my CPU usage.")
        )

if __name__ == "__main__":
    unittest.main()