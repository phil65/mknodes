"""Module containing the documentation."""

from .nodes_section import create_nodes_section
from .internals_section import create_internals_section
from .dev_section import create_development_section
from .root import create_root
from . import routing
from .index_page import create_index_page

__all__ = [
    "create_nodes_section",
    "create_internals_section",
    "create_development_section",
    "create_root",
    "routing",
    "create_index_page",
]
