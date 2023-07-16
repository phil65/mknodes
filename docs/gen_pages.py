"""Generate the code reference pages and navigation."""

from __future__ import annotations

import pathlib
import pprint

import markdownizer
from markdownizer import classhelpers, utils

import mkdocs

root_nav = markdownizer.Nav()
subnav = root_nav.create_nav("Home")
page = subnav.create_page("Introduction")
page += "No time to write a documentation. So we will generate it."
page.add_admonition("Warning This is still beta", typ="danger", title="Warning!")
page += "This is the source for the complete documentation:"
page += markdownizer.Code("python", code=pathlib.Path(__file__).read_text())


def generate_example(kls: type[markdownizer.MarkdownNode]):
    if not hasattr(kls, "examples"):
        return ""
    lines = [f"## Examples for {utils.link_for_class(kls)}\n"]
    for sig in kls.examples():
        sig_txt = utils.format_kwargs(sig)
        example = (
            f"node = markdownizer.{kls.__name__}({sig_txt})\n"
            + "str(node)  # or node.to_markdown()"
        )
        example_code = markdownizer.Code(language="python", code=example)
        lines.append(str(example_code))
        instance = kls(**sig)
        code = markdownizer.Code(language="markdown", code=instance)
        tabs = {"Generated markdown": str(code), "Preview": str(instance)}
        tab_markdown = markdownizer.Tabbed(tabs).to_markdown()
        lines.extend(("generates this Markdown:", tab_markdown, "<br><br><br>"))
    return "\n".join(lines)


nodes_nav = subnav.create_nav("Markdown Nodes")
# get_subclasses just calls __subclasses__ recursively.
for kls in classhelpers.get_subclasses(markdownizer.MarkdownNode):
    if example_text := generate_example(kls):
        subpage = nodes_nav.create_page(kls.__name__)
        subpage += example_text

# Lets generate our Code documentation.
own_docs = root_nav.create_documentation(module=markdownizer)
for klass in own_docs.iter_classes(filter_by___all__=True):
    own_docs.add_class_page(klass=klass)

# We could also add random docs for other modules, too.
mkdocs_docs = root_nav.create_documentation(module=mkdocs)
for klass in mkdocs_docs.iter_classes(recursive=True):
    mkdocs_docs.add_class_page(klass=klass)

tree_page = subnav.create_page("Navigation tree")
lines = [f"{indent * '    '} {repr(node)}" for indent, node in root_nav.yield_nodes()]
tree_page += markdownizer.Code(language="py", code="\n".join(lines))
files_page = subnav.create_page("File map")
virtual_files = root_nav.all_virtual_files()
files_page += markdownizer.Code(language="py", code=pprint.pformat(virtual_files))


root_nav.write()  # Finally, we write the whole tree.
