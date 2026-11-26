# Welcome to MkNodes

This site is also available as: [Zensical](https://phil65.github.io/mknodes/) · [MkDocs](https://phil65.github.io/mknodes/mkdocs/) · [mdBook](https://phil65.github.io/mknodes/mdbook/) · [Sphinx](https://phil65.github.io/mknodes/sphinx/) · [Docsify](https://phil65.github.io/mknodes/docsify/) · [GitHub Markdown](https://github.com/phil65/mknodes/tree/docs-github)

<picture>
 <img alt="" src="https://img.shields.io/pypi/v/mknodes.svg">
</picture>
<picture>
 <img alt="" src="https://img.shields.io/pypi/status/mknodes.svg">
</picture>
<picture>
 <img alt="" src="https://codecov.io/gh/phil65/mknodes/branch/main/graph/badge.svg">
</picture>

> [!NOTE]
> > **Example**
> >
> > > **Bug**
> > >
> > > > **Danger**
> > > >
> > > > > **Failure**
> > > > >
> > > > > > **Warning**
> > > > > >
> > > > > > > **Question**
> > > > > > >
> > > > > > > > **Success**
> > > > > > > >
> > > > > > > > > **Tip**
> > > > > > > > >
> > > > > > > > > > **Info**
> > > > > > > > > >
> > > > > > > > > > > **Abstract**
> > > > > > > > > > >
> > > > > > > > > > > > **Note**
> > > > > > > > > > > >
> > > > > > > > > > > > > **Info**
> > > > > > > > > > > > >
> > > > > > > > > > > > > **get_started_section.py**
> > > > > > > > > > > > >
> > > > > > > > > > > > > ```py
> > > > > > > > > > > > > import typing
> > > > > > > > > > > > >
> > > > > > > > > > > > > import mknodes as mk
> > > > > > > > > > > > > from mknodes.data import datatypes
> > > > > > > > > > > > > from mknodes.manual.a_quick_tour import a_quick_tour
> > > > > > > > > > > > >
> > > > > > > > > > > > >
> > > > > > > > > > > > > nav = mk.MkNav("Get started")
> > > > > > > > > > > > >
> > > > > > > > > > > > > # The same build function, rendered by every site engine (see documentation.yml).
> > > > > > > > > > > > > ENGINE_SITES = {
> > > > > > > > > > > > >     "Zensical": "https://phil65.github.io/mknodes/",
> > > > > > > > > > > > >     "MkDocs": "https://phil65.github.io/mknodes/mkdocs/",
> > > > > > > > > > > > >     "mdBook": "https://phil65.github.io/mknodes/mdbook/",
> > > > > > > > > > > > >     "Sphinx": "https://phil65.github.io/mknodes/sphinx/",
> > > > > > > > > > > > >     "Docsify": "https://phil65.github.io/mknodes/docsify/",
> > > > > > > > > > > > >     "GitHub Markdown": "https://github.com/phil65/mknodes/tree/docs-github",
> > > > > > > > > > > > > }
> > > > > > > > > > > > >
> > > > > > > > > > > > >
> > > > > > > > > > > > > @nav.route.page("Welcome to MkNodes", hide="toc", is_homepage=True)
> > > > > > > > > > > > > def _(page: mk.MkPage) -> None:
> > > > > > > > > > > > >     links = " · ".join(f"[{name}]({url})" for name, url in ENGINE_SITES.items())
> > > > > > > > > > > > >     page += mk.MkText(f"This site is also available as: {links}")
> > > > > > > > > > > > >     page += mk.MkShields(["version", "status", "codecov"])
> > > > > > > > > > > > >     fn_code = mk.MkCode.for_file(__file__)
> > > > > > > > > > > > >     node = mk.MkAdmonition(content=fn_code, title="")
> > > > > > > > > > > > >     for i in typing.get_args(datatypes.AdmonitionTypeStr):
> > > > > > > > > > > > >         node = mk.MkAdmonition(content=node, typ=i, title="")
> > > > > > > > > > > > >     page += node
> > > > > > > > > > > > >
> > > > > > > > > > > > >
> > > > > > > > > > > > > @nav.route.page("Installation", hide="toc", icon="grommet-icons:install")
> > > > > > > > > > > > > def _(page: mk.MkPage) -> None:
> > > > > > > > > > > > >     page += mk.MkInstallGuide()
> > > > > > > > > > > > >
> > > > > > > > > > > > >
> > > > > > > > > > > > > @nav.route.page("Why should I use MkNodes?", hide="toc", icon="ri:question-line")
> > > > > > > > > > > > > def _(page: mk.MkPage) -> None:
> > > > > > > > > > > > >     page += mk.MkTemplate("why_mknodes.jinja")
> > > > > > > > > > > > >
> > > > > > > > > > > > >
> > > > > > > > > > > > > @nav.route.page("A quick node tour", hide="toc", icon="ic:outline-tour")
> > > > > > > > > > > > > def _(page: mk.MkPage) -> None:
> > > > > > > > > > > > >     # Only the commented tour renders Jinja, the raw source at the end must stay as is.
> > > > > > > > > > > > >     page.metadata.render_macros = False
> > > > > > > > > > > > >     a_quick_tour(page)
> > > > > > > > > > > > >
> > > > > > > > > > > > >
> > > > > > > > > > > > > @nav.route.page("Changelog", icon="format-list-group")
> > > > > > > > > > > > > def _(page: mk.MkPage) -> None:
> > > > > > > > > > > > >     page += mk.MkChangelog()
> > > > > > > > > > > > >
> > > > > > > > > > > > > ```

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.get_started_section._**

```python
@nav.route.page("Welcome to MkNodes", hide="toc", is_homepage=True)
def _(page: mk.MkPage) -> None:
    links = " · ".join(f"[{name}]({url})" for name, url in ENGINE_SITES.items())
    page += mk.MkText(f"This site is also available as: {links}")
    page += mk.MkShields(["version", "status", "codecov"])
    fn_code = mk.MkCode.for_file(__file__)
    node = mk.MkAdmonition(content=fn_code, title="")
    for i in typing.get_args(datatypes.AdmonitionTypeStr):
        node = mk.MkAdmonition(content=node, typ=i, title="")
    page += node

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/get_started_section.py
  source_function: _
  source_line_no: 21
hide:
- toc
title: Welcome to MkNodes

```

</details>

</details>
