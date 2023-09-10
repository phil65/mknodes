from __future__ import annotations

import mknodes

from mknodes.info import contexts


INTRO_TEXT = """MkNodes contains an expansive Jinja2 Environment. It is comparable to
the MkDocs macros plugin. It has less settings (you can modify the environment
via code of course though), but has a much larger built-in set of macros and filters.
"""

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"


def create_templating_section(root_nav: mknodes.MkNav):
    """Add the complete "Templating" section to given MkNav."""
    templating_nav = root_nav.add_nav("Templating")
    # first we create the menu on the left:

    create_macros_nav(templating_nav)

    # and then we create the index page (the page you are lookin at right now)

    page = templating_nav.add_index_page(hide_toc=True, icon="material/graph")
    page += mknodes.MkCode.for_object(create_templating_section, header=SECTION_CODE)
    page += mknodes.MkDetailsBlock(INTRO_TEXT, expand=True)


def create_macros_nav(nav: mknodes.MkNav):
    macros_nav = nav.add_nav("Jinja macros")
    page = macros_nav.add_index_page(icon=mknodes.MkClassPage.ICON, hide_toc=True)
    page += mknodes.MkCode.for_object(create_macros_nav, header=PAGE_CODE)
    add_context_doc(page, contexts.ProjectContext)
    for ctx in [contexts.PackageContext, contexts.ThemeContext, contexts.GitContext]:
        page = macros_nav.add_page(ctx.__name__)
        add_context_doc(page, ctx)


def add_context_doc(container, context):
    container += mknodes.MkDocStrings(
        context,
        show_root_toc_entry=False,
        show_if_no_docstring=True,
        heading_level=4,
        show_bases=False,
        show_source=False,
    )


def create_filters_page(nav: mknodes.MkNav):
    page = nav.add_page("Jinja macros", icon=mknodes.MkClassPage.ICON)
    page += mknodes.MkCode.for_object(create_filters_page, header=PAGE_CODE)
    class_page = mknodes.MkClassPage(mknodes.MkCode, virtual=True)
    page += mknodes.MkReprRawRendered(class_page)
