from __future__ import annotations

from mknodes.treelib import noderesolver


def test_resolver(mknodes_project):
    resolver = noderesolver.MkNodeResolver()
    result = resolver.glob("*/*/MkAdm*", mknodes_project._root)
    assert result


def resolving_files(mknodes_project):
    mknodes_project.all_files()
