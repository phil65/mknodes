from __future__ import annotations

import pathlib

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig


class Config:
    def __init__(self, config: MkDocsConfig):
        self._config = config

    def __getattr__(self, name):
        return getattr(self._config, name)

    def get_path(self, path: str) -> str:
        return (
            path
            if self._config.use_directory_urls
            else f"{self._config.site_name}/{path}"
        )

    def get_inventory_info(self) -> list[dict]:
        """Returns list of dicts containing inventory info.

        Shape: [{"url": inventory_url, "domains": ["std", "py"]}, ...]
        """
        try:
            mkdocstrings_cfg = self._config.plugins["mkdocstrings"]
            return mkdocstrings_cfg.config["handlers"]["python"]["import"]
        except KeyError:
            return []

    def get_docs_dir(self) -> pathlib.Path:
        return pathlib.Path(self._config.docs_dir)
