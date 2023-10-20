from __future__ import annotations

from collections.abc import Callable
import pathlib
import types

import jinja2

from mknodes.utils import pathhelpers, reprhelpers


class LoaderMixin:
    loader: jinja2.BaseLoader

    def __or__(self, other: jinja2.BaseLoader):
        own_loaders = self.loaders if isinstance(self, jinja2.ChoiceLoader) else [self]  # type: ignore[list-item]
        if isinstance(other, jinja2.ChoiceLoader):
            other_loaders = other.loaders
        else:
            other_loaders = [other]
        return ChoiceLoader([*own_loaders, *other_loaders])


class PackageLoader(LoaderMixin, jinja2.PackageLoader):
    def __init__(
        self,
        package: str | types.ModuleType,
        package_path: str | None = None,
        encoding: str = "utf-8",
    ) -> None:
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
    def __repr__(self):
        return reprhelpers.get_repr(self, searchpath=self.searchpath)

    def __add__(self, other):
        if isinstance(other, jinja2.FileSystemLoader):
            paths = other.searchpath
        else:
            paths = [other]
        return FileSystemLoader([*self.searchpath, *paths])


class ChoiceLoader(LoaderMixin, jinja2.ChoiceLoader):
    def __repr__(self):
        return reprhelpers.get_repr(self, loaders=self.loaders, _shorten=False)


class DictLoader(LoaderMixin, jinja2.DictLoader):
    def __repr__(self):
        return reprhelpers.get_repr(self, mapping=self.mapping)

    def __add__(self, other):
        if isinstance(other, jinja2.DictLoader):
            mapping = self.mapping | other.mapping
        elif isinstance(other, dict):
            mapping = self.mapping | other
        return DictLoader(mapping)


class FsSpecProtocolPathLoader(LoaderMixin, jinja2.BaseLoader):
    def get_source(
        self,
        environment: jinja2.Environment,
        template: str,
    ) -> tuple[str, str, Callable[[], bool] | None]:
        src = pathhelpers.fsspec_get(template)
        path = pathlib.Path(template).as_posix()
        return src, path, lambda: True


class FsSpecFileSystemLoader(LoaderMixin, jinja2.BaseLoader):
    def __init__(self, fs, **kwargs):
        super().__init__()
        import fsspec

        self.fs = fsspec.filesystem(fs, **kwargs) if isinstance(fs, str) else fs

    def get_source(
        self,
        environment: jinja2.Environment,
        template: str,
    ) -> tuple[str, str, Callable[[], bool] | None]:
        with self.fs.open(template) as file:
            src = file.read().decode()

        path = pathlib.Path(template).as_posix()
        return src, path, lambda: True


def get_loader(
    module_paths: list[str] | None = None,
    file_paths: list[str] | None = None,
    static: dict[str, str] | None = None,
    fsspec_paths: bool = True,
) -> ChoiceLoader:
    loaders: list[jinja2.BaseLoader] = [PackageLoader(p) for p in module_paths or []]
    if file_paths:
        loaders.append(FileSystemLoader(file_paths))
    if static:
        loaders.append(DictLoader(static))
    if fsspec_paths:
        loaders.append(FsSpecProtocolPathLoader())
    return ChoiceLoader(loaders)


resources_loader = PackageLoader("mknodes", "resources")
docs_loader = FileSystemLoader(searchpath="docs/")
fsspec_protocol_loader = FsSpecProtocolPathLoader()
resource_loader = ChoiceLoader([resources_loader, docs_loader, fsspec_protocol_loader])
# material_partials_loader = PackageLoader("material", "partials")


if __name__ == "__main__":
    env = jinja2.Environment()

    import fsspec

    fs = fsspec.filesystem("github", org="phil65", repo="mknodes")
    loader = FsSpecFileSystemLoader(fs)
    result = loader.get_source(env, "README.md")
    print(result)

    loader = FsSpecProtocolPathLoader()
    result = loader.get_source(env, "github://phil65:mknodes@main/README.md")
    print(result)
