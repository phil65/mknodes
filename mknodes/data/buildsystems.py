from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class BuildSystem:
    identifier: str
    build_backend: str
    url: str


hatch = BuildSystem("hatch", "hatchling.build", "https://hatch.pypa.io")
flit = BuildSystem("flit", "flit_core.buildapi", "https://flit.pypa.io")
poetry = BuildSystem("poetry", "poetry.core.masonry.api", "https://python-poetry.org")
setuptools = BuildSystem(
    "setuptools",
    "setuptools.build_meta",
    "https://pypi.org/project/setuptools/",
)
pdm = BuildSystem("pdm", "pdm.backend", "https://pdm.fming.dev/")

BUILD_SYSTEMS: dict[str, BuildSystem] = {
    p.identifier: p for p in [hatch, flit, poetry, setuptools, pdm]
}
