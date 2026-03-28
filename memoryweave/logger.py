"""Logging setup for MemoryWeave.

Keeps all logging config in one place so the rest of the codebase
just does `from memoryweave.logger import get_logger` and moves on.

Logging is off by default — we don't want to spam users' apps with
our internal logs. They opt in by calling `configure_logging()` or
setting the MEMORYWEAVE_LOG_LEVEL environment variable.
"""

from __future__ import annotations

import logging
import os
import sys

# using a named logger hierarchy so users can filter with
# logging.getLogger("memoryweave") and get everything at once
_ROOT_LOGGER_NAME = "memoryweave"

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# map string level names to logging constants — used when reading from env
_LEVEL_MAP: dict[str, int] = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def get_logger(name: str) -> logging.Logger:
    """Get a named logger under the memoryweave hierarchy.

    Every module should call this at the top and use it throughout:

        logger = get_logger(__name__)
        logger.debug("extracting entities from %d chars", len(text))

    Args:
        name: Usually just pass __name__ — it gives you a logger
            like "memoryweave.extractor" or "memoryweave.store".

    Returns:
        A Logger instance under the memoryweave namespace.
    """
    return logging.getLogger(name)


def configure_logging(level: str | int = "info") -> None:
    """Configure MemoryWeave logging for the current session.

    Call this once at app startup if you want to see MemoryWeave logs.
    Without calling this, logging is effectively silent (NullHandler).

    Args:
        level: Log level as a string ("debug", "info", "warning",
            "error") or a logging constant (logging.DEBUG etc).
            Defaults to "info".

    Example:
        >>> import memoryweave
        >>> memoryweave.configure_logging("debug")
        # now all memoryweave logs appear in stdout
    """
    root = logging.getLogger(_ROOT_LOGGER_NAME)

    # resolve string level names to int
    if isinstance(level, str):
        resolved = _LEVEL_MAP.get(level.lower())
        if resolved is None:
            raise ValueError(
                f"Unknown log level {level!r}. "
                f"Choose from: {list(_LEVEL_MAP.keys())}"
            )
        level = resolved

    root.setLevel(level)

    # only add a handler if none exist yet — avoids duplicate log lines
    # if the user calls configure_logging() more than once
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
        handler.setFormatter(formatter)
        root.addHandler(handler)


def _setup_null_handler() -> None:
    """Attach a NullHandler so we don't get 'No handlers' warnings.

    This is the recommended pattern for library loggers — we set up
    a NullHandler by default so nothing appears unless the user
    explicitly calls configure_logging().
    """
    logging.getLogger(_ROOT_LOGGER_NAME).addHandler(logging.NullHandler())


# runs on import — silent by default, respects MEMORYWEAVE_LOG_LEVEL env var
_setup_null_handler()

_env_level = os.getenv("MEMORYWEAVE_LOG_LEVEL")
if _env_level:
    configure_logging(_env_level)
