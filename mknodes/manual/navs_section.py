import mknodes as mk

from mknodes import paths
from mknodes.manual import routing
from mknodes.navs import navrouter


DOC_TEXT = """Now lets create the documentation.
This code will show how to build a simple documentation section.
"""

nav = mk.MkNav("MkNavs")


def create_navs_section(root_nav: mk.MkNav):
    """Add the complete "The Nodes" section to given MkNav."""
    root_nav += nav
    page = nav.add_index_page()
    variables = dict(create_navs_section=create_navs_section, mknode_cls=mk.MkNav)
    page += mk.MkJinjaTemplate("navs/navs_index.jinja", variables=variables)


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
    page += mk.MkJinjaTemplate("navs/nav_from_file.jinja", variables=variables)


@nav.route.nav("Populate MkPages from folder")
def _(nav: mk.MkNav):
    """Create a MkNav based on a folder tree containing markup files."""
    folder = paths.TEST_RESOURCES / "nav_tree/test_folder/"
    nav.parse.folder(folder, hide="toc")
    page = nav.add_index_page(hide="toc", icon="folder")
    variables = dict(folder=folder)
    page += mk.MkJinjaTemplate("navs/nav_from_folder.jinja", variables=variables)


@nav.route.nav("Routing")
def _(nav: mk.MkNav):
    page = routing.nav.add_index_page(icon="material/call-split", hide="toc")
    page += mk.MkCode.for_file(routing.__file__, header="Code for this section")
    page += mk.MkDocStrings(navrouter.NavRouter, header="MkNav.route Docstrings")
    return routing.nav


# @nav.route.nav("MkDefaultWebsite")
def _(nav: mk.MkNav):
    proj = mk.Project.for_path("https://github.com/mkdocstrings/mkdocstrings.git")
    nav += mk.MkDefaultWebsite(section="MkDocStrings", project=proj)


@nav.route.nav("The MkDoc class")
def _(nav: mk.MkNav):
    page = nav.add_index_page(hide="toc", icon="api")
    page += mk.MkAdmonition(DOC_TEXT, typ="tip")
    template = "docs/classpage_custom.jinja"
    mknodes_docs = nav.add_doc(module=mk, class_page=template)
    # now we collect the stuff we want to document.
    mknodes_docs.collect_classes(recursive=True)


@nav.route.page("Context propagation")
def _(page: mk.MkPage):
    page += mk.MkJinjaTemplate("context_propagation.jinja")
