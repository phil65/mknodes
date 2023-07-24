from __future__ import annotations

import dataclasses
import logging

from typing import Literal

from mknodes import mktext


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Shield:
    identifier: str
    title: str
    image_url: str
    url: str

    def to_url(self, user: str, project: str):
        image_url = self.image_url.format(user=user, project=project)
        url = self.url.format(user=user, project=project)
        return f"[![{self.title}]({image_url})]({url})"


build_shield = Shield(
    identifier="build",
    title="PyPI Latest Release",
    image_url="https://github.com/{user}/{project}/workflows/Build/badge.svg",
    url="https://github.com/{user}/{project}/actions/",
)

latest_release_shield = Shield(
    identifier="latest",
    title="PyPI Latest Release",
    image_url="https://img.shields.io/pypi/v/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

package_status_shield = Shield(
    identifier="status",
    title="Package status",
    image_url="https://img.shields.io/pypi/status/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

code_cov_shield = Shield(
    identifier="codecov",
    title="Package status",
    image_url="https://codecov.io/gh/{user}/{project}/branch/master/graph/badge.svg",
    url="https://codecov.io/gh/{user}/{project}/",
)

black_shield = Shield(
    identifier="black",
    title="Code style: black",
    image_url=r"https://img.shields.io/badge/code%20style-black-000000.svg",
    url="https://github.com/psf/black",
)

pyup_shield = Shield(
    identifier="pyup",
    title="PyUp",
    image_url="https://pyup.io/repos/github/{user}/{project}/shield.svg",
    url="https://pyup.io/repos/github/{user}/{project}/",
)

codetriage_shield = Shield(
    identifier="code_triage",
    title="Open Source Helpers",
    image_url="https://www.codetriage.com/{user}/{project}/users.svg",
    url="https://www.codetriage.com/{user}/{project}/",
)

SHIELDS = [
    build_shield,
    latest_release_shield,
    package_status_shield,
    code_cov_shield,
    black_shield,
    pyup_shield,
    codetriage_shield,
]

ShieldTypeStr = Literal[
    "build", "latest", "status", "codecov", "black", "pyup", "code_triage"
]


class MkShields(mktext.MkText):
    """MkCritic block."""

    def __init__(
        self,
        user: str,
        project: str,
        shields: list[ShieldTypeStr],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.user = user
        self.project = project
        self.shields = shields

    def _to_markdown(self) -> str:
        shield_strs = [
            s.to_url(user=self.user, project=self.project)
            for s in SHIELDS
            if s.identifier in self.shields
        ]
        return "".join(shield_strs)

    @staticmethod
    def examples():
        yield dict(
            user="phil65", project="mknodes", shields=["latest", "status", "codecov"]
        )


if __name__ == "__main__":
    mkcritic = MkShields("phil65", "prettyqt", shields=["latest", "status", "codecov"])
    print(mkcritic)
