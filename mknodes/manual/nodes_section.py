import mknodes

from mknodes.utils import classhelpers


INTRO_TEXT = """
Basically everything interesting in this library inherits from MkNode.
It`s the base class for all tree nodes we are building. The tree goes from the root nav
down to single markup elements. We can show the subclass tree by using
the MkClassDiagram Node.
"""

SECTION_CODE = "Code for this section"
PAGE_CODE = "Code for this page"


def create_nodes_section(root_nav: mknodes.MkNav):
    # Basic structure: Theres one root MkNav, MkNavs can contain MkPages and other MkNavs,
    # MkPages contain more atomic MkNodes, like MkText, MkTable, and MkDiagrams.
    # These markup nodes in some cases can contain other Markup nodes.
    # It`s all one big tree.

    nodes_nav = root_nav.add_nav("The nodes")
    overview = nodes_nav.add_index_page(hide_toc=True, icon="material/graph")

    # this here is what you are reading right now.
    overview += mknodes.MkCode.for_object(create_nodes_section, header=SECTION_CODE)
    overview += mknodes.MkDetailsBlock(INTRO_TEXT, expand=True)
    create_nodes_subsection(nodes_nav)
    create_subclass_page(nodes_nav)


def create_nodes_subsection(nav: mknodes.MkNav):
    nodes_nav = nav.add_nav("Nodes")
    # let`s take a look at some of the mentioned Markup nodes.
    # we will now iter all node classes, create a small page (which is part of the menu)
    # and put that page as a link into a table, combined with docstrings.
    table = mknodes.MkTable(columns=["Node", "Docstrings"])
    for kls in classhelpers.iter_subclasses(mknodes.MkNode):
        # iter_subclasses just calls __subclasses__ recursively.
        if "create_example_page" in kls.__dict__:
            page = nodes_nav.add_page(kls.__name__)
            create_class_page(kls, page)
            link = mknodes.MkLink(page, kls.__name__)
            table.add_row((link, kls.__doc__))
    page = nodes_nav.add_index_page(hide_toc=True)
    page += mknodes.MkCode.for_object(create_nodes_subsection, header=SECTION_CODE)
    page += table


def create_class_page(kls: type, page: mknodes.MkPage):
    # Each example page will begin by displaying the code used to create the page.
    page += mknodes.MkCode.for_object(
        create_class_page,
        extract_body=True,
        header=PAGE_CODE,
    )
    page += mknodes.MkCode.for_object(kls.create_example_page, extract_body=True)
    # and afterwards, we show what was added to the page.
    page += "## Output"
    kls.create_example_page(page)


def create_subclass_page(nav: mknodes.MkNav):
    # Lets take a look at the relations of the included nodes.
    # It`s easy to show different diagrams for classes.
    subcls_page = nav.add_page("Subclass tree", hide_toc=True)
    subcls_page += mknodes.MkCode.for_object(create_subclass_page, header=PAGE_CODE)
    subcls_page += mknodes.MkClassDiagram(
        mknodes.MkNode,
        mode="subclass_tree",
        orientation="LR",
    )
