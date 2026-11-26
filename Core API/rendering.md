# Rendering

Renderers turn nodes into the Markdown of a flavour (`material`, the default, or
`github`). See [Markdown flavours](<../The nodes/markdown_flavours.md>) for what changes
between them.

**Example**

```py
import mknodes as mk
from mknodes import rendering

node = mk.MkAdmonition("Careful!", typ="warning")
node.to_markdown(flavor="github")  # > [!WARNING] ...

with rendering.use(rendering.get_renderer("github")):
    str(node)  # nested nodes, templates and str() render in that flavour
```

## <a id="mknodes.rendering.get_renderer"></a>`mknodes.rendering.get_renderer`

```python
def get_renderer(flavor: str | Renderer | None = None) -> Renderer
```

Return a renderer for given flavour name (None: the active renderer).

## <a id="mknodes.rendering.use"></a>`mknodes.rendering.use`

```python
def use(renderer: Renderer) -> Generator[Renderer]
```

Make given renderer the active one inside the context.

## <a id="mknodes.rendering.Renderer"></a>`mknodes.rendering.Renderer`

```python
class Renderer
```

Renders nodes as Markdown of one flavour.

Subclass it for a new flavour and register rules with the `rule` decorator.
Rule lookup walks the node class hierarchy: a rule for `MkBlock` also renders
`MkDetailsBlock`, unless a class in between renders itself (defines
`get_content` / `to_md_unprocessed`) and has no rule of its own.
Rules of parent renderer classes are inherited.

## <a id="mknodes.rendering.MaterialRenderer"></a>`mknodes.rendering.MaterialRenderer`

```python
class MaterialRenderer(Renderer)
```

Material for MkDocs flavour (the default): nodes render themselves.

## <a id="mknodes.rendering.github.GithubRenderer"></a>`mknodes.rendering.github.GithubRenderer`

```python
class GithubRenderer(base.Renderer)
```

Renders GitHub flavoured Markdown (READMEs, issues, wikis).

### <a id="mknodes.rendering.github.GithubRenderer.finalize"></a>`finalize`

```python
def finalize(output: BuildOutput, root: mk.MkNav) -> None
```

Link `[title][dotted.path]` references (GitHub has no autorefs).

## <a id="mknodes.rendering.myst.MystRenderer"></a>`mknodes.rendering.myst.MystRenderer`

```python
class MystRenderer(github.GithubRenderer)
```

Renders MyST Markdown for Sphinx (`myst-parser` + `sphinx-design`).

### <a id="mknodes.rendering.myst.MystRenderer.finalize"></a>`finalize`

```python
def finalize(output: BuildOutput, root: mk.MkNav) -> None
```

Link `[title][dotted.path]` references, add MyST targets for the anchors.

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
title: Rendering

```

</details>

</details>
