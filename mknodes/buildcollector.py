from __future__ import annotations

import pathlib

import mknodes as mk

from mknodes.utils import log


logger = log.get_logger(__name__)


class BuildCollector:
    """MkNodes Project."""

    def __init__(self, nodes: list[mk.MkNode], show_code_admonition: bool = False):
        """The main project to create a website.

        Arguments:
            nodes: The theme to use
            show_code_admonition: Add a code admonition box to each page.
        """
        self.nodes = nodes
        self.show_code_admonition = show_code_admonition
        self.node_files: dict[str, str | bytes] = {}
        self.extra_files: dict[str, str | bytes] = {}
        for node in self.nodes:
            self.extra_files |= node.files
            match node:
                case mk.MkPage() as page:
                    self.collect_page(page)
                case mk.MkNav() as nav:
                    self.collect_nav(nav)

    def collect_page(self, page: mk.MkPage):
        path = page.resolved_file_path
        if self.show_code_admonition and page.created_by:
            code = mk.MkCode.for_object(page.created_by)
            typ = "section" if page.is_index() else "page"
            details = mk.MkAdmonition(
                code,
                title=f"Code for this {typ}",
                collapsible=True,
                typ="quote",
            )
            page.append(details)
        if page.inclusion_level:
            if page.template:
                node_path = pathlib.Path(path)
            elif any(i.page_template for i in page.parent_navs):
                nav = next(i for i in page.parent_navs if i.page_template)
                node_path = pathlib.Path(nav.resolved_file_path)
            else:
                node_path = None
            if node_path:
                html_path = node_path.with_suffix(".html").as_posix()
                page._metadata.template = html_path
                page.template.filename = html_path
                for nav in page.parent_navs:
                    if nav.page_template:
                        p = pathlib.Path(nav.resolved_file_path)
                        parent_path = p.with_suffix(".html").as_posix()
                        page.template.extends = parent_path
                        break
        md = page.to_markdown()
        self.node_files[path] = md

    def collect_nav(self, nav: mk.MkNav):
        logger.info("Processing section %r...", nav.section)
        path = nav.resolved_file_path
        if nav.page_template:
            html_path = pathlib.Path(path).with_suffix(".html").as_posix()
            for parent_nav in nav.parent_navs:
                if parent_nav.page_template:
                    p = pathlib.Path(parent_nav.resolved_file_path)
                    parent_path = p.with_suffix(".html").as_posix()
                    nav.page_template.extends = parent_path
                    break
            nav.metadata.template = html_path
            nav.page_template.filename = html_path
        md = nav.to_markdown()
        self.node_files[path] = md


if __name__ == "__main__":
    project = mk.Project.for_mknodes()
    from mknodes.manual import root

    log.basic()
    root.build(project)
    if project._root:
        nodes = [i[1] for i in project._root.iter_nodes()]
        collector = BuildCollector(nodes)
        print(collector.node_files)
