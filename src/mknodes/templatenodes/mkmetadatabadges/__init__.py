from __future__ import annotations

from typing import Any, Literal, TYPE_CHECKING
from urllib import parse

from mknodes.basenodes import mkcontainer
from mknodes.data import datatypes
from mknodes.info import packageregistry
from mknodes.templatenodes import mkbadge
from mknodes.utils import log

if TYPE_CHECKING:
    from mknodes.basenodes import mknode


logger = log.get_logger(__name__)


class MkMetadataBadges(mkcontainer.MkContainer):
    """Container node for a list of metadata badges.

    Badges are generated locally using "anybadge" package
    """

    ICON = "simple/shieldsdotio"
    STATUS = "new"
    VIRTUAL_CHILDREN = True

    def __init__(
        self,
        typ: datatypes.MetadataTypeStr,
        *,
        package: str | None = None,
        font_size: Literal[10, 11, 12] | None = None,
        font_name: str | None = None,
        num_padding_chars: int | None = None,
        badge_color: str | None = None,
        text_color: str | None = None,
        use_gitlab_style: bool = False,
        block_separator: str = "\n",
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            typ: Metadata badges to show
            package: Package to show badges for. If None, it will get pulled from project
            font_size: Size of font to use
            font_name: Name of font to use
            num_padding_chars: Number of chars to use for padding
            badge_color: Badge color. If none is set, it will be pulled from project.
            text_color: Badge color
            use_gitlab_style: Use Gitlab-scope style
            block_separator: Divider to use between badges
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(block_separator=block_separator, **kwargs)
        self._package = package
        self.typ = typ
        self.font_size: Literal[10, 11, 12] | None = font_size
        self.font_name = font_name
        self.num_padding_chars = num_padding_chars
        self.badge_color = badge_color
        self.text_color = text_color
        self.use_gitlab_style = use_gitlab_style

    @property
    def badge_content(self) -> list[tuple[str, str | None, str | None]]:  # noqa: PLR0911
        ctx = packageregistry.get_info(self._package) if self._package else self.ctx.metadata
        match self.typ:
            case "classifiers":
                items: list[tuple[str, str | None, str | None]] = []
                for category, labels in ctx.classifier_map.items():
                    items.extend([(i, category, None) for i in labels])
                return items
            case "keywords":
                return [(keyword, "", None) for keyword in ctx.keywords]
            case "keywords_combined":
                return [("Keywords", " | ".join(ctx.keywords), None)]
            case "required_python":
                return [("Python", ctx.required_python_version, "https://python.org")]
            case "websites":
                return [(name, parse.urlparse(url).netloc, url) for name, url in ctx.urls.items()]
            case "dependencies":
                return [(p.name, p.version, p.homepage) for p in ctx.required_packages]
            case "installed_packages":
                return [
                    (p.name, p.version, p.homepage)
                    for p in packageregistry.get_installed_packages()
                ]
            case str():
                raise ValueError(self.typ)
            case _ if self.typ in datatypes.CLASSIFIERS:
                labels = ctx.classifier_map.get(self.typ, [])
                return [(i, self.typ, None) for i in labels]

    def get_items(self) -> list[mknode.MkNode]:
        """Return computed badge items."""
        return [
            mkbadge.MkBadge(
                label=label,
                value=value,
                target=link,
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


if __name__ == "__main__":
    node = MkMetadataBadges.with_context("websites")
    print(node)
