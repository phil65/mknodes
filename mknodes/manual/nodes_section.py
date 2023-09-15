import os

import mknodes as mk

from mknodes import paths


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
NODE_PAGE_TEXT = "Code for each MkNode page"
ANNOTATIONS_INFO = """It is always best to use annotations from the *closest* node.
(We could also have used the annotations from MKPage, but since this source code
is displayed by the MkCode node, we use that one.)"""


nav = mk.MkNav("The nodes")


def create_nodes_section(root_nav: mk.MkNav):
    """Add the complete "The Nodes" section to given MkNav."""
    # Basic structure: Theres one root MkNav, MkNavs can contain MkPages and other MkNavs,
    # MkPages contain more atomic MkNodes, like MkText, MkTable, and MkDiagrams.
    # These markup nodes in some cases can contain other Markup nodes.
    # It`s all one big tree.

    # first we create the menu on the left:
    root_nav += nav
    # and then we create the index page (the page you are lookin at right now)

    page = nav.add_index_page(hide_toc=True, icon="graph")
    page += mk.MkCode.for_object(create_nodes_section, header=SECTION_CODE)
    page += mk.MkDetailsBlock(INTRO_TEXT, expand=True)
    page += mk.MkHeader("All the nodes")
    page += mk.MkClassDiagram(mk.MkNode, mode="subclasses", direction="LR", max_depth=3)


def create_section_for_nodes(
    nav: mk.MkNav,
    klasses: list[type[mk.MkNode]],
) -> mk.MkTable:
    """Add a MkPage to the MkNav for each class, create a index MkTable and return it."""
    table = mk.MkTable(columns=["Node", "Docstrings", "Markdown extensions"])
    for kls in klasses:
        # iter_subclasses just calls __subclasses__ recursively.
        if "create_example_page" in kls.__dict__:
            # All MkNode classes carry some metadata, like ICON or REQUIRED_EXTENSIONS.
            # We can use that for building the docs.
            page = nav.add_page(kls.__name__, icon=kls.ICON)
            create_class_page(kls, page)
            link = mk.MkLink(page, kls.__name__, icon=kls.ICON)
            extensions = ", ".join(f"`{i}`" for i in kls.REQUIRED_EXTENSIONS)
            table.add_row((link, kls.__doc__, extensions))
    return table


def create_class_page(kls: type[mk.MkNode], page: mk.MkPage):
    """Create a MkPage with example code for given klass."""
    # Each example page will begin by displaying the code used to create the page.
    page += mk.MkCode.for_object(kls.create_example_page, extract_body=True)
    # page += mk.MkHeader(kls.__doc__.split("\n")[0])
    page += "## Examples"
    if kls.STATUS == "new":  # some classes are marked as "new"
        page.status = "new"  # we use that info to display an icon in the menu.
    kls.create_example_page(page)
    if kls.CSS:
        path = paths.RESOURCES / kls.CSS
        text = path.read_text()
        css_code = mk.MkCode(text, language="css")
        page += mk.MkDetailsBlock(css_code, title="Required CSS")
    code = mk.MkCode.for_object(
        create_class_page,
        extract_body=True,
    )
    admonition = mk.MkDetailsBlock(
        code,
        typ="quote",
        title=code.title,
        header="Code for the subsections",
    )
    page += admonition


@nav.route.nav("Base nodes", show_source=True)
def create_basic_nodes_section(nav: mk.MkNav):
    """Add a sub-MkNav containing all base node pages to given MkNav."""
    klasses = [
        mk.MkNode,
        mk.MkText,
        mk.MkHeader,
        mk.MkCritic,
        mk.MkLink,
        mk.MkKeys,
        mk.MkProgressBar,
        mk.MkImage,
        mk.MkBadge,
        mk.MkBinaryImage,
        mk.MkCard,
        mk.MkSpeechBubble,
        mk.MkJinjaTemplate,
    ]
    page = nav.add_index_page(hide_toc=True)
    page += create_section_for_nodes(nav, klasses)
    code = mk.MkCode.for_object(create_section_for_nodes)
    page += mk.MkAdmonition(code, title=NODE_PAGE_TEXT, collapsible=True, typ="quote")


