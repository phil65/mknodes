from __future__ import annotations

import logging

from mknodes import mknode


logger = logging.getLogger(__name__)

TEXT = """The latest released version is available at the [Python
package index](https://pypi.org/project/{project}).

```sh
pip install {project}
```
"""


class MkInstallGuide(mknode.MkNode):
    """Install guide text (currently PyPi only)."""

    def __init__(
        self,
        project: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.project = project

    def _to_markdown(self) -> str:
        return TEXT.format(project=self.project)

    @staticmethod
    def examples():
        yield dict(project="mknodes")


if __name__ == "__main__":
    installguide = MkInstallGuide(project="mknodes")
    print(installguide)
