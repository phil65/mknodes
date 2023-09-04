import inspect

import mknodes

from mknodes.utils import classhelpers


INTRO_TEXT = """In this section you will find some information about the tree of nodes
 we built during the process."""

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"


def create_internals_section(root_nav: mknodes.MkNav):
    """Create the "Internals" Sub-MkNav and attach it to given MkNav."""
    internals_nav = root_nav.add_nav("Internals")

    page = internals_nav.add_index_page(hide_toc=True, icon="material/magnify")
    page += mknodes.MkCode.for_object(create_internals_section, header=SECTION_CODE)
    page += mknodes.MkAdmonition(INTRO_TEXT)

    # the "Tree" section in the left sidebar shows what we have done up to now.
    create_tree_page(internals_nav)
    # Each tree item can carry virtual files.
    # Lets dispay all files which are currently attached to the tree:
    create_requirements_page(internals_nav)
    create_complete_code_section(internals_nav)


def create_tree_page(nav: mknodes.MkNav):
    """Create the "Tree" MkPage and attach it to given MkNav."""
    page = nav.add_page("Tree", hide_toc=True, icon="material/graph")
    page += mknodes.MkCode.for_object(create_tree_page, header=PAGE_CODE)
    page += mknodes.MkHeader("This is the tree we built up to now.", level=3)
    page += mknodes.MkTreeView(nav.root)


def create_requirements_page(nav: mknodes.MkNav):
    """Create the "Required extensions" MkPage and attach it to given MkNav."""
    page = nav.add_page("Requirements", hide_toc=True, icon="material/puzzle-edit")
    page += mknodes.MkCode.for_object(create_requirements_page, header=PAGE_CODE)
    page += mknodes.MkJinjaTemplate("requirements.md")


def create_complete_code_section(nav: mknodes.MkNav):
    """Create the "Complete code" sub-MkNav and attach it to given MkNav."""
    from mknodes import manual

    code_nav = nav.add_nav("Complete code")
    index = code_nav.add_index_page(hide_toc=True, icon="octicons/code-24")
    index += mknodes.MkCode.for_object(create_complete_code_section, header=SECTION_CODE)
    for _module_name, module in inspect.getmembers(manual, inspect.ismodule):
        filename = module.__name__.split(".")[-1] + ".py"
        page = code_nav.add_page(filename, hide_toc=True)
        page += mknodes.MkCode.for_object(module, title=filename)
    example_page = code_nav.add_page("create_example_page methods")
    for kls in classhelpers.iter_subclasses(mknodes.MkNode):
        # iter_subclasses just calls __subclasses__ recursively.
        if "create_example_page" not in kls.__dict__:
            continue
        header = kls.__name__
        example_page += mknodes.MkCode.for_object(kls.create_example_page, header=header)