@nav.route.nav("Container nodes", show_source=True)
def create_container_nodes_section(nav: mk.MkNav):
    """Add a sub-MkNav containing all template node pages to given MkNav."""
    klasses = [
        mk.MkBlockQuote,
        mk.MkAdmonition,
        mk.MkContainer,
        mk.MkGrid,
        mk.MkCode,
        mk.MkList,
        mk.MkTable,
        mk.MkHtmlTable,
        mk.MkDefinitionList,
        # mk.MkTab,
        mk.MkTabbed,
        mk.MkAnnotations,
        mk.MkFootNotes,
        mk.MkShowcase,
        mk.MkTaskList,
    ]
    page = nav.add_index_page(hide_toc=True)
    page += create_section_for_nodes(nav, klasses)
    code = mk.MkCode.for_object(create_section_for_nodes)
    page += mk.MkAdmonition(code, title=NODE_PAGE_TEXT, collapsible=True, typ="quote")


@nav.route.nav("Presentation nodes", show_source=True)
def create_presentation_nodes_section(nav: mk.MkNav):
    """Add a sub-MkNav containing all template node pages to given MkNav."""
    klasses = [
        mk.MkTreeView,
        mk.MkPrettyPrint,
        mk.MkReprRawRendered,
        mk.MkCodeImage,
        mk.MkDiagram,
    ]
    page = nav.add_index_page(hide_toc=True)
    page += create_section_for_nodes(nav, klasses)
    code = mk.MkCode.for_object(create_section_for_nodes)
    page += mk.MkAdmonition(code, title=NODE_PAGE_TEXT, collapsible=True, typ="quote")


@nav.route.nav("Documentation nodes", show_source=True)
def create_documentation_nodes_section(nav: mk.MkNav):
    """Add a sub-MkNav containing all template node pages to given MkNav."""
    klasses = [
        mk.MkClassDiagram,
        mk.MkDocStrings,
        mk.MkCommentedCode,
        mk.MkConfigSetting,
        mk.MkClassTable,
        mk.MkModuleTable,
        mk.MkPluginFlow,
        mk.MkArgParseHelp,
        mk.MkClickDoc,
    ]
    page = nav.add_index_page(hide_toc=True)
    page += create_section_for_nodes(nav, klasses)
    code = mk.MkCode.for_object(create_section_for_nodes)
    page += mk.MkAdmonition(code, title=NODE_PAGE_TEXT, collapsible=True, typ="quote")


@nav.route.nav("About-the-project nodes", show_source=True)
def create_about_nodes_section(nav: mk.MkNav):
    """Add a sub-MkNav containing all template node pages to given MkNav."""
    klasses = [
        mk.MkChangelog,
        mk.MkCodeOfConduct,
        mk.MkLicense,
        mk.MkDependencyTable,
        mk.MkInstallGuide,
        mk.MkCommitConventions,
        mk.MkPullRequestGuidelines,
        mk.MkDevEnvSetup,
        mk.MkDevTools,
        mk.MkShields,
        mk.MkMetadataBadges,
        mk.MkModuleOverview,
    ]
    if os.environ.get("CI"):
        klasses.append(mk.MkPyDeps)
    page = nav.add_index_page(hide_toc=True)
    page += create_section_for_nodes(nav, klasses)
    code = mk.MkCode.for_object(create_section_for_nodes)
    page += mk.MkAdmonition(code, title=NODE_PAGE_TEXT, collapsible=True, typ="quote")


@nav.route.nav("Special nodes", show_source=True)
def create_special_nodes_section(nav: mk.MkNav):
    """Add a sub-MkNav containing all template node pages to given MkNav."""
    klasses = [mk.MkSnippet, mk.MkInclude, mk.MkIFrame, mk.MkCommandOutput, mk.MkCallable]
    page = nav.add_index_page(hide_toc=True)
    page += create_section_for_nodes(nav, klasses)
    code = mk.MkCode.for_object(create_section_for_nodes)
    page += mk.MkAdmonition(code, title=NODE_PAGE_TEXT, collapsible=True, typ="quote")


@nav.route.nav("Block nodes", show_source=True)
def create_block_nodes_section(nav: mk.MkNav):
    """Add a sub-MkNav containing all template node pages to given MkNav."""
    klasses = [
        mk.MkBlock,
        mk.MkAdmonitionBlock,
        mk.MkDetailsBlock,
        mk.MkHtmlBlock,
        mk.MkTabbedBlocks,
    ]
    page = nav.add_index_page(hide_toc=True)
    page += create_section_for_nodes(nav, klasses)
    code = mk.MkCode.for_object(create_section_for_nodes)
    page += mk.MkAdmonition(code, title=NODE_PAGE_TEXT, collapsible=True, typ="quote")
