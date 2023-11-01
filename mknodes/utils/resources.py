from __future__ import annotations

import abc
import collections.abc
import dataclasses

from typing import Any, ClassVar, Literal

from mknodes.utils import helpers, mergehelpers, reprhelpers


@dataclasses.dataclass(frozen=True)
class Package:
    """A python package requirement."""

    package_name: str
    extras: list[str] = dataclasses.field(default_factory=list)


class Extension(dict):
    """A markdown extension resource."""

    def __init__(self, extension_name: str, **kwargs: Any):
        """Constructor.

        Arguments:
            extension_name: Name of the extension
            kwargs: Optional settings for the extension
        """
        super().__init__(**kwargs)
        self.extension_name = extension_name

    def __str__(self):
        return self.extension_name

    def __repr__(self):
        return f"{type(self).__name__}({self.extension_name!r})"

    def __hash__(self):
        return hash(self.extension_name + str(dict(self)))

    def as_mkdocs_dict(self) -> dict[str, dict]:
        return {self.extension_name: dict(self)}


class Plugin(dict):
    """A plugin resource."""

    def __init__(self, plugin_name: str, **kwargs: Any):
        """Constructor.

        Arguments:
            plugin_name: Name of the plugin
            kwargs: Optional settings for the plugin
        """
        super().__init__(**kwargs)
        self.plugin_name = plugin_name

    def __str__(self):
        return self.plugin_name

    def __repr__(self):
        return f"{type(self).__name__}({self.plugin_name!r})"

    def __hash__(self):
        return hash(self.plugin_name + str(dict(self)))

    def as_mkdocs_dict(self) -> dict[str, dict]:
        return {self.plugin_name: dict(self)}


@dataclasses.dataclass(frozen=True)
class CSSFile:
    """CSS file resource."""

    link: str
    color_scheme: Literal["dark", "light"] | None = None
    onload: str | None = None

    def __repr__(self):
        return reprhelpers.get_dataclass_repr(self)

    def __str__(self):
        return self.link

    def __fspath__(self):
        return self.link

    def is_local(self) -> bool:
        """Whether the css file is a local resource."""
        return not helpers.is_url(self.link)

    def to_html(self) -> str:
        """Return html "link" element which can be put into an HTML page."""
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
class JSFile:
    """A JavaScript link resource."""

    link: str
    defer: bool = False
    async_: bool = False
    crossorigin: Literal["anonymous", "use-credentials"] | None = None
    typ: str = ""
    is_library: bool = False

    def __repr__(self):
        return reprhelpers.get_dataclass_repr(self)

    def __str__(self):
        return self.link

    def __fspath__(self):
        return str(self)

    def is_local(self) -> bool:
        """Whether the js file is a local resource."""
        return not helpers.is_url(self.link)

    def to_html(self) -> str:
        """Return html "script" element which can be put into an HTML page."""
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


class TextResource:
    EXTENSION: str
    filename: str | None
    content: str

    @property
    def resolved_filename(self) -> str:
        """Return a filename consisting of a user-set prefix + a hash value."""
        hashed = helpers.get_hash(self.content)
        return (
            f"{self.filename.removesuffix(self.EXTENSION)}_{hashed}{self.EXTENSION}"
            if self.filename
            else f"{hashed}{self.EXTENSION}"
        )

    def get_asset(self) -> Asset:
        return Asset(filename=self.resolved_filename, content=self.content)

    def __hash__(self):
        return hash(self.content)

    def __repr__(self):
        return reprhelpers.get_repr(self, filename=self.resolved_filename)


@dataclasses.dataclass(frozen=True, repr=False)
class CSSText(TextResource):
    """Class representing non-file-bound CSS."""

    EXTENSION: ClassVar = ".css"
    content: str
    filename: str | None

    def to_html(self) -> str:
        # content = self.content.replace("\n", "")
        return f"<style>\n{self.content}\n</style>"

    def get_cssfile(self) -> CSSFile:
        return CSSFile(link=self.resolved_filename)


