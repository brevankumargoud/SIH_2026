import uuid
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.system_event import SystemEvent
import json

class NetworkMonitorService:
    def __init__(self, db: Session):
        self.db = db

    def record_network_event(
        self,
        source_component: str,
        destination: str,
        port: int,
        protocol: str,
        allowed: bool,
        reason: str
    ):
        """Records network access requests for security auditing."""
        
        # Determine if destination is internal or external
        is_internal = self._is_internal_ip(destination)
        
        metadata = {
            "destination": destination,
            "port": port,
            "protocol": protocol,
            "allowed": allowed,
            "reason": reason,
            "is_internal": is_internal
        }

        severity = "info" if allowed else "warning"
        if not allowed and not is_internal:
            severity = "warning"
            
        event = SystemEvent(
            event_type="network_access",
            severity=severity,
            source=source_component,
            message=f"Network access to {destination}:{port} was {'allowed' if allowed else 'blocked'}.",
            metadata_=metadata
        )
        self.db.add(event)
        self.db.commit()

    def _is_internal_ip(self, ip_or_host: str) -> bool:
        # Simple stub for internal check. In a real system, this would evaluate subnets.
        internal_prefixes = ("127.", "10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.", "localhost")
        return any(ip_or_host.startswith(prefix) for prefix in internal_prefixes)

    def get_external_calls_count(self) -> int:
        """Returns the number of external calls attempted."""
        # Query system events for network_access where is_internal is False
        from sqlalchemy import text
        stmt = text("SELECT COUNT(*) FROM system_events WHERE event_type = 'network_access' AND (metadata->>'is_internal')::boolean = false")
        result = self.db.execute(stmt).scalar()
        return result or 0
