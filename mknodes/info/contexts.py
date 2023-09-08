from __future__ import annotations

import dataclasses

from typing import Any

from mknodes.data import buildsystems, commitconventions, installmethods
from mknodes.utils import log
from mknodes.utils.requirements import Requirements


logger = log.get_logger(__name__)


@dataclasses.dataclass
class GitContext:
    main_branch: str = ""
    repo_name: str = ""
    last_commits: list = dataclasses.field(default_factory=list)
    repo_hoster: str = ""


@dataclasses.dataclass
class ThemeContext:
    name: str = ""
    primary_color: str = ""
    text_color: str = ""
    data: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class PackageContext:
    # PackageInfo
    pretty_name: str = ""
    distribution_name: str = ""
    summary: str = ""
    author_name: str = ""
    author_email: str = ""
    authors: dict[str, str] = dataclasses.field(default_factory=dict)
    classifiers: list = dataclasses.field(default_factory=list)
    classifier_map: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    keywords: list[str] = dataclasses.field(default_factory=list)
    license_name: str | None = ""
    required_python_version: str | None = ""
    required_package_names: list[str] = dataclasses.field(default_factory=list)
    extras: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    urls: dict[str, str] = dataclasses.field(default_factory=dict)
    homepage: str = ""
    repository_url: str = ""
    mkdocs_config: dict | None = None
    task_runners: list = dataclasses.field(default_factory=list)
    social_info: list[dict[str, str]] = dataclasses.field(default_factory=list)
    inventory_url: str | None = ""
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
class GitHubContext:
    """Information about the GitHub repo / user."""

    default_branch: str = ""
    repo_name: str = ""
    workflows: list[dict] = dataclasses.field(default_factory=list)
    avatar_url: str | None = None
    bio: str | None = None
    blog: str | None = None
    company: str | None = None
    contributions: int | None = None
    email: str | None = None
    followers: int = 0
    gravatar_id: str | None = None
    hireable: bool = False
    location: str | None = None
    name: str | None = None
    twitter_username: str | None = None


@dataclasses.dataclass
class ProjectContext:
    """All information about a project."""

    info: PackageContext = dataclasses.field(default_factory=PackageContext)
    git: GitContext = dataclasses.field(default_factory=GitContext)
    github: GitHubContext = dataclasses.field(default_factory=GitHubContext)
    theme: ThemeContext = dataclasses.field(default_factory=ThemeContext)
    requirements: Requirements = dataclasses.field(default_factory=Requirements)


default_package_context = PackageContext(
    pretty_name="MkNodes",
    distribution_name="mknodes",
    summary="Don't write docs. Code them.",
    author_name="Philipp Temminghoff",
    author_email="philipptemminghoff@gmail.com",
    license_name="MIT",
    required_python_version=">= 3.11",
    homepage="",
    repository_url="https://github.com/phil65/mknodes/",
    inventory_url="https://github.io/phil65/mknodes/objects.inv",
)


default_git_context = GitContext(
    main_branch="main",
    repo_name="mknodes",
    repo_hoster="GitHub",
)


default_theme_context = ThemeContext(
    name="material",
    primary_color="AAAAAA",
    text_color="#000000",
)


default_github_context = GitHubContext(
    default_branch="main",
    repo_name="mknodes",
)


default_project_context = ProjectContext(
    info=default_package_context,
    git=default_git_context,
    github=default_github_context,
    theme=default_theme_context,
    requirements=Requirements(),
)


if __name__ == "__main__":
    info = PackageContext()
    print(info)
