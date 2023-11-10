from __future__ import annotations

import contextlib
import dataclasses
import functools
import importlib
import os
import pathlib
import re
import types

from typing import TYPE_CHECKING

from mknodes.data import commitconventions, installmethods, taskrunners, tools
from mknodes.info import (
    contexts,
    # githubinfo,
    grifferegistry,
    license,
    mkdocsconfigfile,
    packageregistry,
    pyproject,
    reporegistry,
)
from mknodes.utils import (
    icons,
    log,
    packagehelpers,
    pathhelpers,
    reprhelpers,
    yamlhelpers,
)


if TYPE_CHECKING:
    import griffe

    from griffe.dataclasses import Alias

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

    def __init__(self, path: str | os.PathLike | None = None):
        """Constructor.

        Arguments:
            path: Path to the repo.
        """
        # packagehelpers.install_or_import(mod_name)
        self.git = reporegistry.get_repo(path or ".")
        self.path = pathlib.Path(self.git.working_dir)
        self.pyproject = pyproject.PyProject(self.path)
        self.mkdocs_config = mkdocsconfigfile.MkDocsConfigFile()
        if (mk_path := self.path / "mkdocs.yml").exists():
            with contextlib.suppress(yamlhelpers.YAMLError):
                self.mkdocs_config = mkdocsconfigfile.MkDocsConfigFile(mk_path)
        # self.github = githubinfo.GitHubRepo(
        #     self.repository_username,
        #     self.repository_name,
        # )
        self._temp_directory = None

    def __fspath__(self):
        return str(self.path)

    @functools.cached_property
    def module(self) -> types.ModuleType:
        """Return the module itself."""
        mod_name = packagehelpers.distribution_to_package(self.git.repo_name)
        return importlib.import_module(mod_name)

    @functools.cached_property
    def griffe_module(self) -> griffe.Module | Alias:
        """Return a griffe Module containing information about the module."""
        # Long-term ideally we would pull all information from here.
        mod_name = packagehelpers.distribution_to_package(self.git.repo_name)
        return grifferegistry.get_module(mod_name)

    def __repr__(self):
        return reprhelpers.get_repr(self, path=self.path)

    @functools.cached_property
    def info(self) -> packageinfo.PackageInfo:
        """Return a PackageInfo object for given distribution."""
        return packageregistry.get_info(self.pyproject.name or self.git.repo_name)

    @functools.cached_property
    def extras(self) -> dict[str, PackageExtra]:
        """Return a dict containing extras and the packages {extra: [package_1, ...]}."""
        dct = {}
        for k, v in self.info.extras.items():
            desc = self.pyproject.extras_descriptions.get(k, "")
            dct[k] = PackageExtra(k, packages=v, description=desc)
        return dct

    @functools.cached_property
    def repository_url(self) -> str:
        """Return url of the repository by querying multiple sources.

        Checks MkDocs config file, Git repository info and project metadata.
        """
        if url := self.mkdocs_config.get("repo_url"):
            return url
        if url := self.git.repo_url:
            return url
        if url := self.info.repository_url:
            return url
        msg = "Could not find any repository url"
        raise RuntimeError(msg)

    @functools.cached_property
    def repository_username(self) -> str:
        """Return the username for the remote repository."""
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(1)
        msg = "Could not detect repository username"
        raise RuntimeError(msg)

    @functools.cached_property
    def repository_name(self) -> str:
        """Return the name of the remote repository."""
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(2)
        msg = "Could not detect repository name"
        raise RuntimeError(msg)

    @functools.cached_property
    def inventory_url(self) -> str | None:
        """Return best guess for a link to an inventory file."""
        if url := self.mkdocs_config.get("site_url"):
            return f"{url.rstrip('/')}/objects.inv"
        return None

    @functools.cached_property
    def package_name(self) -> str:
        """Return name of the package."""
        return self.info.package_name

    @functools.cached_property
    def package_repos(self) -> list[installmethods.InstallMethodStr]:
        """Return a list of package repositories the package is available on."""
        repos = self.pyproject.package_repos or ["pip"]
        has_script = "console_scripts" in self.info.entry_points
        if "pip" in repos and "pipx" not in repos and has_script:
            repos.append("pipx")
        return repos

    @functools.cached_property
    def commit_types(self) -> list[commitconventions.CommitTypeStr]:
        """Return commit types allowed for code commits."""
        return self.pyproject.allowed_commit_types

    @functools.cached_property
    def tools(self) -> list[tools.Tool]:
        """Return a list of build tools used by this package."""
        return [instance for t in tools.TOOLS.values() if (instance := t(self)).used]

    @functools.cached_property
    def docstring_style(self) -> str | None:
        """Return docstring style (google / numpy)."""
        if style := self.pyproject.docstring_style:
            return style
        if section := self.mkdocs_config.mkdocstrings_config:
            return section.get("options", {}).get("docstring_style")
        return None

    @functools.cached_property
    def license_file_path(self) -> pathlib.Path | None:
        """Return license file path (relative to project root) from metadata."""
        for path in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
            if (file := self.path / path).exists():
                return file
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
            lic = license.License.from_name(license_name)
            lic.resolve_by_distribution(self.info.name)
            return lic.content
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
                link=f"https://pypi.org/project/{self.module.__name__}/",
            ),
        )
        return result

    @functools.cached_property
    def task_runners(self) -> list[taskrunners.TaskRunner]:
        """Return list of task runners used by this package."""
        return [
            runner
            for runner in taskrunners.TASK_RUNNERS.values()
            if any(
                pathhelpers.find_cfg_for_folder(i, self.path) for i in runner.filenames
            )
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
            package_repos=self.pyproject.package_repos,
            line_length=self.pyproject.line_length,
        )


if __name__ == "__main__":
    info = FolderInfo("https://github.com/mkdocs/mkdocs.git")
    print(info.context)
    log.basic()
