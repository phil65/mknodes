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
            if v.jinja:
                await node.env.render_string_async(v.jinja)
            if v.python:
                node.env.evaluate(v.python)


@pytest.mark.parametrize("node", instances, ids=lambda x: x.__class__.__name__)
async def test_if_template_output_equals_code_output(node: mk.MkNode):
    if nodefile := node.get_nodefile():
        for k, v in nodefile.output.items():
            if k not in {"markdown", "html"}:
                continue
            result = await node.env.render_string_async(v.template, dict(node=node))
            assert result == await node.to_md_unprocessed()
            break


@pytest.mark.parametrize("node", instances, ids=lambda x: x.__class__.__name__)
async def test_resource_collection_snapshot(node: mk.MkNode, snapshot):
    """Test that resource/dependency collection remains stable across changes.

    This captures the CSS, JS, markdown extensions, plugins, assets, and packages
    required by each node type. If this test fails after changes, verify that the
    new resource requirements are intentional and update snapshots with --snapshot-update.
    """
    resources = await node.get_resources()

    # Convert to serializable dict
    snapshot_data = {
        "css": [str(css) for css in resources.css],
        "js": [str(js) for js in resources.js],
        "markdown_extensions": dict(resources.markdown_extensions),
        "plugins": [p.plugin_name for p in resources.plugins],
        "assets": [str(a) for a in resources.assets],
        "packages": [p.package_name for p in resources.packages],
    }

    # Convert to YAML string for snapshot (handles functions properly)
    import yamling

    snapshot_str = yamling.dump_yaml(
        snapshot_data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=True,
    )
    snapshot.assert_match(snapshot_str, "resources.yaml")


if __name__ == "__main__":
    pytest.main([__file__])
