from __future__ import annotations

import collections
import dataclasses
import pathlib
import types

from typing import Any

from griffe.dataclasses import Module

import mknodes

from mknodes.data import buildsystems, commitconventions, installmethods, tools
from mknodes.info import linkprovider, mkdocsconfigfile, pyproject
from mknodes.utils import log, requirements, superdict


logger = log.get_logger(__name__)


@dataclasses.dataclass
class Context:
    def as_dict(self):
        return {
            field.name: getattr(self, field.name) for field in dataclasses.fields(self)
        }

    @property
    def fields(self) -> list[str]:
        return [i.name for i in dataclasses.fields(self)]


@dataclasses.dataclass
class GitContext(Context):
    main_branch: str = ""
    """Name of the main branch of the repo (`master` / `main`)."""
    repo_name: str = ""
    """Name of the git folder."""
    last_commits: list = dataclasses.field(default_factory=list)
    """List of last commits (Commit objects from `GitPython`)."""
    repo_hoster: str = ""
    """Name of the code hoster (for example `GitHub`)"""
    edit_uri: str | None = None
    """Edit uri (depends on code hoster)."""


@dataclasses.dataclass
class ThemeContext(Context):
    name: str = ""
    """Name of the theme."""
    primary_color: str = ""
    """Primary color."""
    text_color: str = ""
    """Primary text color."""
    data: dict[str, str] = dataclasses.field(default_factory=dict)
    """Additional data of the theme."""


# @dataclasses.dataclass
# class PyProjectContext(Context):
#     # pyproject
#     build_system: buildsystems.BuildSystem = dataclasses.field(
#         default_factory=lambda: buildsystems.hatch,
#     )
#     """The build system set as build backend *[pyproject]*"""
#     configured_build_systems: list = dataclasses.field(default_factory=list)
#     """A list of build systems which are configured in pyproject *[pyproject]*"""
#     tool_section: dict[str, Any] = dataclasses.field(default_factory=dict)
#     """The tool section of the pyproject file (as a dict) *[pyproject]*"""
#     line_length: int | None = None
#     """The line length, if defined by any popular tool *[pyproject]*"""
#     commit_types: list[commitconventions.CommitTypeStr] = dataclasses.field(
#         default_factory=list,
#     )
#     """Commit types defined in pyproject mknodes section *[pyproject]*"""
#     extras_descriptions: dict[str, str] = dataclasses.field(default_factory=dict)
#     """Descriptions for extras, defined in pyproject mknodes section *[pyproject]*"""
#     package_repos: list[installmethods.InstallMethodStr] = dataclasses.field(
#         default_factory=list,
#     )
#     """Package repositories the distribution is distributed on."""
#     docstring_style: str | None = None
#     """Defined in pyproject mknodes section *[pyproject]*"""


@dataclasses.dataclass
class NodeBuildStats:
    render_duration: float = 0
    render_count: int = 0


