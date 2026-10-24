import re

_WAKE_WORD = re.compile(r"\bdinky\b", re.IGNORECASE)


def request_after_wake_word(text: str) -> str | None:
    match = _WAKE_WORD.search(text)
    if match is None:
        return None

    return text[match.end():].lstrip(" ,:;.!?")