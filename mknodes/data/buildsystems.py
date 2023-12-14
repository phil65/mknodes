from __future__ import annotations

import dataclasses
from typing import Literal


RAW_GITHUB = "https://raw.githubusercontent.com"

BuildSystemStr = Literal[
    "hatch",
    "flit",
    "poetry",
    "setuptools",
    "pdm",
    "meson_python",
    "maturin",
]


@dataclasses.dataclass(frozen=True)
class BuildSystem:
    identifier: BuildSystemStr
    build_backend: str
    url: str
    env_setup_cmd: str | None
    logo: str | None = None
    run_prefix: str = ""
    install_url: str | None = None


hatch = BuildSystem(
    identifier="hatch",
    build_backend="hatchling.build",
    url="https://hatch.pypa.io",
    logo="https://raw.githubusercontent.com/pypa/hatch/master/docs/assets/images/logo.svg",
    env_setup_cmd="hatch env create",
    run_prefix="hatch run ",
    install_url=f"{RAW_GITHUB}/pypa/hatch/master/docs/install.md",
)
flit = BuildSystem(
    identifier="flit",
    build_backend="flit_core.buildapi",
    logo="https://flit.pypa.io/en/stable/_static/flit_logo_nobg_cropped.svg",
    url="https://flit.pypa.io",
    env_setup_cmd="flit install",
)
poetry = BuildSystem(
    identifier="poetry",
    build_backend="poetry.core.masonry.api",
    url="https://python-poetry.org",
    logo="https://python-poetry.org/images/logo-origami.svg",
    env_setup_cmd="poetry install",
    run_prefix="poetry run ",
)
setuptools = BuildSystem(
    identifier="setuptools",
    build_backend="setuptools.build_meta",
    logo="https://setuptools.pypa.io/en/latest/_images/banner-640x320.svg",
    url="https://pypi.org/project/setuptools/",
    env_setup_cmd=None,
)
pdm = BuildSystem(
    identifier="pdm",
    build_backend="pdm.backend",
    logo="https://raw.githubusercontent.com/pdm-project/pdm/main/docs/docs/assets/logo_big.png",
    url="https://pdm.fming.dev/",
    env_setup_cmd="pdm install",
    run_prefix="pdm run ",
    install_url=f"{RAW_GITHUB}/pdm-project/pdm/main/docs/docs/index.md#Installation",
)
mesonpy = BuildSystem(
    identifier="meson_python",
    build_backend="mesonpy",
    url="https://github.com/mesonbuild/meson-python",
    logo="https://mesonbuild.com/assets/images/meson_logo.png",
    env_setup_cmd=None,
    install_url=(
        "https://meson-python.readthedocs.io/en/latest/how-to-guides/first-project.html"
    ),
)

maturin = BuildSystem(
    identifier="maturin",
    build_backend="maturin",
    url="https://www.maturin.rs",
    env_setup_cmd=None,
    install_url="https://www.maturin.rs/installation",
)

BUILD_SYSTEMS: dict[BuildSystemStr, BuildSystem] = {
    p.identifier: p for p in [hatch, flit, poetry, setuptools, pdm, mesonpy, maturin]
}
