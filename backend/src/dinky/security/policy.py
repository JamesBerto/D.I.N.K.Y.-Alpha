from dataclasses import dataclass
from enum import IntEnum


class PermissionLevel(IntEnum):
    OBSERVE = 0
    ROUTINE = 1
    USER_DATA = 2
    SYSTEM_CHANGE = 3
    RESTRICTED = 4


@dataclass(frozen=True)
class Decision:
    allowed: bool
    requires_confirmation: bool
    reason: str


class PolicyEngine:
    # A tool must be listed here before D.I.N.K.Y. may use it.
    TOOL_LEVELS = {
        "system.status": PermissionLevel.OBSERVE,
        "app.open_explorer": PermissionLevel.ROUTINE,
    }

    def check(self, tool_name: str) -> Decision:
        level = self.TOOL_LEVELS.get(tool_name)

        if level is None:
            return Decision(False, False, "Unknown tool is blocked.")

        if level == PermissionLevel.RESTRICTED:
            return Decision(False, False, "Restricted tool is blocked.")

        if level in (
            PermissionLevel.USER_DATA,
            PermissionLevel.SYSTEM_CHANGE,
        ):
            return Decision(
                False, True, "Owner confirmation is required."
            )

        return Decision(True, False, "Tool is permitted.")