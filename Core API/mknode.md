# MkNode

The base class of every node, page and nav: tree handling (`parent`, `children`,
`iter_nodes()`), the project context (`ctx`), the Jinja environment (`env`) and the
rendering API (`node.to_markdown()` / `str(node)`, `to_html()`,
`get_resources()`). Rendering is synchronous and never fetches: external inputs
(icons, remote files, LLM texts, ...) come from the inputs store, resolved before rendering.
`to_html(flavor=...)` converts with a parser that knows the flavour:
Python-Markdown for `material`, comrak for `github` / `mdbook`, markdown-it-py with the MyST
plugins (directives mapped to Sphinx-like HTML, an approximation) for `myst`; the last two
need the `html` extra (`pip install mknodes[html]`). Its node page
([MkNode](<../The nodes/Base nodes/mknode.md>)) shows the examples.

**Example**

```py
import mknodes as mk

node = mk.MkAdmonition("Careful!", typ="warning")
markdown = node.to_markdown()  # same as str(node)
html = node.to_html()
github_html = node.to_html(flavor="github")  # needs mknodes[html]
resources = node.get_resources()  # Markdown extensions, CSS, JS
```

## <a id="mknodes.MkNode"></a>`mknodes.MkNode`

```python
class MkNode
```

Base class for everything which can be expressed as Markup.

This class combines tree node functionality with markdown generation.
Starting from the root nav (aka Docs) down to nested Markup blocks,
the whole project can be represented by one tree.

MkNode is the base class for all nodes. We dont instanciate it directly.
All subclasses carry an MkAnnotations node (except the MkAnnotations node itself)
They can also pass an `indent` as well as a `shift_header_levels` keyword argument
in order to modify the resulting markdown.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.api_section._add_page.<locals>._**

```python
@nav.route.page(title, hide="toc")
def _(page: mk.MkPage) -> None:
    page += INTROS[title]
    page += mk.MkCode(EXAMPLES[title].rstrip(), language="py", title="Example")
    for identifier in identifiers:
        page += mk.MkDocStrings(identifier, **DOCSTRING_OPTIONS)

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={},
          plugins=[],
          js=[],
          assets=[],
          packages=[])
```

</details>

<details>
<summary>Metadata</summary>

```yaml
created:
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/api_section.py
  source_function: _add_page.<locals>._
  source_line_no: 168
hide:
- toc
title: MkNode

```

</details>

</details>
