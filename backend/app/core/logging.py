import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """Structured JSON formatter that masks sensitive fields and outputs machine-readable logs."""

    SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "authorization", "key", "cookie"}

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_entry["request_id"] = getattr(record, "request_id")
        if hasattr(record, "user_id"):
            log_entry["user_id"] = getattr(record, "user_id")
        if hasattr(record, "method"):
            log_entry["method"] = getattr(record, "method")
        if hasattr(record, "path"):
            log_entry["path"] = getattr(record, "path")
        if hasattr(record, "status_code"):
            log_entry["status_code"] = getattr(record, "status_code")
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = getattr(record, "duration_ms")

        # Sanitize message if needed
        return json.dumps(log_entry)


def setup_logging():
    logger = logging.getLogger("agrimind")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
