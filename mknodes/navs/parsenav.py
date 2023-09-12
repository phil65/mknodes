"""The Mkdocs Plugin."""

from __future__ import annotations

import ast
import os
import pathlib
import re

from typing import TYPE_CHECKING
from urllib import parse

from mknodes.navs import mknav
from mknodes.pages import mkpage
from mknodes.utils import helpers, log


SECTION_AND_FILE_REGEX = r"^\* \[(.*)\]\((.*\.md)\)"
SECTION_AND_FOLDER_REGEX = r"^\* \[(.*)\]\((.*)\/\)"
SECTION_REGEX = r"^\* (.*)"

ARGS_KWARGS_RE = r".*\((.*)\)"  # get brace content

if TYPE_CHECKING:
    import mknodes

logger = log.get_logger(__name__)


def add_page(path: str | os.PathLike, name: str | None = None, **kwargs):
    import mknodes

    path = os.fspath(path)
    logger.debug("Adding file %r", path)
    node_cls_name = path.removeprefix("->").strip().split("(")[0]
    if path.startswith("->") and node_cls_name in mknodes.__all__:
        node_cls = getattr(mknodes, node_cls_name)
        page = mknodes.MkPage(name, **kwargs)
        if match := re.match(ARGS_KWARGS_RE, path):
            parts = match[1].split(",")
            args = [ast.literal_eval(i.strip()) for i in parts if "=" not in i]
            kwargs_iter = (i.strip().split("=", maxsplit=1) for i in parts if "=" in i)
            kwargs = {i[0]: ast.literal_eval(i[1]) for i in kwargs_iter}
            msg = "Parsed: Node: %s, args: %s, kwargs: %s"
            logger.debug(msg, node_cls.__name__, args, kwargs)
            page += node_cls(*args, **kwargs)
        else:
            page += node_cls()
        return page
    return mkpage.MkPage.from_file(path, title=name, **kwargs)


def from_list(
    ls: list,
    nav: mknodes.MkNav,
):
    for item in ls:
        match item:
            case dict():
                name, val = next(iter(item.items()))
                match val:
                    case dict():
                        logger.debug("Adding nav %r", name)
                        from_dict(val, nav.add_nav(name))
                    case str():
                        nav += add_page(path=val, name=name)
                    case list():
                        logger.debug("Adding nav %r", name)
                        if helpers.is_url(name):
                            name = pathlib.Path(parse.urlsplit(name).path).name
                        from_list(val, nav.add_nav(name))
            case str():
                page = mkpage.MkPage.from_file(item)
                logger.debug("Adding page %s", item)
                nav += page


def from_dict(
    dct: dict[str, str | list | dict],
    nav: mknodes.MkNav,
):
    for k, v in dct.items():
        match v:
            case str():
                nav += add_page(path=v, name=k)
            case dict():
                logger.debug("Adding nav %r", k)
                from_dict(v, nav.add_nav(k))
            case list():
                logger.debug("Adding nav %r", k)
                from_list(v, nav.add_nav(k))


def from_json(
    static_pages: list | dict[str, str | list | dict],
    nav: mknodes.MkNav | None,
):
    if nav is None:
        nav = mknodes.MkNav()
    match static_pages:
        case dict():
            from_dict(static_pages, nav)
        case list():
            from_list(static_pages, nav)


def from_file(
    path: str | os.PathLike,
    section: str | None = None,
    *,
    hide_toc: bool | None = None,
    hide_nav: bool | None = None,
    hide_path: bool | None = None,
    parent: mknav.MkNav | None = None,
) -> mknav.MkNav:
    """Load an existing SUMMARY.md style file.

    For each indentation level in SUMMARY.md, a new sub-nav is created.

    Should support all SUMMARY.md options except wildcards.

    Arguments:
        path: Path to the file
        section: Section name of new nav
        hide_toc: Hide table of contents for all pages
        hide_nav: Hide navigation menu for all pages
        hide_path: Hide breadcrumbs path for all pages
        parent: Optional parent item if the SUMMARY.md shouldnt be used as root nav.

    """
    path = pathlib.Path(path)
    if path.is_absolute():
        path = os.path.relpath(path, pathlib.Path().absolute())
    path = pathlib.Path(path)
    content = path.read_text()
    return mknav.MkNav._from_text(
        content,
        section=section,
        hide_toc=hide_toc,
        hide_nav=hide_nav,
        hide_path=hide_path,
        parent=parent,
        path=path,
    )
    # max_indent = max(len(line) - len(line.lstrip()) for line in content.split("\n"))
    # content = [line.lstrip() for line in content.split("\n")]


