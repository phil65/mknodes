from __future__ import annotations

import logging


logger = logging.getLogger(__name__)


class InstallMethod:
    def __init__(self, project: str):
        self.project = project

    def info_text(self) -> str:
        raise NotImplementedError

    def install_instructions(self) -> str:
        raise NotImplementedError


class PipInstall(InstallMethod):
    def info_text(self):
        return (
            "The latest released version is available at the [Python "
            f"package index](https://pypi.org/project/{self.project})."
        )

    def install_instructions(self):
        return f"pip install {self.project}"


class PipXInstall(InstallMethod):
    def info_text(self):
        return (
            "[pipx](https://github.com/pypa/pipx) allows for the "
            "global installation of Python applications in isolated environments."
        )

    def install_instructions(self):
        return f"pipx install {self.project}"


class CondaForgeInstall(InstallMethod):
    def info_text(self):
        return (
            "See the "
            f"[feedstock](https://github.com/conda-forge/{self.project}-feedstock) "
            "for more details."
        )

    def install_instructions(self):
        return f"conda install -c conda-forge {self.project}"


class HomebrewInstall(InstallMethod):
    def info_text(self):
        return (
            f"See the [formula](https://formulae.brew.sh/formula/{self.project}) "
            "for more details."
        )

    def install_instructions(self):
        return f"brew install {self.project}"


if __name__ == "__main__":
    instructions = PipInstall("mknodes")
    print(instructions.info_text())
