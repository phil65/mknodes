"""Docstrings are data: the page's Jinja pass must render them literally."""

from __future__ import annotations

import dataclasses
import importlib
import sys
import textwrap

import jinja2
import pytest

import mknodes as mk
from mknodes import rendering
from mknodes.build.builder import DocBuilder


PKG = "jinjadocpkg"
MODULE = '''
"""Module with Jinja syntax in its docstrings."""

from pydantic import BaseModel, Field


class Condition(BaseModel):
    """Evaluates {{ ctx.foo }} for each message.

    {% if ctx.bar %}shown literally{% endif %}
    """

    template: str = Field(examples=["{{ ctx.stats.message_count > 10 }}"])
    """Template like {{ ctx.foo }}."""


def check(value: str = "{{ x }}") -> bool:
    """Return whether {% if value %} holds {# not a comment #}."""
    return bool(value)
'''


@pytest.fixture(scope="module")
def pkg(tmp_path_factory):
    root = tmp_path_factory.mktemp("jinjadoc")
    (root / PKG).mkdir()
    (root / PKG / "__init__.py").write_text(textwrap.dedent(MODULE).lstrip())
    sys.path.insert(0, str(root))
    yield PKG
    sys.path.remove(str(root))
    sys.modules.pop(PKG, None)


@pytest.mark.parametrize("flavor", ["github", "mdbook", "myst", "material"])
async def test_docstrings_skip_the_jinja_pass(pkg: str, flavor: str):
    nav = mk.MkNav()
    nav.add_doc(pkg, section_name="API")
    page = nav.add_page("Mixed")
    page += mk.MkText("{{ 1 + 1 }} from Jinja")  # intended Jinja still renders
    page += mk.MkDocStrings(f"{pkg}.Condition")
    condition = importlib.import_module(pkg).Condition
    page += mk.MkClassTable([condition], layout="compact")  # docstring summary via get_doc
    output = await DocBuilder(flavor=flavor).build(nav)
    text = "\n".join(output.pages.values())
    assert "2 from Jinja" in text
    assert "{{ 1 + 1 }}" not in text
    assert "raw %}" not in text
    assert "| Evaluates {{ ctx.foo }} for each message. |" in text  # compact class table
    if flavor == "material":  # mkdocstrings renders `::: path` blocks after the pass
        assert f"::: {pkg}.Condition" in text
        return
    assert "\nEvaluates {{ ctx.foo }} for each message.\n" in text
    assert "{% if ctx.bar %}shown literally{% endif %}" in text
    assert "Template like {{ ctx.foo }}." in text
    assert "{{ ctx.stats.message_count > 10 }}" in text
    assert "Return whether {% if value %} holds {# not a comment #}." in text


async def test_docstrings_unchanged_without_jinja_pass(pkg: str):
    nav = mk.MkNav()
    page = nav.add_page("API")
    page += mk.MkDocStrings(f"{pkg}.Condition")
    output = await DocBuilder(flavor="github", render_jinja=False).build(nav)
    text = "\n".join(output.pages.values())
    assert "Evaluates {{ ctx.foo }} for each message." in text
    assert "raw %}" not in text


async def test_dataclass_info_is_literal():
    @dataclasses.dataclass
    class Info:
        """Shows {{ ctx.foo }}."""

        value: str = "{% if x %}"

    nav = mk.MkNav()
    page = nav.add_page("Info")
    page += mk.MkDataClassInfo(Info())
    output = await DocBuilder().build(nav)
    text = "\n".join(output.pages.values())
    assert "Shows {{ ctx.foo }}." in text
    assert "'{% if x %}'" in text


@pytest.mark.parametrize(
    "env",
    [
        jinja2.Environment(),
        jinja2.Environment(trim_blocks=True, lstrip_blocks=True),
        jinja2.Environment(block_start_string="<%", block_end_string="%>"),
    ],
)
@pytest.mark.parametrize(
    "text",
    [
        "## x {{ ctx.foo }}\n\n{% if a %}b{% endif %}\n",
        "  a {% endraw %} b {%- endraw -%}\n  indented\n",
        "  {# comment #}\n",
        "plain text\n",
    ],
)
def test_literal_round_trip(env: jinja2.Environment, text: str):
    with rendering.jinja_pass(env):
        wrapped = rendering.literal(text)
    source = f"before\n\n{wrapped}\n\nafter"
    assert env.from_string(source).render() == f"before\n\n{text}\n\nafter"


def test_literal_outside_jinja_pass():
    assert rendering.literal("{{ x }}") == "{{ x }}"
