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
    group: str = ""

    def get_image_url(self, user, project, branch):
        return self.image_url.format(user=user, project=project, branch=branch)

    def get_url(self, user, project):
        return self.url.format(user=user, project=project)


# PYPI

latest_version_badge = Badge(
    identifier="version",
    group="pypi",
    title="PyPI Latest Version",
    image_url="https://img.shields.io/pypi/v/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

license_badge = Badge(
    identifier="license",
    group="pypi",
    title="PyPI License",
    image_url="https://img.shields.io/pypi/l/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

package_status_badge = Badge(
    identifier="status",
    group="pypi",
    title="Package status",
    image_url="https://img.shields.io/pypi/status/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

weekly_downloads_badge = Badge(
    identifier="weekly_downloads",
    group="pypi",
    title="Weekly downloads",
    image_url="https://img.shields.io/pypi/dw/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

weekly_downloads_badge = Badge(
    identifier="daily_downloads",
    group="pypi",
    title="Daily downloads",
    image_url="https://img.shields.io/pypi/dd/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

monthly_downloads_badge = Badge(
    identifier="monthly_downloads",
    group="pypi",
    title="Monthly downloads",
    image_url="https://img.shields.io/pypi/dm/{project}.svg",
    url="https://pypi.org/project/{project}/",
)


format_badge = Badge(
    identifier="format",
    group="pypi",
    title="Distribution format",
    image_url="https://img.shields.io/pypi/format/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

wheel_badge = Badge(
    identifier="wheel",
    group="pypi",
    title="Wheel availability",
    image_url="https://img.shields.io/pypi/wheel/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

python_version_badge = Badge(
    identifier="python_version",
    group="pypi",
    title="Python version",
    image_url="https://img.shields.io/pypi/pyversions/{project}.svg",
    url="https://pypi.org/project/{project}/",
)

implementation_badge = Badge(
    identifier="implementation",
    group="pypi",
    title="Implementation",
    image_url="https://img.shields.io/pypi/implementation/{project}.svg",
    url="https://pypi.org/project/{project}/",
)


# MISC

build_badge = Badge(
    identifier="build",
    group="github",
    title="Github Build",
    image_url="https://github.com/{user}/{project}/workflows/Build/badge.svg",
    url="https://github.com/{user}/{project}/actions/",
)

code_cov_badge = Badge(
    identifier="codecov",
    group="quality",
    title="Package status",
    image_url="https://codecov.io/gh/{user}/{project}/branch/{branch}/graph/badge.svg",
    url="https://codecov.io/gh/{user}/{project}/",
)

black_badge = Badge(
    identifier="black",
    group="quality",
    title="Code style: black",
    image_url=r"https://img.shields.io/badge/code%20style-black-000000.svg",
    url="https://github.com/psf/black",
)

pyup_badge = Badge(
    identifier="pyup",
    group="dependencies",
    title="PyUp",
    image_url="https://pyup.io/repos/github/{user}/{project}/shield.svg",
    url="https://pyup.io/repos/github/{user}/{project}/",
)

SHIELDS = [
    license_badge,
    package_status_badge,
    weekly_downloads_badge,
    weekly_downloads_badge,
    monthly_downloads_badge,
    format_badge,
    wheel_badge,
    python_version_badge,
    implementation_badge,
    build_badge,
    code_cov_badge,
    black_badge,
    pyup_badge,
]

BadgeTypeStr = Literal[
    "version",
    "license",
    "status",
    "weekly_downloads",
    "daily_downloads",
    "monthly_downloads",
    "format",
    "wheel",
    "python_version",
    "implementation",
    "build",
    "codecov",
    "black",
    "pyup",
]
