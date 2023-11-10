from __future__ import annotations

import dataclasses

from typing import ClassVar, Literal

from mknodes.utils import log


logger = log.get_logger(__name__)

InstallMethodStr = Literal["pip", "pipx", "conda_forge", "homebrew"]


@dataclasses.dataclass(frozen=True)
class InstallMethod:
    ID: ClassVar
    project: str

    def info_text(self) -> str:
        raise NotImplementedError

    def install_instructions(self) -> str:
        raise NotImplementedError

    @classmethod
    def get_installmethods(cls):
        return {i.ID: i for i in cls.__subclasses__()}

    @classmethod
    def by_id(cls, identifier: str):
        return cls.get_installmethods()[identifier]


class PipInstall(InstallMethod):
    ID = "pip"

    def info_text(self):
        return (
            "The latest released version is available at the [Python "
            f"package index](https://pypi.org/project/{self.project})."
        )

    def install_instructions(self):
        return f"pip install {self.project}"


class PipXInstall(InstallMethod):
    ID = "pipx"

    def info_text(self):
        return (
            "[pipx](https://github.com/pypa/pipx) allows for the "
            "global installation of Python applications in isolated environments."
        )

    def install_instructions(self):
        return f"pipx install {self.project}"


class CondaForgeInstall(InstallMethod):
    ID = "conda_forge"

    def info_text(self):
        return (
            "See the "
            f"[feedstock](https://github.com/conda-forge/{self.project}-feedstock) "
            "for more details."
        )

    def install_instructions(self):
        return f"conda install -c conda-forge {self.project}"


class HomebrewInstall(InstallMethod):
    ID = "homebrew"

    def info_text(self):
        return (
            f"See the [formula](https://formulae.brew.sh/formula/{self.project}) "
            "for more details."
        )

    def install_instructions(self):
        return f"brew install {self.project}"


if __name__ == "__main__":
    instructions = PipInstall("mknodes")
    print(instructions)
