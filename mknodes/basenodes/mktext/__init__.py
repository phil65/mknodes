from __future__ import annotations

from typing import Any, Self

from mknodes.basenodes import mknode
from mknodes.utils import helpers, log, pathhelpers, reprhelpers


logger = log.get_logger(__name__)

RESPONSE_CODE_OK = 200
EXAMPLE_URL = "https://raw.githubusercontent.com/phil65/mknodes/main/README.md"


class MkText(mknode.MkNode):
    """Class for any Markup text.

    All classes inheriting from MkNode can get converted to this Type.
    """

    ICON = "material/text"

    def __init__(
        self,
        text: str | mknode.MkNode | None = "",
        is_jinja_expression: bool = False,
        *,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            text: Markup text
            is_jinja_expression: Whether text is a jinja expression
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self._text = str(text or "")
        self.is_jinja_expression = is_jinja_expression

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            text=self.text,
            is_jinja_expression=self.is_jinja_expression,
            _filter_false=True,
        )

    def __getitem__(self, section_name: str) -> Self | None:
        markdown = self._to_markdown()
        section_text = helpers.extract_header_section(markdown, section_name)
        return None if section_text is None else type(self)(section_text)

    @property
    def text(self) -> str:
        if not self.is_jinja_expression:
            return self._text
        return self.env.render_string(f"{{{{ {self._text} }}}}")

    @text.setter
    def text(self, value):
        self._text = value

    def _to_markdown(self) -> str:
        return self.text

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkText("This is the most basic node. It contains `markdown` text")
        page += mk.MkReprRawRendered(node, header="### Regular")
        if from_url := MkText.from_url(EXAMPLE_URL):
            page += mk.MkReprRawRendered(from_url, header="### From URL")

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
        if section:
            text = helpers.extract_header_section(text, section[0])
        return cls(text) if text is not None else None


if __name__ == "__main__":
    node = MkText("log", is_jinja_expression=True)
    print(node)
