"""The Mkdocs Plugin."""

from __future__ import annotations

# Partly based on mkdocs-gen-files
import collections
from collections.abc import Callable
import importlib
import os
import pathlib
import tempfile

from typing import TYPE_CHECKING, Literal
import urllib.parse

from mkdocs.config import base, config_options
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page

from mknodes import mkdocsconfig, paths, project
from mknodes.plugin import linkreplacer, fileseditor
from mknodes.pages import mkpage
from mknodes.utils import classhelpers
from mknodes.theme import theme

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files


logger = get_plugin_logger(__name__)


def get_callable_from_path(path: str) -> Callable:
    modname, _qualname_separator, qualname = path.partition(":")
    if modname.endswith(".py"):
        obj = classhelpers.import_file(modname)
    else:
        obj = importlib.import_module(modname)
    for attr in qualname.split("."):
        obj = getattr(obj, attr)
    if not callable(obj):
        msg = "Incorrect path"
        raise TypeError(msg)
    return obj


class PluginConfig(base.Config):
    path = config_options.Type(str)


class MkNodesPlugin(BasePlugin[PluginConfig]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_html_content = None
        self._file_mapping = collections.defaultdict(list)
        self._page_mapping = {}
        self._dir = tempfile.TemporaryDirectory(prefix="mknodes_")

    def on_startup(
        self,
        command: Literal["build", "gh-deploy", "serve"],
        dirty: bool = False,
    ):
        """Defined to activate new-style MkDocs plugin handling."""

    def on_config(self, config: MkDocsConfig):
        """Create the project based on MkDocs config."""
        cfg = mkdocsconfig.Config(config)
        skin = theme.Theme.get_theme(config=cfg)
        self.project = project.Project[type(skin)](config=config, theme=skin)
        skin.associated_project = self.project
        project_fn = get_callable_from_path(self.config["path"])
        try:
            project_fn(self.project)
        except SystemExit as e:
            if e.code:
                msg = f"Script {self.config['path']!r} caused {e!r}"
                raise PluginError(msg) from e

    #     if config.nav is None:
    #         file = File(
    #             "/mknodes/blogs/index.md",
    #             src_dir=config.docs_dir,
    #             dest_dir=config.site_dir,
    #             use_directory_urls=config.use_directory_urls,
    #         )
    #         page = SectionPage("blog", file, config, [])
    #         section = Section("Blog", [page])

    #         config.nav = Navigation([section], [])

    def on_files(self, files: Files, config: MkDocsConfig) -> Files:
        """Create the node tree and write files to build folder.

        In this step we build the node tree by calling the user-set method,
        and aggregate all files we need to build the website.
        This includes:

          - Markdown pages (MkPages)
          - Templates
          - CSS files
        """
        if not self.project._root:
            msg = "No root for project created."
            raise RuntimeError(msg)
        root = self.project._root
        cfg = mkdocsconfig.Config(config)
        with fileseditor.FilesEditor(files, cfg, self._dir.name) as ed:
            ed.write_files(self.project.all_files())
            if css := root.all_css():
                self.project.config.register_css("mknodes_nodes.css", css)
            if js_files := root.all_js_files():
                for file in js_files:
                    content = (paths.RESOURCES / file).read_text()
                    self.project.config.register_js(file, content)
            if css := self.project.theme.css:
                self.project.config.register_css("mknodes_theme.css", str(css))
            if extensions := self.project.all_markdown_extensions():
                for ext in extensions:
                    self.project.config.register_extension(ext)
            md = self.project.config.get_markdown_instance()
            for template in self.project.templates:
                if html := template.build_html(md):
                    self.project.config.register_template(template.filename, html)
            for template in root.all_templates():
                html = template.build_html(md)
                self.project.config.register_template(template.filename, html)
        return ed.files

    def on_nav(
        self,
        nav: Navigation,
        files: Files,
        config: MkDocsConfig,
    ) -> Navigation | None:
        """Build mappings needed for linking in following steps."""
        for file_ in files:
            filename = os.path.basename(file_.abs_src_path)  # noqa: PTH119
            url = urllib.parse.unquote(file_.src_uri)
            self._file_mapping[filename].append(url)
        if root := self.project._root:
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
        repo_url = config.repo_url
        edit_uri = config.edit_uri or "edit/main/"
        if not repo_url or not edit_uri:
            return None
        if not edit_uri.startswith(("?", "#")) and not repo_url.endswith("/"):
            repo_url += "/"
        rel_path = self.config["path"]
        if not rel_path.endswith(".py"):
            rel_path = rel_path.replace(".", "/")
            rel_path += ".py"
        base_url = urllib.parse.urljoin(repo_url, edit_uri)
        node = self._page_mapping.get(page.file.src_uri)
        if node and repo_url and (edit_path := node._edit_path):
            # root_path = pathlib.Path(config["docs_dir"]).parent
            # edit_path = str(edit_path.relative_to(root_path))
            rel_path = edit_path
        page.edit_url = urllib.parse.urljoin(base_url, rel_path)
        return page

    def on_page_markdown(
        self,
        markdown: str,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str | None:
        """During this phase links and `°metadata` stuff get replaced."""
        for k, v in self.project.aggregate_info().items():
            if f"°metadata.{k}" in markdown or f"°metadata.{k.lower()}" in markdown:
                markdown = markdown.replace(f"°metadata.{k}", v)
                markdown = markdown.replace(f"°metadata.{k.lower()}", v)
                continue
        uri = page.file.src_uri
        if uri.endswith("SUMMARY.md"):
            return markdown
        link_replacer = linkreplacer.LinkReplacer(uri, mapping=self._file_mapping)
        return link_replacer.replace(markdown)

    def on_post_build(self, config: MkDocsConfig):
        """Delete the temporary template files."""
        if not config.theme.custom_dir:
            return
        for template in self.project.templates:
            path = pathlib.Path(config.theme.custom_dir) / template.filename
            path.unlink(missing_ok=True)
