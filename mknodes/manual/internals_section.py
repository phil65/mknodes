import pprint

import mknodes


INTRO_TEXT = """Lets show some info about the tree we built.
The tree starts from the root nav down to the Markup elements.
"""


def create_internals_section(root_nav: mknodes.MkNav):
    internals_nav = root_nav.add_nav("Internals")

    overview = internals_nav.add_index_page(hide_toc=True, icon="material/magnify")
    overview += INTRO_TEXT
    overview += mknodes.MkCode.for_object(create_internals_section)

    # the "Tree" section in the left sidebar shows what we have done up to now.
    create_tree_page(internals_nav)
    # Each tree item can carry virtual files.
    # Lets dispay all files which are currently attached to the tree:
    create_file_tree_page(internals_nav)
    create_code_page(internals_nav)


def create_tree_page(nav):
    # we create a new page and add a formatted represenation of our Tree.

    page = nav.add_page("Tree", hide_toc=True, icon="material/graph")
    page += mknodes.MkCode.for_object(create_tree_page)
    page.add_header("This is the tree we built up to now.", level=3)
    lines = [f"{level * '    '} {node!r}" for level, node in nav.root.iter_nodes()]
    page += mknodes.MkCode("\n".join(lines))


def create_file_tree_page(nav):
    page = nav.add_page("Files", hide_toc=True, icon="material/file-tree-outline")
    page += mknodes.MkCode.for_object(create_file_tree_page)
    page.add_header("These are the 'virtual' files attached to the tree:", level=3)
    # we want to see all files, so we have to go through the root nav:
    virtual_files = nav.root.all_virtual_files()
    file_txt = pprint.pformat(list(virtual_files.keys()))
    page += mknodes.MkCode(file_txt)


def create_code_page(nav):
    # we create a new page and add a formatted represenation of our Tree.
    from mknodes import manual

    code_nav = nav.add_nav("Complete code")
    index_page = code_nav.add_index_page(hide_toc=True, icon="octicons/code-24")
    index_page += mknodes.MkCode.for_object(create_code_page)
    for module in [
        manual.root,
        manual.nodes_section,
        manual.doc_section,
        manual.internals_section,
        manual.dev_section,
    ]:
        filename = module.__name__.split(".")[-1] + ".py"
        page = code_nav.add_page(filename, hide_toc=True)
        page += mknodes.MkCode.for_object(module, title=filename)
