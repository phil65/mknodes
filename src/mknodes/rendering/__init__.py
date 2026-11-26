"""Renderers: turn a node tree into the Markdown of a given flavour.

```python
import mknodes as mk

node = mk.MkAdmonition("Careful!", typ="warning")
node.to_markdown()  # Material for MkDocs (default)
node.to_markdown(flavor="github")  # GitHub: > [!WARNING] ...
```
"""

import importlib

from mknodes.rendering.base import (
    MaterialRenderer,
    Renderer,
    Rule,
    current,
    in_jinja_pass,
    jinja_pass,
    literal,
    use,
)


# Flavour name -> renderer class (or `module:Class` path, imported on first use).
FLAVORS: dict[str, type[Renderer] | str] = {
    "material": MaterialRenderer,
    "github": "mknodes.rendering.github:GithubRenderer",
    "mdbook": "mknodes.rendering.mdbook:MdbookRenderer",
    "myst": "mknodes.rendering.myst:MystRenderer",
}


def register(renderer: type[Renderer]) -> type[Renderer]:
    """Register a renderer class under its `name` (usable as class decorator)."""
    FLAVORS[renderer.name] = renderer
    return renderer


def get_renderer_class(flavor: str) -> type[Renderer]:
    """Return the renderer class for given flavour name."""
    try:
        renderer = FLAVORS[flavor]
    except KeyError:
        msg = f"Unknown flavor {flavor!r}. Available: {', '.join(FLAVORS)}"
        raise ValueError(msg) from None
    if isinstance(renderer, str):
        module_name, _, class_name = renderer.partition(":")
        renderer = getattr(importlib.import_module(module_name), class_name)
        FLAVORS[flavor] = renderer
    assert isinstance(renderer, type)
    return renderer


def get_renderer(flavor: str | Renderer | None = None) -> Renderer:
    """Return a renderer for given flavour name (None: the active renderer)."""
    match flavor:
        case None:
            return current()
        case Renderer():
            return flavor
        case str():
            return get_renderer_class(flavor)()


__all__ = [
    "FLAVORS",
    "MaterialRenderer",
    "Renderer",
    "Rule",
    "current",
    "get_renderer",
    "get_renderer_class",
    "in_jinja_pass",
    "jinja_pass",
    "literal",
    "register",
    "use",
]
