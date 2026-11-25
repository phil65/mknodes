# MkNodes

#### Don't write docs. Code them.

[![PyPI License](https://img.shields.io/pypi/l/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Package status](https://img.shields.io/pypi/status/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Daily downloads](https://img.shields.io/pypi/dd/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Weekly downloads](https://img.shields.io/pypi/dw/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Monthly downloads](https://img.shields.io/pypi/dm/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Distribution format](https://img.shields.io/pypi/format/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Wheel availability](https://img.shields.io/pypi/wheel/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Python version](https://img.shields.io/pypi/pyversions/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Implementation](https://img.shields.io/pypi/implementation/mknodes.svg)](https://pypi.org/project/mknodes/)
[![Releases](https://img.shields.io/github/downloads/phil65/mknodes/total.svg)](https://github.com/phil65/mknodes/releases)
[![Github Contributors](https://img.shields.io/github/contributors/phil65/mknodes)](https://github.com/phil65/mknodes/graphs/contributors)
[![Github Discussions](https://img.shields.io/github/discussions/phil65/mknodes)](https://github.com/phil65/mknodes/discussions)
[![Github Forks](https://img.shields.io/github/forks/phil65/mknodes)](https://github.com/phil65/mknodes/forks)
[![Github Issues](https://img.shields.io/github/issues/phil65/mknodes)](https://github.com/phil65/mknodes/issues)
[![Github Issues](https://img.shields.io/github/issues-pr/phil65/mknodes)](https://github.com/phil65/mknodes/pulls)
[![Github Watchers](https://img.shields.io/github/watchers/phil65/mknodes)](https://github.com/phil65/mknodes/watchers)
[![Github Stars](https://img.shields.io/github/stars/phil65/mknodes)](https://github.com/phil65/mknodes/stars)
[![Github Repository size](https://img.shields.io/github/repo-size/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Github last commit](https://img.shields.io/github/last-commit/phil65/mknodes)](https://github.com/phil65/mknodes/commits)
[![Github release date](https://img.shields.io/github/release-date/phil65/mknodes)](https://github.com/phil65/mknodes/releases)
[![Github language count](https://img.shields.io/github/languages/count/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Github commits this week](https://img.shields.io/github/commit-activity/w/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Github commits this month](https://img.shields.io/github/commit-activity/m/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Github commits this year](https://img.shields.io/github/commit-activity/y/phil65/mknodes)](https://github.com/phil65/mknodes)
[![Package status](https://codecov.io/gh/phil65/mknodes/branch/main/graph/badge.svg)](https://codecov.io/gh/phil65/mknodes/)
[![PyUp](https://pyup.io/repos/github/phil65/mknodes/shield.svg)](https://pyup.io/repos/github/phil65/mknodes/)

[Read the completely coded documentation!](https://phil65.github.io/mknodes/)

MkNodes lets you build documentation from Python objects instead of hand-written Markdown.
Pages, navigation sections and content blocks are *nodes* that render to
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)-flavored Markdown and know
which Markdown extensions, CSS and JavaScript they need. Many nodes pull their content directly
from your project (pyproject.toml, git history, installed packages, docstrings), so the docs stay
in sync with the code.

## Installation

```bash
pip install mknodes
```

MkNodes includes a site generator (`mknodes build` / `serve` / `generate`) that builds
websites with [Zensical](https://zensical.org) or writes plain Markdown. It does not depend on
MkDocs. (It used to be the separate `mkdocs-mknodes` package.)

## Quickstart

```py
import asyncio

import mknodes as mk

page = mk.MkPage("Overview")
page += mk.MkHeader("My project", level=1)
page += mk.MkAdmonition("Generated with MkNodes!", typ="tip", title="Note")
page += mk.MkTable({"Feature": ["Nodes", "Templating"], "Status": ["yes", "yes"]})
page += mk.MkCode("print('hello')", language="py")

print(asyncio.run(page.to_markdown()))
```

## Features

- **75+ nodes**: admonitions, tabs, tables, code blocks, diagrams, cards, timelines, badges, ...
- **Project-aware nodes**: `MkChangelog`, `MkInstallGuide`, `MkDependencyTable`, `MkLicense`,
  `MkShields`, `MkClassDiagram`, ... build their content from your package and repository.
- **Navigation trees**: `MkNav` sections with decorator-based routing, API docs via `MkDoc`,
  CLI docs via `MkCliNav`, or parse an existing `SUMMARY.md` / folder.
- **Jinja templating**: every node is also a Jinja filter, e.g.
  `{{ "Inlined text" | MkAdmonition(inline="left") }}`.
- **Resource tracking**: required Markdown extensions, CSS and JS are collected per page.
- **Markdown extensions**: `/// mknodes` blocks and executable Python code blocks
  (`mknodes.mdext`).

### Build a website tree

```py
import mknodes as mk


def build(root: mk.MkNav, theme: mk.Theme) -> None:
    @root.route.page("Home", is_index=True)
    def _(page: mk.MkPage):
        page += mk.MkHeader("Welcome", level=1)
        page += mk.MkInstallGuide()

    @root.route.page("Changelog", icon="format-list-group")
    def _(page: mk.MkPage):
        page += mk.MkChangelog()
```

Configure it in `pyproject.toml` and build the website (run inside your project's repository):

```toml
[tool.mknodes]
build-fn = "mypackage.docs:build"
```

```bash
mknodes build                      # pages + mkdocs.generated.yml, then `zensical build`
mknodes serve                      # live preview
mknodes generate --engine markdown --flavor github --generated-dir out  # plain Markdown
```

Without a build function, a default website gets generated (README, API docs, CLI docs,
development pages). Build functions are called as `build_fn(root=..., theme=..., **kwargs)`
(sync or async) and populate `root`.

The CLI also renders Jinja-enhanced Markdown: `mknodes render -i template.md -o output.md`
and `mknodes render-folder -i src_docs -o docs`.

### Markdown extensions

```py
import markdown

from mknodes.mdext.execute_ext import get_custom_fences

md = markdown.Markdown(
    extensions=["pymdownx.superfences", "mknodes.mdext"],
    extension_configs={"pymdownx.superfences": {"custom_fences": get_custom_fences()}},
)
```

````markdown
/// mknodes
{{ "Dynamic Header" | MkHeader(level=2) }}
///

```python exec="true"
print("**Generated at build time!**")
```
````

Use `session="name"` on `exec` blocks to share variables between them. See
[`src/mknodes/mdext/README.md`](src/mknodes/mdext/README.md) for all options.

## Documentation

The [documentation](https://phil65.github.io/mknodes/) is itself built with MkNodes
(see `src/mknodes/manual/`) and shows every node with examples.
