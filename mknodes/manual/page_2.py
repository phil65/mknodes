from __future__ import annotations

import inspect

import mknodes


INTRO_TEXT = """now lets create the documentation.
This code will show how to build a simple documentation section.
"""


def create_page_2(root_nav: mknodes.Nav):
    doc_section = root_nav.add_nav("Documentation")

    overview = doc_section.add_page("Overview", hide_toc=True)
    overview += mknodes.MkText(INTRO_TEXT)

    # we are here right now.
    overview.add_code(inspect.getsource(create_page_2))

    # lets create the complete documentation for our module.
    # Each Documentation section can have global filters for what it should include.
    # In this case, we only want to document stuff which is listed in "__all__".
    mknodes_docs = doc_section.add_documentation(module=mknodes, filter_by___all__=True)
    # we start by adding a nice overview page. This might gain some kwargs for different
    # styles in the future.
    mknodes_docs.add_module_overview()

    # the Documentation Nav hast some helper methods to iterate through the submodules
    # / classes of a module. We can also pass a predicate to filter specific subclasses,
    # or do other fancy stuff to generate a customized, automated documentation.
    for klass in mknodes_docs.iter_classes(recursive=True):
        # now we add some pre-defined pages ("MkClassPages") to our docs.
        # they contain MkDocStrings, a table for eventual subclasses and an
        # inheritance graph. It`s also possible to build custom pages of course.
        mknodes_docs.add_class_page(klass=klass)

    # Not enough documentation for your taste? Let`s document random stuff.
    # What about the std library?
    std_lib_nav = doc_section.add_nav("std_library")
    for stdlib_mod in ["pathlib", "inspect", "logging"]:
        docs = std_lib_nav.add_documentation(module=stdlib_mod)
        docs.add_module_overview()
        for klass in docs.iter_classes(recursive=True):
            docs.add_class_page(klass=klass)

    overview.add_admonition(text="That was easy, right?")
