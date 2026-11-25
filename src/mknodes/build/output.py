"""Build output: everything a node tree produced, independent of the target."""

from __future__ import annotations

import dataclasses
from datetime import datetime
import pathlib
import posixpath
from typing import TYPE_CHECKING, Any

from mknodes.utils import resources


if TYPE_CHECKING:
    from collections.abc import Iterator

    from mknodes.info import contexts
    from mknodes.utils.diagnostics import Diagnostic


@dataclasses.dataclass
class NavItem:
    """An entry of the site navigation.

    Either a link to a page / URL (`target` set) or a section (`children` set).
    """

    title: str
    target: str | None = None
    """Page path (relative to the docs root) or an external URL."""
    children: list[NavItem] = dataclasses.field(default_factory=list)

    @property
    def is_section(self) -> bool:
        return self.target is None

    def iter_targets(self) -> Iterator[str]:
        if self.target:
            yield self.target
        for child in self.children:
            yield from child.iter_targets()


@dataclasses.dataclass
class Script:
    """A script to include in every page."""

    path: str
    """URL or path relative to the docs root."""
    defer: bool = False
    async_: bool = False
    typ: str | None = None


@dataclasses.dataclass
class SiteMetadata:
    """Site metadata inferred from the project."""

    site_name: str | None = None
    site_description: str | None = None
    site_author: str | None = None
    repo_url: str | None = None
    copyright: str | None = None
    social: list[dict[str, str]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_context(cls, ctx: contexts.ProjectContext) -> SiteMetadata:
        info = ctx.metadata
        return cls(
            site_name=info.distribution_name,
            site_description=info.summary,
            site_author=info.author_name,
            repo_url=info.repository_url,
            copyright=f"Copyright © {datetime.now().year} {info.author_name}",
            social=list(info.social_info or []),
        )


@dataclasses.dataclass
class BuildOutput:
    """Everything a node tree produced, independent of the target.

    Pages are rendered in one Markdown flavour (see `mknodes.rendering`). Exporters /
    site generators turn this into files or into the input of a static site engine.
    """

    pages: dict[str, str] = dataclasses.field(default_factory=dict)
    """Markdown pages: path relative to the docs root -> Markdown."""
    assets: dict[str, str | bytes] = dataclasses.field(default_factory=dict)
    """Static files: path relative to the docs root -> content (CSS, JS, images, ...)."""
    nav: list[NavItem] = dataclasses.field(default_factory=list)
    """Navigation tree."""
    markdown_extensions: dict[str, dict[str, Any]] = dataclasses.field(default_factory=dict)
    """Python-Markdown extensions required by the pages: name -> config."""
    extra_css: list[str] = dataclasses.field(default_factory=list)
    """Stylesheets: URLs or paths relative to the docs root (contained in `assets`)."""
    extra_javascript: list[Script] = dataclasses.field(default_factory=list)
    """Scripts: URLs or paths relative to the docs root (contained in `assets`)."""
    templates: dict[str, str] = dataclasses.field(default_factory=dict)
    """Theme template overrides (Material-style Jinja blocks): filename -> template."""
    extra: dict[str, Any] = dataclasses.field(default_factory=dict)
    """Theme variables (`extra` in MkDocs / Zensical configs)."""
    metadata: SiteMetadata = dataclasses.field(default_factory=SiteMetadata)
    """Site metadata inferred from the project."""
    edit_paths: dict[str, str] = dataclasses.field(default_factory=dict)
    """Page path -> repository path of the source that generated it."""
    page_resources: dict[str, resources.Resources] = dataclasses.field(default_factory=dict)
    """Page path -> resources required by that page."""
    flavor: str = "material"
    """Markdown flavour the pages are rendered in."""
    diagnostics: list[Diagnostic] = dataclasses.field(default_factory=list)
    """Problems reported while building (failed nodes / blocks, broken fences, references)."""

    @property
    def files(self) -> dict[str, str | bytes]:
        """Pages and assets combined."""
        return {**self.assets, **self.pages}

    @property
    def resources(self) -> resources.Resources:
        """Resources of all pages merged into one."""
        merged = resources.Resources()
        for res in self.page_resources.values():
            merged.merge(res)
        return merged

    def __repr__(self) -> str:
        return f"{type(self).__name__}(pages={len(self.pages)}, assets={len(self.assets)})"


def nav_from_dict(dct: dict[str, Any]) -> list[NavItem]:
    """Convert a MkNodes nav dict (`MkNav.nav.to_nav_dict()`) into `NavItem`s."""
    items = []
    for title, value in dct.items():
        if isinstance(value, dict):
            items.append(NavItem(title=str(title), children=nav_from_dict(value)))
        else:
            target = str(value)
            if "://" not in target:
                target = pathlib.PurePath(target).as_posix()
            items.append(NavItem(title=str(title), target=target))
    return items


def nav_to_markdown(items: list[NavItem], level: int = 0) -> str:
    """Render the nav as nested Markdown list of links (literate-nav / SUMMARY.md format)."""
    lines: list[str] = []
    indent = "    " * level
    for item in items:
        if item.is_section:
            lines.append(f"{indent}- {item.title}")
            if children := nav_to_markdown(item.children, level + 1):
                lines.append(children)
        else:
            assert item.target
            lines.append(f"{indent}- [{item.title}]({_link(item.target)})")
    return "\n".join(lines)


def _link(target: str) -> str:
    """Return a link target usable in Markdown (spaces encoded, posix separators)."""
    return posixpath.normpath(target).replace(" ", "%20") if "://" not in target else target
