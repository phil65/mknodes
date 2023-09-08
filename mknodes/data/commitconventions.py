from __future__ import annotations

import dataclasses

from typing import Literal

from mknodes.utils import log


logger = log.get_logger(__name__)

ConventionTypeStr = Literal["conventional_commits", "basic"]

CommitTypeStr = Literal[
    "build",
    "chore",
    "ci",
    "deps",
    "doc",
    "docs",
    "feat",
    "fix",
    "ref",
    "revert",
    "add",
    "change",
    "remove",
    "merge",
    "perf",
    "refactor",
    "style",
    "test",
    "tests",
]

TYPE_DESCRIPTIONS: dict[CommitTypeStr, str] = {
    "build": "About packaging, building wheels, etc.",
    "chore": "About packaging or repo/files management.",
    "ci": "About Continuous Integration.",
    "deps": "Dependencies update.",
    "doc": "About documentation.",
    "docs": "About documentation.",
    "feat": "New feature.",
    "fix": "Bug fix.",
    "ref": "Code refactoring.",
    "revert": "Code revert.",
    "add": "Code Addition.",
    "change": "Code change.",
    "remove": "Code removal.",
    "merge": "Code merge.",
    "perf": "About performance.",
    "refactor": "Changes that are not features or bug fixes.",
    "style": "A change in code style/format.",
    "test": "About tests.",
    "tests": "About tests.",
}


@dataclasses.dataclass
class CommitConvention:
    name: str
    display_name: str
    types: set[CommitTypeStr]
    badge: str = ""
    website: str | None = None


basic = CommitConvention(
    name="basic",
    display_name="Basic Style",
    types={"add", "fix", "change", "remove", "merge", "doc"},
)

angular = CommitConvention(
    name="angular",
    display_name="Angular Style",
    website="https://gist.github.com/stephenparish/9941e89d80e2bc58a153",
    types={
        "build",
        "chore",
        "ci",
        "deps",
        "doc",
        "docs",
        "feat",
        "fix",
        "perf",
        "ref",
        "refactor",
        "revert",
        "style",
        "test",
        "tests",
    },
)

conventional_commits = CommitConvention(
    name="conventional_commmits",
    display_name="Conventional commits",
    website="https://www.conventionalcommits.org/en/v1.0.0/",
    badge="https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg",
    types={
        "build",
        "chore",
        "ci",
        "deps",
        "doc",
        "docs",
        "feat",
        "fix",
        "perf",
        "ref",
        "refactor",
        "revert",
        "style",
        "test",
        "tests",
    },
)
