from __future__ import annotations

import dataclasses
import functools

from mknodes.info import yamlfile
from mknodes.utils import helpers, reprhelpers


@dataclasses.dataclass(frozen=True)
class Hook:
    hook_id: str
    alias: str | None = None
    name: str | None = None
    language_version: str | None = None
    files: list[str] | None = None
    exclude: list[str] | None = None
    types: list[str] | None = None
    types_or: list[str] | None = None
    exclude_types: list[str] | None = None
    args: list[str] | None = None
    stages: list[str] | None = None
    additional_dependencies: list[str] | None = None
    always_run: bool | None = None
    verbose: bool | None = None
    log_file: str | None = None
    entry: str | None = None
    language: str | None = None
    pass_filenames: str | None = None
    fail_fast: bool | None = None
    require_serial: bool | None = None
    description: str | None = None
    minimum_pre_commit_version: str | None = None

    def __repr__(self):
        return reprhelpers.get_dataclass_repr(self)


@dataclasses.dataclass(frozen=True)
class Repository:
    repo: str
    rev: str | None
    hooks: list[Hook] = dataclasses.field(default_factory=list)

    def __repr__(self):
        return reprhelpers.get_dataclass_repr(self)


class PreCommitConfigFile(yamlfile.YamlFile):
    SCHEMA = "https://json.schemastore.org/pre-commit-config.json"

    @property
    def hooks(self) -> list[Hook]:
        return [hook for repo in self.repos for hook in repo.hooks]

    @functools.cached_property
    def repos(self) -> list[Repository]:
        repos = []
        for r in self._data["repos"]:
            hooks = [Hook(hook_id=dct.pop("id"), **dct) for dct in r["hooks"]]
            repo = Repository(repo=r["repo"], rev=r.get("rev"), hooks=hooks)
            repos.append(repo)
        return repos

    @property
    def hook_names(self) -> list[str]:
        return helpers.reduce_list([i.hook_id for i in self.hooks])


if __name__ == "__main__":
    info = PreCommitConfigFile(".pre-commit-config.yaml")
    print(info.repos)
