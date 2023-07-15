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

for klass in own_documentation.iter_classes():
    own_documentation.add_class_page(klass=klass)

for klass in inspect_documentation.iter_classes():
    inspect_documentation.add_class_page(klass=klass)

for klass in mkdocs_documentation.iter_classes(recursive=True):
    mkdocs_documentation.add_class_page(klass=klass)

# nav = docs.create_nav(section="ast")

# for klass in astdocs.iter_classes_for_module("ast"):
#     nav.add_class_page(klass=klass, path=f"{klass.__name__}.md")

# nav.pretty_print()
print(str(docs))

# nav.write()
docs.write()
