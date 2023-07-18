"""Generate the code reference pages and navigation."""

from __future__ import annotations

import pathlib
import pprint

import mknodes
from mknodes import classhelpers, utils


root_nav = mknodes.Nav()
page = mknodes.MkPage(path="index.md", hide_toc=True, hide_nav=True)
page.add_header("Not in the mood to write documentation? Let´s code it then!", level=3)
page.add_admonition(
    "API is still evolving, so consider this a preview.", typ="danger", title="Warning!"
)
page += "This is the source code for building this website:"
page.add_code(pathlib.Path(__file__).read_text(), language="py")
# page.add_code(str(page), language="markup")
page.write()


# now lets create the documentation. This is the "manual way" by building custom pages.
home_nav = root_nav.add_nav("User guide")
nodes_nav = home_nav.add_nav("Nodes")
# Basically everything interesting in this library inherits from MkNode.
# It´s the base class for all tree nodes we are building. The tree goes from the root nav
# down to single markup elements. We can show the subclass tree by using
# the MkClassDiagram Node.
subcls_page = home_nav.add_page("Subclass tree")
subcls_page += mknodes.ClassDiagram(
    mknodes.MkNode, mode="subclass_tree", orientation="RL"
)
for kls in classhelpers.get_subclasses(mknodes.MkNode):
    # get_subclasses just calls __subclasses__ recursively.
    subpage = nodes_nav.add_page(kls.__name__)
    if hasattr(kls, "examples"):
        subpage += mknodes.Code.for_object(kls.examples, header="Our combinations")
        # "examples()" yields dicts with constructor keyword arguments for building examples.
        for i, sig in enumerate(kls.examples(), start=1):
            subpage.add_header(f"Example {i} for class {kls.__name__!r}", level=2)
            sig_txt = utils.format_kwargs(sig)
            text = f"node = mknodes.{kls.__name__}({sig_txt})\nstr(node)"
            subpage.add_code(language="py", code=text, title=f"example_{i}.py")
            node = kls(**sig)
            code = mknodes.Code(language="md", code=node, title=f"result_{i}.md")
            subpage.add_tabs({"Preview": str(node), "Generated markdown": str(code)})
            subpage.add_newlines(3)
    subpage.add_mkdocstrings(kls)

# We could also add docs for random other modules, too. Lets document the std library.
std_lib_nav = root_nav.add_nav("std_library")
for stdlib_mod in ["pathlib", "inspect", "logging"]:
    docs = std_lib_nav.add_documentation(module=stdlib_mod)
    for klass in docs.iter_classes(recursive=True):
        docs.add_class_page(klass=klass)

# Lets show some info about the tree we built.
# The tree starts from the root nav down to the Markup elements.
tree_page = root_nav.add_page("Node tree", hide_toc=True, hide_nav=True)
tree_page.add_header("This is the tree we built up to now.", level=3)
lines = [f"{indent * '    '} {repr(node)}" for indent, node in root_nav.yield_nodes()]
tree_page += mknodes.Code(language="py", code="\n".join(lines))
# tree_page += nodes_nav.to_tree_graph(orientation="LR")
virtual_files = root_nav.all_virtual_files()
files_page = root_nav.add_page("File map", hide_toc=True, hide_nav=True)
files_page.add_header("These are the 'virtual' files attached to the tree:", level=3)
file_txt = pprint.pformat(list(virtual_files.keys()))
files_page += mknodes.Code(language="py", code=file_txt)
# print(nodes_nav.to_tree_graph())

root_nav.write()  # Finally, we write the whole tree.
