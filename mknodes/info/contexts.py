from __future__ import annotations

import dataclasses
import pathlib

from typing import Any

from mknodes.data import buildsystems, commitconventions, installmethods
from mknodes.utils import log
from mknodes.utils.requirements import Requirements


logger = log.get_logger(__name__)


@dataclasses.dataclass
class Context:
    def as_dict(self):
        return {
            field.name: getattr(self, field.name) for field in dataclasses.fields(self)
        }


@dataclasses.dataclass
class GitContext(Context):
    main_branch: str = ""
    repo_name: str = ""
    last_commits: list = dataclasses.field(default_factory=list)
    repo_hoster: str = ""


@dataclasses.dataclass
class ThemeContext(Context):
    name: str = ""
    primary_color: str = ""
    text_color: str = ""
    data: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class BuildContext(Context):
    filenames: list[str] = dataclasses.field(default_factory=list)
    original_config: dict = dataclasses.field(default_factory=dict)
    config_override: dict = dataclasses.field(default_factory=dict)
    final_config: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class PackageContext(Context):
    # PackageInfo
    pretty_name: str = ""
    distribution_name: str = ""
    summary: str = ""
    description: str = ""
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
    repository_username: str = ""
    repository_name: str = ""
    repository_path: pathlib.Path = dataclasses.field(default_factory=pathlib.Path)
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
class GitHubContext(Context):
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
class ProjectContext(Context):
    """All information about a project."""

    metadata: PackageContext = dataclasses.field(default_factory=PackageContext)
    git: GitContext = dataclasses.field(default_factory=GitContext)
    github: GitHubContext = dataclasses.field(default_factory=GitHubContext)
    theme: ThemeContext = dataclasses.field(default_factory=ThemeContext)
    requirements: Requirements = dataclasses.field(default_factory=Requirements)

    def as_dict(self):
        return dict(
            metadata=self.metadata.as_dict(),
            requirements=dict(self.requirements),
            theme=self.theme.as_dict(),
            git=self.git.as_dict(),
        )


default_package_context = PackageContext(
    pretty_name="MkNodes",
    distribution_name="mknodes",
    summary="Don't write docs. Code them.",
    description="Long text with description.",
    author_name="Philipp Temminghoff",
    author_email="philipptemminghoff@gmail.com",
    license_name="MIT",
    required_python_version=">= 3.11",
    homepage="",
    repository_url="https://github.com/phil65/mknodes/",
    repository_username="phil65",
    repository_name="mknodes",
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
    metadata=default_package_context,
    git=default_git_context,
    github=default_github_context,
    theme=default_theme_context,
    requirements=Requirements(),
)


if __name__ == "__main__":
    info = PackageContext()
    print(info)
