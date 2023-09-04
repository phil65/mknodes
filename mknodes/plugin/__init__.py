"""The Mkdocs Plugin."""

from __future__ import annotations

import pathlib
import tempfile

from typing import TYPE_CHECKING, Literal
import jinja2

from mkdocs.config import base, config_options
from mkdocs.plugins import BasePlugin, get_plugin_logger
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page

from mknodes import mkdocsconfig, project
from mknodes.plugin import linkreplacer, fileseditor
from mknodes.utils import classhelpers
from mknodes.theme import theme

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files


logger = get_plugin_logger(__name__)


class PluginConfig(base.Config):
    path = config_options.Type(str)
    repo_path = config_options.Type(str, default=".")


class MkNodesPlugin(BasePlugin[PluginConfig]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._page_mapping = {}
        self._dir = tempfile.TemporaryDirectory(prefix="mknodes_")
        logger.debug("Creating temporary dir %s", self._dir.name)
        self.link_replacer = linkreplacer.LinkReplacer()
        logger.debug("Finished initializing plugin")

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
        self.project = project.Project[type(skin)](
            base_url=config.site_url or "",
            use_directory_urls=config.use_directory_urls,
            theme=skin,
            repo_path=self.config.repo_path,
        )
        skin.associated_project = self.project
        project_fn = classhelpers.get_callable_from_path(self.config.path)
        logger.debug("Building page...")
        project_fn(project=self.project)
        logger.debug("Finished building page.")

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
        cfg = mkdocsconfig.Config(config)
        info = self.project.infocollector
        self.project.aggregate_info()
        info["config"] = config
        with fileseditor.FilesEditor(files, cfg, self._dir.name) as ed:
            ed.write_files(self.project.all_files())
            for k, v in info["css"].items():
                cfg.register_css(k, v)
            if js_files := info["js_files"]:
                for k, v in js_files.items():
                    cfg.register_js(k, v)
            if extensions := info["markdown_extensions"]:
                cfg.register_extensions(extensions)
            if social := info["social_info"]:
                extra = cfg._config.extra
                if not extra.get("social"):
                    extra["social"] = social
            md = cfg.get_markdown_instance()
            for template in info["templates"]:
                if html := template.build_html(md):
                    cfg.register_template(template.filename, html)
        return ed.files

    def on_nav(
        self,
        nav: Navigation,
        files: Files,
        config: MkDocsConfig,
    ) -> Navigation | None:
        """Populate LinkReplacer and build path->MkPage mapping for following steps."""
        self.link_replacer.add_files(files)
        return nav

    def on_env(self, env: jinja2.Environment, config: MkDocsConfig, files: Files):
        env.globals["mknodes"] = self.project.infocollector.variables
        logger.debug("Added variables to jinja2 environment.")

    def on_pre_page(
        self,
        page: Page,
        *,
        config: MkDocsConfig,
        files: Files,
    ) -> Page | None:
        """During this phase we set the edit paths."""
        node = self.project.infocollector["page_mapping"].get(page.file.src_uri)
        edit_path = node._edit_path if node else None
        cfg = mkdocsconfig.Config(config)
        if path := cfg.get_edit_url(edit_path):
            page.edit_url = path
        return page

    def on_page_markdown(
        self,
        markdown: str,
        *,
        page: Page,
        config: MkDocsConfig,
        files: Files,
    ) -> str | None:
        """During this phase links get replaced and `jinja2` stuff get rendered."""
        node = self.project.infocollector["page_mapping"].get(page.file.src_uri)
        self.project.infocollector["page"] = page
        self.project.infocollector["mkpage"] = node
        self.project.infocollector.set_mknodes_filters(parent=node)
        markdown = self.project.infocollector.render(markdown)
        return self.link_replacer.replace(markdown, page.file.src_uri)

    def on_post_build(self, config: MkDocsConfig):
        """Delete the temporary template files."""
        if not config.theme.custom_dir:
            return
        for template in self.project.templates:
            path = pathlib.Path(config.theme.custom_dir) / template.filename
            path.unlink(missing_ok=True)
