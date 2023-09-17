from __future__ import annotations

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mkheader, mklink, mknode, mktext
from mknodes.data import buildsystems
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)

EXAMPLE_URL = "http://www.some-github-provider.com/my-project.git"

START_TEXT = """All development for this library happens in the
{link} repo on GitHub.
First, you'll need to download the source code and install an
editable version of the Python package:"""

CLONE_CODE = """
# Clone the repository
git clone {repo_url}
cd {folder_name}
"""


def get_build_backend_section(backend: buildsystems.BuildSystem) -> list[mknode.MkNode]:
    backend_name = backend.identifier.capitalize()
    return [
        mkheader.MkHeader("Build system"),
        mktext.MkText(f"{backend_name} is used as the build system."),
        mkcode.MkCode(f"pip install {backend.identifier}", language="bash"),
        mklink.MkLink(backend.url, "More information"),
    ]


class MkDevEnvSetup(mkcontainer.MkContainer):
    """Text node containing Instructions to set up a dev environment."""

    ICON = "material/dev-to"
    STATUS = "new"

    def __init__(
        self,
        *,
        repo_url: str | None = None,
        build_backend: buildsystems.BuildSystemStr | None = None,
        header: str = "Setting up a development environment",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            repo_url: Repo url to show. If None, it will be pulled from project.
            build_backend: Build backend to show install instructions for.
                            If None, it will be pulled from project.
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self._repo_url = repo_url
        self._build_backend = build_backend

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            repo_url=self._repo_url,
            build_backend=self._build_backend,
            _filter_empty=True,
        )

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

    @property
    def items(self):
        folder_name = self.repo_url.removesuffix(".git").split("/")[-1]
        code = CLONE_CODE.format(repo_url=self.repo_url, folder_name=folder_name)
        link = mklink.MkLink(self.repo_url, folder_name)
        start_text = START_TEXT.format(link=str(link))
        items = [mktext.MkText(start_text), mkcode.MkCode(code, language="md")]
        items.extend(get_build_backend_section(self.build_backend))
        for item in items:
            item.parent = self
        return items

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkDevEnvSetup(header="")
        page += mknodes.MkReprRawRendered(node, header="### From project")
        node = MkDevEnvSetup(header="", repo_url="http://url_to_git_repo.com/name.git")
        page += mknodes.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    setup_text = MkDevEnvSetup(build_backend="flit")
    print(setup_text)
