"""Core documentation builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mknodes.utils import log, resources


if TYPE_CHECKING:
    import mknodes as mk

    from .output import BuildOutput


logger = log.get_logger(__name__)


class DocBuilder:
    """Traverses node tree, renders markdown, collects resources."""

    def __init__(self, render_jinja: bool = True):
        """Constructor.

        Args:
            render_jinja: Whether to render Jinja templates in pages.
        """
        self.render_jinja = render_jinja
        self._files: dict[str, str | bytes] = {}
        self._resources = resources.Resources()

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
        page_count = 0
        # First pass: collect all pages and navs
        for _level, node in root.iter_nodes():
            self._files |= node.files

            match node:
                case mk.MkPage() as page:
                    await self._process_page(page)
                    page_count += 1
                case mk.MkNav() as nav:
                    await self._process_nav(nav)

        # Build nav structure
        nav_structure = root.nav.to_nav_dict()

        return BuildOutput(
            files=self._files,
            resources=self._resources,
            nav_structure=nav_structure,
            page_count=page_count,
        )

    async def _process_page(self, page: mk.MkPage) -> None:
        """Process a single page: render and collect resources.

        Args:
            page: Page to process.
        """
        if page.resolved_metadata.inclusion_level is False:
            return

        path = page.resolved_file_path
        logger.debug("Processing page: %s", path)
        req = await page.get_resources()
        self._resources.merge(req)
        md = await page.to_markdown()
        if self.render_jinja:
            render = page.metadata.get("render_macros", True)
            if render:
                md = await page.env.render_string_async(md)
        self._files[path] = md

    async def _process_nav(self, nav: mk.MkNav) -> None:
        """Process a navigation section.

        Args:
            nav: Navigation to process.
        """
        path = nav.resolved_file_path
        logger.debug("Processing nav: %s", nav.title or "[ROOT]")
        req = await nav.get_node_resources()
        self._resources.merge(req)
        md = await nav.to_markdown()
        self._files[path] = md
