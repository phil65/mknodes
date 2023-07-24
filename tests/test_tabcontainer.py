from __future__ import annotations

import mknodes


def test_tabcontainer():
    tabs = dict(Tab1="Some text", Tab2="Another text")
    node = mknodes.MkTabbed(tabs)
    assert len(node.items) == 2  # noqa: PLR2004
    assert str(node["Tab1"]) == "Some text"
    assert str(node[1]) == "Another text"
    node["Tab3"] = "And another one"
