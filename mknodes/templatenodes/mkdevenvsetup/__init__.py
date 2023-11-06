from __future__ import annotations

from typing import Any

from mknodes.templatenodes import mktemplate
from mknodes.data import buildsystems
from mknodes.utils import log


logger = log.get_logger(__name__)

EXAMPLE_URL = "http://www.some-github-provider.com/my-project.git"


class MkDevEnvSetup(mktemplate.MkTemplate):
    """Text node containing Instructions to set up a dev environment."""

    ICON = "material/dev-to"

    def __init__(
        self,
        *,
        repo_url: str | None = None,
        build_backend: buildsystems.BuildSystemStr | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            repo_url: Repo url to show. If None, it will be pulled from project.
            build_backend: Build backend to show install instructions for.
                            If None, it will be pulled from project.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/markdown/template", **kwargs)
        self._repo_url = repo_url
        self._build_backend = build_backend

    @property
    def repo_url(self) -> str:
        match self._repo_url:
            case None:
                repo_url = self.ctx.metadata.repository_url
            case str():
                repo_url = self._repo_url
            case _:
                raise TypeError(self._repo_url)
        repo_url = repo_url.rstrip("/")
        if not repo_url.endswith(".git"):
            repo_url += ".git"
        return repo_url

    @repo_url.setter
    def repo_url(self, value):
        self._repo_url = value

    @property
    def build_backend(self) -> buildsystems.BuildSystem:  # type: ignore[return]
        if self._build_backend is None:
            return self.ctx.metadata.build_system or buildsystems.setuptools
        return buildsystems.BUILD_SYSTEMS[self._build_backend]

    @build_backend.setter
    def build_backend(self, value):
        self._build_backend = value

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkDevEnvSetup()
        page += mk.MkReprRawRendered(node, header="### From project")
        node = MkDevEnvSetup(repo_url="http://url_to_git_repo.com/name.git")
        page += mk.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    setup_text = MkDevEnvSetup(build_backend="flit")
    print(setup_text)
