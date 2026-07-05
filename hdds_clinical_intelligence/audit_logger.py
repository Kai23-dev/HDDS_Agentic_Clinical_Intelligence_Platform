"""
Clinical audit logging.

Every security- or clinically-significant action (login, upload, pipeline run,
clinician Accept/Reject, data export) is written as one append-only JSON line to
`logs/audit.log`. JSON-per-line is both greppable and machine-parseable, so the
file can be shipped to a SIEM / log analytics workspace (e.g. Azure Monitor) later.

HIPAA/GDPR note: we log **identifiers and actions**, never raw clinical text. An
audit trail that copies PHI into a second file is itself a liability, so callers
should pass patient_id / item names — not note bodies.
"""

import os
import json
import threading
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIT_PATH = os.getenv("AUDIT_LOG_PATH", os.path.join(BASE_DIR, "logs", "audit.log"))

_lock = threading.Lock()
_MAX_STR_DETAIL = 300  # cap free-text details defensively


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(action, actor="anonymous", patient_id=None, resource=None,
              outcome="success", details=None):
    """Append one audit entry. Returns the entry dict. Never raises to callers."""
    if isinstance(details, str):
        details = details[:_MAX_STR_DETAIL]

    entry = {
        "timestamp": _utc_now(),
        "actor": actor,
        "action": action,
        "patient_id": patient_id,
        "resource": resource,
        "outcome": outcome,
        "details": details,
    }
    try:
        line = json.dumps(entry, ensure_ascii=False, default=str)
        with _lock:
            os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
            with open(AUDIT_PATH, "a", encoding="utf-8") as f:
                f.write(line + "\n")
    except Exception as e:  # auditing must never break the request path
        print(f"[audit] failed to write entry: {e}")
    return entry


class AuditLogger:
    """OO wrapper that carries a default actor (e.g. the logged-in clinician)."""

    def __init__(self, actor="system"):
        self.actor = actor

    def log(self, action, **kwargs):
        kwargs.setdefault("actor", self.actor)
        return log_event(action, **kwargs)
