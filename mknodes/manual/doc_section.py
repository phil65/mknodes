from __future__ import annotations

import mknodes


INTRO_TEXT = """now lets create the documentation.
This code will show how to build a simple documentation section.
"""


def create_documentation_section(root_nav: mknodes.MkNav):
    doc_section = root_nav.add_nav("Documentation")

    overview = doc_section.add_index_page(hide_toc=True, icon="material/api")
    overview += mknodes.MkText(INTRO_TEXT)
    overview += mknodes.MkCode.for_object(create_documentation_section)

    # lets create the complete documentation for our module.
    # Each Documentation section can have global filters for what it should include.
    # In this case, we only want to document stuff which is listed in "__all__".
    mknodes_docs = doc_section.add_doc(module=mknodes, filter_by___all__=True)

    # now we collect the stuff we want to document.
    mknodes_docs.collect_classes(recursive=True)

    # We could also filter specific subclasses,
    # or do other fancy stuff to generate a customized, automated documentation
    # like changing the default class page ("MkClassPage") of our docs,
    # (The default contains MkDocStrings, a table for base classes,  eventual subclasses
    # and an inheritance graph.)

    # There is also an extension available for this module which offers tools and
    # new nodes based on PySide6 / PyQt6. We can add its documentation easily:
    # from prettyqt import prettyqtmarkdown

    # addon_docs = doc_section.add_doc(module=prettyqtmarkdown, flatten_nav=True)
    # addon_docs.collect_classes(recursive=True)


if __name__ == "__main__":
    nav = mknodes.MkNav()
    create_documentation_section(nav)
    print(nav.children[0])
