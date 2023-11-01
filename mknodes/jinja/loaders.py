from __future__ import annotations

from collections.abc import Callable
import os
import pathlib
import types

from typing import Any, Self

import fsspec
import fsspec.core
import jinja2

from mknodes.utils import helpers, inspecthelpers, pathhelpers, reprhelpers


class LoaderMixin:
    """Loader mixin which allows to OR loaders into a choice loader."""

    ID: str
    loader: jinja2.BaseLoader
    list_templates: Callable

    def __or__(self, other: jinja2.BaseLoader):
        own_loaders = self.loaders if isinstance(self, jinja2.ChoiceLoader) else [self]  # type: ignore[list-item]
        if isinstance(other, jinja2.ChoiceLoader):
            other_loaders = other.loaders
        else:
            other_loaders = [other]
        return ChoiceLoader([*own_loaders, *other_loaders])

    def __contains__(self, path):
        return pathlib.Path(path).as_posix() in self.list_templates()

    def prefixed_with(self, prefix: str):
        """Return loader wrapped in a PrefixLoader instance with given prefix.

        Arguments:
            prefix: The prefix to use
        """
        return PrefixLoader({prefix: self})  # type: ignore[dict-item]


class PrefixLoader(LoaderMixin, jinja2.PrefixLoader):
    """A loader for prefixing other loaders."""

    ID = "prefix"


class PackageLoader(LoaderMixin, jinja2.PackageLoader):
    """A loader for loading templates from a package."""

    ID = "package"

    def __init__(
        self,
        package: str | types.ModuleType,
        package_path: str | None = None,
        encoding: str = "utf-8",
    ) -> None:
        """Instanciate a PackageLoader.

        `package` can either be a `ModuleType` or a (dotted) module path.

        Arguments:
            package: The python package to create a loader for
            package_path: If given, use the given path as the root.
            encoding: The encoding to use for loading templates
        """
        if isinstance(package, types.ModuleType):
            package = package.__name__
        parts = package.split(".")
        path = "/".join(parts[1:])
        if package_path:
            path = (pathlib.Path(path) / package_path).as_posix()
        super().__init__(parts[0], path, encoding)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            package_name=self.package_name,
            package_path=self.package_path,
        )


class FileSystemLoader(LoaderMixin, jinja2.FileSystemLoader):
    """A loader to load templates from the file system."""

    ID = "filesystem"

    def __repr__(self):
        return reprhelpers.get_repr(self, searchpath=self.searchpath)

    def __add__(self, other):
        if isinstance(other, jinja2.FileSystemLoader):
            paths = other.searchpath
        else:
            paths = [other]
        return FileSystemLoader([*self.searchpath, *paths])

    @classmethod
    def for_class(cls, klass: type) -> Self:
        """Return a FileSystem loader for given class.

         The path will be set to the folder the class's file is contained in.

        Arguments:
            klass: The class to get a loader for.
        """
        path = inspecthelpers.get_file(klass)
        assert path
        return cls(path.parent.as_posix())


class ChoiceLoader(LoaderMixin, jinja2.ChoiceLoader):
    """A loader which combines multiple other loaders."""

    ID = "choice"

    def __repr__(self):
        return reprhelpers.get_repr(self, loaders=self.loaders, _shorten=False)


class DictLoader(LoaderMixin, jinja2.DictLoader):
    """A loader to load static content from a path->template-str mapping."""

    ID = "dict"

    def __repr__(self):
        return reprhelpers.get_repr(self, mapping=self.mapping)

    def __add__(self, other):
        if isinstance(other, jinja2.DictLoader):
            mapping = self.mapping | other.mapping
        elif isinstance(other, dict):
            mapping = self.mapping | other
        return DictLoader(mapping)


