import mknodes as mk

from mknodes import paths
from mknodes.manual import routing
from mknodes.project import Project


DOC_TEXT = """Now lets create the documentation.
This code will show how to build a simple documentation section.
"""

nav = mk.MkNav("MkNavs")


def create_navs_section(root_nav: mk.MkNav):
    """Add the complete "The Nodes" section to given MkNav."""
    root_nav += nav

    routing.create_routing_section(nav)

    page = nav.add_index_page()
    variables = dict(create_navs_section=create_navs_section, mknode_cls=mk.MkNav)
    page += mk.MkJinjaTemplate("navs_index.jinja", variables=variables)


@nav.route.nav("Populate MkPages from SUMMARY.md")
def _(nav: mk.MkNav):
    folder = paths.TEST_RESOURCES / "nav_tree/"
    summary_file = folder / "SUMMARY.md"
    nav.parse.file(summary_file, hide="toc")
    page = nav.add_index_page(hide="toc", icon="file")
    text = summary_file.read_text()
    text = text.replace("](", "] (")  ##
    path = paths.TEST_RESOURCES / "nav_tree/"
    variables = dict(path=path, text=text)
    page += mk.MkJinjaTemplate("nav_from_file.jinja", variables=variables)


@nav.route.nav("Populate MkPages from folder")
def _(nav: mk.MkNav):
    """Create a MkNav based on a folder tree containing markup files."""
    folder = paths.TEST_RESOURCES / "nav_tree/test_folder/"
    nav.parse.folder(folder, hide="toc")
    page = nav.add_index_page(hide="toc", icon="folder")
    variables = dict(folder=folder)
    page += mk.MkJinjaTemplate("nav_from_folder.jinja", variables=variables)


# @nav.route.nav("MkDefaultWebsite")
def _(nav: mk.MkNav):
    proj = Project.for_path("https://github.com/mkdocstrings/mkdocstrings.git")
    website_nav = mk.MkDefaultWebsite(section="MkDocStrings", project=proj)
    nav += website_nav


@nav.route.nav("The MkDoc class")
def _(nav: mk.MkNav):
    page = nav.add_index_page(hide="toc", icon="api")
    page += mk.MkAdmonition(DOC_TEXT, typ="tip")
    mknodes_docs = nav.add_doc(
        module=mk,
        class_page="docs/classpage_custom.jinja",
    )
    # now we collect the stuff we want to document.
    mknodes_docs.collect_classes(recursive=True)
