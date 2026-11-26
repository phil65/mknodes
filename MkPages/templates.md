# Templates

The page template can be edited easily via the [MkPage.template](#mknodes.PageTemplate) attribute.
If any block gets modified then **MkNodes** will generate an individual template HTML file for the page during the build process.

An example:

```py
page.template.tabs.content = mk.MkAdmonition("Some text.")
```
would generate the following template override automatically:

```html
{ % extends "main.html" % }

{ % block content % }
<div class="admonition info">
<p class="admonition-title">Info</p>
<p>Some text</p>
</div>

{ % endblock % }
```

```py
page.template.announce.content = mk.MkMetadataBadges(typ="classifiers")
page.template.footer.content = mk.MkProgressBar(50)
page.template.tabs.content = mk.MkCode("information = 'You can even put MkNodes here!'")
page.template.hero.content = mk.MkHeader("A header!")
```

### PageTemplate Blocks

#### Title block ([MkPage.template.title](#mknodes.pages.templateblocks.TitleBlock))

The title block allows to modify the title tag in HEAD

```py
page.template.title.content = "New title"
```

#### Libs block ([MkPage.template.libs](#mknodes.pages.templateblocks.LibsBlock))

The libs block can be used to add additional JavaScript libraries.

```py
page.template.libs.add_script_file("path_to_file.js")
```

#### Analytics block ([MkPage.template.analytics](#mknodes.pages.templateblocks.AnalyticsBlock))

The analytics block can be used to set custom analytics.

```py
page.template.analytics.content = "<html content>"
```

#### Scripts block ([MkPage.template.scripts](#mknodes.pages.templateblocks.ScriptsBlock))

The scripts block can be used to add custom JavaScript files, put at the end of the HTML body.

```py
page.template.scripts.add_script_file("path_to_script.js")
```

#### Site meta block ([MkPage.template.site_meta](#mknodes.pages.templateblocks.SiteMetaBlock))

The site_meta block contains the site metadata. By default it gets populated by data from
the MkDocs config file.

#### Styles block ([MkPage.template.styles](#mknodes.pages.templateblocks.StylesBlock))

The styles block can be used to add additional CSS.

```py
page.template.styles.add_css("My custom CSS")
```

#### ExtraHead block ([MkPage.template.styles](#mknodes.pages.templateblocks.ExtraHeadBlock))

The extrahead block allows to add content to the HTML head which does not suit the other
categories, like redirecting to another URL.

```py
page.template.extra_head.set_redirect_url("http://some.url")
```

#### HTML blocks

HTML blocks can get populated with Markdown, which will get converted to HTML during the build process.

* [MkPage.template.content_block](#mknodes.pages.templateblocks.HtmlBlock)
* [MkPage.template.footer](#mknodes.pages.templateblocks.HtmlBlock)
* [MkPage.template.site_nav](#mknodes.pages.templateblocks.HtmlBlock)

**MkDocs-Material**-exclusive blocks:

* [MkPage.template.tabs](#mknodes.pages.templateblocks.HtmlBlock)
* [MkPage.template.outdated](#mknodes.pages.templateblocks.HtmlBlock)
* [MkPage.template.hero](#mknodes.pages.templateblocks.HtmlBlock)
* [MkPage.template.announce](#mknodes.pages.templateblocks.HtmlBlock)

```py
page.template.announce.content = mk.MkMetadataBadges(typ="classifiers")
page.template.footer.content = mk.MkProgressBar(50)
page.template.tabs.content = mk.MkCode("information = 'You can even put MkNodes here!'")
page.template.hero.content = mk.MkHeader("A header!")
```

## API

### <a id="mknodes.PageTemplate"></a>`mknodes.PageTemplate`

```python
class PageTemplate
```

A jinja template used to build a website from an MkPage.

### <a id="mknodes.pages.templateblocks"></a>`mknodes.pages.templateblocks`

#### <a id="mknodes.pages.templateblocks.AnalyticsBlock"></a>`AnalyticsBlock`

```python
class AnalyticsBlock(Block)
```

Block for analytics-tags in HEAD.

#### <a id="mknodes.pages.templateblocks.BaseBlock"></a>`BaseBlock`

```python
class BaseBlock(mknode.MkNode)
```

A class representing a block from a page template.

##### <a id="mknodes.pages.templateblocks.BaseBlock.to_markdown"></a>`to_markdown`

```python
def to_markdown(flavor: str | rendering.Renderer | None = None, *, md: markdown.Markdown | None = None) -> str
```

Return the Jinja block (with HTML content) for the page template.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `flavor` | `str \| rendering.Renderer \| None` | Unused: template blocks are theme overrides, not Markdown | None |
| `md` | `markdown.Markdown \| None` | Markdown parser to use | None |

#### <a id="mknodes.pages.templateblocks.BaseJSBlock"></a>`BaseJSBlock`

```python
class BaseJSBlock(BaseBlock)
```

Block for additional libraries.

##### <a id="mknodes.pages.templateblocks.BaseJSBlock.__init__"></a>`__init__`

```python
def __init__(scripts: list[resources.JSFile] | None = None, include_super: bool = True) -> None
```

Constructor.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `scripts` | `list[resources.JSFile] \| None` | List of scripts to add to HTML header libs. | None |
| `include_super` | `bool` | Whether to include the original content. | True |

##### <a id="mknodes.pages.templateblocks.BaseJSBlock.add_script_file"></a>`add_script_file`

```python
def add_script_file(script: resources.JSFile | str | os.PathLike[str]) -> None
```

Add a script file to the block.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `script` | `resources.JSFile \| str \| os.PathLike[str]` | Script to add to the block |  |

#### <a id="mknodes.pages.templateblocks.Block"></a>`Block`

```python
class Block(BaseBlock)
```

Base class for head blocks.

#### <a id="mknodes.pages.templateblocks.ExtraHeadBlock"></a>`ExtraHeadBlock`

```python
class ExtraHeadBlock(Block)
```

Block for extra HEAD content.

Can be used for stuff not covered by other blocks, like changing the
indexing rules.

##### <a id="mknodes.pages.templateblocks.ExtraHeadBlock.set_redirect_url"></a>`set_redirect_url`

```python
def set_redirect_url(url: str) -> None
```

Set a URL which the page should redirect to.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `url` | `str` | URL to redirect to |  |

##### <a id="mknodes.pages.templateblocks.ExtraHeadBlock.set_robots_rule"></a>`set_robots_rule`

```python
def set_robots_rule(rule: str | None = None) -> None
```

Set a rule for search robots.

For valid rule values, check
https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `rule` | `str \| None` | Rule to apply for robots | None |

#### <a id="mknodes.pages.templateblocks.HtmlBlock"></a>`HtmlBlock`

```python
class HtmlBlock(BaseBlock)
```

Base class for blocks which usually contain HTML content.

##### <a id="mknodes.pages.templateblocks.HtmlBlock.__init__"></a>`__init__`

```python
def __init__(block_id: str, *, parent: mk.MkPage | mk.MkNav | None = None) -> None
```

Constructor.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `block_id` | `str` | Name of the block |  |
| `parent` | `mk.MkPage \| mk.MkNav \| None` | Parent node | None |

##### <a id="mknodes.pages.templateblocks.HtmlBlock.block_content"></a>`block_content`

```python
def block_content(md: markdown.Markdown | None = None) -> str
```

Return the actual block content.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `md` | `markdown.Markdown \| None` | Markdown parser to use | None |

#### <a id="mknodes.pages.templateblocks.LibsBlock"></a>`LibsBlock`

```python
class LibsBlock(BaseJSBlock)
```

Block for additional libraries.

#### <a id="mknodes.pages.templateblocks.ScriptsBlock"></a>`ScriptsBlock`

```python
class ScriptsBlock(BaseJSBlock)
```

Block for JavaScripts at end of BODY.

#### <a id="mknodes.pages.templateblocks.SiteMetaBlock"></a>`SiteMetaBlock`

```python
class SiteMetaBlock(Block)
```

Block for meta tags in HEAD.

#### <a id="mknodes.pages.templateblocks.StylesBlock"></a>`StylesBlock`

```python
class StylesBlock(BaseBlock)
```

Block for additional stylesheets.

##### <a id="mknodes.pages.templateblocks.StylesBlock.add_css"></a>`add_css`

```python
def add_css(css: str | dict[str, Any]) -> None
```

Add CSS in form of a string or a CSS-rule like dictionary.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `css` | `str \| dict[str, Any]` | A string or dict containing CSS |  |

#### <a id="mknodes.pages.templateblocks.Super"></a>`Super`

```python
class Super
```

Simple class to use for the jinja super expression.

#### <a id="mknodes.pages.templateblocks.TitleBlock"></a>`TitleBlock`

```python
class TitleBlock(BaseBlock)
```

Block wrapping the HTML title.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.page_section._**

```python
@nav.route.page("Templates", hide="toc", status="new")
def _(page: mk.MkPage) -> None:
    page += mk.MkTemplate("pages/page_templates.jinja")
    assert page.template is not None
    page.template.announce.content = mk.MkMetadataBadges(typ="classifiers")
    page.template.footer.content = mk.MkProgressBar(50)
    code = "information = 'You can even put MkNodes here!'"
    page.template.tabs.content = mk.MkCode(f"{code}")
    page.template.hero.content = mk.MkHeader("A header!")
    css = {
        ":root": {
            "--md-primary-fg-color": "#FF0000",
            "--md-primary-fg-color--light": "#FF0000",
            "--md-primary-fg-color--dark": "#FF0000",
        },
    }
    page.template.styles.add_css(css)

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={},
          plugins=[Plugin('mkdocstrings')],
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
  source_line_no: 54
hide:
- toc
status: new
title: Templates

```

</details>

</details>
