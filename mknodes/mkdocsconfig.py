from __future__ import annotations

import os
import pathlib

from typing import TYPE_CHECKING

import markdown

from mkdocs import config as _config
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import File
from mkdocs.utils import write_file

from mknodes.utils import helpers


logger = get_plugin_logger(__name__)


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
        self.plugin = self._config.plugins["mknodes"]

    def __getattr__(self, name):
        return getattr(self._config, name)

    @property
    def site_url(self) -> str:
        url = self._config.site_url
        if url is None:
            return ""
        return url if url.endswith("/") else f"{url}/"

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

    def register_css(self, filename: str | os.PathLike, css: str):
        site_dir = pathlib.Path(self._config["site_dir"])
        path = (pathlib.Path("assets") / filename).as_posix()
        logger.info("Creating %s...", path)
        self._config.extra_css.append(path)
        write_file(css.encode(), str(site_dir / path))

    def register_template(self, content: str, filename: str):
        if not self._config.theme.custom_dir:
            msg = "No custom dir set"
            raise RuntimeError(msg)
        custom_dir = pathlib.Path(self._config.theme.custom_dir) / filename
        path = pathlib.Path("overrides") / filename
        logger.info("Creating %s...", path.as_posix())
        write_file(content.encode(), str(custom_dir))

    def get_markdown_instance(self) -> markdown.Markdown:
        return markdown.Markdown(
            extensions=self._config["markdown_extensions"],
            extension_configs=self._config["mdx_configs"] or {},
        )

    def get_file(self, path) -> File:
        return File(
            str(path),
            src_dir=self._config.docs_dir,
            dest_dir=self._config.site_dir,
            use_directory_urls=self._config.use_directory_urls,
        )


if __name__ == "__main__":
    cfg = Config()
    print(cfg._config.use_directory_urls)
    cfg.nav = "test"
