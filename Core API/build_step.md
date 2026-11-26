# Build step

[DocBuilder](#mknodes.DocBuilder) renders a node tree into a
[BuildOutput](#mknodes.BuildOutput): pages (Markdown of one flavour), assets, the nav as
[NavItem](#mknodes.build.output.NavItem) tree and the Markdown extensions / CSS / JS the
pages need. [MarkdownExporter](#mknodes.MarkdownExporter) writes it as plain Markdown
files plus a `SUMMARY.md` nav. The site generator (`mknodes build`) does the same and
then runs Zensical, so this is only needed to use MkNodes without it.

**Example**

```py
import mknodes as mk

nav = mk.MkNav()
page = nav.add_page("Usage", is_index=True)
page += mk.MkAdmonition("Install with `pip install mknodes`.", typ="tip")

output = mk.DocBuilder(flavor="github").build(nav)
mk.MarkdownExporter().export(output, "site/")  # index.md + SUMMARY.md
```

## <a id="mknodes.DocBuilder"></a>`mknodes.DocBuilder`

```python
class DocBuilder
```

Renders a node tree (root `MkNav` + optional theme) into a `BuildOutput`.

For each page: render the Markdown in the chosen flavour, collect its resources,
wire up its page template and optionally render it with Jinja. Afterwards the
resources of all pages (+ theme) get turned into assets, stylesheets, scripts and
Markdown extensions, and the nav into a `NavItem` tree.

## <a id="mknodes.BuildOutput"></a>`mknodes.BuildOutput`

```python
class BuildOutput
```

Everything a node tree produced, independent of the target.

Pages are rendered in one Markdown flavour (see `mknodes.rendering`). Exporters /
site generators turn this into files or into the input of a static site engine.

## <a id="mknodes.build.output.NavItem"></a>`mknodes.build.output.NavItem`

```python
class NavItem
```

An entry of the site navigation.

Either a link to a page / URL (`target` set) or a section (`children` set).

### <a id="mknodes.build.output.NavItem.target"></a>`target`

```python
target: str | None = None
```

Page path (relative to the docs root) or an external URL.

## <a id="mknodes.MarkdownExporter"></a>`mknodes.MarkdownExporter`

```python
class MarkdownExporter
```

Writes the pages and assets plus the nav as `SUMMARY.md`.

The result is readable in any Markdown viewer (and on GitHub, with the `github`
flavour). `SUMMARY.md` uses the literate-nav format.

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
title: Build step

```

</details>

</details>
