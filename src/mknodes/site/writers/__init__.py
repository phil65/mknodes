"""Writers turning a `BuildOutput` into the input of a static site engine."""

from __future__ import annotations

from mknodes.site.writers.base import EngineNotFoundError, GeneratedFolder, Writer
from mknodes.site.writers.docsify import DocsifyWriter
from mknodes.site.writers.markdown import MarkdownWriter
from mknodes.site.writers.mdbook import MdbookWriter
from mknodes.site.writers.mkdocs import MkDocsWriter
from mknodes.site.writers.sphinx import SphinxWriter
from mknodes.site.writers.zensical import ZensicalWriter


WRITERS: dict[str, type[Writer]] = {
    "zensical": ZensicalWriter,
    "mkdocs": MkDocsWriter,
    "mdbook": MdbookWriter,
    "sphinx": SphinxWriter,
    "docsify": DocsifyWriter,
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
    "DocsifyWriter",
    "EngineNotFoundError",
    "GeneratedFolder",
    "MarkdownWriter",
    "MdbookWriter",
    "MkDocsWriter",
    "SphinxWriter",
    "Writer",
    "ZensicalWriter",
    "get_writer",
]
