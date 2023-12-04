from __future__ import annotations

from jinjarope import inspectfilters
import pytest

import mknodes as mk


def example_instances():
    page = mk.MkPage.with_context()
    for cls in inspectfilters.list_subclasses(mk.MkNode):
        if cls.nodefile:
            yield from cls.nodefile.iter_example_instances(page)


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
def test_if_example_can_get_rendered(node):
    if nodefile := node.nodefile:
        for v in nodefile.examples.values():
            if "jinja" in v:
                node.env.render_string(v["jinja"])
            if "python" in v:
                node.env.evaluate(v["python"])


@pytest.mark.parametrize("node", example_instances(), ids=lambda x: x.__class__.__name__)
def test_if_template_output_equals_code_output(node: mk.MkNode):
    if nodefile := node.nodefile:
        for k, v in nodefile.output.items():
            if k not in ["markdown", "html"]:
                continue
            result = node.env.render_string(v["template"], dict(node=node))
            assert result == node._to_markdown()
            break
