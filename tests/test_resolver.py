from __future__ import annotations

from mknodes.utils import noderesolver


def test_resolver(full_tree):
    resolver = noderesolver.MkNodeResolver()
    result = resolver.glob("*/*/MkAdm*", full_tree)
    assert result
