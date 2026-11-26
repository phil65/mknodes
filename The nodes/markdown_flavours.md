# Markdown flavours

Nodes render to the Markdown of a *flavour*. The default flavour, `material`, is
Markdown for [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) /
Zensical, using Python-Markdown / PyMdown extensions (admonitions, tabs, attribute
lists, ...). The `github` flavour produces GitHub flavoured Markdown for READMEs, issues
and wikis: alerts, `<details>` blocks, `<kbd>` and plain fenced code. The `mdbook`
flavour is the GitHub flavour for [mdBook](https://rust-lang.github.io/mdBook/)
(optionally with `mdbook-admonish` admonitions), the `myst` flavour the GitHub flavour
with MyST directives (admonitions, dropdowns, tab sets, `{code-block}`) for Sphinx.

```py
import mknodes as mk

node = mk.MkAdmonition("Careful!", typ="warning")
node.to_markdown()  # Material (default)
node.to_markdown(flavor="github")  # > [!WARNING] ...
```

A whole site can be generated in a flavour with the CLI. The `markdown` engine writes
plain Markdown files plus a `SUMMARY.md` nav and defaults to `github`:

```bash
mknodes generate --engine markdown --flavor github --generated-dir build/markdown
```

Each engine has a default flavour, see [Site engines](<../Site generator/site_engines.md>).
The flavour can also be set with the `flavor` setting (see
[Configuration](<../Site generator/configuration.md>)) or passed to
[DocBuilder](../Core%20API/build_step.md#mknodes.DocBuilder). The renderer classes are documented in
[Core API / Rendering](<../Core API/rendering.md>).

## Side by side

Each node is shown as rendered on this site, followed by its Markdown in both flavours.

### Admonition

> [!WARNING]
> **Careful**
>
> Content with **Markdown**.

**Material**

```markdown
!!! warning "Careful"
    Content with **Markdown**.
```

**GitHub**

```markdown
> [!WARNING]
> **Careful**
>
> Content with **Markdown**.
```

### Collapsible admonition

<details>
<summary>Click me</summary>

Hidden until clicked.

</details>

**Material**

```markdown
??? info "Click me"
    Hidden until clicked.
```

**GitHub**

```markdown
<details>
<summary>Click me</summary>

Hidden until clicked.

</details>
```

### Tabs

<details open>
<summary>Python</summary>

```py
import mknodes as mk
```

</details>

<details>
<summary>Shell</summary>

```bash
pip install mknodes
```

</details>

**Material**

````markdown
===! "Python"
    ``` {.py }
    import mknodes as mk
    ```

=== "Shell"
    ``` {.bash }
    pip install mknodes
    ```
````

**GitHub**

````markdown
<details open>
<summary>Python</summary>

```py
import mknodes as mk
```

</details>

<details>
<summary>Shell</summary>

```bash
pip install mknodes
```

</details>
````

### Code block with title

**build.py**

```py
import mknodes as mk

nav = mk.MkNav()
```

**Material**

````markdown
``` {.py  title='build.py'}
import mknodes as mk

nav = mk.MkNav()
```
````

**GitHub**

````markdown
**build.py**

```py
import mknodes as mk

nav = mk.MkNav()
```
````

### Keys

<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Del</kbd>

**Material**

```markdown
++ctrl+alt+del++
```

**GitHub**

```markdown
<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Del</kbd>
```

### Details block

<details>
<summary>More info</summary>

Some details.

</details>

**Material**

```markdown
/// details | More info
    type: tip

Some details.
///
```

**GitHub**

```markdown
<details>
<summary>More info</summary>

Some details.

</details>
```

### Definition list

<dl>
<dt>MkNav</dt>
<dd>

A section of the documentation.

</dd>
<dt>MkPage</dt>
<dd>

A page of the documentation.

</dd>
</dl>

**Material**

```markdown
MkNav
:   A section of the documentation.
MkPage
:   A page of the documentation.
```

**GitHub**

```markdown
<dl>
<dt>MkNav</dt>
<dd>

A section of the documentation.

</dd>
<dt>MkPage</dt>
<dd>

A page of the documentation.

</dd>
</dl>
```

### Critic markup

<ins>

Inserted text

</ins>

**Material**

```markdown
{++

Inserted text

++}
```

**GitHub**

```markdown
<ins>

Inserted text

</ins>
```

### Progress bar

`██████░░░░` 60%

**Material**

```markdown
[=60% "60%"]
```

**GitHub**

```markdown
`██████░░░░` 60%
```

### Link with icon

[<img src="https://api.iconify.design/mdi/github.svg?height=16" alt="github"> Repository](https://github.com/phil65/mknodes)

**Material**

```markdown
[:mdi-github: Repository](https://github.com/phil65/mknodes)
```

**GitHub**

```markdown
[<img src="https://api.iconify.design/mdi/github.svg?height=16" alt="github"> Repository](https://github.com/phil65/mknodes)
```

### Material badge

<img src="https://api.iconify.design/mdi/tag.svg?height=16" alt="tag"> <code>4.1.0</code>

**Material**

```markdown
<span class="md-typeset mdx-badge">
  <span class="mdx-badge__icon">:mdi-tag:</span>
  <span class="mdx-badge__text">4.1.0</span>
</span>
```

**GitHub**

```markdown
<img src="https://api.iconify.design/mdi/tag.svg?height=16" alt="tag"> <code>4.1.0</code>
```

### Docstrings

#### <a id="mknodes.rendering.github.alert"></a>`mknodes.rendering.github.alert`

```python
def alert(typ: str, text: str, title: str | None = None) -> str
```

Return a GitHub alert block (`> [!NOTE]`).

**Material**

````markdown
::: mknodes.rendering.github.alert
    options:
      heading_level: 4
      show_root_heading: True
````

**GitHub**

````markdown
#### <a id="mknodes.rendering.github.alert"></a>`mknodes.rendering.github.alert`

```python
def alert(typ: str, text: str, title: str | None = None) -> str
```

Return a GitHub alert block (`> [!NOTE]`).
````

## GitHub rules

How the `github` flavour renders each node. A node either has a *rule* (a render
function registered with `GithubRenderer.rule`, also used for subclasses which don't
render themselves), an `[output.github]` *template* in its node file, or renders its
*default* Markdown, the same as in the `material` flavour. That is fine for plain
Markdown (text, tables, lists); output that needs Markdown extensions (last column) may
not display on GitHub. Containers rendering their default Markdown still render their
children in the GitHub flavour, and hand-written Material admonitions / tabs in page text
get converted.

| Node                                               | GitHub output            | Details                                                                      | Extensions of the Material output                        |
| -------------------------------------------------- | ------------------------ | ---------------------------------------------------------------------------- | -------------------------------------------------------- |
| [MkAdmonition](Container%20nodes/mkadmonition.md#mknodes.MkAdmonition)               | Rule                     |                                                                              | `admonition`, `pymdownx.details`, `pymdownx.superfences` |
| [MkAnnotations](Container%20nodes/mkannotations.md#mknodes.MkAnnotations)             | Default                  |                                                                              | `pymdownx.superfences`                                   |
| [MkBadge](Image%20nodes/mkbadge.md#mknodes.MkBadge)                         | Rule                     | A shields.io badge image (GitHub drops inline SVG).                          |                                                          |
| [MkBinaryImage](Image%20nodes/mkbinaryimage.md#mknodes.MkBinaryImage)             | Template of `MkImage`    | `[output.github]` in the node file                                           |                                                          |
| `MkBlock`                                          | Rule                     | Unknown PyMdown blocks: keep the content, drop the block.                    |                                                          |
| [MkBlockQuote](Container%20nodes/mkblockquote.md#mknodes.MkBlockQuote)               | Default                  |                                                                              |                                                          |
| [MkCard](Image%20nodes/mkcard.md#mknodes.MkCard)                           | Default                  |                                                                              |                                                          |
| [MkChangelog](About-the-project%20nodes/mkchangelog.md#mknodes.MkChangelog)                 | Default                  |                                                                              |                                                          |
| [MkClassDiagram](Documentation%20nodes/mkclassdiagram.md#mknodes.MkClassDiagram)           | Rule of `MkCode`         | Fenced code block with plain language info string (no attributes).           | `pymdownx.superfences`                                   |
| [MkClassTable](Documentation%20nodes/mkclasstable.md#mknodes.MkClassTable)               | Default                  |                                                                              | `tables`                                                 |
| [MkCliDoc](Documentation%20nodes/mkclidoc.md#mknodes.MkCliDoc)                       | Default                  |                                                                              |                                                          |
| [MkCode](Container%20nodes/mkcode.md#mknodes.MkCode)                           | Rule                     | Fenced code block with plain language info string (no attributes).           | `pymdownx.highlight`, `pymdownx.superfences`             |
| [MkCodeOfConduct](About-the-project%20nodes/mkcodeofconduct.md#mknodes.MkCodeOfConduct)         | Default                  |                                                                              |                                                          |
| [MkCommandOutput](Special%20nodes/mkcommandoutput.md#mknodes.MkCommandOutput)         | Default                  |                                                                              |                                                          |
| [MkCommentedCode](Documentation%20nodes/mkcommentedcode.md#mknodes.MkCommentedCode)         | Default                  |                                                                              |                                                          |
| [MkCommitConventions](About-the-project%20nodes/mkcommitconventions.md#mknodes.MkCommitConventions) | Default                  |                                                                              |                                                          |
| [MkCompactAdmonition](Base%20nodes/mkcompactadmonition.md#mknodes.MkCompactAdmonition) | Rule                     |                                                                              |                                                          |
| [MkConfigSetting](Documentation%20nodes/mkconfigsetting.md#mknodes.MkConfigSetting)         | Default                  |                                                                              |                                                          |
| [MkContainer](Container%20nodes/mkcontainer.md#mknodes.MkContainer)                 | Default                  |                                                                              |                                                          |
| [MkCritic](Base%20nodes/mkcritic.md#mknodes.MkCritic)                       | Rule                     |                                                                              | `pymdownx.critic`                                        |
| `MkDataClassInfo`                                  | Default                  |                                                                              |                                                          |
| [MkDefinitionList](Container%20nodes/mkdefinitionlist.md#mknodes.MkDefinitionList)       | Rule                     |                                                                              | `def_list`                                               |
| `MkDependencyGroups`                               | Default                  |                                                                              | `tables`                                                 |
| [MkDependencyTable](About-the-project%20nodes/mkdependencytable.md#mknodes.MkDependencyTable)     | Default                  |                                                                              | `tables`                                                 |
| [MkDetailsBlock](Container%20nodes/mkdetailsblock.md#mknodes.MkDetailsBlock)           | Rule                     |                                                                              | `pymdownx.blocks.details`                                |
| `MkDevEnvSetup`                                    | Default                  |                                                                              |                                                          |
| [MkDevTools](About-the-project%20nodes/mkdevtools.md#mknodes.MkDevTools)                   | Default                  |                                                                              |                                                          |
| [MkDiagram](Presentation%20nodes/mkdiagram.md#mknodes.MkDiagram)                     | Rule of `MkCode`         | Fenced code block with plain language info string (no attributes).           | `pymdownx.superfences`                                   |
| [MkDocStrings](../Get%20started/a_quick_node_tour.md#mknodes.MkDocStrings)               | Rule                     | API docs rendered from Griffe (GitHub has no mkdocstrings).                  |                                                          |
| [MkFootNotes](Container%20nodes/mkfootnotes.md#mknodes.MkFootNotes)                 | Default                  |                                                                              | `footnotes`                                              |
| [MkHeader](Base%20nodes/mkheader.md#mknodes.MkHeader)                       | Default                  |                                                                              |                                                          |
| [MkHtmlBlock](Container%20nodes/mkhtmlblock.md#mknodes.MkHtmlBlock)                 | Rule                     | The element itself (`/// html \| picture` -> `<picture>...</picture>`).      | `pymdownx.blocks.html`                                   |
| [MkHtmlTable](Container%20nodes/mkhtmltable.md#mknodes.MkHtmlTable)                 | Rule                     | HTML table with unescaped Markdown cells (Material: `<table markdown="1">`). |                                                          |
| [MkIFrame](Special%20nodes/mkiframe.md#mknodes.MkIFrame)                       | Default                  |                                                                              |                                                          |
| [MkIcon](Image%20nodes/mkicon.md#mknodes.MkIcon)                           | Rule                     |                                                                              |                                                          |
| [MkImage](Image%20nodes/mkimage.md#mknodes.MkImage)                         | Template                 | `[output.github]` in the node file                                           |                                                          |
| [MkImageCompare](Image%20nodes/mkimagecompare.md#mknodes.MkImageCompare)           | Default                  |                                                                              |                                                          |
| [MkImageSlideshow](Image%20nodes/mkimageslideshow.md#mknodes.MkImageSlideshow)       | Default                  |                                                                              |                                                          |
| [MkInclude](Special%20nodes/mkinclude.md#mknodes.MkInclude)                     | Default                  |                                                                              |                                                          |
| [MkInstallGuide](About-the-project%20nodes/mkinstallguide.md#mknodes.MkInstallGuide)           | Default                  |                                                                              |                                                          |
| `MkJupyterLite`                                    | Default                  |                                                                              |                                                          |
| [MkKeys](Base%20nodes/mkkeys.md#mknodes.MkKeys)                           | Rule                     |                                                                              | `pymdownx.keys`                                          |
| [MkLicense](About-the-project%20nodes/mklicense.md#mknodes.MkLicense)                     | Default                  |                                                                              |                                                          |
| [MkLink](Base%20nodes/mklink.md#mknodes.MkLink)                           | Rule                     |                                                                              |                                                          |
| [MkList](Container%20nodes/mklist.md#mknodes.MkList)                           | Default                  |                                                                              | `def_list`                                               |
| [MkLlm](Base%20nodes/mkllm.md#mknodes.MkLlm)                             | Default                  |                                                                              |                                                          |
| [MkMaterialBadge](Image%20nodes/mkmaterialbadge.md#mknodes.MkMaterialBadge)         | Rule                     |                                                                              |                                                          |
| [MkMetadataBadges](About-the-project%20nodes/mkmetadatabadges.md#mknodes.MkMetadataBadges)       | Default                  |                                                                              |                                                          |
| [MkModuleTable](Documentation%20nodes/mkmoduletable.md#mknodes.MkModuleTable)             | Default                  |                                                                              | `tables`                                                 |
| [MkPipDepTree](About-the-project%20nodes/mkpipdeptree.md#mknodes.MkPipDepTree)               | Rule of `MkCode`         | Fenced code block with plain language info string (no attributes).           | `pymdownx.superfences`                                   |
| [MkProgressBar](Base%20nodes/mkprogressbar.md#mknodes.MkProgressBar)             | Rule                     |                                                                              | `pymdownx.progressbar`                                   |
| [MkPyDeps](About-the-project%20nodes/mkpydeps.md#mknodes.MkPyDeps)                       | Default                  |                                                                              |                                                          |
| `MkPyScript`                                       | Default                  |                                                                              |                                                          |
| `MkPyodideTerminal`                                | Default                  |                                                                              |                                                          |
| [MkReprRawRendered](Presentation%20nodes/mkreprrawrendered.md#mknodes.MkReprRawRendered)     | Default                  |                                                                              |                                                          |
| [MkShields](About-the-project%20nodes/mkshields.md#mknodes.MkShields)                     | Default                  |                                                                              |                                                          |
| [MkShowcase](Container%20nodes/mkshowcase.md#mknodes.MkShowcase)                   | Default                  |                                                                              |                                                          |
| [MkSpeechBubble](Base%20nodes/mkspeechbubble.md#mknodes.MkSpeechBubble)           | Rule                     |                                                                              |                                                          |
| `MkTab`                                            | Rule                     |                                                                              | `pymdownx.tabbed`                                        |
| `MkTabBlock`                                       | Rule                     |                                                                              | `pymdownx.blocks.tab`                                    |
| `MkTabContainer`                                   | Rule                     | Tabs become `<details>` blocks, the selected (or first) one expanded.        |                                                          |
| [MkTabbed](Container%20nodes/mktabbed.md#mknodes.MkTabbed)                       | Rule of `MkTabContainer` | Tabs become `<details>` blocks, the selected (or first) one expanded.        | `pymdownx.tabbed`, `pymdownx.superfences`                |
| [MkTabbedBlocks](Container%20nodes/mktabbedblocks.md#mknodes.MkTabbedBlocks)           | Rule of `MkTabContainer` | Tabs become `<details>` blocks, the selected (or first) one expanded.        | `pymdownx.blocks.tab`                                    |
| [MkTable](Container%20nodes/mktable.md#mknodes.MkTable)                         | Default                  |                                                                              | `tables`                                                 |
| [MkTaskList](Container%20nodes/mktasklist.md#mknodes.MkTaskList)                   | Default                  |                                                                              | `pymdownx.tasklist`                                      |
| [MkTemplate](Base%20nodes/mktemplate.md#mknodes.MkTemplate)                   | Default                  |                                                                              |                                                          |
| [MkText](Base%20nodes/mktext.md#mknodes.MkText)                           | Default                  |                                                                              |                                                          |
| [MkTimeline](Presentation%20nodes/mktimeline.md#mknodes.MkTimeline)                   | Default                  |                                                                              |                                                          |
| [MkTreeView](Presentation%20nodes/mktreeview.md#mknodes.MkTreeView)                   | Rule of `MkCode`         | Fenced code block with plain language info string (no attributes).           | `pymdownx.highlight`, `pymdownx.superfences`             |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.nodes_section._**

```python
@nav.route.page("Markdown flavours", icon="material/language-markdown")
def _(page: mk.MkPage) -> None:
    documented = [
        *BASE_NODES,
        *IMAGE_NODES,
        *PRESENTATION_NODES,
        *DOCUMENTATION_NODES,
        *ABOUT_THE_PROJECT_NODES,
        *CONTAINER_NODES,
        *SPECIAL_NODES,
    ]
    flavors.build_page(page, documented)

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={'md_in_html': {}, 'tables': {}},
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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/nodes_section.py
  source_function: _
  source_line_no: 123
icon: material/language-markdown
title: Markdown flavours

```

</details>

</details>
