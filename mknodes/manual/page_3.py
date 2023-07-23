from __future__ import annotations

import inspect
import pprint

import mknodes


INTRO_TEXT = """Lets show some info about the tree we built.
The tree starts from the root nav down to the Markup elements.
"""


def create_page_3(root_nav: mknodes.MkNav):
    internals_nav = root_nav.add_nav("Internals")

    overview = internals_nav.add_page("Overview", hide_toc=True)
    overview += INTRO_TEXT

    # we are here right now.
    overview.add_code(inspect.getsource(create_page_3))

    # the "Tree" section in the left sidebar shows what we have done up to now.
    # we create a new page and add a formatted represenation of our Tree.

    tree_page = internals_nav.add_page("Tree", hide_toc=True)
    tree_page.add_header("This is the tree we built up to now.", level=3)
    lines = [f"{level * '    '} {node!r}" for level, node in root_nav.iter_nodes()]
    tree_page += mknodes.MkCode("\n".join(lines))

    # Each tree item can carry virtual files. Lets dispay all files which are currently
    # attached to the tree:
    files_page = internals_nav.add_page("File map", hide_toc=True)
    files_page.add_header("These are the 'virtual' files attached to the tree:", level=3)
    virtual_files = root_nav.all_virtual_files()
    file_txt = pprint.pformat(list(virtual_files.keys()))
    files_page += mknodes.MkCode(file_txt)
    # print(nodes_nav.to_tree_graph())


if __name__ == "__main__":
    nav = mknodes.MkNav()
    create_page_3(nav)
    print(nav.children[0])
