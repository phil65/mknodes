"""Project metadata model: distribution, import packages, repository."""

from __future__ import annotations

import os
import sys
import textwrap
from typing import TYPE_CHECKING

import git
import pytest
from typer.testing import CliRunner

from mknodes import cli
from mknodes.info import folderinfo, packageinfo, projectlayout, reporegistry
from mknodes.utils import icons


if TYPE_CHECKING:
    import pathlib


UV_BUILD = '[build-system]\nrequires = ["uv_build"]\nbuild-backend = "uv_build"\n'
LICENSE = "MIT License\n\nCopyright (c) 2026 Test\n"


def _write(root: pathlib.Path, files: dict[str, str]) -> pathlib.Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text), encoding="utf-8")
    return root


def _git_init(root: pathlib.Path, remote: str | None = None) -> None:
    repo = git.Repo.init(root, initial_branch="main")
    with repo.config_writer() as cw:
        cw.set_value("user", "name", "Test")
        cw.set_value("user", "email", "test@example.com")
    repo.git.add(A=True)
    repo.index.commit("feat: initial commit")
    if remote:
        repo.create_remote("origin", remote)


@pytest.fixture(autouse=True)
def _isolate(monkeypatch: pytest.MonkeyPatch):
    # git hooks (e.g. pre-commit) export GIT_DIR / GIT_INDEX_FILE: don't touch that repo
    for var in [k for k in os.environ if k.startswith("GIT_")]:
        monkeypatch.delenv(var)
    monkeypatch.setattr(sys, "path", list(sys.path))
    before = set(sys.modules)
    yield
    for name in set(sys.modules) - before:
        if name.startswith(("fake_", "mkfixture")):
            del sys.modules[name]


@pytest.fixture
def three_names(tmp_path: pathlib.Path) -> pathlib.Path:
    """Like clawd-code-sdk: repo, distribution and import package are named differently."""
    root = tmp_path / "local-checkout"
    _write(
        root,
        {
            "pyproject.toml": f"""\
                [project]
                name = "fake-clawd-sdk"
                version = "1.2.3"
                description = "Three names"
                license = "MIT"
                authors = [{{ name = "Test", email = "test@example.com" }}]
                dependencies = []

                [project.urls]
                Documentation = "https://acme.github.io/agent-sdk-python/"
                Source = "https://github.com/acme/agent-sdk-python"
                "Spec: Agent SDK (Python, upstream)" = "https://github.com/up/agent-sdk-python"
                "Spec: Settings schema" = "https://json.schemastore.org/settings.json"
                "Spec: no host" = "not a url"

                {UV_BUILD}
                [tool.uv.build-backend]
                module-name = "fake_clawd_sdk"
                """,
            "src/fake_clawd_sdk/__init__.py": '''\
                """Fake SDK."""

                __all__ = ["Client"]


                class Client:
                    """A client."""
                ''',
            "README.md": "# Fake SDK\n",
            "LICENSE": LICENSE,
        },
    )
    _git_init(root, remote="https://example.invalid/acme/agent-sdk-python.git")
    return root


@pytest.fixture
def multi_package(tmp_path: pathlib.Path) -> pathlib.Path:
    """Like agentpool: several top-level modules, listed as uv_build `module-name`."""
    root = tmp_path / "fakepool"
    _write(
        root,
        {
            "pyproject.toml": f"""\
                [project]
                name = "fakepool"
                version = "0.1.0"
                description = "Several packages"
                license = "MIT"
                dependencies = []

                [project.urls]
                Source = "https://github.com/acme/fakepool"

                {UV_BUILD}
                [tool.uv.build-backend]
                module-name = ["fake_pool_config", "fakepool", "fake_pool_server"]
                """,
            "src/fakepool/__init__.py": '"""Main package."""\n\n\nclass Pool:\n    """A pool."""\n',
            "src/fake_pool_config/__init__.py": '"""Config."""\n\n\nclass Config:\n    """Cfg."""\n',
            "src/fake_pool_server/__init__.py": '"""Server."""\n',
            # not part of the distribution (not in module-name)
            "src/fake_pool_sync/__init__.py": '"""Not shipped."""\n',
            "README.md": "# Fakepool\n",
            "LICENSE": LICENSE,
        },
    )
    _git_init(root)
    return root


