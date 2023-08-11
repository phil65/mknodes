from __future__ import annotations

import logging

from typing import Any, Literal

from mknodes.basenodes import mkcontainer, mknode
from mknodes.templatenodes import mkbadge
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


MetadataTypeStr = Literal["classifiers", "keywords", "websites"]


class MkMetadataBadges(mkcontainer.MkContainer):
    """Container node for a list of metadata badges.

    Badges are generated locally using "anybadge" package
    """

    ICON = "simple/shieldsdotio"
    STATUS = "new"

    def __init__(
        self,
        typ: MetadataTypeStr,
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
            typ: Metadata badges to show
            font_size: Size of font to use
            font_name: Name of font to use
            num_padding_chars: Number of chars to use for padding
            badge_color: Badge color
            text_color: Badge color
            use_gitlab_style: Use Gitlab-scope style
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.block_separator = "\n"
        self._typ = typ
        self.font_size = font_size
        self.font_name = font_name
        self.num_padding_chars = num_padding_chars
        self.badge_color = badge_color
        self.text_color = text_color
        self.use_gitlab_style = use_gitlab_style

    def __repr__(self):
        return helpers.get_repr(
            self,
            typ=self._typ,
            font_size=self.font_size,
            font_name=self.font_name,
            badge_color=self.badge_color,
            text_color=self.text_color,
            num_padding_chars=self.num_padding_chars,
            use_gitlab_style=self.use_gitlab_style,
            _filter_empty=True,
            _filter_false=True,
        )

    @property
    def badge_content(self) -> list[tuple]:
        items: list[tuple] = []
        if not self.associated_project:
            return items
        match self._typ:
            case "classifiers":
                dct = self.associated_project.info.get_classifiers()
                for category, labels in dct.items():
                    items.extend([(i, category, None) for i in labels])
            case "keywords":
                items.extend(
                    (keyword, "", None)
                    for keyword in self.associated_project.info.get_keywords()
                )
            case "websites":
                urls = self.associated_project.info.urls
                items.extend((name, "", url) for name, url in urls.items())
        return items

    @property
    def items(self) -> list[mknode.MkNode]:
        return [
            mkbadge.MkBadge(
                label=label,
                value=value,
                link=link,
                font_size=self.font_size,
                font_name=self.font_name,
                badge_color=self.badge_color,
                text_color=self.text_color,
                num_padding_chars=self.num_padding_chars,
                use_gitlab_style=self.use_gitlab_style,
                title=label,
                parent=self,
            )
            for label, value, link in self.badge_content
        ]

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkMetadataBadges(typ="classifiers")
        page += mknodes.MkReprRawRendered(node)
        node = MkMetadataBadges(typ="keywords", use_gitlab_style=True)
        page += mknodes.MkReprRawRendered(node)
        node = MkMetadataBadges(typ="websites")
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    import mknodes

    proj = mknodes.Project(mknodes)
    nav = proj.get_root()
    node = MkMetadataBadges("classifiers")
    page = nav.add_page("test")
    page += node
    nav += page
    print(node)
