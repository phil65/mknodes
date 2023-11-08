from __future__ import annotations

import collections
import contextlib
import functools

from requests import structures

from mknodes.info.cli import clihelpers, commandinfo
from mknodes.utils import log, packagehelpers, reprhelpers


logger = log.get_logger(__name__)


class PackageInfo:
    """Class containing metadata.distribution-related information."""

    def __init__(self, pkg_name: str):
        """Constructor.

        Arguments:
            pkg_name: Name of the package
        """
        self.package_name = pkg_name
        self.distribution = packagehelpers.get_distribution(pkg_name)
        logger.debug("Loaded package info: '%s'", pkg_name)
        self.metadata = packagehelpers.get_metadata(self.distribution).json
        self.classifiers = self.metadata["classifier"]
        self.version = self.metadata["version"]
        self.name = self.metadata["name"]
        self.description = self.metadata["description"]
        self.summary = self.metadata["summary"]

    def __repr__(self):
        return reprhelpers.get_repr(self, pkg_name=self.package_name)

    def __hash__(self):
        return hash(self.package_name)

    @functools.cached_property
    def urls(self) -> structures.CaseInsensitiveDict[str]:
        """A dictionary containing the type of URL and and URL itself.

        Example: {"Documentation": "http://github.io/...", ...}
        """
        urls = {
            v.split(",")[0].strip(): v.split(",")[1].strip()
            for v in self.metadata.get("project_url", [])
        }
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
        requires = packagehelpers.get_requires(self.distribution)
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
        if (kw := self.metadata.get("keywords", [])) and "," in kw[0]:
            return kw[0].split(",")
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

        requires = packagehelpers.get_requires(self.distribution)
        modules = (
            {packagehelpers.get_dependency(i).name for i in requires}
            if requires
            else set()
        )
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
    def cli_info(self) -> commandinfo.CommandInfo | None:
        """Return a CLI info object containing infos about all CLI commands / options."""
        if eps := self.entry_points.get("console_scripts"):
            ep = eps[0].load()
            qual_name = ep.__class__.__module__.lower()
            if qual_name.startswith(("typer", "click")):
                return clihelpers.get_cli_info(ep)
        return None

    @functools.cached_property
    def entry_points(self) -> dict[str, list[packagehelpers.EntryPoint]]:
        """Get entry points for this package."""
        return packagehelpers.get_entry_points(self.distribution)


if __name__ == "__main__":
    info = PackageInfo("jinja2")
    print(list(info.metadata.keys()))
