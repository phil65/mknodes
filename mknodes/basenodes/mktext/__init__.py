from __future__ import annotations

from typing import Any, Self

from jinjarope import mdfilters

from mknodes.basenodes import mknode
from mknodes.utils import log, pathhelpers


logger = log.get_logger(__name__)


class MkText(mknode.MkNode):
    """Class for any Markup text.

    All classes inheriting from MkNode can get converted to this Type.
    """

    ICON = "material/text"

    def __init__(
        self,
        text: str | mknode.MkNode | None = "",
        *,
        render_jinja: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            text: Markup text
            render_jinja: Whether text should get rendered by this node
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self._text = str(text or "")
        self.render_jinja = render_jinja

    def __getitem__(self, section_name: str) -> Self | None:
        markdown = self._to_markdown()
        section_text = mdfilters.extract_header_section(markdown, section_name)
        return None if section_text is None else type(self)(section_text)

    @property
    def text(self) -> str:
        if not self.render_jinja:
            return self._text
        return self.env.render_string(self._text)

    @text.setter
    def text(self, value):
        self._text = value

    def _to_markdown(self) -> str:
        return self.text

    @property
    def children(self):
        if not self.render_jinja:
            return []
        self.env.render_string(self._text, variables=self.variables)
        return self.env.rendered_children

    @children.setter
    def children(self, val):
        pass

    @classmethod
    def from_url(cls, url: str) -> Self | None:
        """Build a MkText node on a remote markup file.

        If the URL contains a "#" (http://.../markdown.md#section),
        it will try to extract the given section.

        All fsspec protocols are supported as URL.

        Arguments:
            url: URL to get markdown from.
        """
        url, *section = url.split("#")
        text = pathhelpers.load_file_cached(url)
        if not section:
            return cls(text)

        extracted = mdfilters.extract_header_section(text, section[0])
        return cls(extracted) if extracted is not None else None


if __name__ == "__main__":
    node = MkText("Test")
    print(repr(node))
