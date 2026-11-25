from __future__ import annotations

from unittest import mock

import pytest
from typer.testing import CliRunner

from mknodes import cli
from mknodes.build import BuildOutput
from mknodes.utils import diagnostics


def _engine_reports(*diags: diagnostics.Diagnostic):
    """Fake engine run: write diagnostics to the file given by the environment."""

    def call(cmd, env):
        with mock.patch.dict("os.environ", env):
            for diag in diags:
                diagnostics.report(diag.kind, diag.message, page=diag.page)
        return 0

    return call


@pytest.fixture
def generate():
    writer = mock.Mock()
    writer.build_command.return_value = ["zensical", "build"]
    output = BuildOutput()
    with mock.patch("mknodes.cli.site._generate", return_value=(writer, output)) as mocked:
        yield mocked


@pytest.mark.parametrize("engine_args", [[], ["--engine", "zensical"], ["-e", "zensical"]])
def test_build(generate, engine_args: list[str]):
    build_fn = "mknodes.site:MkDefaultWebsite"
    args = ["build", "--config-path", "mkdocs.yml", "--build-fn", build_fn, "-s"]
    with mock.patch("subprocess.call", return_value=0) as call:
        result = CliRunner().invoke(cli.cli, args + engine_args, catch_exceptions=False)
    assert result.exit_code == 0
    settings, engine = generate.call_args.args
    assert engine == "zensical"
    assert settings.build_fn == build_fn
    writer, _output = generate.return_value
    writer.build_command.assert_called_once_with(extra_args=["--strict"])
    assert call.call_args.args == (["zensical", "build"],)
    assert diagnostics.FILE_ENV_VAR in call.call_args.kwargs["env"]


def test_build_propagates_exit_code(generate):
    with mock.patch("subprocess.call", return_value=3):
        result = CliRunner().invoke(cli.cli, ["build"], catch_exceptions=False)
    assert result.exit_code == 3  # noqa: PLR2004


@pytest.mark.parametrize("command", ["build", "serve", "generate"])
def test_unsupported_engine_is_rejected(generate, command: str):
    result = CliRunner().invoke(cli.cli, [command, "--engine", "hugo"])
    assert result.exit_code == 2  # noqa: PLR2004
    assert "Unsupported engine 'hugo'" in result.output
    generate.assert_not_called()


@pytest.mark.parametrize("command", ["build", "serve"])
def test_missing_mdbook_fails_before_generating(generate, command: str):
    with mock.patch("shutil.which", return_value=None):
        result = CliRunner().invoke(cli.cli, [command, "--engine", "mdbook"])
    assert result.exit_code == 1
    generate.assert_not_called()


def test_generate_works_without_mdbook(generate):
    with mock.patch("shutil.which", return_value=None):
        result = CliRunner().invoke(cli.cli, ["generate", "--engine", "mdbook"])
    assert result.exit_code == 0
    assert generate.call_args.args[1] == "mdbook"


def test_removed_commands():
    result = CliRunner().invoke(cli.cli, ["create-config"])
    assert result.exit_code != 0


if __name__ == "__main__":
    pytest.main([__file__])


def test_help_keeps_brackets():
    # Rich markup used to swallow "[tool.mknodes]" ("configured in `` of ...").
    result = CliRunner().invoke(cli.cli, ["generate", "--help"], terminal_width=200)
    assert result.exit_code == 0
    assert "[tool.mknodes]" in result.output


ENGINE_DIAG = diagnostics.Diagnostic("exec", "ValueError: boom", page="broken.md")
NODE_DIAG = diagnostics.Diagnostic("node", "Failed to create MkText", page="index.md")


def test_build_collects_engine_diagnostics_non_strict(generate):
    with (
        mock.patch("subprocess.call", side_effect=_engine_reports(ENGINE_DIAG)),
        mock.patch("mknodes.cli.site._report_diagnostics") as report,
    ):
        result = CliRunner().invoke(cli.cli, ["build"], catch_exceptions=False)
    assert result.exit_code == 0
    report.assert_called_once_with([ENGINE_DIAG], strict=False)
    writer, _output = generate.return_value
    writer.build_command.assert_called_once_with(extra_args=[])


@pytest.mark.parametrize("source", ["engine", "generator"])
def test_strict_build_fails_on_diagnostics(generate, source: str):
    _writer, output = generate.return_value
    diags = (ENGINE_DIAG,) if source == "engine" else ()
    if source == "generator":
        output.diagnostics.append(NODE_DIAG)
    with (
        mock.patch("subprocess.call", side_effect=_engine_reports(*diags)),
        mock.patch("mknodes.cli.site._report_diagnostics") as report,
    ):
        result = CliRunner().invoke(cli.cli, ["build", "--strict"], catch_exceptions=False)
    assert result.exit_code == 1
    found = report.call_args.args[0]
    assert found == [ENGINE_DIAG if source == "engine" else NODE_DIAG]
    assert report.call_args.kwargs == {"strict": True}


def test_strict_build_passes_without_diagnostics(generate):
    with mock.patch("subprocess.call", return_value=0):
        result = CliRunner().invoke(cli.cli, ["build", "--strict"], catch_exceptions=False)
    assert result.exit_code == 0


def test_strict_setting_from_pyproject(generate, tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text("[tool.mknodes]\nstrict = true\n")
    monkeypatch.chdir(tmp_path)
    generate.return_value[1].diagnostics.append(NODE_DIAG)
    with mock.patch("subprocess.call", return_value=0):
        result = CliRunner().invoke(cli.cli, ["build"], catch_exceptions=False)
    assert result.exit_code == 1
    assert generate.call_args.args[0].strict is True


def test_strict_generate_fails_on_diagnostics(generate):
    generate.return_value[1].diagnostics.append(NODE_DIAG)
    assert CliRunner().invoke(cli.cli, ["generate"]).exit_code == 0
    assert CliRunner().invoke(cli.cli, ["generate", "--strict"]).exit_code == 1
