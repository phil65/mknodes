from __future__ import annotations

import pathlib
import types

import jinja2

from mknodes.utils import reprhelpers


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
        return reprhelpers.get_repr(self, loaders=self.loaders)


class DictLoader(LoaderMixin, jinja2.DictLoader):
    def __repr__(self):
        return reprhelpers.get_repr(self, mapping=self.mapping)

    def __add__(self, other):
        if isinstance(other, jinja2.DictLoader):
            mapping = self.mapping | other.mapping
        elif isinstance(other, dict):
            mapping = self.mapping | other
        return DictLoader(mapping)


def get_loader(
    module_paths: list[str] | None = None,
    file_paths: list[str] | None = None,
    static: dict[str, str] | None = None,
) -> ChoiceLoader:
    loaders: list[jinja2.BaseLoader] = [PackageLoader(p) for p in module_paths or []]
    if file_paths:
        loaders.append(FileSystemLoader(file_paths))
    if static:
        loaders.append(DictLoader(static))
    return ChoiceLoader(loaders)


resources_loader = PackageLoader("mknodes", "resources")
docs_loader = FileSystemLoader(searchpath="docs/")
resource_loader = ChoiceLoader([resources_loader, docs_loader])


if __name__ == "__main__":
    loader = get_loader(module_paths=["mknodes.theme.material"])
    print(loader.loaders)
