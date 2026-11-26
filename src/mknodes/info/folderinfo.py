import contextlib
import dataclasses
import functools
import importlib
from importlib import metadata
import pathlib
import re
from typing import TYPE_CHECKING

import yamling

from mknodes import inputs
from mknodes.data import installmethods, taskrunners, tools
from mknodes.info import (
    contexts,
    grifferegistry,
    mkdocsconfigfile,
    packageregistry,
    projectlayout,
    pyproject,
    reporegistry,
)
from mknodes.utils import icons, log, pathhelpers, reprhelpers


if TYPE_CHECKING:
    import os
    import types

    import griffe
    from griffe import Alias

    from mknodes.data import commitconventions
    from mknodes.info import packageinfo

logger = log.get_logger(__name__)


GITHUB_REGEX = re.compile(
    r"(?:http?:\/\/|https?:\/\/)?"
    r"(?:www\.)?"
    r"github\.com\/"
    r"(?:\/*)"
    r"([\w\-\.]*)\/"
    r"([\w\-]*)"
    r"(?:\/|$)?"
)


@dataclasses.dataclass(frozen=True)
class PackageExtra:
    """A class describing a package extra, used to define additional dependencies."""

    name: str
    """Name of the extra."""
    packages: list[str] = dataclasses.field(default_factory=list)
    """List of packages which are part of the extra."""
    description: str = ""
    """Optional description for the extra.

    Must be defined in pyproject mknodes section.
    """


