from __future__ import annotations

import inspect

import mknodes

from mknodes import classhelpers, utils


INTRO_TEXT = """
Basically everything interesting in this library inherits from MkNode.
It`s the base class for all tree nodes we are building. The tree goes from the root nav
down to single markup elements. We can show the subclass tree by using
the MkClassDiagram Node.
"""


def create_page_1(root_nav: mknodes.Nav):
    # Basic structure: Theres one root nav, navs can contain pages and other navs,
    # pages contain more atomic markup nodes, like text, tables, and diagrams.
    # These markup nodes in some cases can contain other Markup nodes.
    # It`s all one big tree.

    home_nav = root_nav.add_nav("User guide")
    overview = home_nav.add_page("Overview", hide_toc=True)

    # this here is what you are reading right now.
    overview.add_code(inspect.getsource(create_page_1))
    nodes_nav = home_nav.add_nav("Nodes")

    # for convenience, we can add strings directly to pages.
    # they will get converted to a mknodes.Text node.
    overview += INTRO_TEXT

    # Lets take a look at the relations of the included nodes.
    # It`s easy to show different diagrams for classes.
    subcls_page = home_nav.add_page("Subclass tree", hide_toc=True)
    subcls_page += mknodes.ClassDiagram(
        mknodes.MkNode, mode="subclass_tree", orientation="RL"
    )
    # let`s take a look at some of the mentioned Markup nodes.
    # Some of them have a `examples` classmethod which yields some example signatures
    #  to show the functionality.
    for kls in classhelpers.get_subclasses(mknodes.MkNode):
        # get_subclasses just calls __subclasses__ recursively.
        subpage = nodes_nav.add_page(kls.__name__)
        if hasattr(kls, "examples"):
            subpage += mknodes.Code.for_object(kls.examples, header="Our combinations")
            for i, sig in enumerate(kls.examples(), start=1):
                subpage.add_header(f"Example {i} for class {kls.__name__!r}", level=2)
                sig_txt = utils.format_kwargs(sig)
                text = f"node = mknodes.{kls.__name__}({sig_txt})\nstr(node)"
                subpage.add_code(code=text, title=f"example_{i}.py")
                node = kls(**sig)
                code = mknodes.Code(language="md", code=node, title=f"result_{i}.md")
                subpage.add_tabs({"Preview": str(node), "Generated markdown": str(code)})
                subpage.add_newlines(3)
        subpage.add_mkdocstrings(kls)
