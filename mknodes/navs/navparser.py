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
    path: str | os.PathLike[str],
    name: str | None = None,
    parent: mk.MkNode | None = None,
    **kwargs: Any,
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
    return mk.MkPage.from_file(path, title=name, parent=parent, **kwargs)


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
        path: str | os.PathLike[str],
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

        This method parses a text input formatted similar to a SUMMARY.md file and
        creates a navigation structure based on it. For each indentation level in
        the input text, a new sub-nav is created. The method supports all SUMMARY.md
        options except wildcards.

        The method processes three main patterns in the input text:
        1. Section and folder: Creates a subnav from a SUMMARY.md or index.py file.
        2. Section and file: Creates a page or a subnav with an index page.
        3. Section only: Creates a subnav from the indented lines following it.

        Args:
            text: The input text to parse, formatted like a SUMMARY.md file.
            path: The path of the file containing the input text.
            **kwargs: Additional keyword arguments passed to the pages to create.
                      Can be used to set common properties for all pages.

        Returns:
            The updated navigation structure after processing the input text.

        Examples:
            ```python
            parser = NavParser(nav)
            text = '''
            * [Section 1](folder1/)
            * [Page 1](page1.md)
            * Section 2/
                * [Subpage 1](subpage1.md)
                * [Subpage 2](subpage2.md)
            '''
            updated_nav = parser.text(text, pathlib.Path("path/to/file"))
            ```
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
        folder: str | os.PathLike[str],
        *,
        recursive: bool = True,
        **kwargs: Any,
    ) -> mk.MkNav:
        """Load a MkNav tree from a folder.

        This method creates a navigation structure based on the contents of a specified folder.
        It processes Markdown (.md) and HTML (.html) files, creating a hierarchical navigation
        tree that reflects the folder structure.

        Specific behaviors:
        - SUMMARY.md files are ignored.
        - index.md files become index pages for their respective folders.
        - Hidden folders (starting with '.' or '_') are ignored.
        - Page titles can be overridden using page metadata.

        Args:
            folder: The folder to load .md and .html files from.
            recursive: Whether to include all files recursively from subfolders.
            **kwargs: Additional keyword arguments passed to the created pages.
                      Can be used to set global page properties, e.g., hiding TOC.

        Returns:
            A MkNav object representing the folder's navigation structure.

        Examples:
            ```python
            parser = NavParser(my_nav)
            folder_nav = parser.folder("docs/", recursive=True, toc=False)
            ```
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
        module: str | os.PathLike[str],
        *,
        recursive: bool = True,
        **kwargs: Any,
    ) -> mk.MkNav:
        """Load a MkNav tree from a Module.

        This method creates a navigation structure from a given module. It iterates through
        the module's directory, creating pages for Python files and sub-navigations for
        subdirectories. Each Python file is displayed as a page with its content in a code box.

        Args:
            module: The module to load code files from. Can be a string path or a PathLike object.
            recursive: Whether to include all files recursively.
            **kwargs: Additional keyword arguments passed to the pages being created.
                These can be used to customize page properties, e.g., hiding the TOC.

        Returns:
            An MkNav object representing the navigation structure of the module.

        Example:
            ```python
            parser = NavParser()
            nav = parser.module("mknodes", recursive=True, hide_toc=True)
            ```
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


def parse_new_style_nav(root_nav: mk.MkNav, items: list | dict):
    """Parse and add navigation items to the root navigation in a new style format.

    This function processes a list or dictionary of navigation items and adds them to the
    given root navigation. It supports various types of navigation items including pages,
    sub-navigations, and custom MkNode instances.

    The function recursively processes nested navigation structures and applies conditions
    for rendering items based on the environment.

    Args:
        root_nav: The root navigation object to which items will be added.
        items: A list or dictionary of navigation items to be parsed and added.

    Examples:
        ```python
        import mknodes as mk

        root_nav = mk.MkNav("Root")
        items = [
            {
                "type": "MkPage",
                "title": "Home",
                "is_homepage": True,
                "items": [
                    {"type": "MkHeader", "text": "Welcome"},
                    {"type": "MkText", "text": "This is the homepage."},
                ],
            },
            {
                "Home": [
                    {
                        "About": "https://raw.githubusercontent.com/phil65/mknodes/main/README.md"
                    }
                ]
            },
        ]
        parse_new_style_nav(root_nav, items)
        ```
    """
    import mknodes as mk

    if isinstance(items, dict):
        items = [items]
    for item in items:
        if "type" in item and "title" in item:
            if (
                condition := item.pop("condition", False)
            ) and not root_nav.env.render_condition(condition):
                continue
            kls = getattr(mk, item.pop("type"))
            title = item.pop("title")
            is_index = item.pop("is_index", False)
            is_homepage = item.pop("is_homepage", False)
            nodes = item.pop("items", [])
            instance = kls(**item)
            match instance:
                case mk.MkPage():
                    instance._is_index = is_index
                    instance._is_homepage = is_homepage
                    instance.title = title
                    root_nav += instance
                    for node_dct in nodes:
                        if (
                            condition := node_dct.pop("condition", False)
                        ) and not instance.env.render_condition(condition):
                            continue
                        kls = getattr(mk, node_dct.pop("type"))
                        if header := node_dct.pop("title", None):
                            instance += mk.MkHeader(header)
                        instance += kls(**node_dct)
                case mk.MkNav():
                    instance.title = title
                    root_nav += instance
                case _:
                    page = root_nav.add_page(
                        title,
                        is_index=is_index,
                        is_homepage=is_homepage,
                    )
                    page += instance
        else:
            name, items = next(iter(item.items()))
            if isinstance(items, str):
                root_nav += mk.MkPage.from_file(items, title=name)
            else:
                nav = root_nav.add_nav(name)
                parse_new_style_nav(nav, items)


if __name__ == "__main__":
    log.basic()
    nav = mknav.MkNav()
    nav.parse.module("mknodes/manual/")
    print(nav)