class FolderInfo:
    """Aggregates information about a working dir."""

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        """Constructor.

        Args:
            path: Path to the repo.
        """
        # packagehelpers.install_or_import(mod_name)
        self.git = reporegistry.get_repo(path or ".")
        self.path = pathlib.Path(self.git.working_dir)
        self.pyproject = pyproject.PyProject(self.path)
        self.mkdocs_config = mkdocsconfigfile.MkDocsConfigFile()
        if (mk_path := self.path / "mkdocs.yml").exists():
            with contextlib.suppress(yamling.YAMLError):
                self.mkdocs_config = mkdocsconfigfile.MkDocsConfigFile(mk_path)
        self._temp_directory = None

    def __fspath__(self):
        return str(self.path)

    @functools.cached_property
    def layout(self) -> projectlayout.ProjectLayout:
        """Distribution name, import packages and source layout of the project."""
        return projectlayout.ProjectLayout.resolve(
            self.path, self.pyproject.data, fallback_name=self.git.repo_name
        )

    @functools.cached_property
    def distribution_name(self) -> str:
        """Name of the distribution (`[project.name]`, else the repository name)."""
        return self.layout.distribution

    @functools.cached_property
    def package_names(self) -> list[str]:
        """Names of all import packages of the distribution (primary package first)."""
        return self.layout.package_names

    @functools.cached_property
    def package_name(self) -> str:
        """Name of the primary import package."""
        if primary := self.layout.primary:
            return primary.name
        return projectlayout.normalize_name(self.distribution_name)

    @functools.cached_property
    def module(self) -> types.ModuleType:
        """Return the primary import package."""
        if primary := self.layout.primary:
            return primary.import_module()
        return importlib.import_module(self.package_name)

    @functools.cached_property
    def griffe_module(self) -> griffe.Module | Alias:
        """Return a griffe Module containing information about the module."""
        # Long-term ideally we would pull all information from here.
        self.module  # noqa: B018  (makes a not installed package importable for griffe)
        return grifferegistry.get_module(self.package_name)

    def __repr__(self) -> str:
        return reprhelpers.get_repr(self, path=self.path)

    @functools.cached_property
    def info(self) -> packageinfo.PackageInfo:
        """Return a PackageInfo object for the distribution.

        Uses the installed distribution, else the metadata from `pyproject.toml`.
        """
        from mknodes.info import packageinfo

        name = self.distribution_name
        try:
            return packageregistry.get_info(name)
        except metadata.PackageNotFoundError:
            logger.info("Distribution %s is not installed, using pyproject.toml", name)
            dist = packageinfo.PyProjectDistribution(self.pyproject.data, self.path)
            return packageinfo.PackageInfo(name, distribution=dist)

    @functools.cached_property
    def extras(self) -> dict[str, PackageExtra]:
        """Return a dict containing extras and the packages {extra: [package_1, ...]}."""
        dct = {}
        for k, v in self.info.extras.items():
            dct[k] = PackageExtra(k, packages=v)
        return dct

    @functools.cached_property
    def repository_url(self) -> str:
        """Return url of the repository by querying multiple sources.

        Checks the MkDocs config (`repo_url`), `[project.urls]`, the git remote and the
        installed metadata.
        Returns an empty string if none of them contains a repository url.
        """
        if url := self.mkdocs_config.get("repo_url"):
            return url  # type: ignore[no-any-return]
        urls = self.pyproject.project.get("urls") or {}
        if url := projectlayout.repository_url_from_urls(urls):
            return url
        if url := self.git.repo_url:
            return url
        if url := self.info.repository_url:
            return url
        logger.warning("Could not find any repository url for %s", self.path)
        return ""

    @functools.cached_property
    def repository_username(self) -> str:
        """Return the username for the remote repository (empty if not detectable)."""
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(1)
        return ""

    @functools.cached_property
    def repository_name(self) -> str:
        """Return the name of the remote repository (falls back to the local repo name)."""
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(2)
        return self.git.repo_name

    @functools.cached_property
    def inventory_url(self) -> str | None:
        """Return best guess for a link to an inventory file."""
        if url := self.mkdocs_config.get("site_url"):
            return f"{url.rstrip('/')}/objects.inv"
        return None

    @functools.cached_property
    def package_repos(self) -> list[installmethods.InstallMethod]:
        """Return a list of package repositories the package is available on."""
        repos = self.pyproject.package_repos or ["pip"]
        has_script = "console_scripts" in self.info.entry_points
        if "pip" in repos and "pipx" not in repos and has_script:
            repos.append("pipx")
        klasses = [installmethods.InstallMethod.by_id(i) for i in repos]
        return [i(self.info.name) for i in klasses]

    @functools.cached_property
    def commit_types(self) -> list[commitconventions.CommitTypeStr]:
        """Return commit types allowed for code commits."""
        return self.pyproject.allowed_commit_types

    @functools.cached_property
    def tools(self) -> list[tools.Tool]:
        """Return a list of build tools used by this package."""
        return tools.get_tools_for_folder(self)

    @functools.cached_property
    def docstring_style(self) -> str | None:
        """Return docstring style (google / numpy)."""
        if style := self.pyproject.docstring_style:
            return style
        if section := self.mkdocs_config.mkdocstrings_config:
            return section.get("options", {}).get("docstring_style")  # type: ignore[no-any-return]
        return None

    @functools.cached_property
    def license_file_path(self) -> pathlib.Path | None:
        """Return license file path (relative to project root) from metadata."""
        for path in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
            if (file_path := self.path / path).exists():
                return file_path
        if file := self.info.metadata.get("license_file"):
            return self.path / file if isinstance(file, str) else self.path / file[0]
        return None

    @functools.cached_property
    def license_text(self) -> str | None:
        """Return full license text.

        Text comes either from a local license file or from a template populated with
        metadata.
        """
        if self.license_file_path:
            return self.license_file_path.read_text(encoding="utf-8")
        if license_name := self.info.license_name:
            # SPDX text: an external input (inputs store kind `license`, lock file).
            return inputs.get_input("license", name=license_name)["content"]
        return None

    @functools.cached_property
    def social_info(self) -> list[dict[str, str]]:
        result = []
        if url := self.repository_url:
            result.append(
                dict(icon="fa-brands:github", link=url),
            )
        for link in self.info.urls.values():
            if "github" in link or "pypi.org" in link:
                continue
            if icon := icons.icon_for_url(link):
                result.append(dict(icon=icon, link=link))
        result.append(
            dict(
                icon="fa-brands:python",
                link=f"https://pypi.org/project/{self.distribution_name}/",
            ),
        )
        return result

    @functools.cached_property
    def task_runners(self) -> list[taskrunners.TaskRunner]:
        """Return list of task runners used by this package."""
        return [
            runner
            for runner in taskrunners.TASK_RUNNERS.values()
            if any(pathhelpers.find_cfg_for_folder(i, self.path) for i in runner.filenames)
        ]

    @functools.cached_property
    def context(self) -> contexts.PackageContext:
        return contexts.PackageContext(
            pretty_name=self.mkdocs_config.get("site_name") or self.info.name,
            distribution_name=self.info.name,
            version=self.info.version,
            author_name=self.info.author_name,
            author_email=self.info.author_email,
            docstring_style=self.docstring_style,
            description=self.info.description,
            summary=self.info.summary,
            authors=self.info.authors,
            package_name=self.package_name,
            package_names=self.package_names,
            module=self.module,
            griffe_module=self.griffe_module,
            urls=self.info.urls,
            classifiers=self.info.classifiers,
            classifier_map=self.info.classifier_map,
            keywords=self.info.keywords,
            license_name=self.info.license_name,
            license_text=self.license_text,
            required_python_version=self.info.required_python_version,
            required_packages=self.info.required_packages,
            required_package_names=self.info.required_package_names,
            extras=self.extras,
            tools=self.tools,
            entry_points=self.info.entry_points,
            cli=self.info.cli,
            cli_info=self.info.cli_info,
            mkdocs_config=self.mkdocs_config,
            pyproject_file=self.pyproject,
            social_info=self.social_info,
            repository_path=self.path,
            repository_url=self.repository_url,
            repository_username=self.repository_username,
            repository_name=self.repository_name,
            inventory_url=self.inventory_url,
            task_runners=self.task_runners,
            build_system=self.pyproject.build_system,
            configured_build_systems=self.pyproject.configured_build_systems,
            tool_section=self.pyproject.tool,
            commit_types=self.pyproject.allowed_commit_types,
            package_repos=self.package_repos,
        )


if __name__ == "__main__":
    info = FolderInfo("https://github.com/phil65/mkdocs-mknodes")
    # info = FolderInfo()
    print(info.module)
