"""Generate the code reference pages and navigation."""


from __future__ import annotations

import logging
import sys

import markdownizer
import mkdocs
import inspect

logger = logging.getLogger(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

docs = markdownizer.Docs()
mkdocs_documentation = docs.create_documentation(module=mkdocs)
own_documentation = docs.create_documentation(module=markdownizer)
inspect_documentation = docs.create_documentation(module=inspect)

subnav = docs.create_nav("subnav")
page = subnav.create_page("My first page!")
page.add_admonition("Warning This is still beta", typ="danger", title="Warning!")
page2 = subnav.create_page("And a second one")
subsubnav = subnav.create_nav("SubSubNav")
subsubnav = subsubnav.create_page("SubSubPage")
page2.add_mkdocstrings(logging.LogRecord)
page2.add_mkdocstrings("collections.Counter")

for klass in own_documentation.iter_classes():
    own_documentation.add_class_page(klass=klass)

for klass in inspect_documentation.iter_classes():
    inspect_documentation.add_class_page(klass=klass)

for klass in mkdocs_documentation.iter_classes(recursive=True):
    mkdocs_documentation.add_class_page(klass=klass)

docs.pretty_print()
# docs.write()
