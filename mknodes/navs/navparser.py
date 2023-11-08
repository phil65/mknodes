from __future__ import annotations

import ast
import os
import pathlib

from posixpath import join as urljoin
import re
from typing import TYPE_CHECKING, Any
from urllib import parse

import upath

from mknodes.basenodes import mkcode
from mknodes.navs import mknav
from mknodes.pages import mkpage
from mknodes.utils import classhelpers, helpers, log


if TYPE_CHECKING:
    import mknodes as mk


logger = log.get_logger(__name__)

# for SUMMARY.md parsing
SECTION_AND_FILE_RE = r"^\* \[(.*)\]\((.*)\)"
SECTION_AND_FOLDER_RE = r"^\* \[(.*)\]\((.*)\/\)"
SECTION_RE = r"^\* (.*)"

# for ->MkNode parsing
ARGS_KWARGS_RE = r".*\((.*)\)"  # get brace content


def str2node(
    path: str | os.PathLike,
    name: str | None = None,
    parent: mk.MkNode | None = None,
    **kwargs,
) -> mk.MkPage | mk.MkNav:
    """Parse given path, check for our -> syntax, and return a MkPage / MkNav.

    If -> is detected, return a MkPage containing given MkNode. Otherwise
    open / download the markdown file from given path and put that into an MkPage.

    Arguments:
        path: Path to build a MkPage for (Either path / URL or "-> MkNode")
        name: Name for given MkPage
        parent: Parent for the MkPage
        kwargs: Additional metadata for MkPage
    """
    import mknodes as mk

    path = os.fspath(path)
    logger.debug("Adding file %r", path)
    node_cls_name = path.removeprefix("->").strip().split("(")[0]
    if path.startswith("->") and node_cls_name in mk.__all__:
        node_cls = getattr(mk, node_cls_name)
        args = []
        kwargs = {}
        if match := re.match(ARGS_KWARGS_RE, path):
            parts = match[1].split(",")
            args = [ast.literal_eval(i.strip()) for i in parts if "=" not in i]
            kwargs_iter = (i.strip().split("=", maxsplit=1) for i in parts if "=" in i)
            kwargs = {i[0]: ast.literal_eval(i[1]) for i in kwargs_iter}
        msg = "Parsed: Node: %s, args: %s, kwargs: %s"
        logger.debug(msg, node_cls.__name__, args, kwargs)
        if issubclass(node_cls, mk.MkNav | mk.MkPage):
            return node_cls(*args, parent=parent, **kwargs)
        page = mk.MkPage(name, parent=parent, **kwargs)
        page += node_cls(*args, **kwargs)
        return page
    if path.startswith(r"{{"):
        page = mk.MkPage(name, parent=parent, **kwargs)
        page += mk.MkText(path, render_jinja=True)
        return page
    return mk.MkPage.from_file(path, title=name, **kwargs)


def from_list(
    ls: list,
    nav: mk.MkNav,
    base_path: str = "",
):
    """Parse given list recursively and add found content to given MkNav.

    Arguments:
        ls: List to parse
        nav: MkNav to attach found stuff to
        base_path: All found paths will be relative to this one if given.
    """
    for item in ls:
        match item:
            case dict():
                name, val = next(iter(item.items()))
                match val:
                    case dict():
                        logger.debug("Adding nav %r", name)
                        from_dict(val, nav.add_nav(name), base_path=base_path)
                    case str():
                        path = urljoin(base_path, val)
                        nav += str2node(path=path, name=name, parent=nav)
                    case list():
                        logger.debug("Adding nav %r", name)
                        if helpers.is_url(name):
                            path = parse.urlsplit(name).path
                            name = pathlib.Path(path).name
                        from_list(val, nav.add_nav(name), base_path=base_path)
            case str():
                path = urljoin(base_path, item)
                page = mkpage.MkPage.from_file(path)
                logger.debug("Adding page %s", path)
                nav += page


