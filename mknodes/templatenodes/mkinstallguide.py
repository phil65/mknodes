from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

PIP_TEXT = """The latest released version is available at the [Python
package index](https://pypi.org/project/{project}).

```sh
pip install {project}
```
"""
# !!! warning
#     This method modifies the Python environment in which you choose to install.
# Consider instead using [pipx](#pipx) to avoid dependency conflicts.

PIPX_TEXT = """[pipx](https://github.com/pypa/pipx)
allows for the global installation of Python applications in isolated environments.

```
pipx install {project}
```
"""
HOMEBREW_TEXT = """See the [formula](https://formulae.brew.sh/formula/{project})
for more details.

```
brew install {project}
```
"""

CONDA_TEXT = """See the [feedstock](https://github.com/conda-forge/{project}-feedstock)
for more details.

```
conda install -c conda-forge {project}
```
"""

PROVIDERS = dict(
    pip=PIP_TEXT,
    pipx=PIPX_TEXT,
    Homebrew=HOMEBREW_TEXT,
    Conda=CONDA_TEXT,
)


class MkInstallGuide(mknode.MkNode):
    """Install guide text (currently PyPi only)."""

    ICON = "material/help"

    def __init__(
        self,
        project: str,
        package_managers: list[str] | None = None,
        header_level: int | None = 3,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            project: name of the project to install
            package_managers: package managers the project can be installed with
            header_level: Header level for each section
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.project = project
        self.header_level = header_level
        self.package_managers = package_managers

    def _to_markdown(self) -> str:
        blocks = []
        managers = self.package_managers or ["pip"]
        for k, v in PROVIDERS.items():
            if k in managers:
                if self.header_level:
                    prefix = self.header_level * "#"
                    blocks.append(f"{prefix} {k}\n")
                blocks.append(v.format(project=self.project))
        return "\n\n".join(blocks)

    def __repr__(self):
        return helpers.get_repr(
            self,
            project=self.project,
            package_managers=self.package_managers,
            header_level=self.header_level,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        # MkInstallGuide is just a text snippet for a short Install guide
        # Currently it is only tailored towards PyPi.

        node = MkInstallGuide(project="mknodes", package_managers=["pip", "pipx"])
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    installguide = MkInstallGuide(project="mknodes")
    print(installguide)
