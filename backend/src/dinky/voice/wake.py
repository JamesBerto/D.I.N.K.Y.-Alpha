import re

_WAKE_WORD = re.compile(r"\bdinky\b", re.IGNORECASE)
_STOP_REQUEST = re.compile(
    r"(?:stop(?:\s+listening)?(?:\s*,?\s*please)?|"
    r"quit listening|that's it)[.!?]*",
    re.IGNORECASE,
)


def request_after_wake_word(text: str) -> str | None:
    match = _WAKE_WORD.search(text)
    if match is None:
        return None

    return text[match.end():].lstrip(" ,:;.!?")


def is_stop_request(text: str) -> bool:
    return _STOP_REQUEST.fullmatch(text.strip()) is not None


def test_stop_phrases(self):
        self.assertTrue(is_stop_request("stop listening"))
        self.assertTrue(is_stop_request("stop, please."))


def test_stop_with_extra_action_is_rejected(self):
        self.assertFalse(
            is_stop_request("stop listening and open file explorer")
        )