from __future__ import annotations

import dataclasses
import logging

from typing import Any

from mknodes.data import buildsystems, commitconventions, installmethods
from mknodes.utils.requirements import Requirements


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class GitContext:
    main_branch: str = "main"
    repo_name: str = "mknodes"
    last_commits: list = dataclasses.field(default_factory=list)
    repo_hoster: str = "GitHub"


@dataclasses.dataclass
class ThemeContext:
    name: str = "material"
    primary_color: str = "#AAAAAA"
    text_color: str = "#000000"
    data: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class PackageContext:
    # PackageInfo
    pretty_name: str = "MkNodes"
    distribution_name: str = "mknodes"
    summary: str = "Don't write docs. Code them."
    author_name: str = "Philipp Temminghoff"
    author_email: str = "philipptemminghoff@gmail.com"
    authors: dict[str, str] = dataclasses.field(default_factory=dict)
    classifiers: list = dataclasses.field(default_factory=list)
    classifier_map: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    keywords: list[str] = dataclasses.field(default_factory=list)
    license_name: str | None = "MIT"
    required_python_version: str | None = ">= 3.11"
    required_package_names: list[str] = dataclasses.field(default_factory=list)
    extras: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    urls: dict[str, str] = dataclasses.field(default_factory=dict)
    homepage: str = ""
    repository_url: str = "https://github.com/phil65/mknodes/"
    mkdocs_config: dict | None = None
    task_runners: list = dataclasses.field(default_factory=list)
    social_info: list[dict[str, str]] = dataclasses.field(default_factory=list)
    inventory_url: str | None = "https://github.io/phil65/mknodes/objects.inv"
    # required_packages: dict[PackageInfo, packagehelpers.Dependency] =
    entry_points: dict = dataclasses.field(default_factory=dict)
    # pyproject
    build_system: buildsystems.BuildSystem = dataclasses.field(
        default_factory=lambda: buildsystems.hatch,
    )
    configured_build_systems: list = dataclasses.field(default_factory=list)
    tools: dict[str, Any] = dataclasses.field(default_factory=dict)
    commit_types: list[commitconventions.CommitTypeStr] = dataclasses.field(
        default_factory=list,
    )
    extras_descriptions: dict[str, str] = dataclasses.field(default_factory=dict)
    package_repos: list[installmethods.InstallMethodStr] = dataclasses.field(
        default_factory=list,
    )


@dataclasses.dataclass
class ProjectContext:
    """All information about a project."""

    info: PackageContext = dataclasses.field(default_factory=PackageContext)
    git: GitContext = dataclasses.field(default_factory=GitContext)
    theme: ThemeContext = dataclasses.field(default_factory=ThemeContext)
    requirements: Requirements = dataclasses.field(default_factory=Requirements)


if __name__ == "__main__":
    info = PackageContext()
    print(info)
