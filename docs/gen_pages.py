"""Generate the code reference pages and navigation."""


from __future__ import annotations

import logging
import sys

import markdownizer
import mkdocs
from markdownizer import classhelpers

logger = logging.getLogger(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

docs = markdownizer.Docs(module=markdownizer)
nav = docs.create_nav(section="markdownizer")

nav[("overview",)] = "index.md"

for klass in docs.iter_classes_for_module("markdownizer"):
    nav.add_class_page(klass=klass, path="test")

nav.pretty_print()

# nav.write()
# docs.write_navs()
