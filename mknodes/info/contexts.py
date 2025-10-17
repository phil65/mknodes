from __future__ import annotations

import abc
from collections.abc import Mapping, MutableMapping
import dataclasses
import pathlib
from typing import TYPE_CHECKING, Any

import epregistry
import githarbor
import jinjarope

import mknodes as mk
from mknodes.data import buildsystems, commitconventions, installmethods, tools
from mknodes.info import (
    folderinfo,
    linkprovider,
    mkdocsconfigfile,
    packageregistry,
    pyproject,
)
from mknodes.utils import log, superdict


if TYPE_CHECKING:
    import datetime
    import types

    import clinspector
    from griffe import Alias, Module

    from mknodes.info.packageinfo import PackageInfo
    from mknodes.utils.packagehelpers import Dependency


logger = log.get_logger(__name__)

DEFAULT_LOADER = jinjarope.FileSystemLoader("docs")


@dataclasses.dataclass
class Context:
    """Base class for contexts."""

    def as_dict(self):
        return {
            field.name: getattr(self, field.name) for field in dataclasses.fields(self)
        }

    @property
    def fields(self) -> list[str]:
        return [i.name for i in dataclasses.fields(self)]


@dataclasses.dataclass
class GitContext(Context):
    """Local repository information."""

    main_branch: str = ""
    """Name of the main branch of the repo (`master` / `main`)."""
    repo_name: str = ""
    """Name of the git folder."""
    commits: list[Any] = dataclasses.field(default_factory=list)
    """List of last commits (Commit objects from `GitPython`)."""
    repo_hoster: str = ""
    """Name of the code hoster (for example `GitHub`)"""
    edit_uri: str | None = None
    """Edit uri (depends on code hoster)."""
    current_sha: str = ""
    """SHA of last commit."""
    current_committer: str = ""
    """Committer name for last commit."""
    current_date_committed: datetime.datetime | None = None
    """Date committed for last commit."""
    current_author: str = ""
    """Author email for last commit."""
    current_date_authored: datetime.datetime | None = None
    """Date authored for last commit."""
    last_version: str | None = None
    """Name of last commit tag."""

    def __repr__(self):
        return f"GitContext({self.repo_name!r}: {self.main_branch!r})"


@dataclasses.dataclass
class ThemeContext(Context):
    """Information about the theme."""

    name: str = ""
    """Name of the theme."""
    primary_color: str = ""
    """Primary color."""
    text_color: str = ""
    """Primary text color."""
    data: dict[str, str] = dataclasses.field(default_factory=dict)
    """Additional data of the theme."""
    admonitions: list[Any] = dataclasses.field(default_factory=list)
    css_primary_fg: str = ""
    css_primary_bg: str = ""
    css_primary_bg_light: str = ""
    css_accent_fg: str = ""
    css_accent_fg_transparent: str = ""
    css_accent_bg: str = ""
    css_default_fg: str = ""
    css_default_bg: str = ""

    def __repr__(self):
        return f"ThemeContext({self.name!r})"


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
#     package_repos: list[installmethods.InstallMethod] = dataclasses.field(
#         default_factory=list,
#     )
#     """Package repositories the distribution is distributed on."""
#     docstring_style: str | None = None
#     """Defined in pyproject mknodes section *[pyproject]*"""


