from __future__ import annotations

import functools
import os
import pathlib

from typing import Any
from urllib import parse

import markdown

from mkdocs import config as _config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.utils import write_file

from mknodes.utils import helpers


logger = get_plugin_logger(__name__)


@functools.cache
def load_config(path: str | os.PathLike | None = None):
    path = None if path is None else str(path)
    return _config.load_config(path)


class Config:
    def __init__(self, config: MkDocsConfig | str | os.PathLike | None = None):
        match config:
            case MkDocsConfig():
                self._config: MkDocsConfig = config
            case str() | os.PathLike() as file:
                self._config = load_config(str(file))
            case None:
                file = helpers.find_file_in_folder_or_parent("mkdocs.yml")
                if not file:
                    msg = "Could not find config file"
                    raise FileNotFoundError(msg)
                self._config = load_config(str(file))
                logger.info("Loaded config from %s", file)
            case _:
                raise TypeError(config)
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

    @property
    def docs_dir(self) -> pathlib.Path:
        return pathlib.Path(self._config.docs_dir)

    @property
    def site_dir(self) -> pathlib.Path:
        return pathlib.Path(self._config.site_dir)

    def register_extension(self, extension: str):
        if extension not in self.markdown_extensions:
            logger.info("Adding %s to extensions", extension)
            self.markdown_extensions.append(extension)

    def register_css(self, filename: str | os.PathLike, css: str):
        """Register a css file.

        Writes file to build assets folder and registers extra_css in config

        Arguments:
            filename: Filename to write
            css: file content
        """
        path = (pathlib.Path("assets") / filename).as_posix()
        logger.info("Creating %s...", path)
        self._config.extra_css.append(path)
        write_file(css.encode(), str(self.site_dir / path))

    def register_js(self, filename: str | os.PathLike, js: str):
        """Register a javascript file.

        Writes file to build assets folder and registers extra_javascript in config

        Arguments:
            filename: Filename to write
            js: file content
        """
        path = (pathlib.Path("assets") / filename).as_posix()
        logger.info("Creating %s...", path)
        self._config.extra_javascript.append(path)
        write_file(js.encode(), str(self.site_dir / path))

    def register_template(self, filename: str, content: str):
        """Register a html template.

        Writes file to build custom_dir folder

        Arguments:
            filename: Filename to write
            content: file content
        """
        if not self._config.theme.custom_dir:
            logger.warning("Cannot write %s. No custom_dir set in config.", filename)
            return
        target_path = pathlib.Path(self._config.theme.custom_dir) / filename
        # path = pathlib.Path("overrides") / filename
        logger.info("Creating %s...", target_path.as_posix())
        write_file(content.encode(), str(target_path))

    def get_markdown_instance(
        self,
        additional_extensions: list[str] | None = None,
        config_override: dict[str, Any] | None = None,
    ) -> markdown.Markdown:
        """Return a markdown instance based on given config."""
        extensions = self._config.markdown_extensions
        if additional_extensions:
            extensions = list(set(additional_extensions + extensions))
        configs = self._config.mdx_configs | (config_override or {})
        return markdown.Markdown(extensions=extensions, extension_configs=configs)

    def get_code_repository(self) -> str:
        if self.repo_name:
            return self.repo_name
        repo_host = parse.urlsplit(self.repo_url).netloc.lower()
        if repo_host == "github.com":
            return "GitHub"
        if repo_host == "bitbucket.org":
            return "Bitbucket"
        if repo_host == "gitlab.com":
            return "GitLab"
        return repo_host.split(".")[0].title()


if __name__ == "__main__":
    cfg = Config()
    print(cfg.mdx_configs)