def from_dict(
    dct: dict[str, str | list | dict],
    nav: mk.MkNav,
    base_path: str = "",
):
    """Parse given dict recursively and add found content to given MkNav.

    Arguments:
        dct: Dictionary to parse
        nav: MkNav to attach found stuff to
        base_path: All found paths will be relative to this one if given.
    """
    base_path = base_path.replace("\\", "/")
    for k, v in dct.items():
        match v:
            case str():
                path = urljoin(base_path, v)
                nav += str2node(path=path, name=k, parent=nav)
            case dict():
                logger.debug("Adding nav %r", k)
                from_dict(v, nav.add_nav(k), base_path=base_path)
            case list():
                logger.debug("Adding nav %r", k)
                from_list(v, nav.add_nav(k), base_path=base_path)


class NavParser:
    """Class used for constructing MkNavs."""

    def __init__(self, nav: mk.MkNav):
        """Constructor.

        Arguments:
            nav: MkNav to use for routing
        """
        self._nav = nav

    def json(
        self,
        obj: list | dict[str, str | list | dict],
    ):
        """Parse given list or dict and attach it to given MkNav.

        If no Nav is given, create a new one
        Arguments:
            obj: Dictionary / List to parse
        """
        match obj:
            case dict():
                from_dict(obj, self._nav)
            case list():
                from_list(obj, self._nav)

    def file(
        self,
        path: str | os.PathLike,
        **kwargs: Any,
    ) -> mk.MkNav:
        """Load an existing SUMMARY.md style file.

        For each indentation level in SUMMARY.md, a new sub-nav is created.

        Should support all SUMMARY.md options except wildcards.

        Arguments:
            path: Path to the file
            kwargs: Keyword arguments passed to the pages to create.
                    Can be used to hide the TOC for all pages for example.
        """
        path = pathlib.Path(path)
        if path.is_absolute():
            path = os.path.relpath(path, pathlib.Path().absolute())
            path = pathlib.Path(path)
        return self.text(
            path.read_text(),
            path=path,
            **kwargs,
        )

    def text(
        self,
        text: str,
        path: pathlib.Path,
        **kwargs: Any,
    ) -> mk.MkNav:
        """Create a nav based on a SUMMARY.md-style list, given as text.

        For each indentation level, a new sub-nav is created.

        Should support all SUMMARY.md options except wildcards.

        Arguments:
            text: Text to parse
            path: path of the file containing the text.
            kwargs: Keyword arguments passed to the pages to create.
                    Can be used to hide the TOC for all pages for example.
        """
        lines = text.splitlines()
        for i, line in enumerate(lines):
            # * [Example](example_folder/)

            if m := re.match(SECTION_AND_FOLDER_RE, line):
                folder_path = path.parent / m[2]
                if (file_path := (folder_path / "SUMMARY.md")).exists():
                    subnav = mknav.MkNav(m[1], parent=self._nav)
                    subnav.parse.file(file_path, **kwargs)
                elif (file_path := (folder_path / "index.py")).exists():
                    mod = classhelpers.import_file(file_path)
                    subnav = mod.nav
                    subnav.parent = self._nav
                else:
                    msg = "No SUMMARY.md / index.py found."
                    raise RuntimeError(msg)
                self._nav[m[1]] = subnav
                logger.debug("Created subsection %s from %s", m[1], file_path)

            # * [Example](example_folder/sub_1.md)

            elif m := re.match(SECTION_AND_FILE_RE, line):
                # if following section indented, it is a nav with an index page:
                if unindented := helpers.get_indented_lines(lines[i + 1 :]):
                    subnav = mknav.MkNav(m[1], parent=self._nav)
                    text = "\n".join(unindented)
                    subnav.parse.text(text, path=path, **kwargs)
                    page = subnav.add_page(is_index=True, **kwargs)
                    page += upath.UPath(m[2]).read_text()
                    msg = "Created subsection %s and loaded index page %s"
                    logger.debug(msg, m[1], m[2])
                    self._nav += subnav

                # if not, add as regular page:
                else:
                    p = m[2] if m[2].startswith(("->", r"{{")) else path.parent / m[2]
                    page = str2node(path=p, name=m[1], parent=self._nav, **kwargs)
                    self._nav[m[1]] = page
                    logger.debug("Created page %s from %s", m[1], m[2])

            # * Section/

            elif m := re.match(SECTION_RE, line):
                unindented = helpers.get_indented_lines(lines[i + 1 :]) or []
                logger.debug("Created subsection %s from text", m[1])
                subnav = mknav.MkNav(m[1], parent=self._nav)
                text = "\n".join(unindented)
                subnav.parse.text(text, path=path, **kwargs)
                self._nav[m[1]] = subnav
        return self._nav

    def folder(
        self,
        folder: str | os.PathLike,
        *,
        recursive: bool = True,
        **kwargs: Any,
    ) -> mk.MkNav:
        """Load a MkNav tree from Folder.

        SUMMARY.mds are ignored.
        index.md files become index pages.

        To override the default behavior of using filenames as menu titles,
        the pages can set a title by using page metadata.

        Arguments:
            folder: Folder to load .md files from
            recursive: Whether all .md files should be included recursively.
            kwargs: Keyword arguments passed to the pages to create.
                    Can be used to hide the TOC for all pages for example.
        """
        import mknodes as mk

        folder = pathlib.Path(folder)
        nav = self._nav
        for path in folder.iterdir():
            is_hidden = path.name.startswith(("_", "."))
            if recursive and path.is_dir() and not is_hidden and any(path.iterdir()):
                path = folder / path.parts[-1]
                subnav = mk.MkNav(path.name)
                subnav.parse.folder(folder=path, **kwargs)
                nav += subnav
                logger.debug("Loaded subnav from from %s", path)
            elif path.name == "index.md":
                logger.debug("Loaded index page from %s", path)
                text = path.read_text(encoding="utf-8")
                title = nav.title or "Home"
                nav.index_page = mk.MkPage(title, path=path.name, content=text, **kwargs)
            elif path.suffix in [".md", ".html"] and path.name != "SUMMARY.md":
                text = path.read_text(encoding="utf-8")
                rel_path = path.relative_to(folder)
                nav += mk.MkPage(path=rel_path, content=text, **kwargs)
                logger.debug("Loaded page from from %s", path)
        return nav

    def module(
        self,
        module: str | os.PathLike,
        *,
        recursive: bool = True,
        **kwargs: Any,
    ) -> mk.MkNav:
        """Load a MkNav tree from a Module.

        Will add a page for each module showing the code in a code box.

        Arguments:
            module: Module to load code files for
            recursive: Whether all .md files should be included recursively.
            kwargs: Keyword arguments passed to the pages to create.
                    Can be used to hide the TOC for all pages for example.
        """
        # if isinstance(module, types.ModuleType):
        #     module = inspecthelpers.get_file(module)
        for path in pathlib.Path(module).iterdir():
            is_hidden = path.name.startswith(("_", "."))
            if recursive and path.is_dir() and not is_hidden and any(path.iterdir()):
                subnav = mknav.MkNav(path.name)
                subnav.parse.folder(folder=path, **kwargs)
                self._nav += subnav
                logger.debug("Loaded subnav from from %s", path)
            elif path.suffix in [".py"]:
                page = mkpage.MkPage(path=path.name, title=path.name, **kwargs)
                content = path.read_text(encoding="utf-8")
                page += mkcode.MkCode(content, linenums=1)
                self._nav += page
                logger.debug("Loaded page from from %s", path)
        return self._nav


if __name__ == "__main__":
    log.basic()
    nav = mknav.MkNav()
    nav.parse.module("mknodes/manual/")
    print(nav)
