import logging


class RichState:
    """Route the log output of MkNodes through a rich handler."""

    LOG_NAMES = ("mknodes",)

    def __init__(self, log_names: tuple[str, ...] | None = None, level: int = logging.INFO):
        """Constructor.

        Args:
            log_names: Logger names
            level: Logging level
        """
        from rich.logging import RichHandler

        self.stream = RichHandler(
            level,
            markup=False,
            rich_tracebacks=True,
            omit_repeated_times=False,
        )
        self.stream.name = "MkNodesStreamHandler"
        self.loggers = [logging.getLogger(name) for name in log_names or self.LOG_NAMES]
        for logger in self.loggers:
            # Don't restrict level on logger; use handler
            logger.setLevel(1)
            logger.propagate = False
            logger.addHandler(self.stream)

    def set_level(self, level: int) -> None:
        self.stream.setLevel(level)

    def __del__(self):
        for logger in self.loggers:
            logger.removeHandler(self.stream)
