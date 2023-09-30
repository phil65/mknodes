from __future__ import annotations

import abc
import collections.abc
import dataclasses

from typing import TYPE_CHECKING, Literal

from mknodes.utils import mergehelpers, reprhelpers


if TYPE_CHECKING:
    from mknodes.pages import pagetemplate


@dataclasses.dataclass(frozen=True)
class Package:
    package_name: str
    extras: list[str] = dataclasses.field(default_factory=list)


class Extension(dict):
    def __init__(self, extension_name: str, **kwargs):
        super().__init__(**kwargs)
        self.extension_name = extension_name

    def __str__(self):
        return self.extension_name

    def __repr__(self):
        return f"{type(self).__name__}({self.extension_name!r})"

    def __hash__(self):
        return hash(self.extension_name + str(dict(self)))

    def as_mkdocs_dict(self):
        return {self.extension_name: dict(self)}


class Plugin(dict):
    def __init__(self, plugin_name: str, **kwargs):
        super().__init__(**kwargs)
        self.plugin_name = plugin_name

    def __str__(self):
        return self.plugin_name

    def __repr__(self):
        return f"{type(self).__name__}({self.plugin_name!r})"

    def __hash__(self):
        return hash(self.plugin_name + str(dict(self)))

    def as_mkdocs_dict(self):
        return {self.plugin_name: dict(self)}


@dataclasses.dataclass(frozen=True)
class CSSLink:
    link: str
    color_scheme: Literal["dark", "light"] | None = None
    onload: str | None = None

    def __repr__(self):
        return reprhelpers.dataclass_repr(self)

    def __str__(self):
        return self.link

    def __fspath__(self):
        return self.link

    def to_html(self):
        if self.color_scheme == "light":
            media = ' media="(prefers-color-scheme:light)"'
        elif self.color_scheme == "dark":
            media = ' media="(prefers-color-scheme:dark)"'
        else:
            media = ""
        onload = f" onload={self.onload!r}" if self.onload else ""
        # return '<link rel="stylesheet" href="{{ base_url }}/{path}" />'
        return f'<link rel="stylesheet" href={self.link!r}{media}{onload}/>'


@dataclasses.dataclass(frozen=True)
class JSLink:
    link: str
    defer: bool = False
    async_: bool = False
    crossorigin: Literal["anonymous", "use-credentials"] | None = None
    typ: str = ""
    is_library: bool = False

    def __repr__(self):
        return reprhelpers.dataclass_repr(self)

    def __str__(self):
        return self.link

    def __fspath__(self):
        return self.link

    def to_html(self) -> str:
        html = f'<script src="{self.link}"'
        if self.typ:
            html += f' type="{self.typ}"'
        if self.defer:
            html += " defer"
        if self.async_:
            html += " async"
        if self.crossorigin:
            html += f' crossorigin="{self.crossorigin}"'
        html += "></script>"
        return html


@dataclasses.dataclass(frozen=True)
class JSFile:
    link: str
    defer: bool = False
    async_: bool = False
    crossorigin: Literal["anonymous", "use-credentials"] | None = None
    typ: str = ""
    is_library: bool = False

    def __repr__(self):
        return reprhelpers.dataclass_repr(self)

    def __str__(self):
        return self.link

    def __fspath__(self):
        return self.link

    def to_html(self) -> str:
        html = f'<script src="{self.link}"'
        if self.typ:
            html += f' type="{self.typ}"'
        if self.defer:
            html += " defer"
        if self.async_:
            html += " async"
        if self.crossorigin:
            html += f' crossorigin="{self.crossorigin}"'
        html += "></script>"
        return html


@dataclasses.dataclass(frozen=True)
class CSSFile:
    link: str
    color_scheme: Literal["dark", "light"] | None = None
    onload: str | None = None

    def __repr__(self):
        return reprhelpers.dataclass_repr(self)

    def __str__(self):
        return self.link

    def __fspath__(self):
        return self.link

    def to_html(self):
        if self.color_scheme == "light":
            media = ' media="(prefers-color-scheme:light)"'
        elif self.color_scheme == "dark":
            media = ' media="(prefers-color-scheme:dark)"'
        else:
            media = ""
        onload = f" onload={self.onload!r}" if self.onload else ""
        # return '<link rel="stylesheet" href="{{ base_url }}/{path}" />'
        return f'<link rel="stylesheet" href={self.link!r}{media}{onload}/>'


class CSSText:
    def __init__(self, filename, content):
        self.filename = filename
        self.content = content

    def __hash__(self):
        return hash(self.content)

    def __repr__(self):
        return f"{type(self).__name__}({self.filename!r})"


class RawCSS:
    def __init__(self, content):
        self.content = content

    def __hash__(self):
        return hash(self.content)

    def to_html(self):
        # content = self.content.replace("\n", "")
        return f"<style>\n{self.content}\n</style>"


class Asset:
    def __init__(self, filename, content, target=None):
        self.filename = filename
        self.content = content
        self.target_dir = target

    def __hash__(self):
        return hash(self.content)

    def __repr__(self):
        return f"{type(self).__name__}({self.filename!r})"


@dataclasses.dataclass
class Resources(collections.abc.Mapping, metaclass=abc.ABCMeta):
    css: list[CSSFile | CSSLink | CSSText] = dataclasses.field(default_factory=list)
    """A filepath->filecontent dictionary containing the required CSS."""
    templates: list[pagetemplate.PageTemplate] = dataclasses.field(default_factory=list)
    """A list of required templates."""
    markdown_extensions: dict[str, dict] = dataclasses.field(default_factory=dict)
    """A extension_name->settings dictionary containing the required md extensions."""
    plugins: list[Plugin] = dataclasses.field(default_factory=list)
    """A set of required plugins. (Only for info purposes)"""
    js: list[JSFile | JSLink] = dataclasses.field(default_factory=list)
    """A list of JS file paths."""
    assets: list[Asset] = dataclasses.field(default_factory=list)
    """A list of additional assets required (static files which go into assets dir)."""

    def __getitem__(self, value):
        return getattr(self, value)

    def __setitem__(self, index, value):
        setattr(self, index, value)

    def __len__(self):
        return len(dataclasses.fields(self))

    def __iter__(self):
        return iter(i.name for i in dataclasses.fields(self))

    def __ior__(self, other):
        return self.merge(other)

    def __or__(self, other):
        return self.merge(other)

    @property
    def js_files(self):
        return [i for i in self.js if isinstance(i, JSFile)]

    @property
    def js_links(self):
        return [i for i in self.js if isinstance(i, JSLink)]

    def merge(self, other: collections.abc.Mapping, additive: bool = False):
        """Merge resources with another resources instance or dict.

        Adds resources from other to this instance.

        Arguments:
            other: The resources to merge into this one.
            additive: Merge strategy. Either additive or replace.
        """
        self.templates += other["templates"]
        if other_exts := other["markdown_extensions"]:
            exts = [self.markdown_extensions, other_exts]
            merged = mergehelpers.merge_extensions(exts)
            self.markdown_extensions = mergehelpers.merge_dicts(*merged)
        self.css = list(set(self.css + other["css"]))
        self.plugins = list(set(self.plugins + other["plugins"]))
        self.js = list(set(self.js + other["js"]))
        self.assets = list(set(self.assets + other["assets"]))
        return self


if __name__ == "__main__":
    link = CSSLink("test")
    print(repr(link))
    req = Resources(css=[CSSText("a.css", "CSS")])
    req2 = Resources(css=[CSSText("b.css", "CSS2")])
    req.merge(req2)
    print(req)
