from __future__ import annotations

from collections.abc import Iterable, Iterator
import dataclasses

from typing import Any, TypedDict


class _TocToken(TypedDict):
    """The shape of the dict created by the "toc" markdown extension."""

    level: int
    id: str
    name: str
    children: list[_TocToken]


def get_toc(md: str, toc_config: dict | None = None) -> TableOfContents:
    import markdown

    kwargs: dict[str, Any] = {"extensions": ["toc"]}
    if toc_config:
        kwargs["extension_configs"] = {"toc": toc_config}
    converter = markdown.Markdown(**kwargs)  # type: ignore[arg-type]
    converter.convert(md)
    toc_tokens = getattr(converter, "toc_tokens", [])
    toc = [_parse_toc_token(i) for i in toc_tokens]
    # For the table of contents, always mark the first element as active
    if len(toc):
        toc[0].active = True  # type: ignore[attr-defined]
    return TableOfContents(toc)


@dataclasses.dataclass(frozen=True)
class AnchorLink:
    """A single entry in the table of contents."""

    title: str
    """The text of the item."""
    id: str  # noqa: A003
    """The slug used as part of the URL."""
    level: int
    """The zero-based level of the item."""
    children: list[AnchorLink] = dataclasses.field(default_factory=list)
    """An iterable of any child items."""

    @property
    def url(self) -> str:
        """The hash fragment of a URL pointing to the item."""
        return f"#{self.id}"

    def __str__(self) -> str:
        return self.indent_print()

    def indent_print(self, depth: int = 0) -> str:
        indent = "    " * depth
        ret = f"{indent}{self.title} - {self.url}\n"
        for item in self.children:
            ret += item.indent_print(depth + 1)
        return ret


@dataclasses.dataclass
class TableOfContents(Iterable[AnchorLink]):
    """Represents the table of contents for a given page."""

    items: list[AnchorLink]

    def __iter__(self) -> Iterator[AnchorLink]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __str__(self) -> str:
        return "".join(str(item) for item in self)


def _parse_toc_token(token: _TocToken) -> AnchorLink:
    tokens = [_parse_toc_token(i) for i in token["children"]]
    return AnchorLink(token["name"], token["id"], token["level"], tokens)


if __name__ == "__main__":
    import re

    import markdown

    from markdown.extensions import toc

    from mknodes.treelib import node

    TEXT = "# **test**\n\n### test3\n\n## tsexx\n\n# tsexx\n"

    class TocNode(node.Node):
        def __init__(self, name: str, **kwargs):
            super().__init__(**kwargs)
            self.name = name

    def stripped(md: str):
        html = markdown.Markdown(extensions=["toc"]).convert(md)
        res = re.sub(r"(<[^>]+>)", "", html)
        return re.sub(r"(&[\#a-zA-Z0-9]+;)", "", res)

    # page = mk.MkPage()
    # node = MkText(TEXT)
    # page += node
    # print(repr(page.toc))
    root = TocNode("")
    pat = re.compile("^(#+) (.*)$", re.MULTILINE)
    prev_level = 0

    items = [
        {"level": len(match[1]), "name": match[2], "cleaned": stripped(match[2])}
        for match in pat.finditer(TEXT)
    ]
    print(toc.nest_toc_tokens(items))
