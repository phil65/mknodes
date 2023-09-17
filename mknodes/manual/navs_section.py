import mknodes as mk

from mknodes import paths
from mknodes.manual import routing
from mknodes.project import Project


DOC_TEXT = """Now lets create the documentation.
This code will show how to build a simple documentation section.
"""

INTRO_TEXT = """
Basically everything interesting in this library inherits from MkNode.
It`s the base class for all tree nodes we are building. The tree goes from the root nav
down to single markup elements. We can show the subclass tree by using
the MkClassDiagram Node.
"""

MKPAGE_TIP = "MkPages can also be loaded from files by using MkPage.from_file"

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"

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
    page += mk.MkAdmonition(MKPAGE_TIP, typ="tip")

    # and then we create the index page (the page you are lookin at right now)

    page = nav.add_index_page(hide="toc")
    page += mk.MkCommentedCode(create_navs_section, header=SECTION_CODE)
    page += mk.MkDetailsBlock(INTRO_TEXT, expand=True)
    page += mk.MkHeader("All the navs")
    page += mk.MkClassDiagram(mk.MkNav, mode="subclasses", direction="LR", max_depth=3)
    # A nav section corresponds to a `SUMMARY.md`. You can see that when stringifying it.
    text = str(nav)
    text = text.replace("](", "] (")  ##
    page += mk.MkCode(text, header="The resulting MkNav")


@nav.route.nav("From file", show_source=True)
def create_from_file_section(nav: mk.MkNav):
    """Load an existing SUMMARY.md and attach it to given MkNav."""
    # We will now demonstate loading an existing Nav tree.

    # This path contains Markdown files/ folders and a pre-populated SUMMARY.md.
    folder = paths.TEST_RESOURCES / "nav_tree/"  # Folder content: # (1)
    summary_file = folder / "SUMMARY.md"  # File content: # (2)

    # We will load it as an MkNav...
    nav.parse.file(summary_file, hide="toc")

    # Finally, the page you are seeing right now.
    page = nav.add_index_page(hide="toc", icon="file")

    text = summary_file.read_text()
    text = text.replace("](", "] (")  ##
    # we are wrapping some annotations with Admonitions, that seems to help
    # with nesting / escaping issues in some cases (and it looks nice!).
    path = paths.TEST_RESOURCES / "nav_tree/"
    tree_node = mk.MkTreeView(path, header="Directory tree")
    page += mk.MkAdmonition(tree_node)
    file_content_node = mk.MkCode(text, header="SUMMARY.md content")
    page += mk.MkAdmonition(file_content_node)
    page += ANNOTATIONS_INFO

    # we could also add the annotiation nodes to the page of course:
    page += tree_node
    page += file_content_node


@nav.route.nav("From folder", show_source=True)
def create_from_folder_section(nav: mk.MkNav):
    """Create a MkNav based on a folder tree containing markup files."""
    # We are using a part of the previous nav tree. It's a subfolder without a SUMMARY.md.
    folder = paths.TEST_RESOURCES / "nav_tree/test_folder/"
    nav.parse.folder(folder, hide="toc")

    # Finally, create the index page.
    page = nav.add_index_page(hide="toc", icon="folder")
    page += mk.MkTreeView(folder)
    page += mk.MkDocStrings(mk.MkTreeView)


@pages_nav.route.page("MkClassPage", show_source=True)
def create_mkclasspage_page(page: mk.MkPage):
    class_page = mk.MkClassPage(mk.MkCode, inclusion_level=False)
    page += mk.MkReprRawRendered(class_page)


@pages_nav.route.page("MkModulePage", show_source=True)
def create_mkmodulepage_page(page: mk.MkPage):
    import mkdocs.config

    module_page = mk.MkModulePage(mkdocs.config, inclusion_level=False)
    page += mk.MkReprRawRendered(module_page)


@pages_nav.route.page(
    "Adding to MkPages",
    hide="toc, nav",
    status="new",
    show_source=True,
)
def create_adding_to_mkpages_page(page: mk.MkPage):
    """Create the "Adding to MkPages" MkPage and attach it to given MkNav."""
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
    show_source=True,
)
def create_metadata_page(page: mk.MkPage):
    """Create the "Metadata" MkPage and attach it to given nav."""
    # page.metadata is a dataclass, we can prettyprint these with MkPrettyPrint.
    page += mk.MkPrettyPrint(page.metadata)
    page += mk.MkHtmlBlock(str(page))


def create_mkdefaultwebsite_section(nav: mk.MkNav):
    """Create the "MkDefaultWebsite" sub-MkNav and attach it to given nav."""
    proj = Project.for_path("https://github.com/mkdocstrings/mkdocstrings.git")
    website_nav = mk.MkDefaultWebsite(section="MkDocStrings", project=proj)
    nav += website_nav


@nav.route.nav("MkDoc", show_source=True)
def create_mkdoc_section(nav: mk.MkNav):
    """Create the "Metadata" sub-MkNav and attach it to given nav."""
    nav = nav.add_nav("MkDoc")

    page = nav.add_index_page(hide="toc", icon="api")
    page += mk.MkAdmonition(DOC_TEXT, typ="tip")
    page.env.add_template("docs/classpage_custom.jinja")
    mknodes_docs = nav.add_doc(
        module=mk,
        filter_by___all__=True,
        class_page="docs/classpage_custom.jinja",
    )
    # now we collect the stuff we want to document.
    mknodes_docs.collect_classes(recursive=True)
