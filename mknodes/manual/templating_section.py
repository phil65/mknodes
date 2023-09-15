from __future__ import annotations

import mknodes as mk

from mknodes.info import contexts


INTRO_TEXT = """MkNodes contains an expansive Jinja2 Environment. It is comparable to
the MkDocs macros plugin. It has less settings (you can modify the environment
via code of course though), but has a much larger built-in set of macros and filters.
"""

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"


nav = mk.MkNav("Templating")


def create_templating_section(root_nav: mk.MkNav):
    """Add the complete "Templating" section to given MkNav."""
    root_nav += nav
    page = nav.add_index_page(hide_toc=True, icon="simple/jinja")
    page += mk.MkCode.for_object(create_templating_section, header=SECTION_CODE)
    page += mk.MkDetailsBlock(INTRO_TEXT, expand=True)

    def add_context_doc(container, context):
        container += mk.MkDocStrings(
            context,
            show_root_toc_entry=False,
            show_if_no_docstring=True,
            heading_level=4,
            show_bases=False,
            show_source=False,
        )

    page = nav.add_index_page(icon=mk.MkClassPage.ICON, hide_toc=True)
    add_context_doc(page, contexts.ProjectContext)
    for ctx in [
        contexts.PackageContext,
        contexts.ThemeContext,
        contexts.GitContext,
        contexts.GitHubContext,
    ]:
        page = nav.add_page(ctx.__name__)
        add_context_doc(page, ctx)
