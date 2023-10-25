from __future__ import annotations

import dataclasses

from mknodes.info import yamlfile


@dataclasses.dataclass(frozen=True)
class Hook:
    hook_id: str
    args: list[str] | None = None
    stages: list[str] | None = None
    additional_dependencies: list[str] | None = None


class PreCommitConfigFile(yamlfile.YamlFile):
    SCHEMA = "https://json.schemastore.org/pre-commit-config.json"

    @property
    def hooks(self) -> list[Hook]:
        hook_list = []
        for repo in self._data["repos"]:
            for hook_dct in repo["hooks"]:
                hook = Hook(
                    hook_dct["id"],
                    args=hook_dct.get("args"),
                    stages=hook_dct.get("stages"),
                    additional_dependencies=hook_dct.get("additional_dependencies"),
                )
                hook_list.append(hook)
        return hook_list

    @property
    def hook_names(self):
        return [i.hook_id for i in self.hooks]


if __name__ == "__main__":
    info = PreCommitConfigFile(".pre-commit-config.yaml")
    print(info.hook_names)
