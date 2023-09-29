from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

import markdown

from mknodes.utils import log


logger = log.get_logger(__name__)


class MdConverter(markdown.Markdown):
    def __init__(
        self,
        extensions: Sequence[str | markdown.Extension],
        extension_configs: dict[str, dict[str, Any]],
        output_format: Literal["xhtml", "html"] = "html",
        tab_length: int = 4,
    ):
        exts = ["pymdownx.emoji", "md_in_html", "attr_list"]
        if extensions:
            exts = list({*exts, *extensions})
        super().__init__(
            extensions=exts,
            extension_configs=extension_configs,
            output_format=output_format,
            tab_length=tab_length,
        )

    def register_extensions(self, extensions: dict):
        ext_names = list(extensions.keys())
        self.registerExtensions(ext_names, extensions)
