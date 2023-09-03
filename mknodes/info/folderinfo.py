from __future__ import annotations

import importlib
import logging
import os
import pathlib
import re

from mknodes.data import taskrunners, tools
from mknodes.info import gitrepository, packageinfo, pyproject
from mknodes.utils import helpers, reprhelpers, yamlhelpers


logger = logging.getLogger(__name__)


SOCIALS = {
    "gitter.im": "fontawesome/brands/gitter",
    "matrix.to": "fontawesome/brands/gitter",
    "twitter.com": "fontawesome/brands/twitter",
    "docker.com": "fontawesome/brands/docker",
    "fosstodon.org": "fontawesome/brands/mastodon",
    "discord.gg": "fontawesome/brands/discord",
    "linkedin.com": "fontawesome/brands/linkedin",
    "dev.to": "fontawesome/brands/dev",
    "medium.to": "fontawesome/brands/medium",
}


GITHUB_REGEX = re.compile(
    r"(?:http?:\/\/|https?:\/\/)?"
    r"(?:www\.)?"
    r"github\.com\/"
    r"(?:\/*)"
    r"([\w\-\.]*)\/"
    r"([\w\-]*)"
    r"(?:\/|$)?"  # noqa: COM812
)


class FolderInfo:
    """Aggregates information about a working dir."""

    def __init__(self, path: str | os.PathLike | None = None):
        self.path = pathlib.Path(path or ".")
        self.pyproject = pyproject.PyProject(self.path)
        self.git = gitrepository.GitRepository(self.path)
        if (path := self.path / "mkdocs.yml").exists():
            text = path.read_text(encoding="utf-8")
            self.mkdocs_config = yamlhelpers.load_yaml(text, mode="unsafe")
        else:
            self.mkdocs_config = {}
        mod_name = self.git.get_repo_name()
        self.module = importlib.import_module(mod_name.replace("-", "_").lower())

    def __repr__(self):
        return reprhelpers.get_repr(self, path=self.path)

    @classmethod
    def clone_from(
        cls,
        url: str,
        # path: str | os.PathLike,
        depth: int = 100,
    ):
        import tempfile

        import git

        directory = tempfile.TemporaryDirectory(prefix="mknodes_repo_")
        repo = git.Repo.clone_from(url, directory.name, depth=depth)
        kls = cls(repo.working_dir)
        kls._temp_directory = directory
        return kls

    @property
    def info(self):
        return packageinfo.get_info(self.pyproject.name or self.git.get_repo_name())

    @property
    def repository_url(self) -> str | None:
        return (
            url
            if (url := self.mkdocs_config.get("repo_url"))
            else self.info.repository_url
        )

    @property
    def repository_username(self) -> str | None:
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(1)
        return None

    @property
    def repository_name(self) -> str | None:
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(2)
        return None

    @property
    def package_name(self) -> str:
        return self.module.__name__

    @property
    def package_repos(self) -> list[str]:
        return self.pyproject.package_repos

    @property
    def commit_types(self) -> list[str]:
        return self.pyproject.allowed_commit_types

    @property
    def tools(self) -> list[tools.Tool]:
        """Return a list of build tools used by this package."""
        return [t for t in tools.TOOLS.values() if t.is_used(self)]

    def get_license_file_path(self) -> pathlib.Path | None:
        """Return license file path (relative to project root) from metadata."""
        for path in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
            if (file := self.path / path).exists():
                return file
        if file := self.info.metadata.json.get("license_file"):
            return self.path / file
        return None

    def get_social_info(self) -> list[dict[str, str]]:
        result = []
        if self.repository_url:
            result.append(
                dict(icon="fontawesome/brands/github", link=self.repository_url),
            )
        for link in self.info.urls.values():
            result.extend(
                dict(icon=v, link=link) for k, v in SOCIALS.items() if k in link
            )
        result.append(
            dict(
                icon="fontawesome/brands/python",
                link=f"https://pypi.org/project/{self.module.__name__}/",
            ),
        )
        return result

    def aggregate_info(self) -> dict:
        infos = dict(
            repository_name=self.repository_name,
            repository_username=self.repository_username,
            repository_url=self.repository_url,
        )
        return infos | self.info.metadata.json

    @property
    def task_runners(self) -> list[taskrunners.TaskRunner]:
        """Return list of task runners used by this package."""
        return [
            runner
            for runner in taskrunners.TASK_RUNNERS.values()
            if any(
                helpers.find_file_in_folder_or_parent(i, self.path)
                for i in runner.filenames
            )
        ]


if __name__ == "__main__":
    info = FolderInfo.clone_from("https://github.com/mkdocs/mkdocs.git")
    print(info.get_social_info())
