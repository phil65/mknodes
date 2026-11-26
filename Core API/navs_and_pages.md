# Navs and pages

A documentation is a tree: [MkNav](#mknodes.MkNav) objects are the sections,
[MkPage](#mknodes.MkPage) objects the pages, nodes the content of a page. Nodes get added
with `+=`, navs and pages with `add_nav()` / `add_page()` (or via decorators, see
[Routing](routing.md)). The root nav is what a build function receives.

**Example**

```py
import mknodes as mk

nav = mk.MkNav()  # the root nav
page = nav.add_page("Usage", is_index=True, hide="toc")
page += mk.MkAdmonition("Install with `pip install mknodes`.", typ="tip")
guides = nav.add_nav("Guides")
first_steps = guides.add_page("First steps")
first_steps += "Some text"
```

## <a id="mknodes.MkNav"></a>`mknodes.MkNav`

```python
class MkNav(mknode.MkNode)
```

Nav section, representing a nestable menu.

A nav is named (exception is the root nav, which has section name = None),
has an associated virtual file (in general a SUMMARY.md),
an optional index page and can contain other navs as well as pages and links.

## <a id="mknodes.MkPage"></a>`mknodes.MkPage`

```python
class MkPage(mkcontainer.MkContainer)
```

A node container representing a Markdown page.

A page contains a list of other Markdown nodes, has a virtual Markdown file
associated, and can have metadata (added as header)

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
title: Navs and pages

```

</details>

</details>