@pytest.fixture
def flat_layout(tmp_path: pathlib.Path) -> pathlib.Path:
    """Hatch project with the package next to pyproject.toml (no build config)."""
    root = tmp_path / "flat"
    _write(
        root,
        {
            "pyproject.toml": """\
                [project]
                name = "fake-flat"
                version = "0.2.0"
                description = "Flat layout"
                license = "MIT"
                dependencies = []

                [build-system]
                requires = ["hatchling"]
                build-backend = "hatchling.build"
                """,
            "fake_flat/__init__.py": '"""Flat package."""\n\n\nclass Flat:\n    """Flat."""\n',
            "tests/__init__.py": "",
            "docs/index.md": "# Docs\n",
            "duties.py": "",
            "README.md": "# Flat\n",
            "LICENSE": LICENSE,
        },
    )
    _git_init(root)
    return root


@pytest.fixture
def src_layout(tmp_path: pathlib.Path) -> pathlib.Path:
    """Setuptools src layout with `packages.find`, plus a namespace package."""
    root = tmp_path / "srcproj"
    _write(
        root,
        {
            "pyproject.toml": """\
                [project]
                name = "fake.src-proj"
                version = "0.3.0"
                description = "Src layout"
                license = "MIT"
                dependencies = []

                [build-system]
                requires = ["setuptools"]
                build-backend = "setuptools.build_meta"

                [tool.setuptools.packages.find]
                where = ["src"]
                """,
            "src/fake_src_proj/__init__.py": '"""Src package."""\n\n\nclass Src:\n    """S."""\n',
            "src/fake_src_helpers/__init__.py": '"""Helpers."""\n',
            "README.md": "# Src\n",
            "LICENSE": LICENSE,
        },
    )
    _git_init(root)
    return root


def _layout(root: pathlib.Path) -> projectlayout.ProjectLayout:
    info = folderinfo.FolderInfo(root)
    return info.layout


def test_three_names(three_names: pathlib.Path):
    info = folderinfo.FolderInfo(three_names)
    assert info.git.repo_name == "agent-sdk-python"
    assert info.distribution_name == "fake-clawd-sdk"
    assert info.package_name == "fake_clawd_sdk"
    assert info.package_names == ["fake_clawd_sdk"]
    assert info.layout.packages[0].source == "uv_build"
    assert info.module.__name__ == "fake_clawd_sdk"
    assert info.repository_url == "https://github.com/acme/agent-sdk-python"
    assert info.repository_username == "acme"
    assert info.repository_name == "agent-sdk-python"
    # not installed: metadata comes from pyproject.toml
    assert isinstance(info.info.distribution, packageinfo.PyProjectDistribution)
    assert info.info.version == "1.2.3"
    assert info.info.urls["Spec: Agent SDK (Python, upstream)"] == (
        "https://github.com/up/agent-sdk-python"
    )
    links = [i["link"] for i in info.social_info]
    assert links[0] == "https://github.com/acme/agent-sdk-python"
    assert links[-1] == "https://pypi.org/project/fake-clawd-sdk/"
    ctx = info.context
    assert ctx.package_name == "fake_clawd_sdk"
    assert ctx.distribution_name == "fake-clawd-sdk"


def test_multi_package(multi_package: pathlib.Path):
    layout = _layout(multi_package)
    # primary (matches the distribution name) first, then the configured order
    assert layout.package_names == ["fakepool", "fake_pool_config", "fake_pool_server"]
    assert {p.source for p in layout.packages} == {"uv_build"}
    assert layout.layout == "src"


def test_configured_primary_package(multi_package: pathlib.Path):
    path = multi_package / "pyproject.toml"
    path.write_text(path.read_text() + '\n[tool.mknodes]\npackage = "fake_pool_server"\n')
    assert _layout(multi_package).package_names[0] == "fake_pool_server"


