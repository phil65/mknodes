"""DocBuilder: renders a node tree into an engine-neutral `BuildOutput`."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import dataclasses
import pathlib
from typing import TYPE_CHECKING

import logfire

from mknodes import rendering
from mknodes.build import fencecheck, pagetemplates
from mknodes.build.output import BuildOutput, Script, SiteMetadata, nav_from_dict
from mknodes.mdlib import mdconverter
from mknodes.utils import log, resources


if TYPE_CHECKING:
    import mknodes as mk


logger = log.get_logger(__name__)

# Folder (relative to the docs root) for CSS / JS / assets created by nodes.
ASSETS_DIR = "assets"


async def _render_page_jinja(page: mk.MkPage, md: str) -> str:
    """Render the page Markdown with Jinja (skipped if it contains no Jinja syntax).

    Compiling a whole page is expensive; text without delimiters renders to itself
    (newlines normalized, one trailing newline dropped).
    """
    env = page.env
    markers = (env.variable_start_string, env.block_start_string, env.comment_start_string)
    if env.line_statement_prefix or env.line_comment_prefix or any(m in md for m in markers):
        return await env.render_string_async(md)
    md = md.replace("\r\n", "\n").replace("\r", "\n")
    if not env.keep_trailing_newline and md.endswith("\n"):
        md = md[:-1]
    return md.replace("\n", env.newline_sequence)


@dataclasses.dataclass
class PageResult:
    """Result of rendering a single page."""

    path: str
    markdown: str
    resources: resources.Resources


class DocBuilder:
    """Renders a node tree (root `MkNav` + optional theme) into a `BuildOutput`.

    For each page: render the Markdown in the chosen flavour, collect its resources,
    wire up its page template and optionally render it with Jinja. Afterwards the
    resources of all pages (+ theme) get turned into assets, stylesheets, scripts and
    Markdown extensions, and the nav into a `NavItem` tree.
    """

    def __init__(
        self,
        *,
        flavor: str | rendering.Renderer | None = None,
        render_jinja: bool = True,
        show_page_info: bool = False,
        global_resources: bool = True,
        max_workers: int | None = None,
    ) -> None:
        """Constructor.

        Args:
            flavor: Markdown flavour to render (default: the active renderer, Material).
            render_jinja: Render pages with their Jinja environment (pages can opt out
                          with the `render_macros: false` metadata).
            show_page_info: Append a collapsible box with build info to every page
                            (pages can override with the `show_page_info` metadata).
            global_resources: Collect page CSS / JS for the whole site. If False, they get
                              moved into the page templates (only these pages load them).
            max_workers: Render pages in that many threads (default: sequentially).
        """
        self.renderer = rendering.get_renderer(flavor)
        self.render_jinja = render_jinja
        self.show_page_info = show_page_info
        self.global_resources = global_resources
        self.max_workers = max_workers

    async def build(self, root: mk.MkNav, theme: mk.Theme | None = None) -> BuildOutput:
        """Render given tree.

        Args:
            root: Root nav of the tree.
            theme: Theme whose resources, templates and extras get included.
        """
        import mknodes as mk

        logger.info("Building documentation (flavor: %s)...", self.renderer.name)
        output = BuildOutput(
            metadata=SiteMetadata.from_context(root.ctx),
            flavor=self.renderer.name,
        )
        pages: list[mk.MkPage] = []
        navs: list[mk.MkNav] = []
        files: dict[str, str | bytes] = {}
        # Walk the tree in the target flavour: template nodes render once while their
        # children get collected and reuse that render for their content.
        with rendering.use(self.renderer):
            theme_nodes = list(theme.iter_nodes()) if theme else []
            all_nodes = [*theme_nodes, *root.iter_nodes()]
        for _, node in all_nodes:
            files |= node.files
            match node:
                case mk.MkPage() as page if page.resolved_metadata.inclusion_level is not False:
                    pages.append(page)
                case mk.MkNav() as nav:
                    navs.append(nav)
        # Nav templates first: pages inherit the template reference of their navs.
        for nav in navs:
            pagetemplates.update_nav_template(nav)
        with rendering.use(self.renderer):
            results = await self._render_pages(pages)
            nav_resources = [(await self.renderer.render(nav)).resources for nav in navs]

        req = resources.Resources()
        for result in results:
            files[result.path] = result.markdown
            output.page_resources[result.path] = result.resources
            req.merge(result.resources)
        for res in nav_resources:
            req.merge(res)
        for page in pages:
            if page._edit_path:
                path = pathlib.PurePath(page.resolved_file_path).as_posix()
                output.edit_paths[path] = page._edit_path
        self._add_files(output, files)
        self.renderer.finalize(output, root)
        for path, md in output.pages.items():
            for problem in fencecheck.check_fences(md):
                logger.warning("%s: %s", path, problem)
        if theme:
            req.merge(await theme.get_resources())
            theme.adapt_extensions(req.markdown_extensions)
        self._add_resources(output, req)
        templates = [p.template for p in pages] + [n.page_template for n in navs]
        if theme:
            templates += list(theme.templates)
        await self._add_templates(output, [t for t in templates if t])
        output.nav = nav_from_dict(root.nav.to_nav_dict())
        if theme:
            theme.adapt_extras(output.extra)
        logger.info("Built %s pages, %s assets", len(output.pages), len(output.assets))
        return output

    async def _render_pages(self, pages: list[mk.MkPage]) -> list[PageResult]:
        if not self.max_workers or self.max_workers <= 1:
            return [await self._render_page(page) for page in pages]
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [loop.run_in_executor(pool, self._render_page_sync, p) for p in pages]
            return list(await asyncio.gather(*futures))

    def _render_page_sync(self, page: mk.MkPage) -> PageResult:
        """Render a page in a worker thread (own event loop, renderer set explicitly)."""
        loop = asyncio.new_event_loop()
        try:
            with rendering.use(self.renderer):
                return loop.run_until_complete(self._render_page(page))
        finally:
            loop.close()

    @logfire.instrument("Rendering page {page.title}")
    async def _render_page(self, page: mk.MkPage) -> PageResult:
        path = page.resolved_file_path
        logger.debug("Rendering page %s", path)
        content = await self.renderer.render(page)
        md = content.markdown
        if self.global_resources:
            req = content.resources
        else:
            req = await pagetemplates.move_resources_to_template(page, content.resources)
        show_info = page.resolved_metadata.get("show_page_info")
        if self.show_page_info if show_info is None else show_info:
            info = await self.renderer.render(pagetemplates.create_page_info(page, req))
            md = f"{md}\n\n{info.markdown}"
            req.merge(info.resources)
        # The template must be known before the metadata header gets rendered.
        pagetemplates.update_page_template(page)
        md = self.renderer.process(page, md)
        render = page.metadata.get("render_macros")
        if self.render_jinja if render is None else render:
            md = await _render_page_jinja(page, md)
        return PageResult(path=path, markdown=md, resources=req)

    @staticmethod
    def _add_files(output: BuildOutput, files: dict[str, str | bytes]) -> None:
        """Sort rendered pages and node files into pages (Markdown) and assets."""
        for path, content in files.items():
            posix = pathlib.PurePosixPath(pathlib.PurePath(path).as_posix())
            if posix.suffix == ".md" and isinstance(content, str):
                output.pages[str(posix)] = content
            else:
                output.assets[str(posix)] = content

    @staticmethod
    def _add_resources(output: BuildOutput, req: resources.Resources) -> None:
        """Turn resources into extensions, assets, stylesheets and scripts."""
        for name, cfg in req.markdown_extensions.items():
            output.markdown_extensions[name] = dict(cfg or {})
        for css in req.css:
            if isinstance(css, resources.CSSText):
                css_path = f"{ASSETS_DIR}/{css.resolved_filename}"
                output.assets[css_path] = css.content
            else:
                css_path = str(css)
            if css_path not in output.extra_css:
                output.extra_css.append(css_path)
        # Linked scripts first, then the ones written as assets.
        for js in sorted(req.js, key=lambda j: isinstance(j, resources.JSText)):
            if isinstance(js, resources.JSText):
                js_path = f"{ASSETS_DIR}/{js.resolved_filename}"
                output.assets[js_path] = js.content
            else:
                js_path = str(js)
            if all(s.path != js_path for s in output.extra_javascript):
                script = Script(js_path, js.defer, js.async_, js.typ or None)
                output.extra_javascript.append(script)
        for asset in req.assets:
            in_root = asset.target_dir == "docs_dir"
            asset_path = asset.filename if in_root else f"{ASSETS_DIR}/{asset.filename}"
            output.assets[asset_path] = asset.content

    @staticmethod
    async def _add_templates(output: BuildOutput, templates: list[mk.PageTemplate]) -> None:
        """Render page templates (theme overrides) to HTML."""
        exts = output.markdown_extensions
        md = mdconverter.MdConverter(extensions=list(exts), extension_configs=exts)
        for template in templates:
            if template.filename and (html := await template.build_html(md)):
                output.templates[template.filename] = html
