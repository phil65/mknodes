from __future__ import annotations

import mknodes as mk

from mknodes.info import contexts


INTRO_TEXT = """MkNodes contains an expansive Jinja2 Environment. It is comparable to
the `MkDocs` macros plugin. It has less settings (you can modify the environment
via code of course though), but has a much larger built-in set of macros and filters.

The main features of the environment are 2 things:

* All MkNodes can be used as a filter, as well as a macro:

    * Example for use as a filter: `{ { "classifiers" | MkMetadataBadges } }`
    * Example for use as a macro: `{ { mk.MkHeader("some header") } }`

* Project metadata is also available in the Jinja environment namespace.
  You can see all available info in the subsections of this page.

    * Example: `{ { metadata.license_name } }`

"""

ADDITIONAL_INFO_TEXT = """MkNodes cannot just re-use the MkDocs jinja environment
because at that stage of the build process, our nodes already became text and we need
the nodes for context (mainly to attach a parent to the MkNodes used as macros / filters)
"""

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"

NAMESPACES = {
    "`metadata`": "Package information",
    "`git`": "Local repository information",
    "`github`": "Information about the remote repository",
    "`theme`": "Information about the theme being used",
}

CONTEXTS = [
    contexts.PackageContext,
    contexts.ThemeContext,
    contexts.GitContext,
    contexts.GitHubContext,
]

nav = mk.MkNav("Templating")


def create_templating_section(root_nav: mk.MkNav):
    """Add the complete "Templating" section to given MkNav."""
    root_nav += nav
    page = nav.add_index_page(hide_toc=True)
    page += mk.MkText(INTRO_TEXT)
    page += mk.MkDetailsBlock(ADDITIONAL_INFO_TEXT, expand=True)
    page += "### These are the availabe namespaces:"
    page += mk.MkDefinitionList(NAMESPACES)

    def add_context_doc(container, context):
        container += mk.MkDocStrings(
            context,
            show_root_toc_entry=False,
            show_if_no_docstring=True,
            heading_level=4,
            show_bases=False,
            show_source=False,
        )

    for ctx in CONTEXTS:
        subpage = nav.add_page(ctx.__name__)
        add_context_doc(subpage, ctx)

    code = mk.MkCode.for_object(create_templating_section)
    page += mk.MkAdmonition(code, title=SECTION_CODE, collapsible=True, typ="quote")
