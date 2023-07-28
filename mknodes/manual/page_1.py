from __future__ import annotations

import mknodes

from mknodes.utils import classhelpers


INTRO_TEXT = """
Basically everything interesting in this library inherits from MkNode.
It`s the base class for all tree nodes we are building. The tree goes from the root nav
down to single markup elements. We can show the subclass tree by using
the MkClassDiagram Node.
"""


def create_nodes_section(root_nav: mknodes.MkNav):
    # Basic structure: Theres one root nav, navs can contain pages and other navs,
    # pages contain more atomic markup nodes, like text, tables, and diagrams.
    # These markup nodes in some cases can contain other Markup nodes.
    # It`s all one big tree.

    home_nav = root_nav.add_nav("The nodes")
    overview = home_nav.add_index_page("Overview", hide_toc=True)

    # this here is what you are reading right now.
    overview += mknodes.MkCode.for_object(create_nodes_section)
    nodes_nav = home_nav.add_nav("Nodes")

    # for convenience, we can add strings directly to pages.
    # they will get converted to a mknodes.Text node.
    overview += INTRO_TEXT
    create_subclass_page(home_nav)

    # let`s take a look at some of the mentioned Markup nodes.
    # Some of them have a `examples` classmethod which yields some example signatures
    #  to show the functionality.
    for kls in classhelpers.iter_subclasses(mknodes.MkNode):
        # iter_subclasses just calls __subclasses__ recursively.
        if "create_example_page" in kls.__dict__:
            subpage = nodes_nav.add_page(kls.__name__)
            subpage += "## Code for this page"
            subpage += mknodes.MkCode.for_object(
                kls.create_example_page,
                extract_body=True,
            )
            subpage += "## Output"
            kls.create_example_page(subpage)


def create_subclass_page(nav: mknodes.MkNav):
    # Lets take a look at the relations of the included nodes.
    # It`s easy to show different diagrams for classes.
    subcls_page = nav.add_page("Subclass tree", hide_toc=True)
    subcls_page += mknodes.MkCode.for_object(create_subclass_page)
    subcls_page += mknodes.MkClassDiagram(
        mknodes.MkNode,
        mode="subclass_tree",
        orientation="LR",
    )


if __name__ == "__main__":
    nav = mknodes.MkNav()
    create_nodes_section(nav)
    print(nav.children[0])
