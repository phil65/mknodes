from __future__ import annotations

import pytest

import mknodes as mk


def test_modes():
    mk.MkClassDiagram(mk.MkClassDiagram, mode="mro")
    mk.MkClassDiagram(mk.MkClassDiagram, mode="subclasses")
    mk.MkClassDiagram(mk.MkClassDiagram, mode="baseclasses")


class Meta(type):
    """A metaclass: `Meta.mro()` raises, `Meta.__mro__` works."""


async def test_mro_mode_with_metaclass():
    diagram = mk.MkClassDiagram(Meta, mode="mro")
    md = await diagram.to_markdown()
    assert "Meta" in md
    assert "type" in md


@pytest.mark.parametrize("template", ["classpage.md", "classpage_tabbed.md"])
async def test_class_page_for_metaclass(template: str):
    page = mk.MkClassPage(Meta, template_path=template)
    md = await page.to_markdown()
    assert "Base classes" in md


async def test_class_table_with_classes_unknown_to_griffe():
    # griffe's builtins module has no `type` / `object` members
    md = await mk.MkClassTable([type, object]).to_markdown()
    assert "type" in md
    assert "object" in md


if __name__ == "__main__":
    pytest.main([__file__])
