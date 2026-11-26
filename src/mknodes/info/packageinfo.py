import collections
import contextlib
import functools
from importlib import metadata
from typing import TYPE_CHECKING, Any

import clinspector
import epregistry
from requests import structures

from mknodes.utils import log, packagehelpers, reprhelpers


if TYPE_CHECKING:
    import os
    import pathlib


logger = log.get_logger(__name__)


def _split_project_url(value: str) -> tuple[str, str]:
    """Split a `Project-URL` metadata value (`Label, URL`); labels may contain commas."""
    label, sep, url = value.rpartition(", ")
    if not sep:
        label, _, url = value.partition(",")
    return label.strip(), url.strip()


def _format_person(person: dict[str, str]) -> str:
    name, email = person.get("name", ""), person.get("email", "")
    return f"{name} <{email}>" if name and email else email or name


class PyProjectDistribution(metadata.Distribution):
    """A distribution built from `pyproject.toml` (for projects which are not installed).

    Provides the core metadata (`METADATA`) and the entry points of the `[project]` table,
    so `PackageInfo` works the same as for an installed distribution.
    """

    def __init__(self, data: dict[str, Any], root: pathlib.Path) -> None:
        self._project: dict[str, Any] = data.get("project") or {}
        self._root = root

    def locate_file(self, path: str | os.PathLike[str]) -> pathlib.Path:
        return self._root / path

    def read_text(self, filename: str) -> str | None:
        if filename == "METADATA":
            return self._metadata_text()
        if filename == "entry_points.txt":
            return self._entry_points_text()
        return None

    def _metadata_text(self) -> str:
        p = self._project
        lines = ["Metadata-Version: 2.4", f"Name: {p.get('name', '')}"]
        lines.append(f"Version: {p.get('version') or '0.0.0'}")
        if summary := p.get("description"):
            lines.append(f"Summary: {summary}")
        if keywords := p.get("keywords"):
            lines.append(f"Keywords: {','.join(keywords)}")
        if authors := [_format_person(a) for a in p.get("authors") or []]:
            lines.append(f"Author-email: {', '.join(a for a in authors if a)}")
        if isinstance(lic := p.get("license"), str):
            lines.append(f"License-Expression: {lic}")
        lines += [f"Classifier: {c}" for c in p.get("classifiers") or []]
        if requires_python := p.get("requires-python"):
            lines.append(f"Requires-Python: {requires_python}")
        lines += [f"Project-URL: {k}, {v}" for k, v in (p.get("urls") or {}).items()]
        lines += [f"Requires-Dist: {dep}" for dep in p.get("dependencies") or []]
        for extra, deps in (p.get("optional-dependencies") or {}).items():
            lines.append(f"Provides-Extra: {extra}")
            lines += [f'Requires-Dist: {dep}; extra == "{extra}"' for dep in deps]
        text = "\n".join(lines) + "\n"
        if description := self._readme_text():
            text += f"\n{description}"
        return text

    def _readme_text(self) -> str:
        readme = self._project.get("readme")
        if isinstance(readme, dict):
            if text := readme.get("text"):
                return str(text)
            readme = readme.get("file")
        if isinstance(readme, str) and (path := self._root / readme).is_file():
            return path.read_text(encoding="utf-8")
        return ""

    def _entry_points_text(self) -> str:
        groups = {
            "console_scripts": self._project.get("scripts") or {},
            "gui_scripts": self._project.get("gui-scripts") or {},
            **(self._project.get("entry-points") or {}),
        }
        sections = [
            f"[{group}]\n" + "".join(f"{k} = {v}\n" for k, v in eps.items())
            for group, eps in groups.items()
            if eps
        ]
        return "\n".join(sections)


