import dataclasses
from typing import Literal

from mknodes.utils import log


logger = log.get_logger(__name__)

ConventionTypeStr = Literal["conventional_commits", "basic"]


@dataclasses.dataclass(frozen=True)
class CommitType:
    typ: str
    description: str
    icon: str | None = None


TYPES = [
    CommitType("build", "About packaging, building wheels, etc.", "👷"),
    CommitType("chore", "About packaging or repo/files management.", "📦"),
    CommitType("ci", "About Continuous Integration.", "🚀"),
    CommitType("deps", "Dependencies update.", "⬆️"),
    CommitType("doc", "About documentation.", "📚"),
    CommitType("docs", "About documentation.", "📚"),
    CommitType("feat", "New feature.", "✨"),
    CommitType("fix", "Bug fix.", "🐛"),
    CommitType("ref", "Code refactoring.", "🔨"),
    CommitType("revert", "Code revert.", "⏪"),
    CommitType("add", "Code Addition.", "⚡"),
    CommitType("change", "Code change.", "⚡"),
    CommitType("remove", "Code removal.", "🔥"),
    CommitType("merge", "Code merge.", "🔀"),
    CommitType("perf", "About performance.", "🐎"),
    CommitType("refactor", "Changes that are not features or bug fixes.", "🔨"),
    CommitType("style", "A change in code style/format.", "🎨"),
    CommitType("test", "About tests.", "🚨"),
    CommitType("tests", "About tests.", "🚨"),
]


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


def get_types(
    types: list[CommitTypeStr] | ConventionTypeStr,
) -> list[CommitType]:
    match types:
        case "basic":
            commit_types = list(basic.types)
        case "conventional_commits" | "angular" | None:
            commit_types = list(conventional_commits.types)
        case _:
            commit_types = types
    return [i for i in TYPES if i.typ in commit_types]


@dataclasses.dataclass(frozen=True)
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
