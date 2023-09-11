from __future__ import annotations

from collections.abc import Callable
import functools
import os
import pathlib

from typing import Any, Generic, TypeVar
import urllib.error

from mknodes.info import contexts, folderinfo, packageinfo
from mknodes.navs import mknav
from mknodes.pages import pagetemplate
from mknodes.theme import theme as theme_
from mknodes.utils import (
    classhelpers,
    helpers,
    linkprovider,
    log,
    reprhelpers,
    requirements,
)


logger = log.get_logger(__name__)


T = TypeVar("T", bound=theme_.Theme)


class Project(Generic[T]):
    """MkNodes Project."""

    def __init__(
        self,
        theme: T,
        base_url: str = "",
        use_directory_urls: bool = True,
        repo: str | os.PathLike | None | folderinfo.FolderInfo = None,
        build_fn: str | Callable = "mknodes.navs.mkwebsite:MkWebSite.for_project",
        build_kwargs: dict[str, Any] | None = None,
        clone_depth: int = 100,
    ):
        """The main project to create a website.

        Arguments:
            theme: The theme to use
            base_url: Base url of the website
            use_directory_urls: Whether urls are in directory-style
            repo: Path to the git repository
            build_fn: Callable to create the website with
            build_kwargs: Keyword arguments for the build function
            clone_depth: Amount of commits to clone in case repository is remote.
        """
        self.linkprovider = linkprovider.LinkProvider(
            base_url=base_url,
            use_directory_urls=use_directory_urls,
            include_stdlib=True,
        )
        self.theme: T = theme
        self.theme.associated_project = self
        self.templates = self.theme.templates
        self.error_page: pagetemplate.PageTemplate = self.templates["404.html"]
        match repo:
            case folderinfo.FolderInfo():
                self.folderinfo = repo
            case _ if helpers.is_url(str(repo)):
                self.folderinfo = folderinfo.FolderInfo.clone_from(
                    str(repo),
                    depth=clone_depth,
                )
            case _:
                self.folderinfo = folderinfo.FolderInfo(repo)
        self._root: mknav.MkNav | None = None
        if isinstance(build_fn, str):
            self.build_fn = classhelpers.get_callable_from_path(build_fn)
        else:
            self.build_fn = build_fn
        self.build_kwargs = build_kwargs or {}
        self.build()

    def build(self):
        logger.debug("Building page...")
        self.build_fn(project=self, **self.build_kwargs)
        logger.debug("Finished building page.")
        if not self._root:
            msg = "No root for project created."
            raise RuntimeError(msg)

        from mknodes.basenodes import mknode
        from mknodes.pages import mkpage

        page_mapping = {
            node.resolved_file_path: node
            for _level, node in self._root.iter_nodes()
            if isinstance(node, mkpage.MkPage | mknav.MkNav)
        }
        filenames = list(page_mapping.keys())
        paths = [pathlib.Path(i).stem for i in filenames]
        self.linkprovider.set_excludes(paths)

        from mknodes.pages import mkpage

        variables = self.context.as_dict()

        variables["filenames"] = page_mapping
        variables["page_mapping"] = page_mapping
        variables["requirements"] = self.get_requirements()
        mknode.MkNode._env.globals |= variables

    def __repr__(self):
        return reprhelpers.get_repr(self, repo_path=str(self.folderinfo.path))

    @classmethod
    def for_mknodes(cls, config=None) -> Project:
        from mknodes import mkdocsconfig

        config = mkdocsconfig.Config(config)
        return cls(
            base_url=config.site_url or "",
            use_directory_urls=config.use_directory_urls,
            theme=theme_.Theme.get_theme(config.theme.name, data=config.theme._vars),
            build_fn=config.plugins["mknodes"].config.path,
        )

    @classmethod
    def for_path(cls, path: str, config=None) -> Project:
        from mknodes import mkdocsconfig

        config = mkdocsconfig.Config(config)
        return cls(
            base_url=config.site_url or "",
            use_directory_urls=config.use_directory_urls,
            theme=theme_.Theme.get_theme(config.theme.name, data=config.theme._vars),
            repo=folderinfo.FolderInfo.clone_from(path),
        )

    @property
    def info(self):
        return self.folderinfo.info

    def set_root(self, nav: mknav.MkNav):
        self._root = nav
        nav.associated_project = self

    def get_root(self, **kwargs) -> mknav.MkNav:
        self._root = mknav.MkNav(project=self, **kwargs)
        return self._root

    def get_requirements(self) -> requirements.Requirements:
        """Return requirements for this project based on theme and used nodes."""
        logger.debug("Collecting theme requirements...")
        reqs = self.theme.get_requirements()
        if self._root:
            tree_reqs = self._root.get_requirements()
            logger.debug("Merging tree and theme requirements...")
            reqs.merge(tree_reqs)
        logger.debug("Adapting collected extensions to theme...")
        self.theme.adapt_extensions(reqs.markdown_extensions)
        logger.debug("Setting default markdown extensions...")
        reqs.markdown_extensions["pymdownx.magiclink"] = dict(
            repo_url_shorthand=True,
            user=self.folderinfo.repository_username,
            repo=self.folderinfo.repository_name,
        )
        return reqs

    def all_files(self) -> dict[str, str | bytes]:
        files = self._root.all_virtual_files() if self._root else {}
        return files | self.theme.get_files()

    @functools.cached_property
    def context(self):
        return contexts.ProjectContext(
            metadata=self.folderinfo.context,
            git=self.folderinfo.git.context,
            # github=self.folderinfo.github.context,
            theme=self.theme.context,
            links=self.linkprovider,
            # requirements=self.get_requirements(),
        )

    def populate_linkprovider(self):
        if cfg := self.folderinfo.mkdocs_config:
            invs = cfg.get_section(
                "plugins",
                "mkdocstrings",
                "handlers",
                "python",
                "import",
            )
        else:
            invs = []
        mk_urls = [i["url"] for i in invs]
        urls = {
            v.inventory_url
            for v in packageinfo.registry.values()
            if v.inventory_url is not None and v.inventory_url not in mk_urls
        }
        for inv in invs:
            if "url" not in inv:
                continue
            logger.debug("Downloading %r...", inv["url"])
            try:
                self.linkprovider.add_inv_file(
                    inv["url"],
                    base_url=inv.get("base_url"),
                )
            except urllib.error.HTTPError:
                logger.debug("No file for %r...", inv["url"])
        for url in urls:
            logger.debug("Downloading %r...", url)
            try:
                self.linkprovider.add_inv_file(url)
            except urllib.error.HTTPError:
                logger.debug("No file for %r...", url)


if __name__ == "__main__":
    project = Project.for_mknodes()
    from mknodes.manual import root

    log.basic()
    root.build(project)
    project.populate_linkprovider()
