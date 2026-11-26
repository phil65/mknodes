# Setting the homepage

## Setting the Homepage

If you want an [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) to become your Homepage, set `is_homepage` to True in the [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) constructor for the page you want to become your homepage.

**setting `is_homepage` via constructor**

```py
sub_nav = root_nav.add_nav("My child nav")
# first we create an MkPage with is_homepage set to True
my_homepage = mk.MkPage("My first Homepage", is_homepage=True)
# Then we add it to any given MkNav.
sub_nav += my_homepage
```
`my_homepage` is now both the homepage and a child page from `sub_nav`.

If decorators are used for routing, `is_homepage` can be passed as decorator keyword argument
with the same effect.

**setting `is_homepage` via decorator**

```py
nav = root_nav["My child nav"]

@nav.route.page("My first Homepage", is_homepage=True)
def _(page: mk.MkPage):
    page += ...
    ...
```

## Setting Index pages

**Index pages** is a more general term and can also refer to pages which could be described as a "Sub-Homepages". The homepage itself is also an index page.

For pages with a hierarchical site navigation, you can usually reach the index pages by clicking the section label in the site navigation menu.

> [!NOTE]
> **MkDocs** does not support index pages "out-of-the box". You either need the plugin [mkdocs-section-index](https://github.com/oprypin/mkdocs-section-index) or a theme which
> supports them natively.

To create an index page for a section, you can use the `is_index` keyword argument [MkNav.add_page](../Core%20API/navs_and_pages.md#mknodes.MkNav):

**Setting an index page**

```py
page = nav.add_page(is_index=True)
...
```

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.page_section._**

```python
@nav.route.page("Setting the homepage")
def _(page: mk.MkPage) -> None:
    page += mk.MkTemplate("pages/homepage.jinja")

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
  source_line_no: 29
title: Setting the homepage

```

</details>

</details>
