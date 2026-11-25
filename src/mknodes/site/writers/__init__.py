"""Writers turning a `BuildOutput` into the input of a static site engine."""

from __future__ import annotations

from mknodes.site.writers.base import EngineNotFoundError, GeneratedFolder, Writer
from mknodes.site.writers.markdown import MarkdownWriter
from mknodes.site.writers.mdbook import MdbookWriter
from mknodes.site.writers.mkdocs import MkDocsWriter
from mknodes.site.writers.zensical import ZensicalWriter


WRITERS: dict[str, type[Writer]] = {
    "zensical": ZensicalWriter,
    "mkdocs": MkDocsWriter,
    "mdbook": MdbookWriter,
    "markdown": MarkdownWriter,
}


def get_writer(engine: str) -> type[Writer]:
    """Return the writer class for given engine name."""
    try:
        return WRITERS[engine]
    except KeyError:
        msg = f"Unknown engine {engine!r}. Available: {', '.join(WRITERS)}"
        raise ValueError(msg) from None


__all__ = [
    "WRITERS",
    "EngineNotFoundError",
    "GeneratedFolder",
    "MarkdownWriter",
    "MdbookWriter",
    "MkDocsWriter",
    "Writer",
    "ZensicalWriter",
    "get_writer",
]
