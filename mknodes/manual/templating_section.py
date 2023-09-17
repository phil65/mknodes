from __future__ import annotations

import mknodes as mk

from mknodes.info import contexts


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
    page = nav.add_index_page(hide="toc")
    page += mk.MkJinjaTemplate("template_index.jinja")
    page += mk.MkDetailsBlock(ADDITIONAL_INFO_TEXT, expand=True)
    page += "### These are the availabe namespaces:"
    page += mk.MkDefinitionList(NAMESPACES)
    code = mk.MkCode.for_object(create_templating_section)
    page += mk.MkAdmonition(code, title=SECTION_CODE, collapsible=True, typ="quote")


@nav.route.nav("Jinja Namespace")
def create_jinja_namespace_section(nav: mk.MkNav):
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


# @nav.route.nav("Templates for documentation pages")
# def create_documentation_templates_section(nav: mk.MkNav):
#     page = nav.add_index_page(hide="toc")
#     page += mk.MkAdmonition("This is the default Jinja template for class pages")
#     text = pathlib.Path(paths.RESOURCES / "classpage.md").read_text(encoding="utf-8")
#     text = text.replace(r"{{", "{ {").replace(r"}}", "} }")
#     page += mk.MkCode(text)
