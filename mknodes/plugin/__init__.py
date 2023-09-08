"""The Mkdocs Plugin."""

from __future__ import annotations

import pathlib
import tempfile

from typing import TYPE_CHECKING, Literal

from mkdocs.plugins import BasePlugin, get_plugin_logger

from mknodes import mkdocsconfig, project
from mknodes.pages import mkpage
from mknodes.plugin import linkreplacer, mkdocsbuilder, pluginconfig
from mknodes.utils import helpers
from mknodes.theme import theme
from mknodes.info import folderinfo

if TYPE_CHECKING:
    import jinja2
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files
    from mkdocs.structure.nav import Navigation
    from mkdocs.structure.pages import Page

    # from mkdocs.utils.templates import TemplateContext


logger = get_plugin_logger(__name__)

CommandStr = Literal["build", "serve", "gh-deploy"]


class MkNodesPlugin(BasePlugin[pluginconfig.PluginConfig]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dir = tempfile.TemporaryDirectory(prefix="mknodes_")
        logger.debug("Creating temporary dir %s", self._dir.name)
        self.link_replacer = linkreplacer.LinkReplacer()
        logger.debug("Finished initializing plugin")

    def on_startup(self, command: CommandStr, dirty: bool = False):
        """Clone the repo in case it is a remote one.

        Also activates new-style MkDocs plugin lifecycle.
        """
        if helpers.is_url(self.config.repo_path):
            self.folderinfo = folderinfo.FolderInfo.clone_from(
                self.config.repo_path,
                depth=self.config.clone_depth,
            )
        else:
            self.folderinfo = self.config.repo_path

    def on_config(self, config: MkDocsConfig):
        """Create the project based on MkDocs config."""
        cfg = mkdocsconfig.Config(config)
        skin = theme.Theme.get_theme(config=cfg)
        self.project = project.Project(
            base_url=config.site_url or "",
            use_directory_urls=config.use_directory_urls,
            theme=skin,
            repo=self.folderinfo,
            build_fn=self.config.path,
        )

    def on_files(self, files: Files, config: MkDocsConfig) -> Files:
        """Create the node tree and write files to build folder.

        In this step we build the node tree by calling the user-set method,
        and aggregate all files we need to build the website.
        This includes:

          - Markdown pages (MkPages)
          - Templates
          - CSS files
        """
        cfg = mkdocsconfig.Config(config)
        info = self.project.infocollector
        info["config"] = config
        builder = mkdocsbuilder.MkDocsBuilder(
            files=files,
            config=cfg,
            directory=self._dir.name,
        )
        builder.write_files(self.project.all_files())  # type: ignore[arg-type]
        for k, v in info["css"].items():
            cfg.register_css(k, v)
        if js_files := info["js_files"]:
            for k, v in js_files.items():
                cfg.register_js(k, v)
        if extensions := info["markdown_extensions"]:
            cfg.register_extensions(extensions)
        if social := info["metadata"]["social_info"]:
            extra = cfg._config.extra
            if not extra.get("social"):
                extra["social"] = social
        cfg._config.repo_url = info["metadata"]["repository_url"]
        cfg._config.site_description = info["metadata"]["summary"]
        cfg._config.site_name = info["metadata"]["name"]
        cfg._config.site_author = info["project"].info.author_name
        md = cfg.get_markdown_instance()
        for template in info["templates"]:
            if html := template.build_html(md):
                cfg.register_template(template.filename, html)
        return builder.files

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
        # mknodes_macros = jinjahelpers.get_mknodes_macros()
        # env.globals["mknodes"].update(mknodes_macros)

    def on_pre_page(
        self,
        page: Page,
        *,
        config: MkDocsConfig,
        files: Files,
    ) -> Page | None:
        """During this phase we set the edit paths."""
        node = self.project.infocollector["page_mapping"].get(page.file.src_uri)
        edit_path = node._edit_path if isinstance(node, mkpage.MkPage) else None
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

    # def on_page_context(
    #     self,
    #     context: TemplateContext,
    #     *,
    #     page: Page,
    #     config: MkDocsConfig,
    #     nav: Navigation,
    # ) -> TemplateContext | None:
    #     """Also add our info stuff to the MkDocs jinja context."""
    #     context["mknodes"] = self.project.infocollector.variables
    #     return context

    def on_post_build(self, config: MkDocsConfig):
        """Delete the temporary template files."""
        if not config.theme.custom_dir:
            return
        for template in self.project.templates:
            path = pathlib.Path(config.theme.custom_dir) / template.filename
            path.unlink(missing_ok=True)
