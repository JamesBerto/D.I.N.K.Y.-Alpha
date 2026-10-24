import re


_EXPLORER_COMMAND = re.compile(
    r"(?:hey\s+)?(?:dinky[,:\s]+)?(?:please\s+)?"
    r"open\s+(?:the\s+)?(?:file\s+)?explorer[.!?]*",
    re.IGNORECASE,
)

_STATUS_COMMAND = re.compile(
    r"(?:hey\s+)?(?:dinky[,:\s]+)?(?:please\s+)?"
    r"(?:show|check|display)\s+(?:(?:my|me|the)\s+)?system\s+status[.!?]*",
    re.IGNORECASE,
)


def match_tool(text: str) -> str | None:
    if _EXPLORER_COMMAND.fullmatch(text.strip()):
        return "app.open_explorer"
    if _STATUS_COMMAND.fullmatch(text.strip()):
        return "system.status"
    return None

_DEVICE_STATUS_REFERENCE = re.compile(
    r"\b(?:system\s+status|my\s+(?:cpu|memory|ram|battery))\b",
    re.IGNORECASE,
)


def mentions_device_status(text: str) -> bool:
    return _DEVICE_STATUS_REFERENCE.search(text) is not None