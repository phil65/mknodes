from __future__ import annotations

from abc import ABCMeta
from collections.abc import MutableMapping
import os
import tempfile

from mknodes.info import gitrepository
from mknodes.utils import helpers, log


logger = log.get_logger(__name__)


def get_repo(
    repo_url: str | os.PathLike,
    clone_depth: int = 100,
) -> gitrepository.GitRepository:
    """Return info for given module from registry.

    Arguments:
        repo_url: Name of the module
        clone_depth: Amount of commits to clone if repo is remote.
    """
    return registry.get_repo(repo_url, clone_depth=clone_depth)


class RepoRegistry(MutableMapping, metaclass=ABCMeta):
    """Registry for Git repositories.

    Manages the GitRepository instances and temporary directories.
    """

    def __init__(self):
        self._repos: dict[str, gitrepository.GitRepository] = {}
        self._directories: dict[str, tempfile.TemporaryDirectory] = {}

    def __getitem__(self, value):
        return self._repos.__getitem__(value)

    def __setitem__(self, index, value):
        self._repos[index] = value

    def __delitem__(self, index):
        del self._repos[index]

    def __repr__(self):
        return f"{type(self).__name__}()"

    def __iter__(self):
        return iter(self._repos.keys())

    def __len__(self):
        return len(self._repos)

    def get_repo(
        self,
        repo_url: str | os.PathLike,
        clone_depth: int = 100,
    ) -> gitrepository.GitRepository:
        """Return a GitRepository for given URL / path.

        Arguments:
            repo_url: URL / path of the repository
            clone_depth: Amount of commits to fetch if repo is remote
        """
        repo_url = os.fspath(repo_url)
        if repo_url in self._repos:
            return self._repos[repo_url]
        if not helpers.is_url(repo_url):
            return gitrepository.GitRepository(repo_url)
        directory = tempfile.TemporaryDirectory(prefix="mknodes_repo_")
        logger.info("Created temporary directory %s", directory.name)
        logger.info("Cloning %s with depth %s", repo_url, clone_depth)
        repo = gitrepository.GitRepository.clone_from(
            repo_url,
            directory.name,
            depth=clone_depth,
        )
        logger.info("Finished cloning.")
        repo.temp_directory = directory
        self._directories[str(repo.working_dir)] = directory
        self._repos[repo_url] = repo
        return repo


registry = RepoRegistry()


if __name__ == "__main__":
    reg = RepoRegistry()
    repo = reg.get_repo("https://github.com/mkdocs/mkdocs")
    print(repo)