def test_configured_package_list(multi_package: pathlib.Path):
    path = multi_package / "pyproject.toml"
    text = '\n[tool.mknodes]\npackages = ["fake_pool_sync", "fakepool"]\n'
    path.write_text(path.read_text() + text)
    layout = _layout(multi_package)
    assert layout.package_names == ["fakepool", "fake_pool_sync"]
    assert layout.packages[1].source == "tool.mknodes"


def test_flat_layout(flat_layout: pathlib.Path):
    layout = _layout(flat_layout)
    assert layout.layout == "flat"
    assert layout.package_names == ["fake_flat"]
    assert layout.packages[0].source == "scan"
    assert folderinfo.FolderInfo(flat_layout).module.__name__ == "fake_flat"


def test_src_layout_setuptools(src_layout: pathlib.Path):
    layout = _layout(src_layout)
    assert layout.distribution == "fake.src-proj"
    assert layout.package_names == ["fake_src_proj", "fake_src_helpers"]
    assert layout.packages[0].source == "setuptools"


def test_scan_finds_namespace_packages(tmp_path: pathlib.Path):
    _write(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "fake-ns"\n',
            "src/fake_ns/plugin/__init__.py": "",
            "src/fake_mod.py": "",
        },
    )
    layout = projectlayout.ProjectLayout.resolve(
        tmp_path, {"project": {"name": "fake-ns"}}, fallback_name="x"
    )
    assert layout.package_names == ["fake_ns", "fake_mod"]
    assert layout.packages[0].is_namespace


def test_installed_distribution_top_level():
    # mknodes itself: no pyproject given -> installed metadata (editable: files scan)
    packages = projectlayout._from_installed("mknodes")
    assert [p.name for p in packages] in ([], ["mknodes"])
    jinja = projectlayout._from_installed("jinja2")
    assert [p.name for p in jinja] == ["jinja2"]


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("not a url", None),
        (" upstream)", None),
        ("", None),
        ("https://localhost/x", None),
        ("http://[invalid", None),
        ("https://json.schemastore.org/settings.json", None),
        ("https://x.com/someone", "fa-brands:twitter"),
    ],
)
def test_icon_for_url_never_raises(url: str, expected: str | None):
    assert icons.icon_for_url(url) == expected
    assert icons.icon_for_url(url, default="mdi:link") == (expected or "mdi:link")


def test_project_url_labels_with_commas():
    assert packageinfo._split_project_url("Spec: A (Python, upstream), https://a.b/c") == (
        "Spec: A (Python, upstream)",
        "https://a.b/c",
    )
    assert packageinfo._split_project_url("Source,https://a.b") == ("Source", "https://a.b")


@pytest.mark.parametrize(
    ("fixture", "api_paths"),
    [
        ("three_names", ["API/index.md", "API/Client.md"]),
        (
            "multi_package",
            [
                "API/fakepool/index.md",
                "API/fakepool/Pool.md",
                "API/fake_pool_config/Config.md",
                "API/fake_pool_server/index.md",
            ],
        ),
        ("flat_layout", ["API/index.md", "API/Flat.md"]),
        ("src_layout", ["API/fake_src_proj/Src.md", "API/fake_src_helpers/index.md"]),
    ],
)
def test_build_default_site(
    fixture: str,
    api_paths: list[str],
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
):
    root: pathlib.Path = request.getfixturevalue(fixture)
    monkeypatch.chdir(root)
    monkeypatch.setattr(reporegistry.registry, "_repos", {})
    args = ["build", "--engine", "markdown"]
    result = CliRunner().invoke(cli.cli, args, catch_exceptions=False)
    assert result.exit_code == 0, result.output
    site = root / "docs"  # the markdown engine has no build step
    for rel in api_paths:
        assert (site / rel).is_file(), sorted(str(p.relative_to(site)) for p in site.rglob("*"))
    assert "fake_pool_sync" not in {p.name for p in site.rglob("*")}
