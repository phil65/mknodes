import mknodes as mk


nav = mk.MkNav("Internals")

# - Clone repository (in case it is a remote one)
# - Aggregate information about repository from:

STEP_1 = "Clone the repository (in case it is a remote one)"
STEP_2 = "Aggregate information about the repository from:"
INFO_PROVIDERS = [
    "metadata.Distribution",
    "PyProject File",
    "MkDocs Config file",
    "Other config-related files",
    "Git info (aquired from GitPython)",
    "GitHub info (using PyGitHub)",
]
STEP_3 = "Build the MkNode tree based on Build script / function"
STEP_4 = "Populate mknodes-specific Jinja environment with all collected metadata"
STEP_5 = "Render jinja stuff with our own environment on node level"
STEP_6 = (
    "Convert node tree to a file folder structure containing markdown files (using"
    " literate-nav-style SUMMARY.md files to describe the hierarchy)"
)
STEP_7 = "Gather information from the nodes about required Extensions / CSS / JavaScript"
STEP_8 = "Merge node requirements with provided MkDocs config file"
STEP_9 = "Let mkdocs-literate-nav populate the Navigation based on generated SUMMARY.mds"
STEP_10 = "Let MkDocs convert everything to HTML based on the composite config"


def create_internals_section(root_nav: mk.MkNav):
    """Create the "Internals" Sub-MkNav and attach it to given MkNav."""
    root_nav += nav
    page = nav.add_index_page(hide="toc")
    node = mk.MkTimeline()
    node.add_item(date="Step 1", content=STEP_1)
    ls = mk.MkList(INFO_PROVIDERS)
    node.add_item(
        date="Step 2",
        content=mk.MkContainer([STEP_2, ls], header="#### Aggregate info from:"),
    )
    node.add_item(date="Step 3", content=STEP_3)
    node.add_item(date="Step 4", content=STEP_4)
    node.add_item(date="Step 5", content=STEP_5)
    node.add_item(date="Step 6", content=STEP_6)
    node.add_item(date="Step 7", content=STEP_7)
    node.add_item(date="Step 8", content=STEP_8)
    node.add_item(date="Step 9", content=STEP_9)
    node.add_item(date="Step 10", content=STEP_10)
    page += node
    page.created_by = create_internals_section


# @nav.route.page("Tree", hide="toc", icon="graph")
# def create_tree_page(page: mk.MkPage):
#     page += mk.MkHeader("This is the tree we built up to now.", level=3)
#     tree = page.root.get_tree_repr(detailed=False, max_depth=3)
#     page += mk.MkCode(tree, language="")


@nav.route.page("Requirements", hide="toc", icon="puzzle-edit")
def create_requirements_page(page: mk.MkPage):
    page += mk.MkJinjaTemplate("requirements.md")


@nav.route.page("Build Log", hide="toc", icon="puzzle-edit")
def create_log_page(page: mk.MkPage):
    page += mk.MkText("log() | MkCode", is_jinja_expression=True)


@nav.route.nav("Complete code")
def create_complete_code_section(nav: mk.MkNav):
    nav.parse.module("mknodes/manual/", hide="toc")
