from __future__ import annotations

import markdown
import pytest

import mknodes as mk
from mknodes.build import DocBuilder
from mknodes.site.settings import GeneratorSettings
from mknodes.site.writers import ZensicalWriter
from mknodes.utils import diagnostics


EXEC_FENCE = {
    "name": "python",
    "class": "python",
    "validator": "mknodes.mdext.execute_ext.validator",
    "format": "mknodes.mdext.execute_ext.formatter",
}


def _markdown() -> markdown.Markdown:
    from mknodes.mdext import execute_ext

    fence = {**EXEC_FENCE, "validator": execute_ext.validator, "format": execute_ext.formatter}
    return markdown.Markdown(
        extensions=["mknodes.mdext", "pymdownx.superfences"],
        extension_configs={"pymdownx.superfences": {"custom_fences": [fence]}},
    )


def test_report_collect_and_file(tmp_path, monkeypatch):
    path = tmp_path / "diags.jsonl"
    monkeypatch.setenv(diagnostics.FILE_ENV_VAR, str(path))
    with diagnostics.collect() as outer:
        with diagnostics.collect() as inner, diagnostics.page_context("a.md"):
            diag = diagnostics.report("exec", "boom", location="line 3")
        diagnostics.report("fence", "unclosed", page="b.md")
    assert diag == diagnostics.Diagnostic("exec", "boom", "a.md", "line 3")
    assert inner == [diag]
    assert len(outer) == 2  # noqa: PLR2004
    assert diagnostics.load(path) == outer
    assert str(diag) == "a.md (line 3): [exec] boom"
    summary = diagnostics.summary(outer)
    assert summary.startswith("2 build diagnostics (1 exec, 1 fence):")
    assert diagnostics.load(tmp_path / "missing.jsonl") == []


def test_describe_exception_follows_causes():
    try:
        try:
            1 / 0  # noqa: B018
        except ZeroDivisionError as e:
            msg = "Error when rendering"
            raise RuntimeError(msg) from e
    except RuntimeError as e:
        text = diagnostics.describe_exception(e)
    assert text == "RuntimeError: Error when rendering <- ZeroDivisionError: division by zero"


def test_failing_blocks_render_error_and_report():
    text = '/// mknodes\n{{ 1 / 0 }}\n///\n\n```python exec="true"\nraise ValueError("boom")\n```\n'
    with diagnostics.collect() as found, diagnostics.page_context("page.md"):
        html = _markdown().convert(text)
    # The error stays visible in the page (non-strict dev use).
    assert "mknodes-error" in html
    assert "Execution Error: ValueError" in html
    kinds = {d.kind: d for d in found}
    assert kinds["mknodes-block"].page == "page.md"
    assert "ZeroDivisionError" in kinds["mknodes-block"].message
    assert kinds["mknodes-block"].location == "/// mknodes block: {{ 1 / 0 }}"
    assert kinds["exec"].message == "ValueError: boom"
    assert kinds["exec"].location == 'python exec block: raise ValueError("boom")'


def test_working_blocks_report_nothing():
    text = '/// mknodes\n{{ "x" | MkAdmonition }}\n///\n\n```python exec="true"\nprint("hi")\n```\n'
    with diagnostics.collect() as found:
        _markdown().convert(text)
    assert found == []


@pytest.mark.parametrize("flavor", ["material", "github"])
async def test_build_output_collects_diagnostics(flavor: str):
    root = mk.MkNav()
    page = root.add_page("Broken")
    page += mk.MkText("{{ 'x' | MkAdmonition(nonsense=3) }}", render_jinja=True)
    page += "```python\nnever closed\n"
    fine = root.add_page("Fine")
    fine += "All good."
    output = await DocBuilder(flavor=flavor).build(root)
    kinds = sorted(d.kind for d in output.diagnostics)
    assert kinds == ["fence", "node"]
    assert {d.page for d in output.diagnostics} == {"broken.md"}
    node = next(d for d in output.diagnostics if d.kind == "node")
    assert "Failed to create MkAdmonition" in node.message
    fence = next(d for d in output.diagnostics if d.kind == "fence")
    assert fence.location
    assert fence.location.startswith("line ")


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ([], []),
        (["--strict"], ["--strict", "--clean"]),
        (["--strict", "--clean"], ["--strict", "--clean"]),
    ],
)
def test_zensical_strict_build_skips_cache(tmp_path, args: list[str], expected: list[str]):
    """Cached pages don't run the Markdown extensions: strict builds must not use the cache."""
    writer = ZensicalWriter(GeneratorSettings(project_dir=tmp_path))
    cmd = writer.build_command(extra_args=args)
    assert cmd[cmd.index(str(writer.settings.generated_config_path)) + 1 :] == expected
