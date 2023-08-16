"""Generate the code reference pages and navigation."""

from __future__ import annotations

import prettyqt

import mknodes

prettyqt.import_all()

QT_MODULE_ATTR = "QT_MODULE"


def build(project: mknodes.Project):
    root_nav = project.get_root()
    project.module = prettyqt
    page = root_nav.add_index_page("Overview", hide_toc=True, hide_nav=True)
    page += mknodes.MkHeader("Test script: Build the PrettyQt documentation", level=1)

    qt_docs = root_nav.add_doc(prettyqt, section_name="Qt modules")
    extra_docs = root_nav.add_doc(prettyqt, section_name="Additional modules")

    for submod in qt_docs.iter_modules(predicate=lambda x: hasattr(x, QT_MODULE_ATTR)):
        subdoc = qt_docs.add_doc(submod, flatten_nav=True)
        subdoc.collect_classes()
    for submod in extra_docs.iter_modules(
        predicate=lambda x: not hasattr(x, QT_MODULE_ATTR)
    ):
        subdoc = extra_docs.add_doc(submod)
        subdoc.collect_classes()
