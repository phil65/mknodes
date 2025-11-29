from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from jinjarope import inspectfilters
import pytest

import mknodes as mk


if TYPE_CHECKING:
    from collections.abc import AsyncIterator


async def example_instances() -> AsyncIterator[mk.MkNode]:
    page = mk.MkPage.with_context()
    for cls in inspectfilters.list_subclasses(mk.MkNode):
        if nodefile := cls.get_nodefile():
            async for i in nodefile.iter_example_instances(page):
                yield i


async def collect():
    return [x async for x in example_instances()]


instances = asyncio.run(collect())


@pytest.mark.parametrize("node", instances, ids=lambda x: x.__class__.__name__)
async def test_if_example_can_get_rendered(node: mk.MkNode):
    if nodefile := node.get_nodefile():
        for v in nodefile.examples.values():
            if "jinja" in v:
                await node.env.render_string_async(v["jinja"])
            if "python" in v:
                node.env.evaluate(v["python"])


@pytest.mark.parametrize("node", instances, ids=lambda x: x.__class__.__name__)
async def test_if_template_output_equals_code_output(node: mk.MkNode):
    if nodefile := node.get_nodefile():
        for k, v in nodefile.output.items():
            if k not in {"markdown", "html"}:
                continue
            result = await node.env.render_string_async(v["template"], dict(node=node))
            assert result == await node._to_markdown()
            break


if __name__ == "__main__":
    pytest.main([__file__])
