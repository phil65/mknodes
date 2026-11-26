# Site generator

## Overview

**MkDocs-MkNodes** turns **MkNodes** node trees into websites.

**MkNodes** is a library to create complex documentation websites. It includes a powerful jinja environment to assist in writing Markdown text as well as a a large set of so-called **MkNodes**, which can be used to create re-usable node trees describing a complete website. That node tree covers the whole site navigation, down to single Markdown elements, allowing the creator anytime to switch between programatically creating documentation and writing Markdown "by hand".

This package is the site generator: it runs a build function, collects pages, navigation, assets,
template overrides and the required Markdown extensions from the node tree and writes them as
input for [Zensical](https://zensical.org), which builds the HTML website.

> [!NOTE]
> Still sounds confusing? The best way to learn how everything works is to start with the [MkNodes](https://phil65.github.io/mknodes) documentation.
>
> In addition, all pages on this website include an Admonition box at the bottom, which also includes the code which generated the page. That might be a helpful resource to understand how **MkNodes** can be used.

## Two ways to use it

**1. Zero configuration.** Just run

``` bash
mknodes build
```

in a repository (with or without a `mkdocs.yml` for theme and site settings). This creates a
default website for the project: the `README.md` as index page, API docs, CLI docs (if the
project has a CLI) and a "Development" section with changelog, contribution guidelines,
dependencies and license.

**2. Your own build function.** Point `build-fn` to a callable which populates the root nav:

``` toml
# pyproject.toml
[tool.mknodes]
build-fn = "build_docs.py:build"
```

``` py
import mknodes as mk


def build(root: mk.MkNav, theme: mk.Theme) -> None:
    page = root.add_page("Home", is_index=True, hide="toc")
    page += mk.MkAdmonition("Hello world!")
    root.add_doc(section_name="API", recursive=True)
```

The build function gets called with the keyword arguments `root` and `theme` (plus everything
set via the `kwargs` setting) and may also be `async`. Alternatively, the default build
function `mknodes.site:parse` accepts a node tree written in YAML / TOML via the `pages`
setting (see the use cases section).

Hand-written Markdown pages in the docs folder keep working next to the generated ones
(a `nav` in `mkdocs.yml` comes first, the generated nav gets appended).

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.site._**

```python
@nav.route.page(is_index=True, hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("site/index.jinja")

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/site/__init__.py
  source_function: _
  source_line_no: 16
hide:
- toc
title: Site generator

```

</details>

</details>
