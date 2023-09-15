import inspect

import mknodes as mk

from mknodes.utils import classhelpers


INTRO_TEXT = """In this section you will find some information about the tree of nodes
 we built during the process."""

SECTION_CODE = "Code for this section"

nav = mk.MkNav("Internals")


def create_internals_section(root_nav: mk.MkNav):
    """Create the "Internals" Sub-MkNav and attach it to given MkNav."""
    root_nav += nav
    page = nav.add_index_page(hide_toc=True, icon="magnify")
    page += mk.MkCode.for_object(create_internals_section, header=SECTION_CODE)
    page += mk.MkAdmonition(INTRO_TEXT)


@nav.route.page("Tree", show_source=True, hide_toc=True, icon="graph")
def create_tree_page(page: mk.MkPage):
    """Create the "Tree" MkPage and attach it to given MkNav."""
    page += mk.MkHeader("This is the tree we built up to now.", level=3)
    tree = page.root.get_tree_repr(detailed=False, max_depth=3)
    page += mk.MkCode(tree, language="")


@nav.route.page("Requirements", hide_toc=True, icon="puzzle-edit", show_source=True)
def create_requirements_page(page: mk.MkPage):
    """Create the "Required extensions" MkPage and attach it to given MkNav."""
    page += mk.MkJinjaTemplate("requirements.md")


@nav.route.page("Build Log", show_source=True, hide_toc=True, icon="puzzle-edit")
def create_log_page(page: mk.MkPage):
    """Create the "Required extensions" MkPage and attach it to given MkNav."""
    page += mk.MkText("log() | MkCode", is_jinja_expression=True)


@nav.route.nav("Complete code", show_source=True)
def create_complete_code_section(nav: mk.MkNav):
    """Create the "Complete code" sub-MkNav and attach it to given MkNav."""
    from mknodes import manual

    nav.add_index_page(hide_toc=True, icon="octicons/code-24")
    for _module_name, module in inspect.getmembers(manual, inspect.ismodule):
        filename = module.__name__.split(".")[-1] + ".py"
        page = nav.add_page(filename, hide_toc=True)
        page += mk.MkCode.for_object(module, title=filename)
    example_page = nav.add_page("create_example_page methods")
    for kls in classhelpers.iter_subclasses(mk.MkNode):
        # iter_subclasses just calls __subclasses__ recursively.
        if "create_example_page" not in kls.__dict__:
            continue
        header = kls.__name__
        example_page += mk.MkCode.for_object(kls.create_example_page, header=header)
