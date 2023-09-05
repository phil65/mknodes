from __future__ import annotations

import io
import logging


log_stream = io.StringIO()
log_handler = logging.StreamHandler(log_stream)
log_handler.setLevel(logging.DEBUG)
fmt = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log_handler.setFormatter(fmt)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)
