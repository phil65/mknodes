"""The Mkdocs Plugin."""

from __future__ import annotations

# Partly based on mkdocs-gen-files
import collections
import importlib.util
import logging
import os
import pathlib
import tempfile

from typing import TYPE_CHECKING
import urllib.parse

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.utils import write_file

from mknodes import project
from mknodes.plugin import linkreplacer, fileseditor
from mknodes.pages import mkpage
from mknodes.utils import classhelpers

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.pages import Page
    from mkdocs.structure.nav import Navigation


try:
    from mkdocs.exceptions import PluginError
except ImportError:
    PluginError = SystemExit  # type: ignore


try:
    from mkdocs.plugins import event_priority
except ImportError:

    def event_priority(priority):
        return lambda f: f  # No-op fallback


try:
    from mkdocs.plugins import get_plugin_logger

    logger = get_plugin_logger(__name__)
except ImportError:
    # TODO: remove once support for MkDocs <1.5 is dropped
    logger = logging.getLogger(f"mkdocs.plugins.{__name__}")  # type: ignore[assignment]


class MkNodesPlugin(BasePlugin):
    config_scheme = (("path", config_options.Type(str)),)
    css_filename = "mknodes.css"

    def on_files(self, files: Files, config: MkDocsConfig) -> Files:
        """On_files hook.

        During this phase all Markdown files as well as an aggregated css file
        are written.
        """
        self._dir = tempfile.TemporaryDirectory(prefix="mknodes_")
        self._project = project.Project(config=config, files=files)

        with fileseditor.FilesEditor(files, config, self._dir.name) as ed:
            file_name = self.config["path"]
            if file_name.endswith(".py"):
                module = classhelpers.import_file(file_name)
            else:
                module = importlib.import_module(file_name)
            try:
                module.build(self._project)
            except SystemExit as e:
                if e.code:
                    msg = f"Script {file_name!r} caused {e!r}"
                    raise PluginError(msg) from e
            root = self._project._root
            if not root:
                msg = "No root for project created."
                raise RuntimeError(msg)
            for k, v in root.all_virtual_files(only_children=False).items():
                logger.info("Writing file to %s", k)
                mode = "w" if isinstance(v, str) else "wb"
                with ed.open(k, mode) as file:
                    file.write(v)
            if css := root.all_css():
                logger.info("Creating %s...", self.css_filename)
                config.extra_css.append(self.css_filename)
                path = pathlib.Path(config["site_dir"]) / self.css_filename
                write_file(css.encode(), str(path))
        return ed.files

    def on_nav(
        self,
        nav: Navigation,
        files: Files,
        config: MkDocsConfig,
    ) -> Navigation | None:
        self._file_mapping = collections.defaultdict(list)
        for file_ in files:
            filename = os.path.basename(file_.abs_src_path)  # noqa: PTH119
            self._file_mapping[filename].append(file_.url)
        self._page_mapping = {}
        if root := self._project._root:
            for _level, node in root.iter_nodes():
                if isinstance(node, mkpage.MkPage):
                    self._page_mapping[node.resolved_file_path] = node
        return nav

    def on_pre_page(
        self,
        page: Page,
        *,
        config: MkDocsConfig,
        files: Files,
    ) -> Page | None:
        """During this phase we set the edit paths."""
        repo_url = config.get("repo_url", None)
        edit_uri = config.get("edit_uri", "edit/main/")
        if page.file.src_uri in self._page_mapping and repo_url:
            if not edit_uri.startswith(("?", "#")) and not repo_url.endswith("/"):
                repo_url += "/"
            if edit_path := self._page_mapping[page.file.src_uri]._edit_path:
                # root_path = pathlib.Path(config["docs_dir"]).parent
                # edit_path = str(edit_path.relative_to(root_path))
                rel_path = edit_path
            else:
                rel_path = self.config["path"]
            url = urllib.parse.urljoin(repo_url, edit_uri)
            page.edit_url = urllib.parse.urljoin(url, rel_path)
        return page

    def on_page_markdown(
        self,
        markdown: str,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str | None:
        """During this phase [title](some_page.md) and °metadata stuff gets replaced."""
        #     print(file_.url, file_.dest_uri)
        docs_dir = config["docs_dir"]
        page_url = page.file.src_uri
        for k, v in self._project.info.metadata.items():
            if f"°metadata.{k}" in markdown or f"°metadata.{k.lower()}" in markdown:
                markdown = markdown.replace(f"°metadata.{k}", v)
                markdown = markdown.replace(f"°metadata.{k.lower()}", v)
                continue
        link_replacer = linkreplacer.LinkReplacer(docs_dir, page_url, self._file_mapping)
        return link_replacer.replace(markdown)
