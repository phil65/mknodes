# MkPages

## General information

MkPages are nodes which are children from MkNavs, and represent a single page from a website.
Like already described, a page can either be a regular page or an "index page" for an MkNav.
An index page shows when clicking on a menu item with children, or for the website root.

## Page metadata

MkPages have metadata attached, which can be set via the [MkPage.metadata](metadata.md#mknodes.Metadata) attribute.
[MkPage.metadata](metadata.md#mknodes.Metadata) is also inherited from the parent MkNavs in case they have metadata set.
That metadata can alter the behaviour and appearance of given page. It can be used to
show icons / subtitles in menus, to modify the search ranking, to set a reference to a [PageTemplate](templates.md#mknodes.PageTemplate), and much more.

> [!NOTE]
> The *page information* box at the bottom of each page also contains the metadata content of the current page, as well as the code which created the page. If you're interested how **MkNodes** works, it can help to check out
> these information boxes! (What you will notice: **MkNodes** puts some data about the page instantiation into the metadata.)

<details>
<summary>Further info</summary>

See the [Metadata](metadata.md#mknodes.Metadata) section, the [MkDocs Documentation](https://www.mkdocs.org/user-guide/writing-your-docs/#meta-data) as well as the [MkDocs-Material](https://squidfunk.github.io/mkdocs-material/) docs for further info.

</details>

## Page templates

Each [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) also carries a [PageTemplate](templates.md#mknodes.PageTemplate), which can be used for more advanced modification of a page. For example, page templates can be used to put HTML / Markdown into other areas of the page than just the main content area, like the announcement bar or the site nav section.
Like metadata, the templates also inherit from MkNavs, meaning that a [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) will use the
template of a parent [MkNav](../Core%20API/navs_and_pages.md#mknodes.MkNav) if it has one defined.

More information about templates can be found [here](templates.md).

## Using MkPages

MkPages can get created in many ways:

* By simply use the constructor and add the page to an MkNav:

    **The classic way**

    ```py
    page = MkPage("My page")
    nav += page
    ```

* By using the [nav.route.page](../MkNavs/Using%20decorators/index.md#mknodes.navs.navrouter.NavRouter.page) decorator.

    **Via decorators**

    ```py
    @nav.route.page("My page")
    def _(page): ...
    ```

  More information about routing can be found [here](<../MkNavs/Using decorators/index.md>).

* By using [MkNav.add_page](../Core%20API/navs_and_pages.md#mknodes.MkNav):

    **Via add_page**

    ```py
    page = nav.add_page("My page")
    ```

* By using the alternative constructor [MkPage.from_file](../Core%20API/navs_and_pages.md#mknodes.MkPage):

    **Via MkPage.from_file**

    ```py
    page = MkPage.from_file("path/to/file.md")
    ```

* Or indirectly by using "batch operations" like [nav.parse.folder](../MkNavs/index.md#mknodes.navs.navparser.NavParser.folder)
  and similar (see also: [NavParser](../MkNavs/index.md#mknodes.navs.navparser.NavParser)):

    **Via parse.folder or similar**

    ```py
    nav = MkNav()
    nav.parse.folder("path/to/folder/with/markdown/files/")
    assert nav.nav.get_pages()
    ```

Like many other nodes, MkPages inherits from [MkContainer](../The%20nodes/Container%20nodes/mkcontainer.md#mknodes.MkContainer) and looks to the outside world like a list, meaning you can add nodes to them by using `+=` or `MkPage.append()`.

Each [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) also has an [MkFootnotes](../The%20nodes/Container%20nodes/mkfootnotes.md#mknodes.MkFootNotes) node "embedded" which can be used to easily add footnotes to a page. (Scroll to the bottom to see the result)

**MkFootnotes embedded**

```py
page = MkPage("My page")
page.footnotes[1] = r"Footnotes are numbered, can be set via \__setitem__."
page.footnotes[2] = r"They can also get nested[^3]."
page.footnotes[3] = MkAdmonition("And they can also contain other Markdown (nodes).")
```

## Build process

During the build process, all Markdown nodes which are part of an [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) get collected and scanned for required resources like CSS / JS / static assets. If appropriate, these resources then automatically get inserted into the [PageTemplate](templates.md#mknodes.PageTemplate) and end up in the HTML header.

The final URL of an [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) is determined by its position inside the tree and gets calculated
when the tree gets "serialized" into markdown. The HTML filename is inferred from the page
title in case no specific path is given.

MkPages are not tied to a static site engine: **MkNodes** does not depend on [MkDocs](https://www.mkdocs.org) or any other engine.
The site generator [mkdocs-mknodes](https://phil65.github.io/mkdocs-mknodes/) serializes the MkPages of a tree to Markdown
(including the front matter), writes them into the docs folder together with the nav and the required resources,
and the site engine ([Zensical](https://zensical.org)) builds the HTML website from there.

## Template MkPages

**MkNodes** also contains two special subclasses of [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage), [MkModulePage](mkmodulepage.md#mknodes.MkModulePage) and [MkClassPage](mkclasspage.md#mknodes.MkClassPage).
They get used by the automatic API generator node named [MkDoc](../MkNavs/index.md#mknodes.MkDoc) and contain a **jinja2** template used to create an API / info page for given module / class.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.page_section._**

```python
@nav.route.page(is_index=True)
def _(page: mk.MkPage) -> None:
    page += mk.MkTemplate("pages/mkpage_index.jinja")
    page.footnotes[1] = r"Footnotes are numbered, can be set via \__setitem__."
    page.footnotes[2] = r"They can also get nested[^3]."
    page.footnotes[3] = mk.MkAdmonition("They can also contain other Markdown (nodes).")

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/page_section.py
  source_function: _
  source_line_no: 7
title: MkPages

```

</details>

</details>

[^1]:
    Footnotes are numbered, can be set via \__setitem__.
[^2]:
    They can also get nested[^3].
[^3]:
    > [!NOTE]
    > They can also contain other Markdown (nodes).
