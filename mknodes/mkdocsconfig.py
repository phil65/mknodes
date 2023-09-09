from __future__ import annotations

import contextlib
import functools
import io
import os
import pathlib

from typing import Any
from urllib import parse

import markdown

from mkdocs import config as _config
from mkdocs.commands import get_deps
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger

from mknodes.utils import mergehelpers, pathhelpers


logger = get_plugin_logger(__name__)


@functools.cache
def load_config(path: str | os.PathLike | None = None):
    path = None if path is None else str(path)
    cfg = _config.load_config(path)
    logger.info("Loaded config from path '%s'", path or "mkdocs.yml")
    return cfg


class Config:
    def __init__(self, config: MkDocsConfig | str | os.PathLike | None = None):
        match config:
            case MkDocsConfig():
                self._config: MkDocsConfig = config
            case str() | os.PathLike() as path:
                self._config = load_config(str(path))
            case None:
                if file := pathhelpers.find_file_in_folder_or_parent("mkdocs.yml"):
                    self._config = load_config(str(file))
                else:
                    msg = "Could not find config file"
                    raise FileNotFoundError(msg)
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

    def register_extensions(self, extensions: dict[str, dict]):
        for ext_name in extensions:
            if ext_name not in self.markdown_extensions:
                logger.info("Adding %s to extensions", ext_name)
                self.markdown_extensions.append(ext_name)
        self._config.mdx_configs = mergehelpers.merge_dicts(
            self._config.mdx_configs,
            extensions,
        )

    def register_css(self, filename: str | os.PathLike, css: str):
        """Register a css file.

        Writes file to build assets folder and registers extra_css in config

        Arguments:
            filename: Filename to write
            css: file content
        """
        path = (pathlib.Path("assets") / filename).as_posix()
        self._config.extra_css.append(path)
        abs_path = self.site_dir / path
        logger.info("Registering css file %s...", abs_path)
        pathhelpers.write_file(css, abs_path)

    def register_js(self, filename: str | os.PathLike, js: str):
        """Register a javascript file.

        Writes file to build assets folder and registers extra_javascript in config

        Arguments:
            filename: Filename to write
            js: file content
        """
        path = (pathlib.Path("assets") / filename).as_posix()
        self._config.extra_javascript.append(path)
        abs_path = self.site_dir / path
        logger.info("Registering js file %s...", abs_path)
        pathhelpers.write_file(js, abs_path)

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
        pathhelpers.write_file(content, target_path)

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

    def get_edit_url(self, edit_path: str | None) -> str | None:
        repo_url = self.repo_url
        if not repo_url:
            return None
        edit_uri = self.edit_uri or "edit/main/"
        if not edit_uri.startswith(("?", "#")) and not repo_url.endswith("/"):
            repo_url += "/"
        rel_path = self.plugin.config.path
        if not rel_path.endswith(".py"):
            rel_path = rel_path.replace(".", "/")
            rel_path += ".py"
        base_url = parse.urljoin(repo_url, edit_uri)
        if repo_url and edit_path:
            # root_path = pathlib.Path(config["docs_dir"]).parent
            # edit_path = str(edit_path.relative_to(root_path))
            rel_path = edit_path
        return parse.urljoin(base_url, rel_path)

    def get_install_candidates(self) -> list[str]:
        path = "https://raw.githubusercontent.com/mkdocs/catalog/main/projects.yaml"
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            get_deps.get_deps(path, self._config.config_file_path)
        return [i for i in buffer.getvalue().split("\n") if i]


if __name__ == "__main__":
    cfg = Config()
    print(cfg.theme._vars)
