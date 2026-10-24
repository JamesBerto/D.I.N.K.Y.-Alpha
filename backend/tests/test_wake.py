import unittest

from dinky.voice.wake import is_stop_request, request_after_wake_word


class WakeWordTests(unittest.TestCase):
    def test_wake_word_with_request(self):
        self.assertEqual(
            request_after_wake_word("Hey Dinky, open file explorer."),
            "open file explorer.",
        )

    def test_wake_word_only(self):
        self.assertEqual(request_after_wake_word("Dinky!"), "")

    def test_no_wake_word(self):
        self.assertIsNone(
            request_after_wake_word("Open file explorer.")
        )

    def test_part_of_another_word(self):
        self.assertIsNone(
            request_after_wake_word("The word is undinkyable.")
        )

    def test_stop_phrases(self):
        self.assertTrue(is_stop_request("stop listening"))
        self.assertTrue(is_stop_request("stop, please."))

    def test_stop_with_extra_action_is_rejected(self):
        self.assertFalse(
            is_stop_request("stop listening and open file explorer")
        )


if __name__ == "__main__":
    unittest.main()