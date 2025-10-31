# app/core/mylogger.py
import datetime as dt
import logging
import json
from typing import Optional
from typing_extensions import override

# Optional: populate with builtin LogRecord attributes (for filtering custom fields)
LOG_RECORD_BUILTIN_ATTRS = set(vars(logging.LogRecord("x", 0, "", 0, "", (), None)).keys())


class MyJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter that:
    - Outputs structured JSON for machine parsing.
    - Keeps timestamps in ISO 8601 UTC.
    - Includes exception and stack traces when present.
    - Maps fields based on a configurable fmt_keys dict.
    """

    def __init__(self, *, fmt_keys: Optional[dict[str, str]] = None):
        super().__init__()
        self.fmt_keys = fmt_keys or {
            "timestamp": "asctime",
            "level": "levelname",
            "logger": "name",
            "module": "module",
            "function": "funcName",
            "line": "lineno",
            "thread_name": "threadName",
            "message": "message",
        }

    @override
    def format(self, record: logging.LogRecord) -> str:
        log_dict = self._prepare_log_dict(record)
        return json.dumps(log_dict, default=str, ensure_ascii=False)

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict:
        """Build the dictionary representation of the log record."""
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(record.created, tz=dt.timezone.utc).isoformat(),
        }

        # Attach error information if available
        if record.exc_info:
            always_fields["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {}
        for key, val in self.fmt_keys.items():
            if val in always_fields:
                message[key] = always_fields.pop(val, None)
            else:
                message[key] = getattr(record, val, None)

        # Include remaining always_fields and any custom attributes
        message.update(always_fields)
        for key, value in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS and key not in message:
                message[key] = value

        return message


class NonErrorFilter(logging.Filter):
    """Filter that only allows logs below WARNING level."""
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.WARNING


class ErrorFilter(logging.Filter):
    """Filter that only allows WARNING and higher."""
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.WARNING
