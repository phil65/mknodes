from __future__ import annotations

import io
import logging
import sys


class Logger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def __getattr__(self, val):
        return getattr(self.logger, val)

    def log_dict(self, dct, level=logging.INFO):
        for k, v in dct.items():
            self.logger.log(level, "%s: %s", k, v)


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(f"mkdocs.plugin.{name}" if name else None)


def basic():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


log_stream = io.StringIO()
log_handler = logging.StreamHandler(log_stream)
log_handler.setLevel(logging.DEBUG)
fmt = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log_handler.setFormatter(fmt)
logger = logging.getLogger("mkdocs.plugin")
logger.addHandler(log_handler)