class PackageInfo:
    """Class containing metadata.distribution-related information."""

    def __init__(
        self,
        pkg_name: str,
        distribution: metadata.Distribution | None = None,
    ) -> None:
        """Constructor.

        Args:
            pkg_name: Name of the distribution
            distribution: The distribution (default: the installed one named `pkg_name`)
        """
        self.package_name = pkg_name
        self.distribution = distribution or metadata.distribution(pkg_name)
        logger.debug("Loaded package info: '%s'", pkg_name)
        self.metadata: dict[str, Any] = self.distribution.metadata.json
        self.classifiers: list[str] = self.metadata.get("classifier") or []  # type: ignore[assignment]
        self.version: str = self.metadata.get("version") or ""  # type: ignore[assignment]
        self.name: str = self.metadata.get("name") or ""  # type: ignore[assignment]
        self.description: str = self.metadata.get("description") or ""  # type: ignore[assignment]
        self.summary: str = self.metadata.get("summary") or ""  # type: ignore[assignment]

    def __repr__(self) -> str:
        return reprhelpers.get_repr(self, pkg_name=self.package_name)

    def __hash__(self):
        return hash(self.package_name)

    @functools.cached_property
    def urls(self) -> structures.CaseInsensitiveDict[str]:
        """A dictionary containing the type of URL and and URL itself.

        Example: {"Documentation": "http://github.io/...", ...}
        """
        urls = dict(_split_project_url(v) for v in self.metadata.get("project_url", []))
        if hp := self.metadata.get("home_page"):
            urls["home_page"] = hp.strip()
        return structures.CaseInsensitiveDict(urls)

    @functools.cached_property
    def inventory_url(self) -> str | None:
        """Return best guess for a link to an inventory file."""
        for v in self.urls.values():
            if "github.io" in v or "readthedocs" in v:
                return f"{v.rstrip('/')}/objects.inv"
        if url := self.urls.get("Documentation"):
            return f"{url.rstrip('/')}/objects.inv"
        return None

    @functools.cached_property
    def _required_deps(self) -> list[packagehelpers.Dependency]:
        requires = self.distribution.requires
        return [packagehelpers.get_dependency(i) for i in requires] if requires else []

    @functools.cached_property
    def license_name(self) -> str | None:
        """Get name of the license."""
        if license_name := self.metadata.get("license_expression"):
            return license_name if isinstance(license_name, str) else license_name[0]
        if license_names := self.classifier_map.get("License"):
            return license_names[0].split(" :: ")[-1]
        return None

    @functools.cached_property
    def repository_url(self) -> str | None:
        """Return repository URL from metadata."""
        tags = ["Source", "Repository", "Source Code"]
        return next((self.urls[tag] for tag in tags if tag in self.urls), None)

    @functools.cached_property
    def homepage(self) -> str | None:
        """The URL of the homepage associated to this package."""
        keys = ["Home-page", "Homepage", "home_page", "Documentation"]
        return next((self.urls[k] for k in keys if k in self.urls), self.repository_url)

    @functools.cached_property
    def keywords(self) -> list[str]:
        """Return a list of keywords from metadata."""
        kw = self.metadata.get("keywords", [])
        if kw and "," in kw[0]:
            return kw[0].split(",")
        if kw:
            return kw
        return []

    @functools.cached_property
    def classifier_map(self) -> collections.defaultdict[str, list[str]]:
        """Return a dict containing the classifier categories and values from metadata.

        {category_1: [classifier_1, ...],
         category_2, [classifier_x, ...],
         ...
         }
        """
        classies: collections.defaultdict[str, list[str]] = collections.defaultdict(list)
        for v in self.metadata.get("classifier", []):
            category, value = v.split(" :: ", 1)
            classies[category].append(value.strip())
        return classies

    @functools.cached_property
    def required_package_names(self) -> list[str]:
        """Get a list of names from required packages."""
        return [i.name for i in self._required_deps]

    @functools.cached_property
    def author_email(self) -> str:
        """The first found package author email address."""
        if mail := self.metadata.get("author_email"):
            mail = mail.split(",")[0].split(" ")[-1]
            return mail.replace("<", "").replace(">", "")
        return ""

    @functools.cached_property
    def author_name(self) -> str:
        """The first found package author name."""
        if mail := self.metadata.get("author_email"):
            return mail.split(",")[0].rsplit(" ", 1)[0]
        return ""

    @functools.cached_property
    def authors(self) -> dict[str, str]:
        """Return a dict containing the authors.

        {author 1: email of author 1,
         author_2, email of author 2,
         ...
         }
        """
        authors: dict[str, str] = {}
        for v in self.metadata.get("author_email", "").split(","):
            mail = v.split(" ")[-1]
            mail = mail.replace("<", "").replace(">", "")
            name = v.rsplit(" ", 1)[0]
            authors[name] = mail
        return authors

    @functools.cached_property
    def extras(self) -> collections.defaultdict[str, list[str]]:
        """Return a dict containing extras and the packages {extra: [package_1, ...]}."""
        extras: collections.defaultdict[str, list[str]] = collections.defaultdict(list)
        for dep in self._required_deps:
            for extra in dep.extras:
                extras[extra].append(dep.name)
        return extras

    @functools.cached_property
    def required_python_version(self) -> str | None:
        """The minimum required python version for this package."""
        return self.metadata.get("requires_python")

    @functools.cached_property
    def required_packages(self) -> dict[PackageInfo, packagehelpers.Dependency]:
        from mknodes.info import packageregistry

        requires = self.distribution.requires or []
        # Declared order (not a set: the table order must not depend on hash seeds).
        modules = list(dict.fromkeys(packagehelpers.get_dependency(i).name for i in requires))
        packages = {}
        for mod in modules:
            with contextlib.suppress(Exception):
                info = packageregistry.get_info(mod)
                packages[info] = self._get_dep_info(mod)
        return packages

    def _get_dep_info(self, name: str) -> packagehelpers.Dependency:
        for i in self._required_deps:
            if i.name == name:
                return i
        raise ValueError(name)

    @functools.cached_property
    def cli(self) -> str | None:
        """Get the name of the CLI package being used.

        Detection is done by comparing a list of known CLI apps with required packages.
        """
        for lib in ["typer", "click", "cappa"]:
            if lib in self.required_package_names:
                return lib
        return None

    @functools.cached_property
    def cli_info(self) -> clinspector.CommandInfo | None:
        """Return a CLI info object containing infos about all CLI commands / options."""
        if eps := self.entry_points.get_group("console_scripts"):
            ep = eps[0].load()
            qual_name = ep.__class__.__module__.lower()
            if qual_name.startswith(("typer", "click")):
                return clinspector.get_cmd_info(ep)
        return None

    @functools.cached_property
    def entry_points(self) -> epregistry.ModuleEntryPointRegistry[Any]:
        """Get entry points for this package."""
        name = epregistry.distribution_to_package(self.package_name, fallback=True)
        return epregistry.ModuleEntryPointRegistry(name)


if __name__ == "__main__":
    info = PackageInfo("jinja2")
    print(list(info.metadata.keys()))
