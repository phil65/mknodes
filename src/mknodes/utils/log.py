import io
import logging
import sys
from typing import Any


ROOT_LOGGER_NAME = "mknodes"


class Logger:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def __getattr__(self, val: Any) -> Any:
        return getattr(self.logger, val)


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger below the `mknodes` logger.

    Args:
        name: Logger name (usually `__name__`). Names outside the `mknodes` namespace
              get prefixed, so that all output can be configured via the `mknodes` logger.
    """
    if not name or name == ROOT_LOGGER_NAME:
        return logging.getLogger(ROOT_LOGGER_NAME)
    if name.startswith(f"{ROOT_LOGGER_NAME}."):
        return logging.getLogger(name)
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{name}")


def basic() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)


log_stream = io.StringIO()
log_handler = logging.StreamHandler(log_stream)
log_handler.setLevel(logging.DEBUG)
fmt = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log_handler.setFormatter(fmt)
logger = logging.getLogger(ROOT_LOGGER_NAME)
logger.addHandler(log_handler)
