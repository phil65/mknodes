from __future__ import annotations

import dataclasses

from typing import Literal


# ![Static Badge](https://img.shields.io/badge/built_with-mknodes-yellow?link=www.pypa.org)


@dataclasses.dataclass(frozen=True)
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

daily_downloads_badge = Badge(
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


# GITHUB

github_releases_badge = Badge(
    identifier="releases",
    group="github",
    title="Releases",
    image_url="https://img.shields.io/github/downloads/{user}/{project}/total.svg",
    url="https://github.com/{user}/{project}/releases",
)


github_contributors_badge = Badge(
    identifier="contributors",
    group="github",
    title="Github Contributors",
    image_url="https://img.shields.io/github/contributors/{user}/{project}",
    url="https://github.com/{user}/{project}/graphs/contributors",
)

github_discussions_badge = Badge(
    identifier="discussions",
    group="github",
    title="Github Discussions",
    image_url="https://img.shields.io/github/discussions/{user}/{project}",
    url="https://github.com/{user}/{project}/discussions",
)

github_forks_badge = Badge(
    identifier="forks",
    group="github",
    title="Github Forks",
    image_url="https://img.shields.io/github/forks/{user}/{project}",
    url="https://github.com/{user}/{project}/forks",
)

github_issues_badge = Badge(
    identifier="issues",
    group="github",
    title="Github Issues",
    image_url="https://img.shields.io/github/issues/{user}/{project}",
    url="https://github.com/{user}/{project}/issues",
)

github_pull_requests_badge = Badge(
    identifier="pull_requests",
    group="github",
    title="Github Issues",
    image_url="https://img.shields.io/github/issues-pr/{user}/{project}",
    url="https://github.com/{user}/{project}/pulls",
)

github_watchers_badge = Badge(
    identifier="watchers",
    group="github",
    title="Github Watchers",
    image_url="https://img.shields.io/github/watchers/{user}/{project}",
    url="https://github.com/{user}/{project}/watchers",
)


github_stars_badge = Badge(
    identifier="stars",
    group="github",
    title="Github Stars",
    image_url="https://img.shields.io/github/stars/{user}/{project}",
    url="https://github.com/{user}/{project}/stars",
)


github_repo_size_badge = Badge(
    identifier="repo_size",
    group="github",
    title="Github Repository size",
    image_url="https://img.shields.io/github/repo-size/{user}/{project}",
    url="https://github.com/{user}/{project}",
)

github_last_commit_badge = Badge(
    identifier="last_commit",
    group="github",
    title="Github last commit",
    image_url="https://img.shields.io/github/last-commit/{user}/{project}",
    url="https://github.com/{user}/{project}/commits",
)

github_release_date_badge = Badge(
    identifier="release_date",
    group="github",
    title="Github release date",
    image_url="https://img.shields.io/github/release-date/{user}/{project}",
    url="https://github.com/{user}/{project}/releases",
)


github_language_count_badge = Badge(
    identifier="language_count",
    group="github",
    title="Github language count",
    image_url="https://img.shields.io/github/languages/count/{user}/{project}",
    url="https://github.com/{user}/{project}",
)

# needs branch
# github_build_badge = Badge(
#     identifier="build",
#     group="github",
#     title="Github Build",
#     image_url="https://github.com/{user}/{project}/workflows/Build/badge.svg",
#     url="https://github.com/{user}/{project}/actions/",
# )

github_weekly_commits_badge = Badge(
    identifier="weekly_commits",
    group="github",
    title="Github commits this week",
    image_url="https://img.shields.io/github/commit-activity/w/{user}/{project}",
    url="https://github.com/{user}/{project}",
)

github_monthly_commits_badge = Badge(
    identifier="monthly_commits",
    group="github",
    title="Github commits this month",
    image_url="https://img.shields.io/github/commit-activity/m/{user}/{project}",
    url="https://github.com/{user}/{project}",
)

github_yearly_commits_badge = Badge(
    identifier="yearly_commits",
    group="github",
    title="Github commits this year",
    image_url="https://img.shields.io/github/commit-activity/y/{user}/{project}",
    url="https://github.com/{user}/{project}",
)


# MISC
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
    latest_version_badge,
    license_badge,
    package_status_badge,
    daily_downloads_badge,
    weekly_downloads_badge,
    monthly_downloads_badge,
    format_badge,
    wheel_badge,
    python_version_badge,
    implementation_badge,
    # github_build_badge,
    github_releases_badge,
    github_contributors_badge,
    github_discussions_badge,
    github_forks_badge,
    github_issues_badge,
    github_pull_requests_badge,
    github_watchers_badge,
    github_stars_badge,
    github_repo_size_badge,
    github_last_commit_badge,
    github_release_date_badge,
    github_language_count_badge,
    github_weekly_commits_badge,
    github_monthly_commits_badge,
    github_yearly_commits_badge,
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
    "releases",
    "contributors",
    "discussions",
    "forks",
    "issues",
    "pull_requests",
    "watchers",
    "stars",
    "repo_size",
    "last_commit",
    "release_date",
    "language_count",
    "build",
    "weekly_commits",
    "monthly_commits",
    "yearly_commits",
    "codecov",
    "black",
    "pyup",
]
