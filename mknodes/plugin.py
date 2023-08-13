"""The Mkdocs Plugin."""

from __future__ import annotations

# Partly based on mkdocs-gen-files
import collections
import importlib.util
import logging
import os
import pathlib
import re
import sys
import tempfile
import types

from typing import TYPE_CHECKING
import urllib.parse

from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page

from mknodes import project


if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files


try:
    from mkdocs.exceptions import PluginError
except ImportError:
    PluginError = SystemExit  # type: ignore

from mkdocs_gen_files.config_items import ListOfFiles
from mkdocs_gen_files.editor import FilesEditor


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


# For Regex, match groups are:
#       0: Whole markdown link e.g. [Alt-text](url)
#       1: Alt text
#       2: Full URL e.g. url + hash anchor
#       3: Filename e.g. filename.md
#       4: File extension e.g. .md, .png, etc.
#       5. hash anchor e.g. #my-sub-heading-link
AUTOLINK_RE = r"\[([^\]]+)\]\((([^)/]+\.(md|png|jpg))(#.*)*)\)"


def import_file(path: str | os.PathLike) -> types.ModuleType:
    module_name = pathlib.Path(path).stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise RuntimeError
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


class LinkReplacerPlugin:
    def __init__(self, base_docs_url: str, page_url: str, mapping: dict[str, list[str]]):
        self.mapping = mapping
        self.page_url = page_url
        self.base_docs_url = pathlib.Path(base_docs_url)
        # Absolute URL of the linker
        self.linker_url = os.path.dirname(self.base_docs_url / page_url)  # noqa: PTH120

    def __call__(self, match):
        filename = urllib.parse.unquote(match.group(3).strip())
        if filename not in self.mapping:
            return f"`{match.group(3).replace('.md', '')}`"
        filenames = self.mapping[filename]
        if len(filenames) > 1:
            text = "%s: %s has multiple targets: %s"
            logger.debug(text, self.page_url, match.group(3), filenames)
        abs_link_url = (self.base_docs_url / filenames[0]).parent
        # need os.replath here bc pathlib.relative_to throws an exception
        # when linking across drives
        rel_path = os.path.relpath(abs_link_url, self.linker_url)
        rel_link_url = os.path.join(rel_path, filename)  # noqa: PTH118
        new_text = match.group(0).replace(match.group(2), rel_link_url)
        to_replace_with = rel_link_url + (match.group(5) or "")
        new_text = match.group(0).replace(match.group(2), to_replace_with)
        new_text = new_text.replace("\\", "/")
        text = "LinkReplacer: %s: %s -> %s"
        logger.debug(text, self.page_url, match.group(3), rel_link_url)
        return new_text


class MkNodesPlugin(BasePlugin):
    config_scheme = (("scripts", ListOfFiles(required=True)),)
    _edit_paths: dict

    def on_files(self, files: Files, config: MkDocsConfig) -> Files:
        self._dir = tempfile.TemporaryDirectory(prefix="mknodes_")
        self._project = project.Project(config=config, files=files)

        with FilesEditor(files, config, self._dir.name) as ed:
            for file_name in self.config["scripts"]:
                module = import_file(file_name)
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
            root.write()
        self._edit_paths = dict(ed.edit_paths)
        return ed.files

    def on_page_markdown(
        self,
        markdown: str,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str | None:
        base_docs_url = config["docs_dir"]
        page_url = page.file.src_uri
        mapping = collections.defaultdict(list)
        for file_ in files:
            filename = os.path.basename(file_.abs_src_path)  # noqa: PTH119
            mapping[filename].append(file_.url)
        #     print(file_.url, file_.dest_uri)
        plugin = LinkReplacerPlugin(base_docs_url, page_url, mapping)
        for k, v in self._project.info.metadata.items():
            if f"°metadata.{k}" in markdown or f"°metadata.{k.lower()}" in markdown:
                markdown = markdown.replace(f"°metadata.{k}", v)
                markdown = markdown.replace(f"°metadata.{k.lower()}", v)
                continue
        return re.sub(AUTOLINK_RE, plugin, markdown)

    def on_page_content(self, html, page: Page, config: MkDocsConfig, files: Files):
        repo_url = config.get("repo_url", None)
        edit_uri = config.get("edit_uri", None)

        src_path = pathlib.PurePath(page.file.src_path).as_posix()
        if src_path in self._edit_paths:
            path = self._edit_paths.pop(src_path)
            if repo_url and edit_uri:
                # Ensure urljoin behavior is correct
                if not edit_uri.startswith(("?", "#")) and not repo_url.endswith("/"):
                    repo_url += "/"
                url = urllib.parse.urljoin(repo_url, edit_uri)
                page.edit_url = path and urllib.parse.urljoin(url, path)
        return html

    @event_priority(-100)
    def on_post_build(self, config: MkDocsConfig):
        self._dir.cleanup()

        if unused_edit_paths := {k: str(v) for k, v in self._edit_paths.items() if v}:
            msg = "mknodes: These set_edit_path invocations went unused: %r"
            logger.warning(msg, unused_edit_paths)
