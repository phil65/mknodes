import mknodes as mk

from mknodes import paths
from mknodes.manual import routing
from mknodes.project import Project


DOC_TEXT = """Now lets create the documentation.
This code will show how to build a simple documentation section.
"""

ANNOTATIONS_INFO = """It is always best to use annotations from the *closest* node.
(We could also have used the annotations from MKPage, but since this source code
is displayed by the MkCode node, we use that one.)"""


nav = mk.MkNav("Navigation & Pages")

pages_nav = nav.add_nav("MkPage")


def create_navs_section(root_nav: mk.MkNav):
    """Add the complete "The Nodes" section to given MkNav."""
    # Basic structure: Theres one root MkNav, MkNavs can contain MkPages and other MkNavs,
    # MkPages contain more atomic MkNodes, like MkText, MkTable, and MkDiagrams.
    # These markup nodes in some cases can contain other Markup nodes.
    # It`s all one big tree.

    # MkNavs can either be populated manually with MkPages and MkNavs, or we can load
    # existing folders containing markup files. There are two ways for this:
    #
    #   * Load an existing SUMMARY.md and create a nav based on given file content.
    #
    root_nav += nav

    # Another approach to set up navs is by using decorators. We will explain that here:
    routing.create_routing_section(nav)

    # Navs contain also contain pages. This section provides some info how to use MkPages.
    page = pages_nav.add_index_page(hide="toc")
    page += mk.MkJinjaTemplate("mkpage_index.jinja")

    page = nav.add_index_page(hide="toc")
    variables = dict(create_navs_section=create_navs_section, mknode_cls=mk.MkNode)
    page += mk.MkJinjaTemplate("navs_index.jinja", variables=variables)


@nav.route.nav("From file")
def _(nav: mk.MkNav):
    """Load an existing SUMMARY.md and attach it to given MkNav."""
    # We will now demonstate loading an existing Nav tree.

    # This path contains Markdown files/ folders and a pre-populated SUMMARY.md.
    folder = paths.TEST_RESOURCES / "nav_tree/"  # Folder content: # (1)
    summary_file = folder / "SUMMARY.md"  # File content: # (2)
    nav.parse.file(summary_file, hide="toc")

    page = nav.add_index_page(hide="toc", icon="file")
    text = summary_file.read_text()
    text = text.replace("](", "] (")  ##
    path = paths.TEST_RESOURCES / "nav_tree/"
    tree_node = mk.MkTreeView(path, header="Directory tree")
    page += mk.MkAdmonition(tree_node)
    file_content_node = mk.MkCode(text, header="SUMMARY.md content")
    page += mk.MkAdmonition(file_content_node)
    page += ANNOTATIONS_INFO
    page += tree_node
    page += file_content_node


@nav.route.nav("From folder")
def _(nav: mk.MkNav):
    """Create a MkNav based on a folder tree containing markup files."""
    # We are using a part of the previous nav tree. It's a subfolder without a SUMMARY.md.
    folder = paths.TEST_RESOURCES / "nav_tree/test_folder/"
    nav.parse.folder(folder, hide="toc")
    page = nav.add_index_page(hide="toc", icon="folder")
    page += mk.MkTreeView(folder)
    page += mk.MkDocStrings(mk.MkTreeView)


@pages_nav.route.page("MkClassPage")
def _(page: mk.MkPage):
    variables = dict(example_class=mk.MkCode)
    page += mk.MkJinjaTemplate("mkclasspage.jinja", variables=variables)


@pages_nav.route.page("MkModulePage")
def _(page: mk.MkPage):
    import mkdocs.config

    variables = dict(example_module=mkdocs.config)
    page += mk.MkJinjaTemplate("mkmodulepage.jinja", variables=variables)


@pages_nav.route.page("Adding to MkPages", hide="toc", status="new")
def _(page: mk.MkPage):
    page += mk.MkAdmonition("You can add other MkNodes to a page sequentially.")
    page += "Adding strings also works, they get converted to MkText nodes."
    page += "### ...and text starting with # will become a MkHeader."
    page += "Every MkPage has a MkFootNotes node built-in[^1]."
    page.footnotes[1] = "Super cool, right?"


@pages_nav.route.page(
    "Metadata",
    status="deprecated",
    search_boost=2.0,
    subtitle="Subtitle",
    description="Description",
)
def _(page: mk.MkPage):
    page += mk.MkJinjaTemplate("page_metadata.jinja")


@pages_nav.route.page("Templates", hide="toc", status="new")
def _(page: mk.MkPage):
    page += mk.MkJinjaTemplate("page_templates.jinja")
    page.template.announce_block.content = mk.MkMetadataBadges(typ="classifiers")
    page.template.footer_block.content = mk.MkProgressBar(50)
    code = "information = 'You can even put MkNodes here!'"
    page.template.tabs_block.content = mk.MkCode(f"{code}")
    page.template.hero_block.content = mk.MkHeader("A header!")


# @nav.route.nav("MkDefaultWebsite")
def create_mkdefaultwebsite_section(nav: mk.MkNav):
    proj = Project.for_path("https://github.com/mkdocstrings/mkdocstrings.git")
    website_nav = mk.MkDefaultWebsite(section="MkDocStrings", project=proj)
    nav += website_nav


@nav.route.nav("MkDoc")
def _(nav: mk.MkNav):
    nav = nav.add_nav("MkDoc")

    page = nav.add_index_page(hide="toc", icon="api")
    page += mk.MkAdmonition(DOC_TEXT, typ="tip")
    mknodes_docs = nav.add_doc(
        module=mk,
        filter_by___all__=True,
        class_page="docs/classpage_custom.jinja",
    )
    # now we collect the stuff we want to document.
    mknodes_docs.collect_classes(recursive=True)
