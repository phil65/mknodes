from __future__ import annotations

import dataclasses
import pathlib
import types

from typing import Any

import mknodes

from mknodes.data import buildsystems, commitconventions, installmethods, tools
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
    module: types.ModuleType | None = None
    """The module object itself."""
    distribution_name: str = ""
    """The name of the distribution [Metadata]"""
    summary: str = ""
    """A summary for the distribution [Metadata]"""
    description: str = ""
    """A description for the distribution [Metadata]"""
    author_name: str = ""
    """The author name of the distribution [Metadata]"""
    author_email: str = ""
    """A description for the distribution [Metadata]"""
    authors: dict[str, str] = dataclasses.field(default_factory=dict)
    """All authors of the distribution [Metadata]"""
    classifiers: list = dataclasses.field(default_factory=list)
    """Distribution classifiers [Metadata]"""
    classifier_map: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    """Distribution classifiers, sorted by category [Metadata]"""
    keywords: list[str] = dataclasses.field(default_factory=list)
    """Distribution keywords [Metadata]"""
    required_python_version: str | None = ""
    """The required python version for the distribution [Metadata]"""
    required_package_names: list[str] = dataclasses.field(default_factory=list)
    extras: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    urls: dict[str, str] = dataclasses.field(default_factory=dict)
    homepage: str = ""
    license_name: str | None = ""
    """Name of the license"""
    license_text: str | None = ""
    """The complete license text"""
    pretty_name: str = ""
    """A pretty name for the distribution (like MkNodes) [MkDocs site name]"""
    repository_url: str = ""
    repository_username: str = ""
    repository_name: str = ""
    repository_path: pathlib.Path = dataclasses.field(default_factory=pathlib.Path)
    mkdocs_config: dict | None = None
    tools: list[tools.Tool] = dataclasses.field(default_factory=list)
    """A list of tools found for the distribution."""
    task_runners: list = dataclasses.field(default_factory=list)
    social_info: list[dict[str, str]] = dataclasses.field(default_factory=list)
    inventory_url: str | None = ""
    """A best guess for an inventory URL for the package."""
    entry_points: dict = dataclasses.field(default_factory=dict)
    # required_packages: dict[PackageInfo, packagehelpers.Dependency] =
    # pyproject
    build_system: buildsystems.BuildSystem = dataclasses.field(
        default_factory=lambda: buildsystems.hatch,
    )
    """The build system set as build backend [pyproject.py]"""
    configured_build_systems: list = dataclasses.field(default_factory=list)
    """A list of build systems which are configured in pyproject [pyproject.py]"""
    tool_section: dict[str, Any] = dataclasses.field(default_factory=dict)
    """The tool section of the pyproject file (as a dict) [pyproject.py]"""
    commit_types: list[commitconventions.CommitTypeStr] = dataclasses.field(
        default_factory=list,
    )
    """Commit types defined in pyproject mknodes section [pyproject.py]"""
    extras_descriptions: dict[str, str] = dataclasses.field(default_factory=dict)
    """Descriptions for the extras, defined in pyproject mknodes section [pyproject.py]"""
    package_repos: list[installmethods.InstallMethodStr] = dataclasses.field(
        default_factory=list,
    )
    """Package repositories the distribution is distributed on.
    Defined in pyproject mknodes section [pyproject.py]"""


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
            # requirements=dict(self.requirements),
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
    module=mknodes,
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
    # requirements=Requirements(),
)


if __name__ == "__main__":
    info = PackageContext()
    print(info)
