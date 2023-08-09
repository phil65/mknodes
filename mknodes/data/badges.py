from __future__ import annotations

import dataclasses

from typing import Literal


# ![Static Badge](https://img.shields.io/badge/built_with-mknodes-yellow?link=www.pypa.org)


@dataclasses.dataclass
class Badge:
    identifier: str
    title: str
    image_url: str
    url: str

    def get_image_url(self, user, project, branch):
        return self.image_url.format(user=user, project=project, branch=branch)

    def get_url(self, user, project):
        return self.url.format(user=user, project=project)


build_badge = Badge(
    identifier="build",
    title="Github Build",
    image_url="https://github.com/{user}/{project}/workflows/Build/badge.svg",
    url="https://github.com/{user}/{project}/actions/",
)

latest_version_badge = Badge(
    identifier="version",
    title="PyPI Latest Version",
    image_url="https://img.shields.io/pypi/v/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

license_badge = Badge(
    identifier="license",
    title="PyPI License",
    image_url="https://img.shields.io/pypi/l/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

package_status_badge = Badge(
    identifier="status",
    title="Package status",
    image_url="https://img.shields.io/pypi/status/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

code_cov_badge = Badge(
    identifier="codecov",
    title="Package status",
    image_url="https://codecov.io/gh/{user}/{project}/branch/{branch}/graph/badge.svg",
    url="https://codecov.io/gh/{user}/{project}/",
)

black_badge = Badge(
    identifier="black",
    title="Code style: black",
    image_url=r"https://img.shields.io/badge/code%20style-black-000000.svg",
    url="https://github.com/psf/black",
)

pyup_badge = Badge(
    identifier="pyup",
    title="PyUp",
    image_url="https://pyup.io/repos/github/{user}/{project}/shield.svg",
    url="https://pyup.io/repos/github/{user}/{project}/",
)

codetriage_badge = Badge(
    identifier="code_triage",
    title="Open Source Helpers",
    image_url="https://www.codetriage.com/{user}/{project}/users.svg",
    url="https://www.codetriage.com/{user}/{project}/",
)

SHIELDS = [
    build_badge,
    latest_version_badge,
    package_status_badge,
    code_cov_badge,
    black_badge,
    pyup_badge,
    codetriage_badge,
    license_badge,
]

BadgeTypeStr = Literal[
    "build",
    "version",
    "status",
    "codecov",
    "black",
    "pyup",
    "code_triage",
    "license",
]