class FsSpecProtocolPathLoader(LoaderMixin, jinja2.BaseLoader):
    """A jinja loader for fsspec filesystems.

    This loader allows to access templates from an fsspec protocol path,
    like "github://phil65:mknodes@main/README.md"

    Examples:
        ``` py
        loader = FsSpecProtocolPathLoader()
        env = Environment(loader=loader)
        env.get_template("github://phil65:mknodes@main/docs/icons.jinja").render()
        ```
    """

    ID = "fsspec_protocol_path"

    def get_source(
        self,
        environment: jinja2.Environment | None,
        template: str,
    ) -> tuple[str, str, Callable[[], bool] | None]:
        url, *section = template.split("#")
        src = pathhelpers.fsspec_get(url)
        if section:
            src = helpers.extract_header_section(src, section[0]) or src
        path = pathlib.Path(template).as_posix()
        return src, path, lambda: True

    def list_templates(self) -> list[str]:
        return []

    def __contains__(self, path: str):
        try:
            self.get_source(None, path)
        except FileNotFoundError:
            return False
        else:
            return True

    def __repr__(self):
        return reprhelpers.get_repr(self)


class FsSpecFileSystemLoader(LoaderMixin, jinja2.BaseLoader):
    """A jinja loader for fsspec filesystems.

    This loader allows to access templates from an fsspec filesystem.

    Template paths must be relative to the filesystem root.
    In order to access templates via protocol path, see `FsSpecProtocolPathLoader`.

    Examples:
        ``` py
        # protocol path
        loader = FsSpecFileSystemLoader("dir::github://phil65:mknodes@main/docs")
        env = Environment(loader=loader)
        env.get_template("icons.jinja").render()

        # protocol and storage options
        loader = FsSpecFileSystemLoader("github", org="phil65", repo="mknodes")
        env = Environment(loader=loader)
        env.get_template("docs/icons.jinja").render()

        # fsspec filesystem
        fs = fsspec.filesystem("github", org="phil65", repo="mknodes")
        loader = FsSpecFileSystemLoader(fs)
        env = Environment(loader=loader)
        env.get_template("docs/icons.jinja").render()
        ```

    """

    ID = "fsspec"

    def __init__(self, fs: fsspec.AbstractFileSystem | str, **kwargs: Any):
        """Constructor.

        Arguments:
            fs: Either a protocol path string or an fsspec filesystem instance.
                Also supports "::dir" prefix to set the root path.
            kwargs: Optional storage options for the filesystem.
        """
        super().__init__()
        if isinstance(fs, str):
            if "://" in fs:
                self.fs, self.path = fsspec.core.url_to_fs(fs, **kwargs)
            else:
                self.fs = fsspec.filesystem(fs, **kwargs)
        else:
            self.fs = fsspec.filesystem(fs, **kwargs) if isinstance(fs, str) else fs
            self.path = ""
        self.storage_options = kwargs

    def __repr__(self):
        return reprhelpers.get_repr(self, fs=self.fs.protocol, **self.storage_options)

    def list_templates(self) -> list[str]:
        return self.fs.ls(self.fs.root_marker)

    def get_source(
        self,
        environment: jinja2.Environment,
        template: str,
    ) -> tuple[str, str, Callable[[], bool] | None]:
        with self.fs.open(template) as file:
            src = file.read().decode()

        path = pathlib.Path(template).as_posix()
        return src, path, lambda: True


