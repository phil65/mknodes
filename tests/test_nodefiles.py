from __future__ import annotations

from typing import TYPE_CHECKING

from jinjarope import inspectfilters
import pytest

import mknodes as mk


if TYPE_CHECKING:
    from collections.abc import Iterator


def example_instances() -> Iterator[mk.MkNode]:
    page = mk.MkPage.with_context()
    for cls in inspectfilters.list_subclasses(mk.MkNode):
        if nodefile := cls.get_nodefile():
            yield from nodefile.iter_example_instances(page)


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
def test_if_example_can_get_rendered(node: mk.MkNode):
    if nodefile := node.get_nodefile():
        for v in nodefile.examples.values():
            if "jinja" in v:
                node.env.render_string(v["jinja"])
            if "python" in v:
                node.env.evaluate(v["python"])


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
async def test_if_template_output_equals_code_output(node: mk.MkNode):
    if nodefile := node.get_nodefile():
        for k, v in nodefile.output.items():
            if k not in {"markdown", "html"}:
                continue
            result = node.env.render_string(v["template"], dict(node=node))
            assert result == await node._to_markdown()
            break


if __name__ == "__main__":
    pytest.main([__file__])
