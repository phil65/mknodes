from __future__ import annotations

import pytest

import mknodes as mk
from mknodes.treelib import noderesolver


def test_resolver():
    resolver = noderesolver.MkNodeResolver()
    root = mk.MkNav()
    sub = root.add_nav("SubNav")
    page = sub.add_page("Test")
    page += mk.MkAdmonition("Test")
    result = resolver.glob("*/*/MkAdm*", root)
    assert result


if __name__ == "__main__":
    pytest.main([__file__])
