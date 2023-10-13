"""Module containing the documentation."""

from .root import build
from . import routing
from .index_page import create_index_page

__all__ = [
    "build",
    "routing",
    "create_index_page",
]
