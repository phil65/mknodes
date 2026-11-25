"""The MkDocs and mdBook site engines (writers + mdBook flavour)."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tomllib
from typing import TYPE_CHECKING
from unittest import mock

import pytest

import mknodes as mk
from mknodes.build import NavItem
from mknodes.rendering import materialtext
from mknodes.rendering.mdbook import MdbookRenderer
from mknodes.site import GeneratorSettings, generate_output, yamlconfig
from mknodes.site.writers import EngineNotFoundError, MdbookWriter, MkDocsWriter, get_writer
from mknodes.site.writers.mdbook import nav_to_summary

from .test_generator import BUILD_SCRIPT, MKDOCS_YML, REPO_ROOT


if TYPE_CHECKING:
    import pathlib


HAS_MKDOCS = bool(importlib.util.find_spec("mkdocs") and importlib.util.find_spec("material"))
HAS_MDBOOK = shutil.which("mdbook") is not None


@pytest.fixture
def project(tmp_path: pathlib.Path) -> pathlib.Path:
    (tmp_path / "build.py").write_text(BUILD_SCRIPT)
    (tmp_path / "mkdocs.yml").write_text(MKDOCS_YML.format(repo=REPO_ROOT.as_posix()))
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "handwritten.md").write_text("# Hand-written\n")
    (docs / "page.jinja").write_text("{{ 1 }}")
    (tmp_path / "overrides").mkdir()
    return tmp_path


def test_engine_flavours(project: pathlib.Path):
    settings = GeneratorSettings.load(project)
    flavours = {name: get_writer(name)(settings).resolved_flavor for name in ["zensical", "mkdocs", "mdbook", "markdown"]}  # fmt: skip
    assert flavours == {
        "zensical": "material",
        "mkdocs": "material",
        "mdbook": "mdbook",
        "markdown": "github",
    }


def test_mkdocs_writer(project: pathlib.Path):
    settings = GeneratorSettings.load(project)
    writer = MkDocsWriter(settings)
    cfg_path = writer.write(generate_output(settings, flavor=writer.get_renderer()))
    text = cfg_path.read_text()
    assert "build with `mkdocs build -f mkdocs.generated.yml`" in text
    cfg = yamlconfig.loads(text)
    assert cfg["INHERIT"] == "mkdocs.yml"
    assert cfg["plugins"] == ["search"]  # MkDocs can't load the `mknodes` entry
    assert (project / "docs" / "Section" / "details.md").is_file()
    assert writer.build_command()[1:4] == ["-m", "mkdocs", "build"]


@pytest.mark.skipif(not HAS_MKDOCS, reason="mkdocs / mkdocs-material not installed")
def test_mkdocs_builds_generated_site(project: pathlib.Path):
    settings = GeneratorSettings.load(project)
    writer = MkDocsWriter(settings)
    writer.write(generate_output(settings, flavor=writer.get_renderer()))
    cmd = writer.build_command()
    result = subprocess.run(cmd, cwd=project, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    site = project / "site"
    assert (site / "Section" / "details" / "index.html").is_file()
    assert (site / "handwritten" / "index.html").is_file()
    assert "admonition" in (site / "index.html").read_text()


def test_mkdocs_missing(project: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("mknodes.site.writers.mkdocs._has_module", lambda _name: False)
    writer = MkDocsWriter(GeneratorSettings.load(project))
    with pytest.raises(EngineNotFoundError, match="mkdocs"):
        writer.build_command()


def _write_book(project: pathlib.Path, **kwargs) -> MdbookWriter:
    settings = GeneratorSettings.load(project, **kwargs)
    writer = MdbookWriter(settings)
    writer.write(generate_output(settings, flavor=writer.get_renderer()))
    return writer


def test_mdbook_writer(project: pathlib.Path):
    writer = _write_book(project)
    book = project / "book"
    config = tomllib.loads((book / "book.toml").read_text())
    assert config["book"]["title"] == "Fixture"
    assert config["book"]["src"] == "src"
    assert config["build"] == {"build-dir": "../site", "create-missing": False}
    summary = (book / "src" / "SUMMARY.md").read_text()
    assert summary == (
        "# Fixture\n\n[Intro](index.md)\n\n"
        "- [Section]()\n"
        "    - [Details](Section/details.md)\n"
        "    - [Other](Section/other.md)\n"
    )
    index = (book / "src" / "index.md").read_text()
    assert index.startswith("# Intro\n")  # title heading, no front matter
    assert "> [!NOTE]\n> Hi there" in index  # mdBook renders GitHub alerts
    assert (book / "src" / "handwritten.md").read_text() == "# Hand-written\n"
    assert not (book / "src" / "page.jinja").exists()
    assert "/src/SUMMARY.md" in (book / ".gitignore").read_text()
    # regenerating without changes keeps files untouched
    assert _write_book(project).folder.changed == []
    with mock.patch("shutil.which", return_value="/usr/bin/mdbook"):
        cmd = writer.build_command(extra_args=["--strict"])
    assert cmd == ["mdbook", "build", str(book)]


def test_mdbook_admonish(project: pathlib.Path):
    (project / "pyproject.toml").write_text(
        '[tool.mknodes.mdbook.preprocessor.admonish]\ncommand = "mdbook-admonish"\n'
        '[tool.mknodes.mdbook.output.html]\ndefault-theme = "navy"\n'
    )
    writer = _write_book(project)
    renderer = writer.get_renderer()
    assert isinstance(renderer, MdbookRenderer)
    assert renderer.admonish
    config = tomllib.loads((project / "book" / "book.toml").read_text())
    assert config["preprocessor"]["admonish"]["command"] == "mdbook-admonish"
    assert config["output"]["html"]["default-theme"] == "navy"
    assert config["output"]["html"]["no-section-label"] is True
    index = (project / "book" / "src" / "index.md").read_text()
    assert "```admonish info\nHi there\n```" in index


def test_mdbook_refuses_docs_dir(project: pathlib.Path):
    with pytest.raises(ValueError, match="must not be"):
        _write_book(project, generated_dir="docs")


def test_mdbook_missing(project: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("shutil.which", lambda _name: None)
    writer = MdbookWriter(GeneratorSettings.load(project))
    with pytest.raises(EngineNotFoundError, match="cargo install mdbook"):
        writer.build_command()


@pytest.mark.skipif(not HAS_MDBOOK, reason="mdbook not installed")
def test_mdbook_builds_generated_book(project: pathlib.Path):
    writer = _write_book(project)
    cmd = writer.build_command()
    result = subprocess.run(cmd, cwd=project, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    site = project / "site"
    assert (site / "Section" / "details.html").is_file()
    assert 'href="../index.html"' in (site / "Section" / "details.html").read_text()
    assert "blockquote-tag-note" in (site / "index.html").read_text()


def test_nav_to_summary():
    nav = [
        NavItem("Home", "index.md"),
        NavItem("Guide", children=[NavItem("Guide", "Guide/index.md"), NavItem("A", "A b/a.md")]),
        NavItem("Again", "index.md"),
        NavItem("PyPI", "https://pypi.org"),
    ]
    assert nav_to_summary(nav, "T [x]") == (
        "# T [x]\n\n[Home](index.md)\n\n- [Guide](Guide/index.md)\n    - [A](A%20b/a.md)\n"
    )


@pytest.mark.parametrize("flavor", ["github", "mdbook"])
async def test_code_block_options_degrade(flavor: str):
    page = mk.MkPage("Code")
    page += '``` py title="Setup `x`" hl_lines="2"\nx = 1\n```'
    page += "```rust,ignore\nfn main() {}\n```"
    page += mk.MkCode("y = 2", language="python", title="y.py")
    md = await page.to_markdown(flavor=flavor)
    assert "```rust,ignore\n" in md
    assert "**Setup `x`**\n\n```py\nx = 1\n```" in md
    assert "**y.py**\n\n```python\ny = 2\n```" in md


def test_parse_fence_info():
    assert materialtext.parse_fence_info("{.python  title='a b' linenums='4'}") == (
        "python",
        {"title": "a b", "linenums": "4"},
    )
    assert materialtext.parse_fence_info('py title="x"') == ("py", {"title": "x"})
    assert materialtext.parse_fence_info("rust,ignore") == ("rust,ignore", {})


@pytest.mark.parametrize("flavor", ["github", "mdbook"])
async def test_hand_written_blocks_degrade(flavor: str):
    page = mk.MkPage("Blocks")
    page += '/// details | "Why?"\n    type: warning\nBecause.\n///'
    page += "/// html | div[style='x']\nInside\n///"
    page += "::: mknodes.rendering.github.alert\n    options:\n      show_root_heading: true"
    md = await page.to_markdown(flavor=flavor)
    assert "<details>\n<summary>Why?</summary>\n\nBecause." in md
    assert "///" not in md
    assert "Inside" in md
    assert ":::" not in md
    assert '<a id="mknodes.rendering.github.alert"></a>' in md


async def test_admonish_blocks():
    page = mk.MkPage("Blocks")
    page += '!!! tip "Hint"\n    Text'
    page += "/// details | More\nHidden\n///"
    md = await page.to_markdown(flavor=MdbookRenderer(admonish=True))
    assert '```admonish tip title="Hint"\nText\n```' in md
    assert '```admonish note title="More" collapsible=true\nHidden\n```' in md