def from_text(
    text: str,
    path: pathlib.Path,
    *,
    section: str | None = None,
    hide_toc: bool | None = None,
    hide_nav: bool | None = None,
    hide_path: bool | None = None,
    parent: mknav.MkNav | None = None,
) -> mknav.MkNav:
    """Create a nav based on a SUMMARY.md-style list, given as text.

    For each indentation level, a new sub-nav is created.

    Should support all SUMMARY.md options except wildcards.

    Arguments:
        text: Text to parse
        section: Section name for the nav
        hide_toc: Hide table of contents for all pages
        hide_nav: Hide navigation menu for all pages
        hide_path: Hide breadcrumbs path for all pages
        parent: Optional parent-nav in case the new nav shouldnt become the root nav.
        path: path of the file containing the text.
    """
    nav = mknav.MkNav(section, parent=parent)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        # for first case we need to check whether following lines are indented.
        # If yes, then the path describes an index page.
        # * [Example](example_folder/sub_1.md)
        if match := re.match(SECTION_AND_FILE_REGEX, line):
            if unindented := helpers.get_indented_lines(lines[i + 1 :]):
                subnav = mknav.MkNav._from_text(
                    "\n".join(unindented),
                    section=match[1],
                    hide_toc=hide_toc,
                    hide_nav=hide_nav,
                    hide_path=hide_path,
                    parent=nav,
                    path=path,
                )
                page = subnav.add_index_page(
                    hide_toc=hide_toc,
                    hide_nav=hide_nav,
                    hide_path=hide_path,
                )
                page += pathlib.Path(match[2]).read_text()
                logger.debug(
                    "Created subsection %s and loaded index page %s",
                    match[1],
                    match[2],
                )
                nav += subnav
            else:
                page = mkpage.MkPage.from_file(
                    path=path.parent / match[2],
                    hide_toc=hide_toc,
                    hide_nav=hide_nav,
                    hide_path=hide_path,
                    parent=nav,
                )
                nav[match[1]] = page
                logger.debug("Created page %s from %s", match[1], match[2])
        # * [Example](example_folder/)
        elif match := re.match(SECTION_AND_FOLDER_REGEX, line):
            file_path = path.parent / f"{match[2]}/SUMMARY.md"
            subnav = mknav.MkNav.from_file(
                file_path,
                section=match[1],
                hide_toc=hide_toc,
                hide_nav=hide_nav,
                hide_path=hide_path,
                parent=nav,
            )
            nav[match[1]] = subnav
            logger.debug("Created subsection %s from %s", match[1], file_path)
        # * Example
        elif match := re.match(SECTION_REGEX, line):
            unindented = helpers.get_indented_lines(lines[i + 1 :]) or []
            subnav = mknav.MkNav._from_text(
                "\n".join(unindented),
                section=match[1],
                hide_toc=hide_toc,
                hide_nav=hide_nav,
                hide_path=hide_path,
                parent=nav,
                path=path,
            )
            logger.debug("Created subsection %s from text", match[1])
            nav[match[1]] = subnav
    return nav


def from_folder(
    folder: str | os.PathLike,
    *,
    recursive: bool = True,
    hide_toc: bool | None = None,
    hide_nav: bool | None = None,
    hide_path: bool | None = None,
    parent: mknav.MkNav | None = None,
) -> mknav.MkNav:
    """Load a mknav.MkNav tree from Folder.

    SUMMARY.mds are ignored.
    index.md files become index pages.

    To override the default behavior of using filenames as menu titles,
    the pages can set a title by using page metadata.

    Arguments:
        folder: Folder to load .md files from
        recursive: Whether all .md files should be included recursively.
        hide_toc: Whether to hide the toc for all pages
        hide_nav: Whether to hide the nav for all pages
        hide_path: Whether to hide the path for all pages
        parent: Optional parent-nav in case the new nav shouldnt become the root nav.
    """
    folder = pathlib.Path(folder)
    nav = mknav.MkNav(folder.name if parent else None, parent=parent)
    for path in folder.iterdir():
        if path.is_dir() and recursive and any(path.iterdir()):
            path = folder / path.parts[-1]
            subnav = mknav.MkNav.from_folder(
                folder=path,
                hide_toc=hide_toc,
                hide_nav=hide_nav,
                hide_path=hide_path,
                parent=nav,
            )
            nav += subnav
            logger.debug("Loaded subnav from from %s", path)
        elif path.name == "index.md":
            page = mkpage.MkPage(
                path=path.name,
                content=path.read_text(),
                hide_toc=hide_toc,
                hide_nav=hide_nav,
                hide_path=hide_path,
                parent=nav,
            )
            logger.debug("Loaded index page from %s", path)
            nav.index_page = page
            nav.index_title = nav.section or "Home"
        elif path.suffix in [".md", ".html"] and path.name != "SUMMARY.md":
            page = mkpage.MkPage(
                path=path.relative_to(folder),
                content=path.read_text(),
                hide_toc=hide_toc,
                hide_nav=hide_nav,
                hide_path=hide_path,
                parent=nav,
            )
            nav += page
            logger.debug("Loaded page from from %s", path)
    return nav


if __name__ == "__main__":
    import mknodes

    from mknodes import mkdocsconfig

    cfg = mkdocsconfig.Config()
    nav = mknodes.MkNav()
    dct = cfg.plugins["mknodes"].config.kwargs
    from_json(dct, nav)
    print(list(nav.descendants))
