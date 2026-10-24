import re


_EXPLORER_COMMAND = re.compile(
    r"(?:hey\s+)?(?:dinky[,:\s]+)?(?:please\s+)?"
    r"open\s+(?:the\s+)?(?:file\s+)?explorer[.!?]*",
    re.IGNORECASE,
)


def match_tool(text: str) -> str | None:
    if _EXPLORER_COMMAND.fullmatch(text.strip()):
        return "app.open_explorer"
    return None