@dataclasses.dataclass
class PackageContext(Context):
    """Information about a package."""

    # PackageInfo
    module: types.ModuleType | None = None
    """The module object itself."""
    griffe_module: Module | Alias | None = None
    """The module object itself."""
    docstring_style: str | None = None
    """The style used for DocStrings."""
    distribution_name: str = ""
    """The name of the distribution *[Metadata]*"""
    version: str = ""
    """The version of the distribution *[Metadata]*"""
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
    classifiers: list[str] = dataclasses.field(default_factory=list)
    """Distribution classifiers *[Metadata]*"""
    classifier_map: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    """Distribution classifiers, sorted by category *[Metadata]*"""
    keywords: list[str] = dataclasses.field(default_factory=list)
    """Distribution keywords *[Metadata]*"""
    required_python_version: str | None = ""
    """The required python version for the distribution *[Metadata]*"""
    required_package_names: list[str] = dataclasses.field(default_factory=list)
    """The names of the dependencies."""
    required_packages: dict[PackageInfo, Dependency] = dataclasses.field(
        default_factory=dict
    )
    """PackageInfos for the dependencies."""
    extras: dict[str, folderinfo.PackageExtra] = dataclasses.field(default_factory=dict)
    """The extras of the distribution."""
    urls: Mapping[str, str] = dataclasses.field(default_factory=dict)
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
    task_runners: list[Any] = dataclasses.field(default_factory=list)
    """Task runners used by the distribution."""
    social_info: list[dict[str, str]] = dataclasses.field(default_factory=list)
    """A icon-name -> URL dictionary containing ."""
    inventory_url: str | None = ""
    """A best guess for an inventory URL for the package."""
    entry_points: epregistry.ModuleEntryPointRegistry = dataclasses.field(
        default_factory=epregistry.ModuleEntryPointRegistry
    )
    """A dictionary containing the entry points of the distribution."""
    cli: str | None = None
    """The cli package name used by the distribution."""
    cli_info: clinspector.CommandInfo | None = None
    """An object containing information about all cli commands."""

    # required_packages: dict[PackageInfo, packagehelpers.Dependency] =

    # pyproject
    build_system: buildsystems.BuildSystem = dataclasses.field(
        default_factory=lambda: buildsystems.hatch,
    )
    """The build system set as build backend *[pyproject]*"""
    configured_build_systems: list[Any] = dataclasses.field(default_factory=list)
    """A list of build systems which are configured in pyproject *[pyproject]*"""
    tool_section: superdict.SuperDict[Any] = dataclasses.field(
        default_factory=superdict.SuperDict,
    )
    """The tool section of the pyproject file.

    Comes as a SuperDict. (A Mutable mapping with extended capabilities) *[pyproject]*
    """
    line_length: int | None = None
    """The line length, if defined by any popular tool *[pyproject]*"""
    commit_types: list[commitconventions.CommitTypeStr] = dataclasses.field(
        default_factory=list,
    )
    """Commit types defined in pyproject mknodes section *[pyproject]*"""
    package_repos: list[installmethods.InstallMethod] = dataclasses.field(
        default_factory=list,
    )
    """Package repositories the distribution is distributed on.
    Defined in pyproject mknodes section *[pyproject]*
    """

    def __repr__(self):
        return f"PackageContext({self.distribution_name!r})"


@dataclasses.dataclass
class GitHubContext(Context):
    """Information about the GitHub repo / user."""

    default_branch: str = ""
    """The default branch of the repository."""
    repo_name: str = ""
    """The repository name."""
    workflows: list[githarbor.Workflow] = dataclasses.field(default_factory=list)
    """A list of configured workflows."""
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
    followers: int | None = None
    """The follower count of the user."""
    gravatar_id: str | None = None
    """The gravatar id associated with the user."""
    hireable: bool | None = None
    """Whether the user is hireable."""
    location: str | None = None
    """The user location, as set on GitHub."""
    name: str | None = None
    """The GitHub username."""
    twitter_username: str | None = None
    """The twitter username."""

    def __repr__(self):
        return f"GitHubContext({self.repo_name!r})"

    @classmethod
    def from_url(cls, url: str) -> GitHubContext:
        """Create GitHubContext from a GitHubRepository instance.

        Args:
            url: URL to the repository.

        Returns:
            GitHubContext: Populated context instance.
        """
        repo = githarbor.create_repository(url)
        workflows = repo.list_workflows()
        user = repo.get_repo_user()

        return cls(
            default_branch=repo.default_branch,
            repo_name=f"{repo.owner}/{repo.name}",
            workflows=workflows,
            avatar_url=user.avatar_url,
            bio=user.bio,
            blog=user.blog,
            company=user.company,
            email=user.email,
            followers=user.followers,
            gravatar_id=user.gravatar_id,
            hireable=user.hireable,
            location=user.location,
            name=user.name,
            twitter_username=user.twitter_username,
        )


@dataclasses.dataclass
class EnvironmentContext(MutableMapping[str, Any], metaclass=abc.ABCMeta):
    loader: dict[str, dict[str, Any]] = dataclasses.field(default_factory=dict)
    block_start_string: str | None = None
    block_end_string: str | None = None
    variable_start_string: str | None = None
    variable_end_string: str | None = None
    undefined: str | None = None

    def __getitem__(self, value):
        return getattr(self, value)

    def __setitem__(self, index, value):
        setattr(self, index, value)

    def __delitem__(self, index):
        setattr(self, index, None)

    def __len__(self):
        return len(dataclasses.fields(self))

    def __iter__(self):
        return iter(i.name for i in dataclasses.fields(self))


