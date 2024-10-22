from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import markdown

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Sequence


logger = log.get_logger(__name__)

DEFAULT_EXTS: Sequence[str | markdown.Extension] = [
    "toc",
    "tables",
    # "fenced_code",
    "pymdownx.emoji",
    "pymdownx.superfences",
    "md_in_html",
    "attr_list",
    "admonition",
]


class MdConverter(markdown.Markdown):
    def __init__(
        self,
        extensions: Sequence[str | markdown.Extension] | None = None,
        extension_configs: dict[str, dict[str, Any]] | None = None,
        custom_fences: list[dict] | None = None,
        output_format: Literal["xhtml", "html"] = "html",
        tab_length: int = 4,
    ):
        configs = extension_configs or {}
        if custom_fences:
            dct = configs.setdefault("pymdownx.superfences", {})
            ls = dct.setdefault("custom_fences", [])
            ls.extend(custom_fences)
        exts = list({*DEFAULT_EXTS, *extensions}) if extensions else DEFAULT_EXTS
        super().__init__(
            extensions=exts,
            extension_configs=configs,
            output_format=output_format,
            tab_length=tab_length,
        )

    def register_extensions(self, extensions: dict[str, Any]):
        ext_names = list(extensions.keys())
        self.registerExtensions(ext_names, extensions)
