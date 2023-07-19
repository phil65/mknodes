"""Generate the code reference pages and navigation."""

from __future__ import annotations

import prettyqt
import mknodes

prettyqt.import_all()

QT_MODULE_ATTR = "QT_MODULE"

root_nav = mknodes.MkNav()
page = mknodes.MkPage(path="index.md", hide_toc=True, hide_nav=True)
page.add_header("Not in the mood to write documentation? Let´s code it then!", level=3)
page.write()

qt_docs = root_nav.add_documentation(prettyqt, section_name="Qt modules")
extra_docs = root_nav.add_documentation(prettyqt, section_name="Additional modules")

for submod in qt_docs.iter_modules(predicate=lambda x: hasattr(x, QT_MODULE_ATTR)):
    subdoc = qt_docs.add_documentation(submod)
    subdoc.add_module_overview()
    for klass in subdoc.iter_classes():
        subdoc.add_class_page(klass=klass, flatten=True)
for submod in extra_docs.iter_modules(predicate=lambda x: not hasattr(x, QT_MODULE_ATTR)):
    subdoc = extra_docs.add_documentation(submod)
    subdoc.add_module_overview()
    for klass in subdoc.iter_classes():
        subdoc.add_class_page(klass=klass, flatten=True)


# root_nav.pretty_print()
root_nav.write()  # Finally, we write the whole tree.