@dataclasses.dataclass
class ContextConfig(Mapping[str, Any], metaclass=abc.ABCMeta):
    repo_url: str = "."
    clone_depth: int = 100
    jinja_config: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    llm_config: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    base_url: str = ""
    use_directory_urls: bool = True

    def __getitem__(self, value):
        return getattr(self, value)

    def __setitem__(self, index, value):
        setattr(self, index, value)

    def __len__(self):
        return len(dataclasses.fields(self))

    def __iter__(self):
        return iter(i.name for i in dataclasses.fields(self))


@dataclasses.dataclass
class ProjectContext(Context):
    """All information about a project."""

    metadata: PackageContext = dataclasses.field(default_factory=PackageContext)
    """Information about a package."""
    git: GitContext = dataclasses.field(default_factory=GitContext)
    """Local repository information."""
    github: GitHubContext = dataclasses.field(default_factory=GitHubContext)
    """Information about the GitHub repo / user."""
    theme: ThemeContext = dataclasses.field(default_factory=ThemeContext)
    """Information about the theme."""
    links: linkprovider.LinkProvider = dataclasses.field(
        default_factory=linkprovider.LinkProvider,
    )
    """Link source."""
    env_config: jinjarope.EnvConfig = dataclasses.field(
        default_factory=lambda: jinjarope.EnvConfig(loader=DEFAULT_LOADER)
    )
    # resources: Resources = dataclasses.field(default_factory=Resources)
    # pyproject: pyproject.PyProject = dataclasses.field(
    #     default_factory=pyproject.PyProject,
    # )

    @classmethod
    def for_config(
        cls,
        *args: dict[str, Any],
        theme_context: ThemeContext | None = None,
        **kwargs: Any,
    ):
        """The main project to create a website.

        Args:
            args: Config mapping
            theme_context: Optional theme context
            kwargs: Keyword arguments to override config values
        """
        from mknodes.info import folderinfo as fi, linkprovider, reporegistry

        cfg = {k: v for d in args for k, v in d.items()}
        cfg.update(kwargs)
        links = linkprovider.LinkProvider(
            base_url=cfg.get("base_url", ""),
            use_directory_urls=cfg.get("use_directory_urls", True),
            include_stdlib=True,
        )
        repo_url = cfg.get("repo_url") or "."
        clone_depth = cfg.get("clone_depth", 100)
        try:
            git_repo = reporegistry.get_repo(repo_url, clone_depth=clone_depth)
        except Exception as e:  # noqa: BLE001
            print(f"Error fetching repository: {e}")
            git_repo = None
        folderinfo = fi.FolderInfo(git_repo.working_dir if git_repo else ".")
        return cls(
            metadata=folderinfo.context,
            git=folderinfo.git.context,
            theme=theme_context or ThemeContext(),
            links=links,
            env_config=cfg.get("env_config", jinjarope.EnvConfig(loader=DEFAULT_LOADER)),
        )

    async def populate_linkprovider(self):
        if self.metadata.mkdocs_config is None:
            return
        invs = self.metadata.mkdocs_config.get_inventory_infos()
        mk_urls = {i["url"]: i.get("base_url") for i in invs if "url" in i}
        for url, base_url in mk_urls.items():
            self.links.add_inv_file(url, base_url=base_url)
        for url in packageregistry.registry.inventory_urls:
            if url not in mk_urls:
                self.links.add_inv_file(url)

    def as_dict(self):
        return dict(
            metadata=self.metadata,
            git=self.git,
            github=self.github,
            # resources=dict(self.resources),
            theme=self.theme,
            links=self.links,
        )


def get_default_project_context():
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
    default_package_context = PackageContext(
        pretty_name="MkNodes",
        version="1.0.0",
        distribution_name="mknodes",
        summary="Don't write docs. Code them.",
        description="Long text with description.",
        author_name="Philipp Temminghoff",
        author_email="philipptemminghoff@gmail.com",
        license_name="MIT",
        required_python_version=">= 3.13",
        homepage="",
        cli="typer",
        module=mk,
        repository_url="https://github.com/phil65/mknodes/",
        repository_username="phil65",
        repository_name="mknodes",
        inventory_url="https://github.io/phil65/mknodes/objects.inv",
    )

    return ProjectContext(
        metadata=default_package_context,
        git=default_git_context,
        github=default_github_context,
        theme=default_theme_context,
        links=linkprovider.LinkProvider(),
        env_config=jinjarope.EnvConfig(),
        # resources=Resources(),
    )


if __name__ == "__main__":
    info = PackageContext()
    print(info.fields)
