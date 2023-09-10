"""The Mkdocs Plugin."""

from __future__ import annotations

import pathlib
import urllib.parse

from typing import TYPE_CHECKING, Literal

from mkdocs.plugins import BasePlugin, get_plugin_logger

from mknodes import mkdocsconfig, project
from mknodes.basenodes import mknode
from mknodes.pages import mkpage
from mknodes.plugin import linkreplacer, mkdocsbuilder, pluginconfig
from mknodes.theme import theme

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
        self.link_replacer = linkreplacer.LinkReplacer()
        logger.debug("Finished initializing plugin")

    def on_startup(self, command: CommandStr, dirty: bool = False):
        """Activates new-style MkDocs plugin lifecycle."""

    def on_config(self, config: MkDocsConfig):
        """Create the project based on MkDocs config."""
        skin = theme.Theme.get_theme(
            theme_name=config.theme.name or "material",
            data=config.theme._vars,  # type: ignore[attr-defined]
        )
        self.project = project.Project(
            base_url=config.site_url or "",
            use_directory_urls=config.use_directory_urls,
            theme=skin,
            repo=self.config.repo_path,
            build_fn=self.config.path,
            build_kwargs=self.config.kwargs,
            clone_depth=self.config.clone_depth,
        )

    def on_files(self, files: Files, config: MkDocsConfig) -> Files:
        """Create the node tree and write files to build folder.

        In this step we aggregate all files and info we need to build the website.
        This includes:

          - Markdown pages (MkPages)
          - Templates
          - CSS files
        """
        cfg = mkdocsconfig.Config(config)
        self.builder = mkdocsbuilder.MkDocsBuilder(
            files=files,
            config=cfg,
            directory=self.config.build_folder,
        )
        logger.info("Generating pages...")
        build_files = self.project.all_files()

        logger.info("Writing pages to disk...")
        self.builder.write_files(build_files)  # type: ignore[arg-type]
        logger.info("Finished writing pages to disk")

        requirements = self.project.get_requirements()
        logger.info("Adding requirements to Config and build...")
        for k, v in requirements.css.items():
            cfg.register_css(k, v)
        for k, v in requirements.js_files.items():
            cfg.register_js(k, v)
        if extensions := requirements.markdown_extensions:
            cfg.register_extensions(extensions)
        md = cfg.get_markdown_instance()
        for template in requirements.templates:
            if html := template.build_html(md):
                cfg.register_template(template.filename, html)

        logger.info("Updating MkDocs config metadata...")
        ctx = self.project.context
        if not config.extra.get("social"):
            config.extra["social"] = ctx.metadata.social_info
        config.repo_url = ctx.metadata.repository_url
        config.site_description = ctx.metadata.summary
        config.site_name = ctx.metadata.distribution_name
        config.site_author = ctx.metadata.author_name
        return self.builder.files

    def on_nav(
        self,
        nav: Navigation,
        files: Files,
        config: MkDocsConfig,
    ) -> Navigation | None:
        """Populate LinkReplacer and build path->MkPage mapping for following steps."""
        for file_ in files:
            filename = pathlib.Path(file_.abs_src_path).name
            url = urllib.parse.unquote(file_.src_uri)
            self.link_replacer.mapping[filename].append(url)
        return nav

    def on_env(self, env: jinja2.Environment, config: MkDocsConfig, files: Files):
        """Add our own info to the MkDocs environment."""
        node_env = mknode.MkNode._env
        env.globals["mknodes"] = node_env.globals
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
        mapping = mknode.MkNode._env.globals["page_mapping"]
        node = mapping.get(page.file.src_uri)  # type: ignore[attr-defined]
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
        mapping = mknode.MkNode._env.globals["page_mapping"]
        node = mapping.get(page.file.src_uri)  # type: ignore[attr-defined]
        markdown = node.env.render_string(markdown)
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
    #     return context

    def on_post_build(self, config: MkDocsConfig):
        """Delete the temporary template files."""
        if not config.theme.custom_dir:
            return
        for template in self.project.templates:
            path = pathlib.Path(config.theme.custom_dir) / template.filename
            path.unlink(missing_ok=True)
