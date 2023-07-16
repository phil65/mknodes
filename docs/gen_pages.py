"""Generate the code reference pages and navigation."""

from __future__ import annotations

import pathlib
import pprint

import markdownizer
from markdownizer import classhelpers, utils

import mkdocs

root_nav = markdownizer.Nav()

home_nav = root_nav.create_nav("Home")

intro_page = home_nav.create_page("Introduction", hide_toc=True)
intro_page += "### Not in the mood to write documentation? Let´s code it then!"
intro_page.add_admonition(
    "API is still evolving, so consider this a preview.", typ="danger", title="Warning!"
)
intro_page += "This is the source code for building this website:"
intro_page.add_code(pathlib.Path(__file__).read_text(), language="py")


def generate_example(kls: type[markdownizer.MarkdownNode]):
    if not hasattr(kls, "examples"):
        return ""
    lines = [f"## Examples for {utils.link_for_class(kls)}\n"]
    # "examples()" yields dicts with keyword arguments for building examples.
    for sig in kls.examples():
        sig_txt = utils.format_kwargs(sig)
        example = (
            f"node = markdownizer.{kls.__name__}({sig_txt})\n"
            + "str(node)  # or node.to_markdown()"
        )
        example_code = markdownizer.Code(language="py", code=example)
        lines.append(str(example_code))
        instance = kls(**sig)
        code = markdownizer.Code(language="markdown", code=instance)
        tabs = {"Generated markdown": str(code), "Preview": str(instance)}
        tab_markdown = markdownizer.Tabbed(tabs).to_markdown()
        lines.extend(("generates this Markdown:", tab_markdown, "<br><br><br>"))
    return "\n".join(lines)


nodes_nav = home_nav.create_nav("Markdown Nodes")
# get_subclasses just calls __subclasses__ recursively.
for kls in classhelpers.get_subclasses(markdownizer.MarkdownNode):
    if example_text := generate_example(kls):
        subpage = nodes_nav.create_page(kls.__name__)
        subpage += example_text

# Lets generate our Code documentation.
own_docs = root_nav.create_documentation(module=markdownizer)
for klass in own_docs.iter_classes(filter_by___all__=True):
    # the default class page contains MkDocStrings, a mermaid inheritance diagram
    # and tables with links to child classes.
    own_docs.add_class_page(klass=klass)

# We could also add docs for random other modules, too.
mkdocs_docs = root_nav.create_documentation(module=mkdocs)
for klass in mkdocs_docs.iter_classes(recursive=True):
    mkdocs_docs.add_class_page(klass=klass)

# Lets show some info about the tree we built.
# The tree starts from the root nav down to the Markup elements.
tree_page = home_nav.create_page("Navigation tree", hide_toc=True)
lines = [f"{indent * '    '} {repr(node)}" for indent, node in root_nav.yield_nodes()]
tree_page += markdownizer.Code(language="py", code="\n".join(lines))
virtual_files = root_nav.all_virtual_files()
files_page = home_nav.create_page("File map", hide_toc=True)
files_page += markdownizer.Code(language="py", code=pprint.pformat(virtual_files))


root_nav.write()  # Finally, we write the whole tree.