class LoaderRegistry:
    """Registry which caches and builds jinja loaders."""

    def __init__(self) -> None:
        self.fs_loaders: dict[str, FileSystemLoader] = {}
        self.fsspec_loaders: dict[str, FsSpecFileSystemLoader] = {}
        self.package_loaders: dict[str, PackageLoader] = {}

    def by_path(
        self,
        path: str | os.PathLike,
    ) -> FileSystemLoader | FsSpecFileSystemLoader:
        """Convenience method to get a suiting loader for given path.

        Return a FsSpec loader for protocol-like paths or else a FileSystem loader.

        Arguments:
            path: The path to get a loader for
        """
        if "://" in str(path):
            return self.get_fsspec_loader(str(path))
        return self.get_filesystem_loader(path)

    def get_fsspec_loader(self, path: str) -> FsSpecFileSystemLoader:
        """Return a FsSpec loader for given path from registry.

        If the loader does not exist yet, create and cache it.

        Arguments:
            path: The path to get a loader for
        """
        if path in self.fsspec_loaders:
            return self.fsspec_loaders[path]
        loader = FsSpecFileSystemLoader(path)
        self.fsspec_loaders[path] = loader
        return loader

    def get_filesystem_loader(self, path: str | os.PathLike) -> FileSystemLoader:
        """Return a FileSystem loader for given path from registry.

        If the loader does not exist yet, create and cache it.

        Arguments:
            path: The path to get a loader for
        """
        path = pathlib.Path(path).as_posix()
        if path in self.fs_loaders:
            return self.fs_loaders[path]
        loader = FileSystemLoader(path)
        self.fs_loaders[path] = loader
        return loader

    def get_package_loader(self, package: str) -> PackageLoader:
        """Return a Package loader for given (dotted) package path from registry.

        If the loader does not exist yet, create and cache it.

        Arguments:
            package: The package to get a loader for
        """
        if package in self.package_loaders:
            return self.package_loaders[package]
        loader = PackageLoader(package)
        self.package_loaders[package] = loader
        return loader

    def get_loader(
        self,
        dir_paths: list[str] | None = None,
        module_paths: list[str] | None = None,
        static: dict[str, str] | None = None,
        fsspec_paths: bool = True,
    ) -> ChoiceLoader:
        """Construct a ChoiceLoader based on given keyword arguments and return it.

        Loader is constructed from cached sub-loaders if existing, otherwise they are
        created (and cached).

        Arguments:
            dir_paths: Directory paths (either FsSpec-protocol URLs to a folder or
                       filesystem paths)
            module_paths: (dotted) package paths
            static: A dictionary containing a path-> template mapping
            fsspec_paths: Whether a loader for FsSpec protcol paths should be added
        """
        m_paths = helpers.reduce_list(module_paths or [])
        loaders: list[jinja2.BaseLoader] = [self.get_package_loader(p) for p in m_paths]
        for file in helpers.reduce_list(dir_paths or []):
            if "://" in file:
                loaders.append(self.get_fsspec_loader(file))
            else:
                loaders.append(self.get_filesystem_loader(file))
        if static:
            loaders.append(DictLoader(static))
        if fsspec_paths:
            loaders.append(FsSpecProtocolPathLoader())
        return ChoiceLoader(loaders)


registry = LoaderRegistry()

docs_loader = registry.get_filesystem_loader("docs/")
fsspec_protocol_loader = FsSpecProtocolPathLoader()
resource_loader = ChoiceLoader([docs_loader, fsspec_protocol_loader])


def from_json(dct_or_list) -> jinja2.BaseLoader | None:
    if not dct_or_list:
        return None
    loaders = []
    ls = dct_or_list if isinstance(dct_or_list, list) else [dct_or_list]
    for item in ls:
        if isinstance(item, jinja2.BaseLoader):
            loaders.append(item)
            continue
        if isinstance(item, str):
            if "://" in item:
                loaders.append(FsSpecFileSystemLoader(item))
            else:
                loaders.append(FileSystemLoader(item))
            continue
        for kls in jinja2.BaseLoader.__subclasses__():
            if not issubclass(kls, LoaderMixin):
                continue
            dct_copy = item.copy()
            if dct_copy.pop("type") == kls.ID:  # type: ignore[attr-defined]
                path = dct_copy.pop("path")
                instance = kls(path, **dct_copy)  # type: ignore[call-arg]
                loaders.append(instance)
    if len(loaders) == 1:
        return loaders[0]
    if len(loaders) > 1:
        return ChoiceLoader(loaders)
    return None


LOADERS = dict(
    fsspec=FsSpecFileSystemLoader,
    filesystem=FileSystemLoader,
    package=PackageLoader,
    dictionary=DictLoader,
)


if __name__ == "__main__":
    from mknodes.jinja import environment

    loader = FsSpecFileSystemLoader("dir::github://phil65:mknodes@main/docs")
    env = environment.Environment()
    env.loader = loader
    template = env.get_template("icons.jinja")
    print(template.render())
    loader = FsSpecProtocolPathLoader()
    result = loader.get_source(env, "github://phil65:mknodes@main/README.md")
    print(repr(loader))
