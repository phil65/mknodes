from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

import markdown

from mknodes.utils import log


logger = log.get_logger(__name__)

DEFAULT_EXTS: Sequence[str | markdown.Extension] = [
    "toc",
    "tables",
    # "fenced_code",
    "pymdownx.emoji",
    "md_in_html",
    "attr_list",
    "admonition",
]


class MdConverter(markdown.Markdown):
    def __init__(
        self,
        extensions: Sequence[str | markdown.Extension] | None = None,
        extension_configs: dict[str, dict[str, Any]] | None = None,
        output_format: Literal["xhtml", "html"] = "html",
        tab_length: int = 4,
    ):
        exts = list({*DEFAULT_EXTS, *extensions}) if extensions else DEFAULT_EXTS
        super().__init__(
            extensions=exts,
            extension_configs=extension_configs or {},
            output_format=output_format,
            tab_length=tab_length,
        )

    def register_extensions(self, extensions: dict):
        ext_names = list(extensions.keys())
        self.registerExtensions(ext_names, extensions)
