"""The Mkdocs Plugin."""

from __future__ import annotations

# Partly based on mkdocs-gen-files
import collections
import importlib
import os
import pathlib
import tempfile

from typing import TYPE_CHECKING, Literal
import urllib.parse

from mkdocs.config import config_options
from mkdocs.exceptions import PluginError
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page

from mknodes import mkdocsconfig, project
from mknodes.plugin import linkreplacer, fileseditor
from mknodes.pages import mkpage
from mknodes.utils import classhelpers
from mknodes.theme import theme

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files


logger = get_plugin_logger(__name__)


class MkNodesPlugin(BasePlugin):
    config_scheme = (("path", config_options.Type(str)),)

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
        self._project = project.Project[type(skin)](config=config, theme=skin)
        skin.associated_project = self._project

    #     if config.nav is None:
    #         file = File(
    #             "/mknodes/blogs/index.md",
    #             src_dir=config["docs_dir"],
    #             dest_dir=config["site_dir"],
    #             use_directory_urls=config["use_directory_urls"],
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
            for k, v in self._project.all_files().items():
                logger.info("Writing file to %s", k)
                mode = "w" if isinstance(v, str) else "wb"
                with ed.open(k, mode) as file:
                    file.write(v)
            if css := root.all_css():
                self._project.config.register_css("mknodes_nodes.css", css)
            if css := self._project.theme.css:
                self._project.config.register_css("mknodes_theme.css", str(css))
            for template in self._project.templates:
                if html := template.build_html():
                    self._project.config.register_template(
                        html,
                        filename=template.filename,
                    )
            for template in root.all_templates():
                self._project.config.register_template(
                    template.build_html(),
                    filename=template.filename,
                )
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
            self._file_mapping[filename].append(file_.url)
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
        for k, v in self._project.info.metadata.items():
            if f"°metadata.{k}" in markdown or f"°metadata.{k.lower()}" in markdown:
                markdown = markdown.replace(f"°metadata.{k}", v)
                markdown = markdown.replace(f"°metadata.{k.lower()}", v)
                continue
        link_replacer = linkreplacer.LinkReplacer(
            base_docs_url=config.docs_dir,
            page_url=page.file.src_uri,
            mapping=self._file_mapping,
        )
        return link_replacer.replace(markdown)

    def on_post_build(self, config: MkDocsConfig):
        """Delete the temporary template files."""
        if not config.theme.custom_dir:
            return
        for template in self._project.templates:
            path = pathlib.Path(config.theme.custom_dir) / template.filename
            path.unlink(missing_ok=True)
