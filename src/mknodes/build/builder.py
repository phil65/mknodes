"""Core documentation builder."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import logfire

from mknodes.utils import icons, log, resources


if TYPE_CHECKING:
    import mknodes as mk

    from .output import BuildOutput


@dataclass
class PageResult:
    """Result of processing a single page."""

    path: str
    content: str
    resources: resources.Resources


logger = log.get_logger(__name__)


class DocBuilder:
    """Traverses node tree, renders markdown, collects resources."""

    def __init__(self, render_jinja: bool = True, max_workers: int | None = None) -> None:
        """Constructor.

        Args:
            render_jinja: Whether to render Jinja templates in pages.
            max_workers: Maximum number of worker threads for parallel processing.
        """
        self.render_jinja = render_jinja
        self.max_workers = max_workers
        self._files: dict[str, str | bytes] = {}
        self._file_resources: dict[str, resources.Resources] = {}

    async def build(self, root: mk.MkNav) -> BuildOutput:
        """Build documentation from a navigation tree.

        Args:
            root: Root navigation node to build from.

        Returns:
            BuildOutput containing all files and collected resources.
        """
        import mknodes as mk
        from mknodes.build.output import BuildOutput

        logger.info("Starting documentation build...")

        # Collect all nodes, separate pages and navs
        pages: list[mk.MkPage] = []
        navs: list[mk.MkNav] = []
        for _level, node in root.iter_nodes():
            self._files |= node.files
            match node:
                case mk.MkPage() as page:
                    pages.append(page)
                case mk.MkNav() as nav:
                    navs.append(nav)

        # Process pages in parallel
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [loop.run_in_executor(pool, self._process_page_sync, page) for page in pages]
            page_results = list(await asyncio.gather(*futures))

        for result in page_results:
            if result:
                self._files[result.path] = result.content
                self._file_resources[result.path] = result.resources

        # Process navs (fast, no parallelization needed)
        for nav in navs:
            await self._process_nav(nav)

        nav_structure = root.nav.to_nav_dict()
        return BuildOutput(
            files=self._files,
            file_resources=self._file_resources,
            nav_structure=nav_structure,
            page_count=len([r for r in page_results if r]),
        )

    def _process_page_sync(self, page: mk.MkPage) -> PageResult | None:
        """Process a page synchronously (for thread pool).

        Args:
            page: Page to process.

        Returns:
            PageResult or None if skipped.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._process_page(page))
        finally:
            loop.close()

    @logfire.instrument("Processing page {page.title}")
    async def _process_page(self, page: mk.MkPage) -> PageResult | None:
        """Process a single page: render and collect resources.

        Args:
            page: Page to process.

        Returns:
            PageResult or None if skipped.
        """
        if page.resolved_metadata.inclusion_level is False:
            return None

        path = page.resolved_file_path
        logger.debug("Processing page: %s", path)
        # Single-pass: get markdown and aggregated resources together
        content = await page.get_content()
        req = self._with_base_extensions(content.resources, page)
        md = content.markdown
        # Apply page's processors
        for proc in page.get_processors():
            md = proc.run(md)
        if self.render_jinja:
            render = page.metadata.get("render_macros", True)
            if render:
                md = await page.env.render_string_async(md)
        return PageResult(path=path, content=md, resources=req)

    @logfire.instrument("Processing nav {nav.title}")
    async def _process_nav(self, nav: mk.MkNav) -> None:
        """Process a navigation section.

        Args:
            nav: Navigation to process.
        """
        path = nav.resolved_file_path
        logger.debug("Processing nav: %s", nav.title or "[ROOT]")
        # Single-pass: get markdown and aggregated resources together
        content = await nav.get_content()
        self._file_resources[path] = self._with_base_extensions(content.resources, nav)
        md = content.markdown
        # Apply nav's processors
        for proc in nav.get_processors():
            md = proc.run(md)
        self._files[path] = md

    def _with_base_extensions(
        self, req: resources.Resources, node: mk.MkNode
    ) -> resources.Resources:
        """Add base markdown extensions to resources."""
        base_extensions: dict[str, dict[str, Any]] = {
            "attr_list": {},
            "md_in_html": {},
            "pymdownx.emoji": {
                "emoji_index": icons.twemoji,
                "emoji_generator": icons.to_svg,
            },
            "pymdownx.magiclink": dict(
                repo_url_shorthand=True,
                user=node.ctx.metadata.repository_username,
                repo=node.ctx.metadata.repository_name,
            ),
        }
        result = resources.Resources(markdown_extensions=base_extensions)
        result.merge(req)
        return result
