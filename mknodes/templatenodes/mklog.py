from __future__ import annotations

from io import StringIO
import logging

from typing import Any

from mknodes.basenodes import mkcode
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class MkLog(mkcode.MkCode):
    """Node collecting log data. Displays them as simple text afterwards."""

    ICON = "octicons/log-24"

    def __init__(
        self,
        log_level: int = logging.DEBUG,
        log_format: str | None = None,
        time_format: str | None = None,
        logger: logging.Logger | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            log_level: name of the log_level to install
            log_format: Log format to use
            time_format: Time format of log lines
            logger: Logger to attach our handler to. None means root logger
            kwargs: Keyword arguments passed to parent
        """
        self.log_level = log_level
        self.time_format = time_format  # %a %b %-d %Y %-I:%M:%S %p
        self._log_format = log_format
        formatter = logging.Formatter(fmt=self.log_format, datefmt=self.time_format)
        self.log_stream = StringIO()

        log_handler = logging.StreamHandler(self.log_stream)
        log_handler.setLevel(log_level)
        log_handler.setFormatter(formatter)
        logger = logger or logging.getLogger()
        logger.addHandler(log_handler)
        title = f"Logger: {logger.name}"
        super().__init__(title=title, language="", linenums=1, **kwargs)

    @property
    def log_format(self):
        return self._log_format or "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    @log_format.setter
    def log_format(self, value):
        self._log_format = value

    @property
    def text(self) -> str:
        return self.log_stream.getvalue()

    @text.setter
    def text(self, value) -> str:
        pass

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            log_level=self.log_level,
            log_format=self._log_format,
            time_format=self.time_format,
            _filter_empty=True,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        logger = logging.getLogger("test.logger")
        logger.setLevel(logging.DEBUG)

        node = MkLog(logger=logger)
        logger.info("Info log")
        logger.warning("Debug log")
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    node = MkLog(log_level=logging.DEBUG, logger=logger)
    logger.info("test")
    logger.warning("test")
    print(node)
