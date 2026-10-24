from collections.abc import Callable

from dinky.audit import AuditStore
from dinky.security.policy import PolicyEngine
from dinky.tools.system_status import get_system_status


class ToolRouter:
    def __init__(self, audit: AuditStore) -> None:
        self.audit = audit
        self.policy = PolicyEngine()
        self.handlers: dict[str, Callable[[], dict]] = {
            "system.status": get_system_status,
        }

    def execute(self, tool_name: str, source: str) -> dict:
        decision = self.policy.check(tool_name)

        if not decision.allowed:
            self.audit.record(tool_name, source, "denied")
            raise PermissionError(decision.reason)

        handler = self.handlers.get(tool_name)
        if handler is None:
            self.audit.record(tool_name, source, "failed")
            raise RuntimeError(f"No handler for permitted tool: {tool_name}")

        try:
            result = handler()
        except Exception:
            self.audit.record(tool_name, source, "failed")
            raise

        self.audit.record(tool_name, source, "succeeded")
        return result