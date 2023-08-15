from __future__ import annotations

import logging
import pathlib

from typing import TYPE_CHECKING, Literal

from mkdocs import config as _config

from mknodes.utils import helpers


logger = logging.getLogger(__name__)

COLORS = {
    "red": {"color": "#ef5552", "text": "#ffffff"},
    "pink": {"color": "#e92063", "text": "#ffffff"},
    "purple": {"color": "#ab47bd", "text": "#ffffff"},
    "deep purple": {"color": "#7e56c2", "text": "#ffffff"},
    "indigo": {"color": "#4051b5", "text": "#ffffff"},
    "blue": {"color": "#2094f3", "text": "#ffffff"},
    "light blue": {"color": "#02a6f2", "text": "#ffffff"},
    "cyan": {"color": "#00bdd6", "text": "#ffffff"},
    "teal": {"color": "#009485", "text": "#ffffff"},
    "green": {"color": "#4cae4f", "text": "#ffffff"},
    "light green": {"color": "#8bc34b", "text": "#ffffff"},
    "lime": {"color": "#cbdc38", "text": "#000000"},
    "yellow": {"color": "#ffec3d", "text": "#000000"},
    "amber": {"color": "#ffc105", "text": "#000000"},
    "orange": {"color": "#ffa724", "text": "#000000"},
    "deep orange": {"color": "#ff6e42", "text": "#ffffff"},
    "brown": {"color": "#795649", "text": "#ffffff"},
    "grey": {"color": "#757575", "text": "#ffffff"},
    "blue grey": {"color": "#546d78", "text": "#ffffff"},
    "black": {"color": "#000000", "text": "#ffffff"},
    "white": {"color": "#ffffff", "text": "#000000"},
}

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig


class Config:
    def __init__(self, config: MkDocsConfig | None = None):
        if config:
            self._config = config
        else:
            file = helpers.find_file_in_folder_or_parent("mkdocs.yml")
            if not file:
                msg = "Could not find config file"
                raise FileNotFoundError(msg)
            self._config = _config.load_config(str(file))
            logger.info("Loaded config from %s", file)

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

    def get_primary_color(self) -> str:
        color = self._get_color("primary", fallback="indigo")
        return COLORS[color]["color"]

    def get_text_color(self) -> str:
        color = self._get_color("primary", fallback="indigo")
        return COLORS[color]["text"]

    def get_accent_color(self) -> str:
        # sourcery skip: use-or-for-fallback
        color = self._get_color("accent", fallback="")
        if not color:
            color = self._get_color("primary", fallback="indigo")
        return COLORS[color]["color"]

    def _get_color(self, color_type: Literal["primary", "accent"], fallback: str) -> str:
        palette = self._config.theme.get("palette")
        match palette:
            case list():
                return palette[0].get(color_type, fallback)
            case dict():
                return palette.get(color_type, fallback)
            case _:
                return fallback


if __name__ == "__main__":
    cfg = Config()
    print(cfg.get_primary_color())
