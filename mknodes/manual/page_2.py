from __future__ import annotations

import inspect

import mknodes


INTRO_TEXT = """now lets create the documentation.
This code will show how to build a simple documentation section.
"""


def create_page_2(root_nav: mknodes.MkNav):
    doc_section = root_nav.add_nav("Documentation")

    overview = doc_section.add_page("Overview", hide_toc=True)
    overview += mknodes.MkText(INTRO_TEXT)

    # we are here right now.
    overview.add_code(inspect.getsource(create_page_2))

    # lets create the complete documentation for our module.
    # Each Documentation section can have global filters for what it should include.
    # In this case, we only want to document stuff which is listed in "__all__".
    mknodes_docs = doc_section.add_doc(module=mknodes, filter_by___all__=True)

    # the Documentation Nav hast some helper methods to iterate through the submodules
    # / classes of a module. We can also pass a predicate to filter specific subclasses,
    # or do other fancy stuff to generate a customized, automated documentation.
    # now we add some pre-defined pages ("MkClassPages") to our docs.
    # they contain MkDocStrings, a table for eventual subclasses and an
    # inheritance graph. It`s also possible to build custom pages of course.
    mknodes_docs.collect_classes(recursive=True)

    # Not enough documentation for your taste? Let`s document random stuff.
    # What about the std library?
    std_lib_nav = doc_section.add_nav("std_library")
    for stdlib_mod in ["pathlib", "inspect", "logging"]:
        docs = std_lib_nav.add_doc(module=stdlib_mod)
        docs.collect_classes(recursive=True)

    overview.add_admonition(text="That was easy, right?")


if __name__ == "__main__":
    nav = mknodes.MkNav()
    create_page_2(nav)
    print(nav.children[0])
