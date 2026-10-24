from dinky.audit import AuditStore
from dinky.tools.router import ToolRouter


class SystemStatusService:
    def __init__(self, audit: AuditStore) -> None:
        self.router = ToolRouter(audit)

    def read(self, source: str) -> dict:
        return self.router.execute("system.status", source)