import mknodes as mk


INTRO_TEXT = """In this section you will find some information about the tree of nodes
 we built during the process."""

SECTION_CODE = "Code for this section"

nav = mk.MkNav("Internals")


def create_internals_section(root_nav: mk.MkNav):
    """Create the "Internals" Sub-MkNav and attach it to given MkNav."""
    root_nav += nav
    page = nav.add_index_page(hide="toc")
    page += INTRO_TEXT
    page += mk.MkCode.for_object(create_internals_section, header=SECTION_CODE)


@nav.route.page("Tree", show_source=True, hide="toc", icon="graph")
def create_tree_page(page: mk.MkPage):
    """Create the "Tree" MkPage and attach it to given MkNav."""
    page += mk.MkHeader("This is the tree we built up to now.", level=3)
    tree = page.root.get_tree_repr(detailed=False, max_depth=3)
    page += mk.MkCode(tree, language="")


@nav.route.page("Requirements", hide="toc", icon="puzzle-edit", show_source=True)
def create_requirements_page(page: mk.MkPage):
    """Create the "Required extensions" MkPage and attach it to given MkNav."""
    page += mk.MkJinjaTemplate("requirements.md")


@nav.route.page("Build Log", show_source=True, hide="toc", icon="puzzle-edit")
def create_log_page(page: mk.MkPage):
    """Create the "Required extensions" MkPage and attach it to given MkNav."""
    page += mk.MkText("log() | MkCode", is_jinja_expression=True)


@nav.route.nav("Complete code", show_source=True)
def create_complete_code_section(nav: mk.MkNav):
    """Create the "Complete code" sub-MkNav and attach it to given MkNav."""
    nav.parse.module("mknodes/manual/", hide="toc")
