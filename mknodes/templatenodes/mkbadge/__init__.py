from __future__ import annotations

import functools
import html

from typing import Any, Literal

from jinjarope import htmlfilters, textfilters, utils

from mknodes.basenodes import mkimage
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


StyleStr = Literal["default", "gitlab-scoped"]


@functools.cache
def get_badge(
    label: str = "",
    value: str = "",
    *,
    font_size: int | None = None,
    font_name: str | None = None,
    num_padding_chars: int | None = None,
    badge_color: str | None = None,
    text_color: str | None = None,
    use_gitlab_style: bool = False,
) -> str:
    import anybadge

    badge = anybadge.Badge(
        label=html.escape(label),
        value=html.escape(value),
        font_size=font_size,
        font_name=font_name,
        num_padding_chars=num_padding_chars,
        default_color=badge_color,
        text_color=text_color,
        style="gitlab-scoped" if use_gitlab_style else "default",
    )
    return htmlfilters.clean_svg(badge.badge_svg_text)


class MkBadge(mkimage.MkImage):
    """Node for a locally-created badge (based on "anybadge").

    The node creates a badge svg, appends it to the virtual files, and
    shows it as an image.
    """

    ICON = "simple/shieldsdotio"
    REQUIRED_PACKAGES = [resources.Package("anybadge")]

    def __init__(
        self,
        label: str | tuple[str, str],
        value: str | None = None,
        *,
        font_size: Literal[10, 11, 12] | None = None,
        font_name: str | None = None,
        num_padding_chars: int | None = None,
        badge_color: str | None = None,
        text_color: str | None = None,
        use_gitlab_style: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            label: Left part of the badge. If given a tuple, use 2nd item as value.
            value: Right part of the badge
            font_size: Size of font to use
            font_name: Name of font to use
            num_padding_chars: Number of chars to use for padding
            badge_color: Badge color
            text_color: Badge color
            use_gitlab_style: Use Gitlab-scope style
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("", **kwargs)
        if isinstance(label, tuple):
            self.label, self.value = label
        else:
            self.label = label
            self.value = value
        self.font_size = font_size
        self.font_name = font_name
        self.num_padding_chars = num_padding_chars
        self._badge_color = badge_color
        self._text_color = text_color
        self.use_gitlab_style = use_gitlab_style

    @property
    def badge_color(self) -> str | None:
        if isinstance(self._badge_color, str):
            return self._badge_color
        return self.ctx.theme.primary_color

    def _to_markdown(self):
        inner = htmlfilters.html_link(self.data.replace("\n", ""), self.url)
        return f"<body>{inner}</body>"

    @property
    def text_color(self) -> str | None:
        if isinstance(self._text_color, str):
            return self._text_color
        color = self.ctx.theme.text_color
        return f"{color},#fff" if self.use_gitlab_style else f"#fff,{color}"

    @property
    def data(self) -> str:
        return get_badge(
            label=self.label,
            value=self.value,
            font_size=self.font_size,
            font_name=self.font_name,
            num_padding_chars=self.num_padding_chars,
            badge_color=self.badge_color,
            text_color=self.text_color,
            use_gitlab_style=self.use_gitlab_style,
        )

    @property
    def path(self) -> str:
        hashed = utils.get_hash(repr(self))
        unique = f"{self.label}_{self.value}_{hashed}.svg"
        return textfilters.slugify(unique)


if __name__ == "__main__":
    img = MkBadge("Left", "right")
    print(img.data)
