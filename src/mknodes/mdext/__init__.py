"""Markdown extensions for mknodes."""

from __future__ import annotations

from .execute_ext import ExecuteExtension, makeExtension as makeExecuteExtension
from .mknodes_ext import MkNodesExtension, makeExtension as makeMkNodesExtension

__all__ = [
    "ExecuteExtension",
    "MkNodesExtension",
    "makeExecuteExtension",
    "makeMkNodesExtension",
]


def makeExtension(**kwargs):  # noqa: N802
    """Create MkNodes extension for markdown module loading.

    Markdown loads extensions by module path and looks for makeExtension().
    Usage in mkdocs.yml: `- mknodes.mdext`
    """
    return makeMkNodesExtension(**kwargs)