@dataclasses.dataclass
class BuildContext(Context):
    page_mapping: dict = dataclasses.field(default_factory=dict)
    """A dictionary mapping all page filenames to the corresponding MkPages."""
    requirements: requirements.Requirements = dataclasses.field(
        default_factory=requirements.Requirements,
    )
    """All requirements (JS, CSS, extensions) inferred from the build."""
    node_stats: list[NodeBuildStats] = dataclasses.field(default_factory=list)
    """Some stats about nodes construction."""
    node_counter: collections.Counter = dataclasses.field(
        default_factory=collections.Counter,
    )
    """Counter containing the amount of creations for each node class."""

    # original_config: dict = dataclasses.field(default_factory=dict)
    # config_override: dict = dataclasses.field(default_factory=dict)
    # final_config: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class PackageContext(Context):
    # PackageInfo
    module: types.ModuleType | None = None
    """The module object itself."""
    griffe_module: Module | None = None
    """The module object itself."""
    docstring_style: str | None = None
    """The style used for DocStrings."""
    distribution_name: str = ""
    """The name of the distribution *[Metadata]*"""
    summary: str = ""
    """A summary for the distribution *[Metadata]*"""
    description: str = ""
    """A description for the distribution *[Metadata]*"""
    author_name: str = ""
    """The author name of the distribution *[Metadata]*"""
    author_email: str = ""
    """A description for the distribution *[Metadata]*"""
    authors: dict[str, str] = dataclasses.field(default_factory=dict)
    """All authors of the distribution *[Metadata]*"""
    classifiers: list = dataclasses.field(default_factory=list)
    """Distribution classifiers *[Metadata]*"""
    classifier_map: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    """Distribution classifiers, sorted by category *[Metadata]*"""
    keywords: list[str] = dataclasses.field(default_factory=list)
    """Distribution keywords *[Metadata]*"""
    required_python_version: str | None = ""
    """The required python version for the distribution *[Metadata]*"""
    required_package_names: list[str] = dataclasses.field(default_factory=list)
    """The names of the dependencies."""
    required_packages: dict = dataclasses.field(default_factory=dict)
    """PackageInfos for the dependencies."""
    extras: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    """The extras of the distribution."""
    urls: dict[str, str] = dataclasses.field(default_factory=dict)
    """A set of URLs related to the distribution."""
    homepage: str = ""
    """The main website of the distribution."""
    license_name: str | None = ""
    """Name of the license"""
    license_text: str | None = ""
    """The complete license text"""
    pretty_name: str = ""
    """A pretty name for the distribution (like **MkNodes**) *[MkDocs site name]*"""
    repository_url: str = ""
    """The URL to the remote code repository."""
    repository_username: str = ""
    """The username for the remote code repository."""
    repository_name: str = ""
    """The repository name of the distribution."""
    repository_path: pathlib.Path = dataclasses.field(default_factory=pathlib.Path)
    """The path to the local git repository."""
    mkdocs_config: mkdocsconfigfile.MkDocsConfigFile | None = None
    """A dict-like File containing the MkDocs config."""
    pyproject_file: pyproject.PyProject = dataclasses.field(
        default_factory=pyproject.PyProject,
    )
    """A dict-like File containing the PyProject data."""
    tools: list[tools.Tool] = dataclasses.field(default_factory=list)
    """A list of tools found for the distribution."""
    task_runners: list = dataclasses.field(default_factory=list)
    """Task runners used by the distribution."""
    social_info: list[dict[str, str]] = dataclasses.field(default_factory=list)
    """A icon-name -> URL dictionary containing ."""
    inventory_url: str | None = ""
    """A best guess for an inventory URL for the package."""
    entry_points: dict = dataclasses.field(default_factory=dict)
    """A dictionary containing the entry points of the distribution."""
    cli: str | None = None
    """The cli package used by the distribution."""

    # required_packages: dict[PackageInfo, packagehelpers.Dependency] =

    # pyproject
    build_system: buildsystems.BuildSystem = dataclasses.field(
        default_factory=lambda: buildsystems.hatch,
    )
    """The build system set as build backend *[pyproject]*"""
    configured_build_systems: list = dataclasses.field(default_factory=list)
    """A list of build systems which are configured in pyproject *[pyproject]*"""
    tool_section: superdict.SuperDict[Any] = dataclasses.field(
        default_factory=superdict.SuperDict,
    )
    """The tool section of the pyproject file.

    Comes as a SuperDict. (A Mutable mapping with extended capabilities) *[pyproject]*"""
    line_length: int | None = None
    """The line length, if defined by any popular tool *[pyproject]*"""
    commit_types: list[commitconventions.CommitTypeStr] = dataclasses.field(
        default_factory=list,
    )
    """Commit types defined in pyproject mknodes section *[pyproject]*"""
    extras_descriptions: dict[str, str] = dataclasses.field(default_factory=dict)
    """Descriptions for the extras, defined in pyproject mknodes section *[pyproject]*"""
    package_repos: list[installmethods.InstallMethodStr] = dataclasses.field(
        default_factory=list,
    )
    """Package repositories the distribution is distributed on.
    Defined in pyproject mknodes section *[pyproject]*"""


@dataclasses.dataclass
class GitHubContext(Context):
    """Information about the GitHub repo / user."""

    default_branch: str = ""
    """The default branch of the repository."""
    repo_name: str = ""
    """The repository name."""
    workflows: list[dict] = dataclasses.field(default_factory=list)
    """A dictionary (workflow-name -> workflow-yaml) containing workflows."""
    avatar_url: str | None = None
    """The url of the GitHub avatar."""
    bio: str | None = None
    """The user biography."""
    blog: str | None = None
    """The user blog URL."""
    company: str | None = None
    """The company associated with the user."""
    email: str | None = None
    """The user email address."""
    followers: int = 0
    """The follower count of the user."""
    gravatar_id: str | None = None
    """The gravatar id associated with the user."""
    hireable: bool = False
    """Whether the user is hireable."""
    location: str | None = None
    """The user location, as set on GitHub."""
    name: str | None = None
    """The GitHub username."""
    twitter_username: str | None = None
    """The twitter username."""


@dataclasses.dataclass
class ProjectContext(Context):
    """All information about a project."""

    metadata: PackageContext = dataclasses.field(default_factory=PackageContext)
    git: GitContext = dataclasses.field(default_factory=GitContext)
    github: GitHubContext = dataclasses.field(default_factory=GitHubContext)
    theme: ThemeContext = dataclasses.field(default_factory=ThemeContext)
    links: linkprovider.LinkProvider = dataclasses.field(
        default_factory=linkprovider.LinkProvider,
    )
    # requirements: Requirements = dataclasses.field(default_factory=Requirements)
    # pyproject: pyproject.PyProject = dataclasses.field(
    #     default_factory=pyproject.PyProject,
    # )

    def as_dict(self):
        return dict(
            metadata=self.metadata,
            git=self.git,
            github=self.github,
            # requirements=dict(self.requirements),
            theme=self.theme,
            links=self.links,
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
    cli="typer",
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
    edit_uri="edit/main/docs/",
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
    links=linkprovider.LinkProvider(),
    # requirements=Requirements(),
)


if __name__ == "__main__":
    info = PackageContext()
    print(info.fields)
