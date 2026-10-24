from dinky.audit import AuditStore
from dinky.tools.system_status import get_system_status


class SystemStatusService:
    def __init__(self, audit: AuditStore) -> None:
        self.audit = audit

    def read(self, source: str) -> dict:
        try:
            status = get_system_status()
        except Exception:
            self.audit.record("system.status", source, "failed")
            raise

        self.audit.record("system.status", source, "succeeded")
        return status