@dataclasses.dataclass(frozen=True, repr=False)
class JSText(TextResource):
    """Class representing non-file-bound JavaScript code."""

    EXTENSION: ClassVar = ".js"
    content: str
    filename: str | None
    defer: bool = False
    async_: bool = False
    crossorigin: Literal["anonymous", "use-credentials"] | None = None
    typ: str = ""
    is_library: bool = False

    def get_jsfile(self) -> JSFile:
        return JSFile(
            link=self.resolved_filename,
            async_=self.async_,
            defer=self.defer,
            crossorigin=self.crossorigin,
            typ=self.typ,
            is_library=self.is_library,
        )


class Asset:
    """An asset resource."""

    def __init__(self, filename: str, content: str, target: str | None = None):
        """Constructor.

        Arguments:
            filename: Filename for the asset
            content: File content
            target: target directory for the asset file
        """
        self.filename = filename
        self.content = content
        self.target_dir = target

    def __hash__(self):
        return hash(self.content)

    def __repr__(self):
        return f"{type(self).__name__}({self.filename!r})"


@dataclasses.dataclass
class Resources(collections.abc.Mapping, metaclass=abc.ABCMeta):
    """A resource bundle containing different assets.

    Most of the time this class is used for bundling required resources
    for a specific node.
    """

    css: list[CSSType] = dataclasses.field(default_factory=list)
    """A filepath->filecontent dictionary containing the required CSS."""
    markdown_extensions: dict[str, dict] = dataclasses.field(default_factory=dict)
    """A extension_name->settings dictionary containing the required md extensions."""
    plugins: list[Plugin] = dataclasses.field(default_factory=list)
    """A set of required plugins. (Only for info purposes)"""
    js: list[JSType] = dataclasses.field(default_factory=list)
    """A list of JS file paths."""
    assets: list[Asset] = dataclasses.field(default_factory=list)
    """A list of additional assets required (static files which go into assets dir)."""
    packages: list[Package] = dataclasses.field(default_factory=list)
    """A list of required packages."""

    def __getitem__(self, value):
        return getattr(self, value)

    def __setitem__(self, index, value):
        setattr(self, index, value)

    def __contains__(self, other):
        if any(i == other for i in self.markdown_extensions):
            return True
        if any(i.plugin_name == other for i in self.plugins):
            return True
        return super().__contains__(other)

    def __len__(self):
        return len(dataclasses.fields(self))

    def __iter__(self):
        return iter(i.name for i in dataclasses.fields(self))

    def __ior__(self, other):
        return self.merge(other)

    def __or__(self, other):
        return self.merge(other)

    def remove(self, *resources):
        for resource in resources:
            if resource in self.css:
                self.css.remove(resource)
            if resource in self.plugins:
                self.plugins.remove(resource)
            if resource in self.js:
                self.js.remove(resource)
            if resource in self.assets:
                self.assets.remove(resource)
            if resource in self.packages:
                self.packages.remove(resource)
            if resource in self.markdown_extensions:
                self.markdown_extensions.pop(resource)

    @property
    def js_files(self) -> list[JSText]:
        """All JavaScript files of this resource bundle."""
        return [i for i in self.js if isinstance(i, JSText)]

    @property
    def js_links(self) -> list[JSFile]:
        """All JavaScript links of this resource bundle."""
        return [i for i in self.js if isinstance(i, JSFile)]

    @property
    def js_libs(self) -> list[JSFile | JSText]:
        """All JavaScript links of this resource bundle."""
        return [i for i in self.js if i.is_library]

    def merge(self, other: collections.abc.Mapping, additive: bool = False):
        """Merge resources with another resources instance or dict.

        Adds resources from other to this instance.

        Arguments:
            other: The resources to merge into this one.
            additive: Merge strategy. Either additive or replace.
        """
        if other_exts := other["markdown_extensions"]:
            exts = [self.markdown_extensions, other_exts]
            merged = mergehelpers.merge_extensions(exts)
            self.markdown_extensions = mergehelpers.merge_dicts(*merged)
        self.css = helpers.reduce_list(self.css + other["css"])
        self.plugins = helpers.reduce_list(self.plugins + other["plugins"])
        self.js = helpers.reduce_list(self.js + other["js"])
        self.assets = helpers.reduce_list(self.assets + other["assets"])
        self.packages = helpers.reduce_list(self.packages + other["packages"])
        return self


CSSType = CSSFile | CSSText
JSType = JSFile | JSText


if __name__ == "__main__":
    link = JSText("jkfdjl", "kfjdsdkljf", async_=True)
    print(link)
