import os

import mknodes as mk


BASE_NODES = [
    mk.MkNode,
    mk.MkText,
    mk.MkHeader,
    mk.MkCompactAdmonition,
    mk.MkCritic,
    mk.MkLink,
    mk.MkKeys,
    mk.MkProgressBar,
    mk.MkSpeechBubble,
    mk.MkTemplate,
]

IMAGE_NODES = [
    mk.MkImage,
    mk.MkImageCompare,
    mk.MkImageSlideshow,
    mk.MkBadge,
    mk.MkIcon,
    mk.MkMaterialBadge,
    mk.MkBinaryImage,
    mk.MkCard,
]

PRESENTATION_NODES = [
    mk.MkTreeView,
    mk.MkPrettyPrint,
    mk.MkReprRawRendered,
    mk.MkDiagram,
    mk.MkTimeline,
]

DOCUMENTATION_NODES = [
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

ABOUT_THE_PROJECT_NODES = [
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
    mk.MkPipDepTree,
]

if os.environ.get("CI"):
    ABOUT_THE_PROJECT_NODES.append(mk.MkPyDeps)

CONTAINER_NODES = [
    mk.MkBlockQuote,
    mk.MkAdmonition,
    mk.MkContainer,
    # mk.MkGrid,
    mk.MkCode,
    mk.MkList,
    mk.MkTable,
    mk.MkHtmlTable,
    mk.MkDefinitionList,
    mk.MkDetailsBlock,
    mk.MkHtmlBlock,
    mk.MkTabbedBlocks,
    mk.MkTabbed,
    mk.MkAnnotations,
    mk.MkFootNotes,
    mk.MkShowcase,
    mk.MkTaskList,
]

SPECIAL_NODES = [mk.MkInclude, mk.MkIFrame, mk.MkCommandOutput, mk.MkCallable]


def create_section_for_nodes(
    nav: mk.MkNav,
    klasses: list[type[mk.MkNode]],
) -> mk.MkTable:
    table = mk.MkTable(columns=["Node", "Docstrings", "Markdown extensions"])
    for kls in klasses:
        if "create_example_page" in kls.__dict__:
            page = nav.add_page(kls.__name__, icon=kls.ICON)
            create_class_page(kls, page)
            link = mk.MkLink(page, kls.__name__, icon=kls.ICON)
            extensions = ", ".join(f"`{i}`" for i in kls.REQUIRED_EXTENSIONS)
            table.add_row((link, kls.__doc__, extensions))
    return table


def create_class_page(kls: type[mk.MkNode], page: mk.MkPage):
    page += mk.MkCode.for_object(kls.create_example_page, extract_body=True)
    page += "## Examples"
    if kls.STATUS:
        page.metadata.status = kls.STATUS
    elif kls.JS_FILES:
        page.metadata.status = "js"
    elif kls.CSS:
        page.metadata.status = "css"
    kls.create_example_page(page)
    page.created_by = create_class_page


nav = mk.MkNav("The nodes")


@nav.route.page(is_index=True)
def _(page: mk.MkPage):
    page += mk.MkTemplate("nodes_index.jinja")


@nav.route.nav("Base nodes")
def _(nav: mk.MkNav):
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, BASE_NODES)
    page.created_by = create_section_for_nodes


@nav.route.nav("Image nodes")
def _(nav: mk.MkNav):
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, IMAGE_NODES)
    page.created_by = create_section_for_nodes


@nav.route.nav("Container nodes")
def _(nav: mk.MkNav):
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, CONTAINER_NODES)
    page.created_by = create_section_for_nodes


@nav.route.nav("Presentation nodes")
def _(nav: mk.MkNav):
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, PRESENTATION_NODES)
    page.created_by = create_section_for_nodes


@nav.route.nav("Documentation nodes")
def _(nav: mk.MkNav):
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, DOCUMENTATION_NODES)
    page.created_by = create_section_for_nodes


@nav.route.nav("About-the-project nodes")
def _(nav: mk.MkNav):
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, ABOUT_THE_PROJECT_NODES)
    page.created_by = create_section_for_nodes


@nav.route.nav("Special nodes")
def _(nav: mk.MkNav):
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, SPECIAL_NODES)
    page.created_by = create_section_for_nodes
