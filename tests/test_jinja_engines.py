"""Selecting the template engine; node environments of both engines."""

import importlib.util
from typing import TYPE_CHECKING

import jinjarope
import pytest

import mknodes as mk
from mknodes.info import contexts
from mknodes.jinja import nodeenvironment
from mknodes.site.settings import GeneratorSettings


if TYPE_CHECKING:
    import pathlib


HAS_MINIJINJA = importlib.util.find_spec("minijinja") is not None
ENGINES = [
    "jinja2",
    pytest.param("minijinja", marks=pytest.mark.skipif(not HAS_MINIJINJA, reason="no minijinja")),
]


def _node(engine: str | None) -> mk.MkPage:
    ctx = contexts.ProjectContext(env_config=jinjarope.EnvConfig(engine=engine))
    return mk.MkPage(context=ctx)


def test_default_engine_is_jinja2(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv(nodeenvironment.ENGINE_ENV_VAR, raising=False)
    env = mk.MkText("x").env
    assert type(env) is nodeenvironment.NodeEnvironment
    assert env.engine_name == "jinja2"


def test_env_var_selects_engine(monkeypatch: pytest.MonkeyPatch):
    pytest.importorskip("minijinja")
    monkeypatch.setenv(nodeenvironment.ENGINE_ENV_VAR, "minijinja")
    assert mk.MkText("x").env.engine_name == "minijinja"


def test_context_config_wins_over_env_var(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(nodeenvironment.ENGINE_ENV_VAR, "minijinja")
    assert _node("jinja2").env.engine_name == "jinja2"


def test_unknown_engine():
    with pytest.raises(ValueError, match="Unknown template engine"):
        _ = _node("mako").env


def test_settings_set_engine(tmp_path: pathlib.Path):
    pytest.importorskip("minijinja")
    (tmp_path / "pyproject.toml").write_text('[tool.mknodes]\njinja-engine = "minijinja"\n')
    settings = GeneratorSettings.load(tmp_path)
    assert settings.jinja_engine == "minijinja"
    assert settings.get_jinja_config().engine == "minijinja"
    assert GeneratorSettings.load(tmp_path, jinja_engine="jinja2").jinja_engine == "jinja2"


def test_settings_reject_unknown_engine(tmp_path: pathlib.Path):
    settings = GeneratorSettings.load(tmp_path, jinja_engine="mako")
    with pytest.raises(ValueError, match="Unknown template engine"):
        settings.get_jinja_config()


@pytest.mark.parametrize("engine", ENGINES)
def test_render_nodes_collects_nodes(engine: str):
    page = _node(engine)
    template = (
        '{{ "a" | MkHeader }}{{ mk.MkCode("b") }}{{ _mk.MkText("c") }}'
        '{% set n = "d" | MkText %}{{ n.get_text() | upper }}'
    )
    result = page.env.render_nodes(string=template)
    assert page.env.engine_name == engine
    # `_mk` holds the plain classes: their nodes are not collected (same in both engines)
    assert [type(n).__name__ for n in result.children] == ["MkHeader", "MkCode", "MkText"]
    assert result.markdown == "## a``` {.python }\nb\n```cD"


@pytest.mark.parametrize("engine", ENGINES)
def test_filters_with_context_and_environment(engine: str):
    page = _node(engine)
    link = page.env.render_string("{{ 'https://example.com' | url }}", base_url="")
    assert link == "https://example.com"
    assert page.env.render_string('{{ cls | getattr("__name__") }}', cls=mk.MkText) == "MkText"
